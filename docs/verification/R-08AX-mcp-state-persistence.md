# R-08AX MCP Trace State Persistence

- Date: 2026-08-11
- Result: `PASS_CODE_ONLY`
- Runtime action: none

## Problem reproduced

The MCP adapter previously kept all trace state only in `self.traces`. Reconstructing the adapter after an MCP process restart therefore produced `unknown trace_id` and prevented a pending S01 chain from continuing.

Strict RED was preserved in `tests/integration/test_mcp_state_persistence.py`. Before implementation, all three tests failed because `SafeMCPAdapter` did not accept the required `state_dir` argument:

```text
3 failed
TypeError: SafeMCPAdapter.__init__() got an unexpected keyword argument 'state_dir'
```

## Implementation

- Added an optional persistence directory to `SafeMCPAdapter`; ordinary in-memory tests remain isolated when it is omitted.
- The executable MCP server uses `data/mcp-state/`.
- Each trace is stored in its own `<trace_id>.json` file.
- Writes use a unique temporary file, flush plus `fsync`, and `os.replace` under a process-local re-entrant lock.
- Startup reconstructs IncidentCase, EvidenceItem, ResponsePlan, ApprovalRecord, AuditReview, scenario data, risk path, and AuditLedger.
- Startup rejects invalid schema, trace mismatches, invalid Pydantic models, and broken ledger hash chains with a fixed safe error that does not echo state content.
- Runtime state and MCP log files are ignored by Git.

## Verification

```text
state persistence tests: 9 passed in 1.13s
MCP adapter + persistence tests: 21 passed in 1.04s
full pytest: 63 passed in 1.55s
git diff --check: passed
```

The tests prove that a trace stopped at `pending_approval` survives Adapter reconstruction, can still receive one valid human decision, reaches a qualified Audit, and survives another reconstruction with all five ledger events. A tampered persisted ledger is rejected without leaking the modified content, and no temporary files remain after successful writes.

## Independent QA correction

The first independent QA correctly found that a schema-valid `approved` ApprovalRecord could be inserted while leaving the valid ledger without an approval event. Two RED tests reproduced that semantic bypass and an impossible Response-without-Evidence state (`2 failed, 3 passed`). Loading now requires complete stage dependencies and enforces that a decided ApprovalRecord matches exactly one `human_operator` approval ledger event, the current plan reference, decision, reason-digest format, and decision timestamp.

The second independent QA then rebuilt a valid hash chain around two deeper state-machine violations: placing `approval.approved` before `response.pending_approval`, and removing `response.pending_approval` while retaining the ResponsePlan and approval. The third strict RED reproduced both (`2 failed, 5 passed`). Loading now derives the only valid event sequence from the persisted objects and requires an exact match of event count, actor, event type, and object reference across `incident -> evidence -> response -> approval -> audit` (with approval omitted while pending). The third independent QA confirmed that both valid-hash bypasses fail closed; both earlier FAIL records remain historical evidence.

The third independent QA confirmed those event-state fixes, then found two remaining legal-model gaps: a pending chain could restore a forged Pydantic-valid `qualified` AuditReview, and a Response stage could restore the runtime-unreachable `not_requested` Approval status with a matching valid-hash event. The fourth strict RED reproduced both (`2 failed, 7 passed`). Response-stage loading now permits only `pending`, `approved`, or `rejected`; persisted AuditReview is deterministically rebuilt from all restored inputs and the ledger and must match every persisted field.

The fourth independent QA passed. It independently confirmed rejection and non-disclosure for both final gaps, all nine declared AuditReview fields under Pydantic-valid tampering, and valid-rehash event order/missing/duplicate/reference attacks. It also passed all reachable pending/approved/rejected restart combinations and instrumented five mutations as one `fsync` plus one `os.replace` each with unique temporary names and no residue. The three earlier FAIL records remain historical evidence for the superseded implementations.

## Scope boundary

No Docker, MCP process, AgentTeams resource, browser, Matrix message, S01 replay, approval, commit, or push was performed. Live process-restart verification requires a separate runtime authorization and current `runtime` preflight.
