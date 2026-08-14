# V-OPT2-02 Second-Corrected Independent QA

- Owner: 05
- Task: third independent QA for `V-OPT2-02`
- Scope: second-corrected deterministic offline Eval candidate, repository-only
- Plan/Base/HEAD: `9b725e48df05e78b20713d523c1af3f627572a4e`
- Branch: `codex/adopt-apache-license`
- Preflight: `READY_CODE`
- First FAIL retained SHA-256: `D54D8A91784824A5FB6777EB61C03C2E29AB2B11E4DE289F6EFCDE5D25F825B8`
- Corrected FAIL retained SHA-256: `EC5382696CC33F7579D8FBBC8C3498EE7354DF493E72B4633D73E7B04F149164`
- Runtime/live status: unknown; no runtime/live activity performed
- Verdict: **FAIL**

## Verdict

**FAIL**. The second correction closes exact local verifier binding, failed-run
denominator retention, the named `RuntimeError`/`AssertionError` exit-3 probes,
dataset/claim wording, and all older data/schema/trace/determinism blockers.
However, an unexpected internal `TypeError` is still silently classified as
input/output failure with exit 2. In addition, the formal invalid-approval Eval
case does not execute the required wrong-decision probe even though an
independent adapter call proves the verifier can reject it. The Handoff's main
exit-code contract also still omits exit 3. Each contradicts the current third
QA contract, so this revision cannot receive PASS.

This is repository-only evidence for the exact uncommitted candidate above. It
does not establish current runtime/live state, production behavior, external
approval delivery, latency, cost, or availability.

## Third-cycle focal probes

### Approval binding

An independent synthetic `SafeMCPAdapter` trace and high-risk plan produced:

| Probe | Result |
| --- | --- |
| Wrong trace ID | rejected: `unknown trace_id` |
| Wrong plan reference | rejected: `plan_ref does not match current response plan` |
| Wrong decision with correct trace/plan/event | rejected: `approval event is not authorized` |
| Unbound event with correct trace/plan | rejected: `approval event is not authorized` |

The fixed Eval result keeps `invalid-high-risk-approval`,
`normal-corroborated`, and `tampered-ledger` in the approval metric and reports
`3/3`. Exact verifier logic now compares event ID, trace ID, plan ID, and
decision.

The remaining coverage defect is that `_run_adapter(..., valid_binding=False)`
only embeds wrong-trace, wrong-plan, and unbound-event probes. It does not call
the adapter with the wrong decision, and the focused direct verifier test only
covers wrong trace/plan. Thus the invalid case's passing metric does not
reproducibly depend on all four required rejection modes.

Minimal fix: add a correct event/trace/plan plus `decision="rejected"` adapter
probe to the invalid-approval path, require the fixed authorization error, and
test that all four probes execute before the same invalid case contributes its
passing approval numerator/denominator entry.

### Failed scenario-run denominator

A predeclared normal case constructed with `scenario_run=false` remained
applicable: numerator 0, denominator 1, `passed=false`. Conflicting remains the
only non-executed capability boundary and is explicitly non-applicable. The
previous denominator-escape defect is closed.

### Exit-code separation

Expected malformed dataset, missing JSON-output parent, and missing
Markdown-output parent each returned exit 2, emitted exactly
`evaluation failed: invalid input or output`, and produced no traceback.

Injected internal `RuntimeError` and `AssertionError` each returned exit 3,
emitted exactly `evaluation failed: internal error`, did not expose injected
text, and did not use input/output wording.

An injected internal `TypeError("sensitive internal type defect")` instead
returned exit 2 and `evaluation failed: invalid input or output`. The broad
exit-2 tuple catches every `TypeError`, including evaluator/programming defects,
so the claimed classification is not type-safe and still masks internal errors.

Minimal fix: remove bare `TypeError` from the CLI exit-2 catch. Convert only
known input/schema type failures to `EvaluationInputError` at their validation
boundary; allow unexpected `TypeError` to reach the fixed exit-3 handler. Add
TypeError alongside RuntimeError and AssertionError in the non-leakage tests.

### Dataset version and capability claims

The dataset, generated result, and Handoff consistently use `1.1.0`. The
Handoff now scopes the insufficient terminal to a local source-code projection,
states runtime/live unknown, and explicitly denies that it is a production
observation. No current production claim was found.

One documentation inconsistency remains: the Handoff's main run contract lists
only exit codes 0, 1, and 2, while the second-correction section and runner add
exit 3. Minimal fix: reconcile the primary contract to list and define all four
codes.

## Replayed earlier blockers

- Missing required kind, duplicate case ID, duplicate declared trace ID,
  malformed nested approval, invalid provenance, and invalid corroboration were
  independently rejected before evaluation.
- Nested dataset schema validation and generated-result schema validation are
  active. Malformed metric arrays and wrong summary types/exit code were
  rejected.
- Four executed cases emitted four distinct trace IDs. Ledger integrity uses
  `unique_trace` aggregation and reported `4/4`. The conflicting case has no
  emitted trace and remains an honest `expected_fail_closed` OPT2-04 boundary.
- Provenance and corroboration both participate in semantic validation and
  fixture construction; independent mutations were rejected.
- All eight empty core metrics reported denominator 0 and `passed=false`.
- All eight metrics retain explicit applicable cases, numerator, denominator,
  zero policy, evidence source, failure class, aggregation, and stable ordering.
- Two isolated CLI runs returned 0. JSON SHA-256 was identically
  `EC6A06D31EA1DFB8559DE7783FE038655886FB3BBA9D51699DA99853709B7AA8`;
  Markdown SHA-256 was identically
  `0F1E00C9C6FDB1FCCC64CDB0C6A6194314DE9C02E80099B8DA702F97DBE11819`.
  JSON/Markdown numerator and denominator rows matched for all eight metrics;
  summary was 8 passed, 0 failed, dataset version `1.1.0`.
- No source scenario ID, title, or legacy dataset `expected` field selects the
  oracle branch.
- No public Contract, six-tool allowlist, canonical ledger sequence,
  persistence code, 01–04 role code, runtime/live resource, Matrix action,
  credential, commit, or push was changed or invoked.

## Independent commands and results

| Check | Result |
| --- | --- |
| `pwsh -File .\scripts\sectrace-preflight.ps1 -Mode code` | `READY_CODE` |
| `python -m pytest -q -p no:cacheprovider tests/evaluation` | `17 passed` |
| `python -m pytest -q -p no:cacheprovider tests/security/test_repository_hygiene.py` | `16 passed` |
| `python -m pytest -q -p no:cacheprovider` | `161 passed` |
| Four adapter approval counterexamples | all independently rejected |
| Approval metric | invalid + normal + tampered, `3/3` |
| Injected failed scenario | retained at `0/1`, FAIL |
| Expected input/output failures | exit 2, fixed non-leaking stderr, no traceback |
| Internal RuntimeError / AssertionError | exit 3, fixed non-leaking stderr |
| Internal TypeError | **incorrect exit 2/input-output classification** |
| Five-kind/schema/duplicate/provenance/corroboration probes | all rejected as required |
| Unique-trace ledger | four unique traces, `4/4` |
| Empty population | all eight core `0/0` metrics fail |
| Two isolated normal CLI runs | deterministic hashes and JSON/Markdown consistency PASS |
| `git diff --check` / `git diff --cached --check` | PASS |

## Repository-state audit

Before this file was added, HEAD matched the required base, staged/tracked diff
was empty, and untracked state contained only the Handoff, both preserved FAIL
records, `evaluation/**`, and `tests/evaluation/**`. This cycle writes only the
present QA record. Both historical hashes are rechecked after this write.

## Fixed completion report

```text
STATUS: FAIL
PLAN_COMMIT: 9b725e48df05e78b20713d523c1af3f627572a4e
BASE_COMMIT: 9b725e48df05e78b20713d523c1af3f627572a4e
FINAL_COMMIT: NO_COMMIT
FILES_CHANGED: docs/verification/V-OPT2-02-second-corrected-independent-qa.md
HANDOFF: V-OPT2-02 third independent repository-only QA
TESTS_RUN: code preflight; focused Eval; repository hygiene; full pytest; four SafeMCPAdapter approval counterexamples; failed-run denominator; input/output and RuntimeError/AssertionError/TypeError exit probes; all earlier schema/category/duplicate/trace/ledger/provenance/zero probes; two isolated deterministic CLI/hash runs; JSON/Markdown consistency; claim/version/diff/staged/untracked audits
TEST_RESULT: FAIL — internal TypeError is mislabeled exit 2, wrong-decision is absent from the formal invalid-case evidence path, and the primary Handoff contract omits exit 3
NEW_BEHAVIOR: none; third independent QA record only
UNCHANGED_SAFETY_BOUNDARIES: synthetic/de-identified local evaluation only; runtime/live unknown; no public Contract, six-tool, canonical ledger/persistence, Matrix, approval action, commit, or push change
KNOWN_LIMITATIONS: no runtime/live/production evidence and no implemented OPT2-04 conflicting terminal
NEXT_HANDOFF: owner 00 should narrow exit-2 exception typing, embed and test the wrong-decision adapter probe in the invalid metric case, reconcile the primary 0/1/2/3 exit-code contract, then return another uncommitted candidate to owner 05
```
