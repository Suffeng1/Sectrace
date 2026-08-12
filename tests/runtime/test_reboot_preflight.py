from pathlib import Path
import re


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "sectrace-preflight.ps1"
RUNBOOK = REPO_ROOT / "docs" / "runtime" / "reboot-preflight.md"


def test_reboot_preflight_assets_and_three_modes_exist() -> None:
    assert SCRIPT.is_file()
    assert RUNBOOK.is_file()

    script = SCRIPT.read_text(encoding="utf-8")
    assert 'ValidateSet("code", "runtime", "live")' in script
    assert "ConvertTo-Json" in script
    assert "BLOCKED_MCP_SERVICE_NOT_RUNNING" in script
    assert "MANUAL_REQUIRED" in script


def test_reboot_preflight_script_has_no_mutating_or_messaging_commands() -> None:
    script = SCRIPT.read_text(encoding="utf-8")
    forbidden_invocations = (
        r"(?im)^\s*Start-(?:Process|Service|ScheduledTask)\b",
        r"(?im)^\s*Stop-(?:Process|Service|ScheduledTask)\b",
        r"(?im)^\s*Restart-(?:Service|Computer)\b",
        r"(?im)^\s*(?:&\s*)?docker\s+(?:start|restart|stop|rm)\b",
        r"(?im)^\s*(?:&\s*)?agt\s+(?:apply|create|delete|update)\b",
        r"(?im)^\s*(?:Send-|Approve-|Reject-)\w*\b",
    )
    for pattern in forbidden_invocations:
        assert re.search(pattern, script) is None, pattern

    assert "Get-ScheduledTask" not in script
    assert "docker logs" not in script
    assert "Get-Content" not in script


def test_agents_requires_lowest_necessary_preflight_gate() -> None:
    agents = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    assert "sectrace-preflight.ps1" in agents
    assert "lowest necessary mode" in agents
    assert "new conversation" in agents
    assert "computer reboot" in agents
    assert "runtime mutation" in agents
    assert "must not be used as a launcher" in agents


def test_readme_links_resume_after_reboot_runbook() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    assert "Resume after reboot" in readme
    assert "docs/runtime/reboot-preflight.md" in readme
    assert "scripts/sectrace-preflight.ps1" in readme


def test_runtime_treats_local_demo_ui_as_optional_observation() -> None:
    script = SCRIPT.read_text(encoding="utf-8")
    assert 'Add-Check "local_demo_ui_reachable"' in script
    assert 'Write-Result "BLOCKED_LOCAL_UI"' not in script


def test_runtime_checks_core_tcp_gates_before_optional_demo_and_mcp() -> None:
    script = SCRIPT.read_text(encoding="utf-8")
    ordered_markers = (
        'Add-Check "controller_api_tcp"',
        'Add-Check "model_gateway_tcp"',
        'Add-Check "manager_api_tcp"',
        'Add-Check "local_demo_ui_reachable"',
        'Add-Check "host_mcp_listener"',
    )
    positions = [script.index(marker) for marker in ordered_markers]
    assert positions == sorted(positions)
    assert 'Write-Result "BLOCKED_CONTROLLER_API_TCP"' in script
    assert 'Write-Result "BLOCKED_MODEL_GATEWAY_TCP"' in script
    assert 'Write-Result "BLOCKED_MANAGER_API_TCP"' in script


def test_mcp_listener_is_not_reported_as_process_presence() -> None:
    script = SCRIPT.read_text(encoding="utf-8")
    assert "host_mcp_process_present" not in script
    assert 'Add-Check "host_mcp_listener"' in script
