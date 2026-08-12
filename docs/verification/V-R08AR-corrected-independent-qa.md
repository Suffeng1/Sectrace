# Corrected R-08AR Independent QA

- Date: 2026-08-09
- Result: **PASS**
- Scope: corrected reboot/resume preflight only
- Supersedes for the corrected implementation: `docs/verification/V-R08AR-HOLD.md`
- Historical withdrawn result remains non-authoritative: `docs/verification/V-R08AR-independent-qa.md`

## Evidence reviewed

- `scripts/sectrace-preflight.ps1`
- `docs/runtime/reboot-preflight.md`
- `tests/runtime/test_reboot_preflight.py`
- `docs/verification/R-08AR-reboot-preflight.md`
- `docs/handoffs/H-R08AR.md`
- `AGENTS.md`
- `README.md`
- `docs/verification/V-R08AR-HOLD.md`

## Independent focused regression

```text
.......                                                                  [100%]
7 passed in 0.02s
```

The suite covers the original three-mode/JSON/read-only/documentation gates and the three corrections: optional demo UI, ordered core TCP gates, and removal of the listener-as-process category.

## Independent mode execution

```text
CODE status=READY_CODE safe_output=True exit=0 last_check=python_runtime checks=3 manual=0
RUNTIME status=BLOCKED_DOCKER_ENGINE safe_output=True exit=3 last_check=docker_engine checks=4 manual=0
LIVE status=BLOCKED_DOCKER_ENGINE safe_output=True exit=3 last_check=docker_engine checks=4 manual=0
```

The current boot has no available Docker engine. Both runtime and live modes correctly stopped at that first dependency. The live run did not inspect Element/browser state and did not produce `MANUAL_REQUIRED`, which is the correct fail-fast behavior.

## Corrected dependency and blocking semantics

The runtime order is correct:

1. code gates;
2. Docker engine;
3. exact Controller and Manager containers;
4. Controller API TCP on 18001;
5. model gateway TCP on 18080;
6. Manager API TCP on 18888;
7. four production Worker phases and production Team phase;
8. optional local demo UI observation on 19080;
9. Host MCP listener → TCP → initialize;
10. Commander running → DNS → TCP → initialize.

The three core TCP gates are true blockers and each has a distinct blocked status. The local Python demo UI is emitted as `local_demo_ui_reachable` with state `optional`; there is no `BLOCKED_LOCAL_UI` result, so an unavailable replay UI cannot prevent general Controller/Manager/MCP diagnostics or live S01 preparation.

## MCP evidence semantics

- `host_mcp_process_present` is absent.
- The script reports only `host_mcp_listener`, Host TCP, and Host initialize.
- Listener absence stops as `BLOCKED_MCP_SERVICE_NOT_RUNNING` without claiming process identity.
- TCP and initialize run only after listener presence.
- Commander checks run only after every Host MCP gate passes.

This resolves the withdrawn QA concern that listener state was mislabeled as independent process evidence.

## Live and browser boundary

Live mode inherits all runtime gates and checks only Element page TCP reachability afterward. If reachable, it returns five categorical `MANUAL_REQUIRED` items. It does not read or control a browser session, authentication state, Matrix identifiers, rooms, messages, mentions, or pending-approval content.

`MANUAL_REQUIRED` is not permission to send. Any S01 still requires separate explicit one-send authorization, and approval/rejection remains user-only.

## Read-only and disclosure boundary

Static review and focused tests found no ability to:

- start, stop, or restart Docker, a service, scheduled task, Manager, or Worker;
- send/retry Matrix or S01 messages;
- approve/reject a plan;
- apply/create/update/delete AgentTeams resources;
- modify configuration, code, YAML, bind/allowlist, or Git;
- read scheduled-task definitions/actions, configuration content, environment values, browser sessions, raw logs, MCP response bodies, secrets, or Matrix identifiers;
- touch `sectrace-smoke`.

Output remains one compressed JSON object containing only schema/mode/status, safe categories, booleans, exit codes, coarse HTTP category, duration, and manual labels.

## Documentation gates

- The runbook describes the corrected dependency order, optional local UI, listener-only MCP semantics, live manual gate, separate mutation authorization, and smoke prohibition.
- AGENTS mandates the lowest necessary mode for new conversations, reboots, and meaningful runtime changes and prohibits treating preflight as a launcher.
- README exposes the resume entry, code-mode example, runbook link, script link, and no-launch/no-send warning.
- R-08AR verification and Handoff append explicit superseding corrections and require fresh QA rather than reusing the withdrawn PASS.

## Conclusion

The corrected R-08AR is **PASS**. It now implements the lowest-necessary-mode principle without making the local demo UI a universal blocker, adds ordered Controller/gateway/Manager core TCP gates, uses accurate MCP listener/TCP/initialize semantics, and preserves fail-fast read-only behavior. This PASS validates the preflight mechanism only; it does not start Docker, authorize runtime mutation, send S01, approve a plan, or change V-08/V-05 status.
