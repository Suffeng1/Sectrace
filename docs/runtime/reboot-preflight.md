# SecTrace Resume/Reboot Preflight

This is the authoritative gate for resuming SecTrace after a computer reboot, a long stopped period, a new Codex conversation, or a meaningful runtime change.

Historical PASS records prove only the recorded point in time. They never replace a fresh preflight on the current boot/runtime state.

## Choose the lowest necessary mode

| Mode | Use when | Requires Docker/Element |
|---|---|---|
| `code` | Editing or reviewing repository code/docs/tests without live runtime work | No |
| `runtime` | Diagnosing or validating Controller, Manager, Workers, Team, UI, or MCP transport | Docker is required; Element is not |
| `live` | Any live Matrix/S01 observation or dispatch preparation | Runtime gates plus Element and manual confirmations |

Ordinary code and documentation work must not force the user to open Docker or Element. Any live S01 work must pass the `live` gate on the current boot.

## Commands

Run from PowerShell; output is one machine-readable JSON object.

```powershell
pwsh -File .\scripts\sectrace-preflight.ps1 -Mode code
pwsh -File .\scripts\sectrace-preflight.ps1 -Mode runtime
pwsh -File .\scripts\sectrace-preflight.ps1 -Mode live
```

The script is read-only. It is not a launcher and contains no start/stop/restart, resource mutation, message send, or approval action.

## Dependency order and stop gates

### `code`

1. Confirm the formal repository identity.
2. Confirm Git repository access.
3. Confirm Python is available.
4. On failure, stop with `BLOCKED_CODE_PREFLIGHT`.

### `runtime`

After all `code` checks:

1. Docker engine.
2. Exact production Controller and Manager running.
3. Controller API, model gateway, and Manager local TCP reachability.
4. Four production Workers Running and the production Team Active, with only sanitized phase booleans recorded.
5. Observe the local Python demo UI as optional, non-blocking state; require it only for local replay/demo work.
6. Host MCP listener, then Host TCP and MCP initialize.
7. Only after Host MCP passes: Commander running, DNS, TCP, and MCP initialize.

If the Host MCP listener is absent, stop immediately as `BLOCKED_MCP_SERVICE_NOT_RUNNING`. Do not infer process state, and do not diagnose Manager, Commander business logic, Matrix consumption, or Agent handoff from that state.

### `live`

After every `runtime` check passes:

1. Confirm the Element page is reachable.
2. Return `MANUAL_REQUIRED` for the user to confirm:
   - logged in as the allowed human operator;
   - correct production Worker ingress room;
   - structured Manager mention selected through the UI;
   - official Matrix channel shows running/configured/connected;
   - no unresolved `pending_approval` exists.

The script never reads a browser session, Matrix identifiers, messages, or credentials. A live S01 requires a separate explicit one-send authorization after the manual confirmations. `pending_approval` always stops automation and only the user may approve or reject.

## Actions requiring separate authorization

The preflight never authorizes or performs any mutation. Each of these still requires explicit, current user authorization:

- starting/stopping/restarting Docker, MCP, Manager, Worker, or any task;
- changing configuration, bind/allowlist, code, Worker/Team resources, or MCP tools;
- apply/delete operations;
- sending or retrying S01 or any Matrix message;
- approving or rejecting a plan;
- commit or push.

Never touch `sectrace-smoke` while running or responding to this gate.

## Resume checklist

1. Select the lowest necessary mode.
2. Run the script and retain only its safe JSON categories/booleans/exit codes.
3. Stop at the first blocked category.
4. Ask for a separate authorization for the exact required mutation.
5. Re-run the same read-only mode after the authorized repair.
6. Do not replace current evidence with a historical verification result.
