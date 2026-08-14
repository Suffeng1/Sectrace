# R-09B6 MCP verifier reload

- Date: 2026-08-11
- Result: `RELOADED_FAIL_CLOSED_LIVE_VALID_EVENT_PENDING`
- MCP stop/start calls: one / one
- Matrix sends/S01/approval: zero
- MCP tool mutations: zero

## Preconditions and controlled reload

The current runtime preflight returned `READY_RUNTIME`. The reload wrapper
validated the R-09B5 DPAPI credential store, exactly one listener/PID, a Python
process using `-m src.app.mcp_server`, and a combined hash of the formal MCP state
directory.

The wrapper stopped the old MCP process once and hidden-started one replacement
from the formal repository. The child received exactly four process-local verifier
settings: Matrix homeserver, DPAPI-decrypted access token, fixed Commander room,
and fixed approver `<matrix-user-id>`. No credential was
placed in process arguments or task output. The wrapper exited 0 after asserting a
distinct new PID, singleton listener, and unchanged state-directory hash. No
fallback start or retry occurred.

The wrapper's JSON summary was not forwarded by the outer command, so the action
was not repeated. Independent read-only confirmation immediately afterward
returned `READY_RUNTIME`, including Host and Commander TCP plus Streamable HTTP
initialize 2xx.

## Live schema

Commander `mcporter` discovery returned exactly six expected tools. The live
`sectrace.ledger.log_approval` schema contains exactly:

- `trace_id`;
- `decision`;
- `plan_ref`;
- `approval_event_id`.

The removed caller-controlled `approver` and `reason` arguments are absent. This
proves the replacement process loaded the hardened source rather than the prior
runtime schema.

## Matrix verifier controls

Using only DPAPI-decrypted credentials in a short-lived verification process, the
verifier fetched the existing R-08BG admin approval event. Safe projections
confirmed the expected event ID, fixed admin sender, `m.room.message` type, and
`m.text` message type.

The historical event body is not a JSON object and therefore cannot satisfy the
new exact six-field approval schema or trace/plan/decision bindings. The verifier
rejected it with only the fixed `approval event is not authorized` error. A
nonexistent event ID was also rejected with the same fixed error. These controls
prove credential/room read access and live fail-closed behavior without modifying
the ledger.

The repository positive structured-event control passed as part of 44 focused
security tests. A live positive structured event does not yet exist and was not
invented or sent under this ticket, so live valid-event acceptance remains pending.

## Boundary and next gate

No Matrix message, S01, approval, Audit, MCP tool mutation, Manager configuration,
container restart, smoke action, commit, or push occurred. Temporary reload and
verification scripts were removed. The `mcp-server-patterns` guidance influenced
the work by preserving Streamable HTTP, verifying schema-first registration and
structured fail-closed responses, and keeping credentials outside tool arguments.

The minimum next live gate requires a separately authorized, admin-origin,
synthetic structured approval event in the fixed Commander room. It must not be
applied to a trace or ledger; the verifier may only read it once to confirm positive
acceptance, then a mismatched trace/plan control must fail closed.
