# V-R08AX State-Machine Independent QA

- Date: 2026-08-11
- Scope: R-08AX third correction only
- Conclusion: **FAIL**
- Earlier records: preserved; neither prior FAIL was overwritten
- Runtime action: none

## Outcome

The exact ledger event-state machine closes both bypasses from the second QA. Independently rehashed chains with an approval before Response, a missing Response event, duplicate events, or wrong incident/evidence/response/approval/audit references all failed closed without exposing persisted content.

Two deeper legal-model/legal-hash semantic states are still accepted:

1. A reachable pending-approval Audit state can have its persisted `AuditReview` changed from `not_qualified` to a Pydantic-valid `qualified` projection while leaving its exact valid ledger untouched. Restart accepts and restores the forged qualified Audit because loading validates only Audit Pydantic shape and trace ID; it does not recompute or compare the Audit projection against Incident, Evidence, Response, Approval, and Ledger.
2. A Response-stage Approval can be changed to Pydantic-valid `not_requested` with a matching `approval.not_requested` event and a recomputed valid exact ledger sequence. Restart accepts it, although the MCP approval tool can only generate `approved` or `rejected`, and Response creation always persists `pending`.

These are remaining fail-closed gaps in persisted object semantics, so the third correction cannot pass yet.

## Blocking reproductions

All probes used synthetic temporary files only.

```text
forged_qualified_audit_loaded=true
not_requested_response_loaded=true
```

The forged Audit probe retained the canonical expected event sequence and valid ledger hashes. The only mutation was to Pydantic-valid AuditReview fields. The `not_requested` probe used a matching actor/type/plan-bound payload and recomputed the entire valid hash chain.

Relevant implementation:

- `src/app/mcp_adapter.py:134-138` validates restored Audit only by Pydantic model and trace ID.
- `src/app/mcp_adapter.py:170-192` treats every Approval status other than `pending` as a decided status, including `not_requested`.
- `src/app/mcp_adapter.py:194-204` validates the Audit ledger event but not the AuditReview projection itself.

## Independent state-machine matrix

| Probe | Result |
|---|---|
| Incident-only legal state | PASS |
| Incident → Evidence legal state | PASS |
| Pending Response legal state | PASS |
| Approved legal state | PASS |
| Rejected → not-qualified Audit → restart | PASS |
| Pending → not-qualified Audit legal state | PASS |
| Approved → qualified Audit → completed restart | PASS |
| Approval before Response, valid rehash | Rejected — PASS |
| Missing Response event, valid rehash | Rejected — PASS |
| Duplicate Evidence event, valid rehash | Rejected — PASS |
| Wrong Incident payload reference | Rejected — PASS |
| Wrong Evidence payload reference | Rejected — PASS |
| Wrong Response payload reference | Rejected — PASS |
| Wrong Approval payload reference | Rejected — PASS |
| Wrong Audit payload reference | Rejected — PASS |
| Error non-disclosure for all rejection probes | PASS |
| Forged qualified AuditReview on pending chain | Accepted — **FAIL** |
| `not_requested` Approval in Response stage | Accepted — **FAIL** |

## TDD and regression evidence

The reported third RED (`2 failed / 5 passed`) is mechanically credible because the immediately preceding implementation independently accepted both reordered/missing Response-event probes. The exact historical console output remains self-reported rather than an immutable artifact.

Fresh execution:

```text
code preflight: READY_CODE
persistence + MCP focused suite: 19 passed in 0.90s
full suite: 61 passed in 1.21s
git diff --check: passed (line-ending warnings only)
independent valid-rehash state-machine matrix: required ordering/reference attacks rejected
additional legal-model/legal-hash probes: 2 semantic gaps reproduced
```

The full suite used process-local `GIT_CONFIG_COUNT` safe-directory injection only. No global or repository Git configuration was changed.

## Minimum fix and rerun

1. For a persisted Audit, deterministically rebuild `AuditReview` from the restored Incident, Evidence, Response, Approval, and ledger, then require exact equality with the persisted Audit model (including status, integrity result, missing requirements, references, report, and ledger hash), or persist only inputs and recompute Audit on load.
2. When Response exists, restrict restored Approval status to the reachable set `pending`, `approved`, or `rejected`; reject `not_requested` regardless of a syntactically matching event.
3. Add valid-rehash negative tests for a forged qualified Audit on a pending chain and a Response-stage `not_requested` Approval.
4. Rerun persistence, MCP focused, full suite, independent state-machine probes, and `git diff --check`.

## Boundary

This verdict covers only the third corrected R-08AX implementation. It does not alter V-08B or V-05. No business code, runtime, Docker, MCP process, browser, Matrix, S01, approval action, Git configuration, commit, or push was modified or invoked.

