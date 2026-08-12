# V-R08AX Independent QA

- Date: 2026-08-11
- Scope: repository/code only
- Conclusion: **FAIL**
- Runtime mutation: none

## Blocking finding

Persisted approval state is validated as a Pydantic object and for `trace_id`, but it is not checked for semantic consistency with the ledger. A schema-valid change from `pending` to `approved`, with a valid timestamp and an otherwise unchanged valid three-record ledger, is accepted during restart. Calling Audit after that restart produces `audit_status=qualified` even though the ledger contains no `approval.approved` event.

Independent temporary-data reproduction:

```text
approval_ledger_mismatch_loaded=true
approval_ledger_mismatch_qualified=true
```

This violates the fail-closed persistence boundary and the human-approval evidence chain. Ledger hash validation alone does not protect the separately persisted Approval object.

Relevant implementation locations:

- `src/app/mcp_adapter.py:95-104` validates only ledger structure/hash/trace continuity.
- `src/app/mcp_adapter.py:115-124` accepts a Pydantic-valid Approval independently of ledger approval events.
- `src/app/mcp_adapter.py:261-279` consumes that restored Approval when projecting Audit.

## Criteria results

| Criterion | Result | Independent evidence |
|---|---|---|
| Strict RED | PASS with provenance limitation | HEAD's constructor has no `state_dir`; all three new tests pass that argument, so the recorded `TypeError` RED is mechanically credible. The preserved evidence is a self-authored summary rather than an immutable raw artifact. |
| Omitted `state_dir` remains memory-only and isolated | PASS | Independent probe created two default adapters; state from one was absent from the other. Existing adapter tests also remained green. |
| Formal server uses `data/mcp-state` | PASS | `src/app/mcp_server.py:11-14`. |
| One file per trace | PASS | `_state_path` maps an allowlisted trace to `<trace_id>.json`; independent probe observed one JSON file for one trace. |
| Unique temp, flush, `fsync`, `os.replace` | PASS | `src/app/mcp_adapter.py:143-162`; UUID temp name and no residual temp file observed. |
| All five mutations persist | PASS at implementation level | Persist calls follow create, analyze, plan, approval, and audit. Restart probes recovered the three pre-approval mutations and then the approval/audit mutations with a valid five-record ledger. |
| Restart restores scenario/Incident/Evidence/risk path/Response/Approval/Audit/Ledger | PASS | Independent probes compared pending-state fields and recovered completed Approval, qualified Audit, and five ledger records. |
| Pydantic/trace/schema/hash failures reject without content echo | PARTIAL / FAIL overall | Independent probes confirmed rejection of invalid schema, outer trace, Incident model, and ledger hash with the fixed filename-only error. However a schema-valid Approval/ledger semantic mismatch loads and qualifies, so the persisted chain is not fail-closed. |
| Same-adapter process concurrency ordering | PASS | `RLock` wraps every public tool call; a two-thread duplicate approval probe yielded exactly one success and one rejection with a valid ledger. |
| State/log ignore rules | PASS | `git check-ignore -v` matched `data/mcp-state/`, `mcp_server.log`, and `mcp_server.err.log`. |
| No real-action execution capability | PASS | Tool allowlist contains projection/intake/evidence/response/audit/ledger operations only; unknown execution tool remains rejected. |

## R-08B separation

The sixth `sectrace.ledger.log_approval` tool, approval-input hardening, and README's five-to-six tool wording belong to the existing R-08B work. R-08AX adds persistence/load/locking and persists that existing approval projection. This FAIL is specifically about R-08AX restoring the R-08B approval state without proving that it matches the tamper-evident ledger.

## Executed verification

```text
code preflight: READY_CODE
focused MCP adapter + persistence: 15 passed in 1.11s
full suite first run: 56 passed, 1 infrastructure failure (Git safe.directory in child process)
full suite with process-local GIT_CONFIG_COUNT safe.directory injection: 57 passed in 1.30s
independent positive persistence/integrity/concurrency probe: all checks passed
independent approval-ledger mismatch probe: reproduced unsafe load and qualified Audit
git diff --check: passed (line-ending warnings only)
```

No Git configuration was modified. No Docker, MCP server, browser, Matrix, S01, approval action, runtime change, commit, or push was performed. All dynamic persistence checks used synthetic data in automatically removed temporary directories.

## Minimum fix and rerun

On load, enforce phase and ledger semantic coherence before accepting a trace:

1. `pending` Approval must have no approval decision event.
2. `approved` or `rejected` must match exactly one corresponding `human_operator` approval ledger event for the current plan reference.
3. Reject impossible partial phase combinations, such as Response without Evidence/Approval, and validate persisted risk-path shape/references.
4. Add negative tests for approval/ledger mismatch and phase inconsistency, then rerun the focused persistence suite, full suite, independent tamper probes, and `git diff --check`.

