# V-OPT2-02 Independent QA

- Owner: 05
- Task: `V-OPT2-02`
- Scope: OPT2-02 deterministic offline evaluation candidate, repository-only
- Plan/Base/HEAD: `9b725e48df05e78b20713d523c1af3f627572a4e`
- Branch: `codex/adopt-apache-license`
- Preflight: `READY_CODE`
- Runtime/live activity: none
- Verdict: **FAIL**

## Verdict

**FAIL**. The focused, hygiene, and full test suites pass, two isolated normal
CLI runs are byte-for-byte deterministic, the fixed dataset contains the five
requested labels, and the conflicting case is honestly marked as an OPT2-04
capability boundary. Those positive results do not close substantive failures
in approval applicability, dataset/schema validation, per-trace accounting,
exception handling, and CLI exit-code behavior. The current harness can report
8/8 PASS for invalid evaluation populations and can convert an unrelated
validator exception into a successful invalid-approval result.

This is repository-only QA of the uncommitted candidate at the HEAD above. It
does not attest current runtime, live Matrix, production availability, latency,
cost, or external approval delivery.

## Passing observations

- The runner does not select an oracle branch from source scenario IDs, a title,
  or a dataset legacy `expected` field. The synthetic production input contains
  a fixed local `scenario_id` and `expected.severity_hint`, but neither is read
  from the source case to select the evaluation oracle.
- The checked-in dataset explicitly contains `normal`, `insufficient`,
  `conflicting`, `invalid_approval`, and `tampered_ledger` case labels.
- The conflicting result is `expected_fail_closed` with
  `capability_boundary: true`; it does not claim that OPT2-04 or a persisted
  conflicting terminal exists.
- The tampered-ledger path changes a real local ledger hash and submits it to the
  Audit verifier. The normal fixed dataset reports the expected tamper rejection.
- Dataset/result version fields exist. Case and metric ordering are stable.
  Two isolated CLI runs returned 0 and produced identical JSON hashes and
  identical Markdown hashes. All eight Markdown numerator/denominator rows
  matched the JSON metric records.
- No public Contract, six-tool allowlist, canonical ledger sequence, persistence
  implementation, role business code, runtime, or live resource was changed by
  OPT2-02. Data and execution remained synthetic and local.

## Substantive findings

### 1. Invalid approval is neither exercised nor counted correctly

`evaluation/runner.py` constructs an invalid `ResponsePlan` with
`requires_approval=False`, catches any `ValueError`, and calls that a rejected
approval. It never exercises the production approval verifier or its trace/plan
binding and non-caller-self-attestation checks. A counterexample replacing the
constructor with one that raises `ValueError("unrelated-validator-failure")`
still returned a passing `risk_terminal` result.

The same branch is excluded by `approval_applicable = required and normal_path`.
The current `approval_binding_rate` therefore has only
`normal-corroborated` as an applicable case (`1/1`); the invalid-approval case
has `approval_applicable: false`. This contradicts the required selector of
cases that have a plan and require approval and makes the invalid-binding
metric incapable of detecting its named failure.

Minimal fix: drive a valid high-risk plan through the real approval-binding
entry point with an invalid binding; match a specific typed failure/error code;
select approval cases from plan/approval applicability rather than outcome
path; add valid, invalid, and relevant tampered-plan counterexamples.

### 2. Dataset coverage and identity are not validated

`_validate_dataset` checks only the top-level key sets and that there are at
least five cases. A temporary dataset with all five `case_kind` values changed
to `normal` still returned `8 passed`, exit 0. Duplicate case IDs are likewise
accepted. `case_kind` can also contradict corroboration, approval, and ledger
semantics without rejection.

Minimal fix: enforce unique `case_id`, required five-kind coverage, allowed
enums/types, and cross-field semantic invariants before any case runs. Add
negative tests for an empty required class, duplicate ID/trace, and mismatched
kind versus semantic fields.

### 3. Trace and ledger metrics are not per trace

Every executed case is converted to synthetic `scenario_id: EVAL`, which makes
the production trace `tr_eval`. The result omits `trace_id`, so duplicate traces
cannot be audited or aggregated. `ledger_integrity_rate` then counts case
records, not unique traces, despite its required “按 trace” denominator.

Minimal fix: derive a stable unique trace input from a non-oracle case identity,
emit the trace ID in each case result, reject duplicate traces, and aggregate
trace/ledger metrics over unique trace identities.

### 4. Scenario-run and other evidence are synthetic successes

Conflicting and invalid-approval branches do not call `run_demo`, yet every case
unconditionally reports `scenario_run: true`. Several non-executed branch values
for trace continuity, stage order, and ledger integrity are also assigned true
constants and then partially hidden by applicability selectors. Thus the
scenario-run metric is effectively unable to fail for a returned case.

Minimal fix: record actual attempted/completed execution and concrete evidence
references; unexpected case exceptions must produce a failed case/result rather
than disappear or become success. Give each metric a meaningful failure class
instead of the universal `evaluation_mismatch` value.

### 5. Provenance is explicit but not semantically effective

The dataset has explicit provenance/corroboration fields and removes the old
S02/S03 case-level `expected` ambiguity. However, the runner reads
corroboration only; changing all provenance counts, subject flags, and ordered
sequence flags leaves the complete Eval result unchanged. Provenance is
therefore decorative rather than a verified input to the semantic fixture.

Minimal fix: define provenance/corroboration invariants and construct or reject
the fixture from both signal groups. Add one-field perturbation tests showing
that invalid or materially different provenance cannot yield the same success.

### 6. Dataset and result schemas do not enforce the declared contract

The dataset schema only requires case field names; it accepts the real dataset
after a required nested approval field is removed. The runner does not execute
the schema and later fails with an uncaught key/type error. The result schema
accepts an empty metric object, wrong summary types, and `exit_code: 99`. Neither
schema constrains the eight metric records, nested result/case shapes, enums,
additional properties, or uniqueness.

Minimal fix: fully specify nested Draft 2020-12 schemas with types, enums,
required fields and `additionalProperties: false`; validate input before
execution and output before writing; map schema failure to exit 2.

### 7. CLI input/output failure code is not stable

Only `run_evaluation` is inside the CLI exception boundary. Removing a nested
approval field produced a traceback and process exit 1. Writing to a missing
output directory also produced a traceback and exit 1. Both violate the
documented input/output failure code 2.

Minimal fix: put dataset validation, rendering, and both output writes inside a
controlled error boundary that returns 2, preferably using temporary writes
and atomic replacement. Test each output path independently and malformed
nested input.

### 8. Zero-denominator policy permits vacuous core success

All eight metrics share `not_applicable_pass`. Directly evaluating an empty
case-result list yields eight `0/0` passing metrics. Together with the missing
class validation, a required capability category can disappear silently.

Minimal fix: define zero policy per metric. Core all-case/trace/ledger coverage
must fail or be an input error at zero; only genuinely optional selectors may
produce an explicit N/A pass.

## Independent commands and results

| Check | Result |
| --- | --- |
| `pwsh -File .\scripts\sectrace-preflight.ps1 -Mode code` | `READY_CODE` |
| `python -m pytest -q -p no:cacheprovider tests/evaluation` | `5 passed` |
| `python -m pytest -q -p no:cacheprovider tests/security/test_repository_hygiene.py` | `16 passed` |
| `python -m pytest -q -p no:cacheprovider` | `149 passed` |
| Two isolated `python -m evaluation.runner` runs | exits `0,0`; JSON hashes equal; Markdown hashes equal; summary `8 passed, 0 failed` |
| All case kinds changed to `normal` | incorrectly returned exit 0 and `8 passed` |
| Unrelated `ValueError` injected into invalid-approval constructor | incorrectly accepted as successful rejection |
| Approval selector audit | only normal case applicable; invalid approval excluded |
| Duplicate trace audit | every executed fixture uses `EVAL` / `tr_eval`; result has no trace ID |
| Dataset schema with missing nested approval field | incorrectly schema-valid |
| Result schema with empty metric/wrong summary types/exit 99 | incorrectly schema-valid |
| Malformed nested dataset via CLI | traceback, process exit 1 instead of 2 |
| Missing output parent via CLI | traceback, process exit 1 instead of 2 |
| `git diff --check` / `git diff --cached --check` | PASS |
| staged audit | empty |

## Repository-state audit

Before this QA file was added, HEAD was exactly the required base, staged state
was empty, and untracked state contained only
`docs/handoffs/H-OPT2-02.md`, `evaluation/**`, and
`tests/evaluation/**`. This QA adds only the present file under the owner-05
write boundary. Python cache files created by tests are ignored and are not
formal artifacts.

## Fixed completion report

```text
STATUS: FAIL
PLAN_COMMIT: 9b725e48df05e78b20713d523c1af3f627572a4e
BASE_COMMIT: 9b725e48df05e78b20713d523c1af3f627572a4e
FINAL_COMMIT: NO_COMMIT
FILES_CHANGED: docs/verification/V-OPT2-02-independent-qa.md
HANDOFF: V-OPT2-02 independent repository-only QA
TESTS_RUN: code preflight; focused Eval; repository hygiene; full pytest; two isolated CLI/hash runs; oracle/category/approval/exception/trace/schema/CLI/tamper counterexamples; diff/staged/untracked audits
TEST_RESULT: FAIL — suites pass, but substantive deterministic Eval contract defects remain
NEW_BEHAVIOR: none; independent QA record only
UNCHANGED_SAFETY_BOUNDARIES: synthetic/de-identified local evaluation only; no public Contract, six-tool, canonical ledger/persistence, runtime/live, Matrix, approval action, commit, or push change
KNOWN_LIMITATIONS: this record does not establish runtime/live/production performance or OPT2-04 conflicting-evidence support
NEXT_HANDOFF: owner 00 should apply the minimal fixes above, add focused counterexample tests, and return a revised uncommitted candidate to owner 05
```
