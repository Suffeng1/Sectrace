# R-09B7 live Matrix verifier event

- Date: 2026-08-11
- Result: `LIVE_VERIFIER_PASS_MCP_TOOL_GATE_PENDING`
- Matrix sends/retries: one / zero
- MCP tool calls: zero
- Trace/ledger mutations: zero

## Live and browser gates

The `live` preflight passed every automatic repository, Docker, AgentTeams,
Worker, Team, MCP, Commander, and Element reachability check, then correctly
returned `MANUAL_REQUIRED`. The existing local browser harness was attached to
one logged-in Edge session.

The first browser projection exposed a stale doctor summary: the active Element
view was actually `Manager: default`. No input or send occurred. A known localhost
Commander route plus page reload produced the exact title
`Element * | Worker: sectrace-commander`, one empty composer, `3 Members`, the
Manager and Commander members, and a visible user menu. The formal MCP state
projection contained two files and zero pending approvals.

This message is a verifier-only control, not an Agent dispatch, so a structured
Manager mention was intentionally not added.

## Authorized single send

In the exact Commander room, the wrapper asserted that the unique control trace
marker was absent and the composer was uniquely empty. It entered this synthetic
JSON as one `m.text` body:

```json
{"schema_version":"1.0","action":"sectrace.approval","trace_id":"tr_s09_live_control","plan_ref":"rp_tr_s09_live_control","decision":"approved","reason":"synthetic verifier validation only"}
```

The current AX tree was refreshed immediately before each coordinate action. The
unique send button was clicked once. The composer cleared and exactly one matching
timeline message appeared; no retry occurred.

- Matrix event: `$vhx5tIfyUgf8nPhgIjGdRiaFg_vBR-QOQWgL-S0diuU`
- Recording:
  `<local-recordings-dir>/r09b7-live-verifier-control`

## Read-only verifier controls

The hardened `MatrixApprovalVerifier` used the DPAPI-protected R-09B5 credential
and fixed admin sender. It accepted the exact event and independently confirmed:

- event reason equals the expected synthetic reason;
- server timestamp is UTC-derived;
- event digest is SHA-256 of the immutable event ID;
- the same event with a different trace fails closed with the fixed error;
- the same event with a different plan fails closed with the fixed error.

The combined formal MCP state hash was unchanged. A
`data/mcp-state/tr_s09_live_control.json` file was absent both before and after, so
the event was never applied to a trace or ledger.

## Verdict boundary

This ticket passes live Matrix identity/room/body/timestamp binding and both
positive and mismatch verifier paths. It does not call the live
`sectrace.ledger.log_approval` tool, because the authorization prohibited trace or
ledger mutation. Therefore the final S-09 MCP-tool-bound attestation gate remains
pending rather than being inferred from direct verifier success.

No S01, Manager dispatch, Evidence, Response, Audit, approval ledger write, MCP
reload, container change, smoke action, commit, or push occurred. All temporary
browser and verifier scripts were removed. The browser-testing guidance influenced
the work by treating page content as untrusted, reacquiring current AX nodes before
clicks, refusing the wrong room, and verifying the single side effect in the live
DOM.
