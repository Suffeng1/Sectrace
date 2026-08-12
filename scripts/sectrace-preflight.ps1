[CmdletBinding()]
param(
    [ValidateSet("code", "runtime", "live")]
    [string]$Mode = "code"
)

$ErrorActionPreference = "SilentlyContinue"
$repoRoot = Split-Path -Parent $PSScriptRoot
$checks = [System.Collections.Generic.List[object]]::new()
$manual = [System.Collections.Generic.List[object]]::new()
$startedAt = [DateTimeOffset]::UtcNow

function Add-Check {
    param([string]$Category, [bool]$Passed, [int]$ExitCode = 0, [string]$State = "checked")
    $checks.Add([ordered]@{ category = $Category; passed = $Passed; exit_code = $ExitCode; state = $State })
}

function Test-TcpPort {
    param([string]$HostName, [int]$Port)
    $client = [Net.Sockets.TcpClient]::new()
    try {
        $async = $client.BeginConnect($HostName, $Port, $null, $null)
        return $async.AsyncWaitHandle.WaitOne(2000) -and $client.Connected
    } catch { return $false } finally { $client.Close() }
}

function Get-ExactContainerRunning {
    param([string]$Name)
    $names = @(docker ps --filter "name=^/$Name$" --format "{{.Names}}" 2>$null)
    return $names.Count -eq 1
}

function Get-AgentResourceReady {
    param([string]$Kind, [string]$Name, [string]$ExpectedPhase)
    $raw = docker exec agentteams-controller agt get $Kind $Name -o json 2>$null
    $exitCode = $LASTEXITCODE
    if ($exitCode -ne 0) { return [ordered]@{ passed = $false; exit_code = $exitCode } }
    try {
        $resource = $raw | Out-String | ConvertFrom-Json
        return [ordered]@{ passed = ([string]$resource.phase -eq $ExpectedPhase); exit_code = 0 }
    } catch { return [ordered]@{ passed = $false; exit_code = 1 } }
}

function Invoke-HostInitialize {
    $body = '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"sectrace-preflight","version":"1.0"}}}'
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:19090/mcp" -Method Post -ContentType "application/json" -Headers @{ Accept = "application/json, text/event-stream" } -Body $body -TimeoutSec 5
        $mediaType = [string]$response.Headers."Content-Type"
        $passed = $response.StatusCode -ge 200 -and $response.StatusCode -lt 300 -and $mediaType -match "(?i)application/json|text/event-stream"
        return [ordered]@{ passed = $passed; exit_code = $(if ($passed) { 0 } else { 1 }); http_category = $(if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 300) { "2xx" } else { "non_2xx" }) }
    } catch { return [ordered]@{ passed = $false; exit_code = 1; http_category = "request_failed" } }
}

function Invoke-CommanderInitialize {
    param([string]$ContainerName)
    $script = @"
const body={jsonrpc:'2.0',id:1,method:'initialize',params:{protocolVersion:'2025-03-26',capabilities:{},clientInfo:{name:'sectrace-preflight',version:'1.0'}}};
fetch('http://host.docker.internal:19090/mcp',{method:'POST',headers:{'content-type':'application/json','accept':'application/json, text/event-stream'},body:JSON.stringify(body)}).then(r=>{const ct=r.headers.get('content-type')||'';const ok=r.status>=200&&r.status<300&&/application\/json|text\/event-stream/i.test(ct);process.stdout.write(JSON.stringify({passed:ok,http_category:r.status>=200&&r.status<300?'2xx':'non_2xx'}));process.exit(ok?0:1)}).catch(()=>process.exit(2));
"@
    $raw = docker exec $ContainerName node -e $script 2>$null
    $exitCode = $LASTEXITCODE
    if ($exitCode -ne 0) { return [ordered]@{ passed = $false; exit_code = $exitCode; http_category = "request_failed" } }
    try {
        $result = $raw | Out-String | ConvertFrom-Json
        return [ordered]@{ passed = ($result.passed -eq $true); exit_code = 0; http_category = [string]$result.http_category }
    } catch { return [ordered]@{ passed = $false; exit_code = 1; http_category = "unavailable" } }
}

function Write-Result {
    param([string]$Status)
    [ordered]@{
        schema_version = "1.0"; mode = $Mode; status = $Status; checks = $checks
        manual_confirmations = $manual
        duration_seconds = [math]::Round(([DateTimeOffset]::UtcNow - $startedAt).TotalSeconds, 1)
        safe_output = $true
    } | ConvertTo-Json -Depth 6 -Compress
}

$formalRepo = (Split-Path -Leaf $repoRoot) -eq "project_005_SecTrace安全事件多Agent协同审计系统"
Add-Check "formal_repository" $formalRepo $(if ($formalRepo) { 0 } else { 1 })
& git -c "safe.directory=$repoRoot" -C $repoRoot rev-parse --is-inside-work-tree 1>$null 2>$null
$gitExit = $LASTEXITCODE
Add-Check "git_repository" ($gitExit -eq 0) $gitExit
$python = Get-Command python -ErrorAction SilentlyContinue
$pythonExit = 1
if ($null -ne $python) { & python --version 1>$null 2>$null; $pythonExit = $LASTEXITCODE }
Add-Check "python_runtime" ($pythonExit -eq 0) $pythonExit
if ($checks.Where({ -not $_.passed }).Count -gt 0) { Write-Result "BLOCKED_CODE_PREFLIGHT"; exit 2 }
if ($Mode -eq "code") { Write-Result "READY_CODE"; exit 0 }

& docker info --format "{{.ServerVersion}}" 1>$null 2>$null
$dockerExit = $LASTEXITCODE
Add-Check "docker_engine" ($dockerExit -eq 0) $dockerExit
if ($dockerExit -ne 0) { Write-Result "BLOCKED_DOCKER_ENGINE"; exit 3 }

$controllerRunning = Get-ExactContainerRunning "agentteams-controller"
$managerRunning = Get-ExactContainerRunning "agentteams-manager"
Add-Check "controller_running" $controllerRunning $(if ($controllerRunning) { 0 } else { 1 })
Add-Check "manager_running" $managerRunning $(if ($managerRunning) { 0 } else { 1 })
if (-not ($controllerRunning -and $managerRunning)) { Write-Result "BLOCKED_AGENTTEAMS_CORE"; exit 4 }

$controllerApiTcp = Test-TcpPort "127.0.0.1" 18001
Add-Check "controller_api_tcp" $controllerApiTcp $(if ($controllerApiTcp) { 0 } else { 1 })
if (-not $controllerApiTcp) { Write-Result "BLOCKED_CONTROLLER_API_TCP"; exit 5 }

$modelGatewayTcp = Test-TcpPort "127.0.0.1" 18080
Add-Check "model_gateway_tcp" $modelGatewayTcp $(if ($modelGatewayTcp) { 0 } else { 1 })
if (-not $modelGatewayTcp) { Write-Result "BLOCKED_MODEL_GATEWAY_TCP"; exit 6 }

$managerApiTcp = Test-TcpPort "127.0.0.1" 18888
Add-Check "manager_api_tcp" $managerApiTcp $(if ($managerApiTcp) { 0 } else { 1 })
if (-not $managerApiTcp) { Write-Result "BLOCKED_MANAGER_API_TCP"; exit 7 }

$resourceFailures = 0
foreach ($worker in @("sectrace-commander", "sectrace-evidence", "sectrace-response", "sectrace-audit")) {
    $state = Get-AgentResourceReady "workers" $worker "Running"
    Add-Check "worker_$($worker.Replace('sectrace-', ''))_running" $state.passed $state.exit_code
    if (-not $state.passed) { $resourceFailures++ }
}
$teamState = Get-AgentResourceReady "teams" "sectrace-audit-team" "Active"
Add-Check "team_active" $teamState.passed $teamState.exit_code
if (-not $teamState.passed) { $resourceFailures++ }
if ($resourceFailures -gt 0) { Write-Result "BLOCKED_AGENT_RESOURCES"; exit 5 }

$localDemoUiReachable = Test-TcpPort "127.0.0.1" 19080
Add-Check "local_demo_ui_reachable" $localDemoUiReachable $(if ($localDemoUiReachable) { 0 } else { 1 }) "optional"

$listener = @(Get-NetTCPConnection -State Listen -LocalPort 19090 -ErrorAction SilentlyContinue).Count -gt 0
Add-Check "host_mcp_listener" $listener $(if ($listener) { 0 } else { 1 })
if (-not $listener) { Write-Result "BLOCKED_MCP_SERVICE_NOT_RUNNING"; exit 7 }

$hostTcp = Test-TcpPort "127.0.0.1" 19090
Add-Check "host_mcp_tcp" $hostTcp $(if ($hostTcp) { 0 } else { 1 })
if (-not $hostTcp) { Write-Result "BLOCKED_HOST_MCP_TCP"; exit 8 }
$hostInitialize = Invoke-HostInitialize
Add-Check "host_mcp_initialize" $hostInitialize.passed $hostInitialize.exit_code $hostInitialize.http_category
if (-not $hostInitialize.passed) { Write-Result "BLOCKED_HOST_MCP_INITIALIZE"; exit 9 }

$commanderNames = @(docker ps --format "{{.Names}}" 2>$null | Where-Object { $_ -match "(?i)sectrace-commander" })
$commanderRunning = $commanderNames.Count -eq 1
Add-Check "commander_container_running" $commanderRunning $(if ($commanderRunning) { 0 } else { 1 })
if (-not $commanderRunning) { Write-Result "BLOCKED_COMMANDER_CONTAINER"; exit 10 }
$commanderName = $commanderNames[0]
& docker exec $commanderName getent hosts host.docker.internal 1>$null 2>$null
$dnsExit = $LASTEXITCODE
Add-Check "commander_dns" ($dnsExit -eq 0) $dnsExit
if ($dnsExit -ne 0) { Write-Result "BLOCKED_COMMANDER_DNS"; exit 11 }

$tcpScript = "const n=require('net'),s=n.createConnection({host:'host.docker.internal',port:19090});let done=false;const finish=c=>{if(done)return;done=true;s.destroy();process.exit(c)};s.setTimeout(2500);s.on('connect',()=>finish(0));s.on('timeout',()=>finish(2));s.on('error',()=>finish(1));"
& docker exec $commanderName node -e $tcpScript 1>$null 2>$null
$commanderTcpExit = $LASTEXITCODE
Add-Check "commander_mcp_tcp" ($commanderTcpExit -eq 0) $commanderTcpExit
if ($commanderTcpExit -ne 0) { Write-Result "BLOCKED_COMMANDER_MCP_TCP"; exit 12 }
$commanderInitialize = Invoke-CommanderInitialize $commanderName
Add-Check "commander_mcp_initialize" $commanderInitialize.passed $commanderInitialize.exit_code $commanderInitialize.http_category
if (-not $commanderInitialize.passed) { Write-Result "BLOCKED_COMMANDER_MCP_INITIALIZE"; exit 13 }
if ($Mode -eq "runtime") { Write-Result "READY_RUNTIME"; exit 0 }

$elementReachable = Test-TcpPort "127.0.0.1" 18088
Add-Check "element_page_reachable" $elementReachable $(if ($elementReachable) { 0 } else { 1 })
if (-not $elementReachable) { Write-Result "BLOCKED_ELEMENT_PAGE"; exit 14 }
foreach ($item in @("user_logged_in", "correct_worker_room", "structured_manager_mention", "matrix_channel_running_configured_connected", "no_pending_approval")) {
    $manual.Add([ordered]@{ category = $item; status = "MANUAL_REQUIRED" })
}
Write-Result "MANUAL_REQUIRED"
exit 20
