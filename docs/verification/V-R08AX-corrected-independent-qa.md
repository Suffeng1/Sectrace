# V-R08AX Corrected Independent QA

- Date: 2026-08-11
- Scope: corrected R-08AX only
- Conclusion: **FAIL**
- Supersedes original verdict: no; `V-R08AX-independent-qa.md` remains historical evidence
- Runtime action: none

## Outcome

The correction closes the original Approval-object-versus-decision-event mismatch and rejects the reported impossible Response-without-Evidence state. All requested direct approval checks passed independently. However, a model-valid state with a fully valid recomputed hash chain can still omit or reorder the Response ledger event and be accepted as an approved chain. Audit then returns `qualified`.

This is a remaining semantic fail-closed bypass: the loader binds Approval to one decision event, but does not bind the persisted Response stage and approval decision to the required ledger sequence.

## Blocking reproductions

Both probes used only synthetic temporary data and recomputed a canonical, valid hash chain after mutation.

### Approval recorded before the response request

The existing valid `approval.approved` record was placed before `response.pending_approval`; all hashes and event IDs were recomputed.

```text
bypass_approval_before_request_loaded=true
bypass_approval_before_request_qualified=true
```

### Response request ledger event absent

The persisted ResponsePlan and its correctly bound Approval remained, but `response.pending_approval` was removed from the ledger and the chain was rehashed.

```text
missing_response_event_loaded=true
missing_response_event_qualified=true
```

The current checks at `src/app/mcp_adapter.py:137-168` validate the decision event's actor, status, plan reference, reason digest, and timestamp, but do not require the corresponding Response ledger event or enforce incident → evidence → response → approval → audit ordering.

## Corrected checks independently confirmed

| Requirement | Result | Evidence |
|---|---|---|
| Pending has no decision event and no timestamp | PASS | Pending with timestamp was rejected; pending with a valid decision event was rejected. |
| Approved/rejected has exactly one matching decision event | PASS | Safe generated approved and rejected states loaded; zero and two decision events were rejected. |
| Actor is `human_operator` | PASS | A validly rehashed wrong-actor event was rejected. |
| Event type matches Approval status | PASS | A validly rehashed status mismatch was rejected. |
| Payload binds current plan ID | PASS | A validly rehashed wrong-plan payload was rejected. |
| Reason digest is 64 lowercase hexadecimal characters | PASS | A validly rehashed malformed digest was rejected. |
| Decision timestamp matches ledger timestamp | PASS | Timestamp mismatch was rejected. |
| Errors do not echo persisted state | PASS | Rejection paths returned only the fixed `invalid persisted trace: <synthetic filename>` form. |
| Response requires Evidence | PASS | Response with both Evidence fields removed was rejected. |
| Audit requires Response | PASS | Audit state without Response/Approval was rejected. |
| Pending → restart → approved → Audit | PASS | Normal synthetic continuation produced qualified Audit. |
| Completed restart | PASS | Approval, qualified Audit, and five ledger records survived reconstruction. |
| Legal-model/legal-hash semantic bypass search | **FAIL** | Missing and out-of-order Response ledger event variants both loaded and qualified. |

## RED and regression evidence

The reported correction RED of `2 failed / 3 passed` is mechanically credible: the pre-correction loader independently accepted both the forged approved-without-decision state and Response-without-Evidence state. The exact historical output remains self-reported rather than an immutable raw artifact.

Fresh execution:

```text
code preflight: READY_CODE
persistence + MCP focused suite: 17 passed in 0.91s
full suite: 59 passed in 1.15s
git diff --check: passed (line-ending warnings only)
direct approval/phase/non-leakage matrix: all enumerated correction checks passed
additional valid-hash semantic probes: 2 bypasses reproduced
```

The full test process used only process-local `GIT_CONFIG_COUNT` safe-directory injection. No global or repository Git configuration was modified.

## Minimum fix and rerun

During load, validate the persisted stage objects against an exact ledger state machine, at minimum:

1. ResponsePlan requires exactly one matching `response.pending_approval` event for its current `plan_id`.
2. The response event must follow the required incident/evidence stages and precede any approval decision event.
3. A persisted Audit requires the corresponding audit event after the response/approval state, and restored Audit fields must agree with the reconstructed chain.
4. Add negative tests for a missing Response event and an approval event ordered before the Response event, using a recomputed valid hash chain.

Then rerun the five persistence tests plus new negatives, focused MCP tests, full suite, independent semantic matrix, and `git diff --check`.

## Boundary

This verdict covers only corrected R-08AX persistence semantics. It does not change V-08B or V-05 status. No business code, Docker, MCP process, browser, Matrix, S01, real approval, Git configuration, commit, or push was changed or invoked.

