# V-OPT2-02 Corrected Independent Re-QA

- Owner: 05
- Task: `V-OPT2-02` corrected independent re-QA
- Scope: corrected deterministic offline Eval candidate, repository-only
- Plan/Base/HEAD: `9b725e48df05e78b20713d523c1af3f627572a4e`
- Branch: `codex/adopt-apache-license`
- Preflight: `READY_CODE`
- Prior FAIL retained: `docs/verification/V-OPT2-02-independent-qa.md`
- Prior FAIL SHA-256: `D54D8A91784824A5FB6777EB61C03C2E29AB2B11E4DE289F6EFCDE5D25F825B8`
- Runtime/live activity: none
- Verdict: **FAIL**

## Verdict

**FAIL**. The corrected candidate closes most concrete data, schema, trace,
metric, and CLI examples from the first QA, and all focused/hygiene/full tests
pass. It still does not close the required real approval-binding semantics or
the requirement that runner failures not be silently swallowed. In addition,
`scenario_run_rate` can still remove a failed attempted case from its own
denominator, and the corrected Handoff contains version and current-production
fact drift. Any one of these is substantive; together they prevent PASS.

This record covers only local deterministic repository behavior at the exact
HEAD and uncommitted working tree above. It is not runtime/live, production,
latency, cost, availability, Matrix, or external approval evidence.

## First-FAIL blocker replay

| First blocker | Corrected independent result |
| --- | --- |
| Invalid approval real binding and denominator | **PARTIAL / FAIL**. Denominator is correctly `3/3` and includes invalid, normal, and tampered cases. The adapter path is exercised, but its injected verifier does not bind the event to exact trace/plan values. |
| Missing five kinds | PASS: changing conflicting to normal is rejected as `invalid evaluation dataset`. |
| Duplicate case/trace | PASS: duplicate case ID and duplicate declared trace ID are rejected. Executed results emit four distinct trace IDs; conflicting emits no trace. |
| Ledger per unique trace | PASS: aggregation is `unique_trace`, denominator `4`, equal to four emitted executed traces. |
| `scenario_run` real execution semantics | **PARTIAL / FAIL**. Conflicting is correctly non-executed/excluded, but an executed case with `scenario_run=false` and `scenario_applicable=false` disappears from the denominator and leaves the metric passing. |
| Provenance/corroboration participation | PASS for tested invariants: independent provenance and corroboration mutations are rejected, and fixture construction reads both. |
| Nested dataset/result schemas and runner validation | PASS: nested dataset omission, malformed metric array, and wrong summary types/exit code are rejected; runner validates input and generated result. |
| Malformed input/output exit 2 without traceback | PASS for malformed dataset and both missing-parent output paths: exit 2, fixed stderr, no traceback. **However**, the same handler also swallows unrelated internal exceptions; see finding 3. |
| Core `0/0` failure | PASS: all eight empty core metrics have denominator 0 and `passed=false`. |

## Remaining substantive findings

### 1. The approval verifier does not implement trace/plan binding

`_LocalApprovalVerifier.verify` accepts the fixed valid event whenever
`trace_id` and `plan_ref` are merely non-empty. An independent probe using the
valid event with `trace_id="wrong-trace"` and `plan_ref="wrong-plan"` was
accepted. Therefore the corrected invalid-approval case proves rejection of an
unrecognized event ID, not binding of an approval event to the exact trace and
plan. The Handoff claim that a real plan binding is exercised is not supported.

Minimal fix: initialize the deterministic verifier with the expected trace ID
and plan ID, require exact equality for both, and independently probe wrong
event, wrong trace, and wrong plan. Alternatively exercise the production
verifier with a fully synthetic authorized event fixture and its actual binding
rules.

### 2. A failed scenario run can escape the scenario-run denominator

For executed results, `_result` sets `scenario_applicable` equal to
`scenario_run`. The scenario metric selects only `scenario_applicable` cases.
Changing one executed case to `scenario_run=false` and
`scenario_applicable=false` removed it from the metric; the remaining cases
reported `3/3 PASS`. Applicability must describe whether a case was intended to
execute, independently of whether execution succeeded.

Minimal fix: make every non-boundary pipeline case scenario-applicable before
execution, retain it after failure, and set only `scenario_run=false`. Add a
failed-execution result probe asserting numerator decreases while denominator
does not.

### 3. The CLI still silently swallows unrelated internal exceptions

`main` catches bare `Exception` and always emits
`evaluation failed: invalid input or output`, exit 2. Replacing
`run_evaluation` with a function that raises an unrelated `RuntimeError`
produced exactly that input/output response. This masks evaluator defects and
violates the requested counterexample boundary even though expected malformed
input/output cases now behave correctly.

Minimal fix: catch only the explicit JSON/schema/input and output exceptions
that belong to exit 2. Unexpected execution/programming exceptions must remain
distinguishable and must not be labeled input/output failure; add an internal
exception probe.

### 4. Corrected Handoff facts are internally inconsistent

The Handoff still says the fixed dataset is `1.0.0`, while the dataset and the
corrected section say `1.1.0`. It also describes a “current production audit
projection” despite this cycle having only code preflight and no runtime/live
validation. These are release-fact and capability-scope defects, although the
underlying corrected dataset correctly emits `1.1.0`.

Minimal fix: state dataset `1.1.0` consistently and describe the insufficient
terminal as the current local source-code projection, explicitly not a current
runtime/production observation.

## Passing corrected behavior

- Required five-kind coverage, unique case IDs, unique declared trace IDs, and
  cross-field semantic invariants are validated before execution.
- Dataset schema constrains nested types/enums/additional properties. Result
  schema constrains case records, exactly eight ordered metrics, summary types,
  and result exit codes; both schemas are executed by the runner.
- The invalid, normal, and tampered approval-required cases are present in the
  approval denominator (`3/3`). The invalid case runs a local adapter path and
  no unrelated `ValueError` is accepted inside its narrow rejection handler.
- Four pipeline cases are executed with four distinct emitted trace IDs.
  Conflicting remains `expected_fail_closed`, `capability_boundary=true`,
  `scenario_run=false`, and `trace_id=null`; it does not pretend OPT2-04 exists.
- Ledger integrity aggregates four unique traces. Tampering still passes
  through the actual local Audit hash-chain check and is rejected.
- Provenance and corroboration both participate in validation/fixture semantics;
  independent invalid mutations are rejected.
- Eight metrics have explicit applicability, numerator, denominator, zero
  policy, evidence source, failure class, and aggregation. Empty core
  populations fail.
- Two isolated CLI runs returned 0 and produced identical JSON SHA-256
  `EC6A06D31EA1DFB8559DE7783FE038655886FB3BBA9D51699DA99853709B7AA8`
  and identical Markdown SHA-256
  `0F1E00C9C6FDB1FCCC64CDB0C6A6194314DE9C02E80099B8DA702F97DBE11819`.
  All eight Markdown numerator/denominator rows matched JSON; summary was 8/0.
- No public Contract, six-tool allowlist, canonical ledger sequence,
  persistence implementation, 01–04 role code, runtime/live resource, Matrix
  action, credential, commit, or push was changed or invoked.

## Independent commands and results

| Check | Result |
| --- | --- |
| `pwsh -File .\scripts\sectrace-preflight.ps1 -Mode code` | `READY_CODE` |
| `python -m pytest -q -p no:cacheprovider tests/evaluation` | `14 passed` |
| `python -m pytest -q -p no:cacheprovider tests/security/test_repository_hygiene.py` | `16 passed` |
| `python -m pytest -q -p no:cacheprovider` | `158 passed` |
| Two isolated CLI/hash runs | exits `0,0`; JSON hashes equal; Markdown hashes equal; JSON/Markdown metric rows consistent |
| Missing kind, duplicate case, duplicate trace | all rejected |
| Nested dataset omission | schema and runner reject |
| Independent provenance/corroboration mutations | both rejected |
| Result metric/summary corruption | result schema rejects |
| Malformed input and each output failure path | exit 2, fixed stderr, no traceback |
| Approval applicability | invalid + normal + tampered, `3/3` |
| Wrong non-empty trace/plan with valid local approval event | incorrectly accepted |
| Executed scenario changed to failed/non-applicable | incorrectly excluded; remaining metric `3/3 PASS` |
| Unexpected internal `RuntimeError` through `main` | incorrectly labeled input/output failure, exit 2 |
| Empty metric population | all eight `0/0` metrics fail |
| `git diff --check` / `git diff --cached --check` | PASS |

## Repository-state audit

Before adding this file, HEAD was the required base, staged state was empty,
and untracked state contained only the corrected Handoff, the preserved first
FAIL, `evaluation/**`, and `tests/evaluation/**`. The first FAIL SHA-256 was
captured before this re-QA and is rechecked after writing this record. This
cycle writes only the present corrected QA file.

## Fixed completion report

```text
STATUS: FAIL
PLAN_COMMIT: 9b725e48df05e78b20713d523c1af3f627572a4e
BASE_COMMIT: 9b725e48df05e78b20713d523c1af3f627572a4e
FINAL_COMMIT: NO_COMMIT
FILES_CHANGED: docs/verification/V-OPT2-02-corrected-independent-qa.md
HANDOFF: V-OPT2-02 corrected independent repository-only re-QA
TESTS_RUN: code preflight; focused Eval; repository hygiene; full pytest; two isolated deterministic CLI/hash runs; all first-FAIL category/identity/trace/ledger/scenario/provenance/schema/CLI/zero counterexamples; approval exact-binding and internal-exception probes; diff/staged/untracked audits
TEST_RESULT: FAIL — most original defects are closed, but exact approval binding, failed-run metric applicability, exception classification, and Handoff facts remain defective
NEW_BEHAVIOR: none; corrected independent QA record only
UNCHANGED_SAFETY_BOUNDARIES: synthetic/de-identified local evaluation only; no public Contract, six-tool, canonical ledger/persistence, runtime/live, Matrix, approval action, commit, or push change
KNOWN_LIMITATIONS: no runtime/live/production claim, no OPT2-04 conflicting terminal, and no external approval delivery evidence
NEXT_HANDOFF: owner 00 should apply the four minimal corrections above, add wrong-trace/wrong-plan, failed-execution-denominator, and internal-exception tests, reconcile Handoff facts, then return another uncommitted candidate to owner 05
```
