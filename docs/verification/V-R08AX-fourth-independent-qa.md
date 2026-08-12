# V-R08AX Fourth Independent QA

- Date: 2026-08-11
- Scope: R-08AX fourth correction only
- Conclusion: **PASS**
- Earlier records: all three historical FAIL records preserved
- Runtime action: none

## Outcome

The fourth correction closes both findings from the third QA:

- Response-stage persisted Approval now rejects `not_requested` before deriving any decision event.
- Persisted AuditReview is rebuilt from the restored Incident, Evidence, Response, Approval, and complete ledger, then compared field-for-field using JSON-mode model dumps.

Independent temporary-data probes confirmed that both original attacks now fail closed, every declared AuditReview field is protected against Pydantic-valid substitution, normal pending/approved/rejected Audit combinations still restart correctly, and the exact ledger state machine remains enforced.

## Original finding reproductions

```text
original_forged_audit_rejected=true
original_forged_audit_nonleak=true
original_not_requested_rejected=true
original_not_requested_nonleak=true
```

The `not_requested` probe included a matching `human_operator` event, current plan reference, valid reason digest and timestamp, and a fully recomputed valid hash chain. The forged Audit probe retained its original valid ledger and changed only Pydantic-valid AuditReview values.

## Audit field matrix

Each declared AuditReview field was independently changed to another Pydantic-valid value. Every file was rejected with the fixed synthetic-filename-only error.

| Field | Result |
|---|---|
| `trace_id` | Rejected — PASS |
| `evidence_refs` | Rejected — PASS |
| `response_plan_ref` | Rejected — PASS |
| `approval_ref` | Rejected — PASS |
| `missing_requirements` | Rejected — PASS |
| `report_markdown` | Rejected — PASS |
| `ledger_hash` | Rejected — PASS |
| `audit_status` | Rejected — PASS |
| `integrity_check` | Rejected — PASS |

This verifies status, integrity, references, missing requirements, report content, and terminal ledger hash against the deterministic rebuilt projection rather than trusting persisted output.

## Legal restart combinations

| State | Result |
|---|---|
| Pending Response without Audit | Loaded — PASS |
| Pending Response with not-qualified Audit | Loaded — PASS |
| Approved before Audit | Loaded — PASS |
| Approved with qualified Audit and completed restart | Loaded — PASS |
| Rejected with not-qualified Audit and completed restart | Loaded — PASS |

## State-machine, non-disclosure, and atomicity

- Validly rehashed approval-before-Response, missing event, duplicate event, and wrong-reference ledgers were rejected.
- Rejection messages did not echo persisted model, report, reference, or ledger content.
- Instrumentation across create, analyze, plan, approval, and audit observed exactly five `fsync` calls and five `os.replace` calls.
- Every mutation used a distinct UUID-suffixed `.tmp` source, all replacements targeted the same per-trace JSON file, and no temporary file remained.
- The process-local `RLock` still encloses every public tool call, preserving same-adapter mutation order.
- No execution or real-action tool was added.

## TDD and regression evidence

The reported fourth RED (`2 failed / 7 passed`) is mechanically credible because the preceding implementation independently accepted both new negative cases. The exact historical console transcript remains self-reported rather than an immutable artifact.

Fresh execution:

```text
code preflight: READY_CODE
persistence + MCP focused suite: 21 passed in 1.20s
full suite: 63 passed in 1.46s
git diff --check: passed (line-ending warnings only)
independent Audit/state-machine/atomicity matrix: all checks passed
```

The full suite used process-local `GIT_CONFIG_COUNT` safe-directory injection only. No global or repository Git configuration was modified.

## Scope boundary

PASS applies only to the fourth corrected R-08AX repository implementation and its code-level restart semantics. It does not overwrite the three historical FAIL records, does not constitute a live MCP process restart, and does not alter V-08B or V-05. No business code, Docker, MCP process, browser, Matrix, S01, approval action, runtime state, Git configuration, commit, or push was modified or invoked.

