# R-08AR Independent QA

- Date: 2026-08-09
- Result: **PASS**
- Current independent runtime gate: `BLOCKED_DOCKER_ENGINE`
- Recorded R-08AR runtime gate: `BLOCKED_LOCAL_UI` (point-in-time evidence, not reproduced in the later QA run)

## Evidence reviewed

- `docs/runtime/reboot-preflight.md`
- `scripts/sectrace-preflight.ps1`
- `tests/runtime/test_reboot_preflight.py`
- `AGENTS.md`
- `README.md`
- `docs/verification/R-08AR-reboot-preflight.md`
- `docs/handoffs/H-R08AR.md`

## Focused regression

```text
....                                                                     [100%]
4 passed in 0.01s
```

The tests independently confirm the three declared modes, JSON result path, key blocked/manual categories, static mutation prohibitions, mandatory AGENTS gate, and README entry.

## Independent mode execution

### Code mode

```text
mode=code
status=READY_CODE
safe_output=True
exit=0
checks=3
```

The code mode checks only formal repository identity, Git access, and Python availability. It does not require Docker or Element.

### Runtime mode

The later independent QA run returned:

```text
mode=runtime
status=BLOCKED_DOCKER_ENGINE
safe_output=True
exit=3
last_check=docker_engine
last_pass=False
checks=4
```

The script stopped at the first current failure and did not inspect Controller, Manager, Workers, Team, UI, MCP, Commander, Matrix, or live stages afterward.

R-08AR's earlier recorded run reached `BLOCKED_LOCAL_UI` after Docker, Controller, Manager, four production Workers, and Team passed. That result remains valid only for its recorded point in time. It cannot be represented as the current QA runtime state because Docker was unavailable in the later independent run. This difference is expected under the runbook's rule that historical PASS results never replace a fresh preflight.

The `BLOCKED_LOCAL_UI` branch itself is correctly implemented: it occurs after production resource checks and before Host MCP/Commander probes, returns exit code 6, and performs no recovery action.

## Three-mode and dependency-order assessment

- `code`: repository → Git → Python, then `READY_CODE`.
- `runtime`: all code gates → Docker → Controller/Manager → four Workers/Team → local UI → Host listener/TCP/initialize → Commander running/DNS/TCP/initialize.
- `live`: all runtime gates → Element reachability → five `MANUAL_REQUIRED` confirmations.

Every blocked branch emits one compressed JSON object and exits immediately. The output schema contains `schema_version`, `mode`, `status`, sanitized checks, manual confirmations, duration, and `safe_output`.

## Read-only and disclosure boundary

Static review found no capability to:

- start, stop, or restart a service, task, Docker container, Manager, or Worker;
- send or retry S01 or another Matrix message;
- approve or reject a plan;
- apply, create, update, or delete AgentTeams resources;
- mutate configuration, bind/allowlist, Worker/Team YAML, business code, or Git;
- read browser sessions, scheduled-task definitions/actions, configuration files, environment values, raw logs, or response bodies;
- touch `sectrace-smoke`.

The script emits only categories, booleans, exit codes, coarse HTTP categories, duration, and manual-confirmation labels. No secret, Matrix identifier, PID, command line, path value, raw message, raw log, or MCP response body is projected.

The category `host_mcp_process_present` currently mirrors listener presence rather than inspecting a process object. This is a non-blocking naming limitation because the subsequent TCP and MCP initialize gates establish endpoint readiness without exposing process details; it must not be cited as independent process-identity proof.

## AGENTS and README gates

- AGENTS mandates the lowest necessary mode for a new conversation, computer reboot, or meaningful runtime change.
- AGENTS explicitly states that the preflight is not a launcher and does not authorize mutations.
- README has the `Resume after reboot` entry, code-mode example, runbook link, script link, and read-only warning.

## Conclusion

R-08AR is **PASS**. The assets implement a three-mode, machine-readable, fail-fast, read-only resume gate with appropriate authorization boundaries. The current environment is `BLOCKED_DOCKER_ENGINE`; the earlier `BLOCKED_LOCAL_UI` result is historical point-in-time evidence and must not be substituted for the current state. No service may be started automatically from either result.
