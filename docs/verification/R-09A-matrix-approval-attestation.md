# R-09A Matrix approval attestation

- Date: 2026-08-11
- Finding: `csf_df3939280f62a0c7898f8d54`
- Outcome: `CODE_FIXED_LIVE_VERIFICATION_PENDING`
- Scope: repository implementation and deterministic tests only
- Runtime mutation: none

## Vulnerable path and invariant

The shared MCP tool previously accepted caller-supplied
`approver=human_operator` and `reason`. Any reachable MCP client could therefore
forge the human gate. The required invariant is that only one event fetched by
the server from a fixed Matrix room, authored by the configured human identity,
and exactly bound to the current trace, plan, and decision may mutate Approval.

## Minimal implementation

- `src/app/approval_verifier.py` fetches one Matrix event with a server-held
  credential and validates event ID, configured sender, fixed room path, message
  type, exact JSON body, trace, plan, decision, reason bound, and server timestamp.
- `sectrace.ledger.log_approval` now requires `approval_event_id`; `approver` and
  `reason` are absent from its FastMCP schema.
- Missing verifier configuration rejects approval before mutation. Partial
  configuration stops startup.
- The ledger persists only SHA-256 digests of event ID and verified reason.
- Existing historical decided traces remain loadable; new approvals use the
  attested payload form.
- Commander repository prompts permit only the event-reference call and forbid
  identities, room IDs, reasons, or credentials in tool arguments.

## Matrix message contract

The human message body is one JSON object:

```json
{"schema_version":"1.0","action":"sectrace.approval","trace_id":"<trace_id>","plan_ref":"<plan_ref>","decision":"approved","reason":"synthetic operator review"}
```

The server process receives all or none of these environment variables:

- `SECTRACE_MATRIX_HOMESERVER_URL`
- `SECTRACE_MATRIX_ACCESS_TOKEN`
- `SECTRACE_APPROVAL_ROOM_ID`
- `SECTRACE_APPROVER_USER_ID`

Values remain outside Git, prompts, task files, test output, and MCP arguments.

## TDD and verification

RED:

- The original self-assertion regression failed because the old adapter accepted
  the forged caller input and did not raise.

GREEN and bypass review:

- unconfigured self-assertion is rejected with zero serialized-state change;
- valid event produces the server timestamp and event digest;
- wrong sender/event/type/trace/plan/decision/text/timestamp all fail closed with
  the same non-disclosing error;
- FastMCP schema contains only event ID, trace, plan, and decision;
- approved/rejected, audit qualification, persistence, state machine, production
  resources, and repository hygiene remain covered.

Commands:

- focused security/integration/runtime/hygiene suite: `80 passed`;
- full repository suite: `114 passed`;
- original PoC plus legitimate control: `2 passed`;
- `git diff --check`: pass.

## Remaining live gate

The running MCP process still has the old loaded code. A separate runtime ticket
must provision or select a least-privilege Matrix verifier identity, configure the
four environment values outside Git, reload MCP once, pass live preflight, and
exercise one new synthetic pending trace and one user-authored structured Matrix
event. No such runtime action occurred in R-09A.
