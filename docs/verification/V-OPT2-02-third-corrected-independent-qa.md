# V-OPT2-02 Third-Corrected Independent QA

- Owner: 05
- Task: fourth independent QA for `V-OPT2-02`
- Scope: third-corrected deterministic offline Eval candidate, repository-only
- Plan/Base/HEAD: `9b725e48df05e78b20713d523c1af3f627572a4e`
- Branch: `codex/adopt-apache-license`
- Preflight: `READY_CODE`
- First FAIL SHA-256: `D54D8A91784824A5FB6777EB61C03C2E29AB2B11E4DE289F6EFCDE5D25F825B8`
- Corrected FAIL SHA-256: `EC5382696CC33F7579D8FBBC8C3498EE7354DF493E72B4633D73E7B04F149164`
- Second-corrected FAIL SHA-256: `0218E42AC07593D80DF791E504B75A238180DDA13392E06B2D5E816EA2E49CE6`
- Runtime/live status: unknown; no runtime/live activity performed
- Verdict: **FAIL**

## Verdict

**FAIL**. The third correction closes all three blockers from the preceding QA:
the formal invalid-approval result now depends on all four ordered adapter
probes; internal TypeError joins RuntimeError and AssertionError at fixed,
non-leaking exit 3; and the Handoff consistently defines the 0/1/2/3 contract.
All focused, hygiene, full, determinism, report, trace, schema, and prior
counterexample checks pass.

One new required hard gate fails: dataset semantic validation is not complete
for every case. A semantically contradictory approval object on the conflicting
case is accepted in first, middle, and last positions and the evaluation returns
PASS. This violates the explicit fourth-round requirement that semantic
mutation of every case be rejected.

This result is repository-only for the exact uncommitted candidate above. It
does not establish runtime/live or production state, external approval delivery,
latency, cost, or availability.

## Blocking finding

### Conflicting approval semantics are not validated

For the conflicting case, the dataset declares:

```json
{"required": false, "decision": "not_requested", "binding_valid": null}
```

The independent probe replaced it with the contradictory but schema-valid:

```json
{"required": false, "decision": "approved", "binding_valid": true}
```

`run_evaluation` accepted this mutation when the case was placed first, middle,
or last, and still returned exit 0. The conflicting validator branch checks
only `not approval["required"]`; it does not constrain decision or binding.
The conflicting execution branch then emits a hard-coded expected boundary
PASS without consuming those fields.

Related provenance mutations (`same_subject=false` and
`ordered_risk_sequence=true`) are also accepted for conflicting, showing that
the branch validates only a subset of the declared semantic object. The
approval contradiction alone is sufficient for FAIL because it represents an
approved/bound record while simultaneously declaring approval not required.

Minimal fix: require the conflicting approval object to equal
`{"required": false, "decision": "not_requested", "binding_valid": null}`;
define and enforce the intended conflicting provenance invariants; add
field-by-field semantic mutations for the middle conflicting case and repeat
them after reordering to first/last.

## Passing focal checks

### Formal invalid-approval evidence

- The generated invalid-approval case reports exactly, in order:
  `wrong_trace`, `wrong_plan`, `wrong_decision`, `unbound_event`.
- All four are actual `SafeMCPAdapter` `sectrace.ledger.log_approval` calls.
- If the wrong-decision call is artificially accepted, the evaluation raises
  `approval binding probe was accepted` instead of counting the metric.
- Invalid, normal, and tampered cases remain in approval applicability; the
  fixed report is `3/3`.

### Exit-code contract

| Boundary | Independent result |
| --- | --- |
| Normal PASS | exit 0; summary 8/0 |
| Wrong oracle / metric gate | exit 1; summary 7/1 |
| Malformed dataset | exit 2; fixed input/output stderr; no traceback |
| Schema-invalid type | exit 2; fixed input/output stderr; no traceback |
| Either output path failure | exit 2; fixed input/output stderr; no traceback |
| Internal TypeError | exit 3; fixed internal-error stderr; injected text absent |
| Internal RuntimeError | exit 3; fixed internal-error stderr; injected text absent |
| Internal AssertionError | exit 3; fixed internal-error stderr; injected text absent |

The Handoff primary contract lists all four codes, uses dataset `1.1.0`, scopes
claims to the local repository, and states runtime/live unknown.

### Replayed prior gates

- Directed semantic mutations for normal, insufficient, conflicting,
  invalid-approval, and tampered-ledger were rejected in first/middle/last
  positions when the mutation violated the invariants that the current code
  actually defines. The broader conflicting approval probe above exposes the
  missing invariant and is the sole blocker.
- Missing kind, duplicate case ID, duplicate declared trace ID, nested approval
  omission, normal provenance mutation, and corroboration mismatch were rejected.
- A predeclared failed scenario remained in denominator 1 with numerator 0 and
  failed the scenario-run metric.
- Four executed cases emitted four distinct trace IDs. Ledger integrity uses
  `unique_trace` aggregation and reports `4/4`.
- Every empty core metric reports denominator 0 and `passed=false`.
- Nested dataset and generated-result schemas reject malformed metric and
  summary structures. All eight metrics retain fixed order and required fields.
- Conflicting remains a non-executed `expected_fail_closed` capability boundary
  with no trace; it does not claim OPT2-04 exists.
- No oracle branch is selected from source scenario ID, title, or legacy
  dataset `expected`.
- Two isolated CLI runs produced identical JSON SHA-256
  `8010784B33DF82D94C3E54EA00A3B43CC60E511787464C9B89BFB4CE6119C982`
  and identical Markdown SHA-256
  `0F1E00C9C6FDB1FCCC64CDB0C6A6194314DE9C02E80099B8DA702F97DBE11819`.
  JSON/Markdown numerator-denominator rows matched; both exited 0.
- No public Contract, six-tool allowlist, canonical ledger sequence,
  persistence code, 01–04 role code, runtime/live resource, Matrix action,
  credential, commit, or push was changed or invoked.

## Independent commands and results

| Check | Result |
| --- | --- |
| `pwsh -File .\scripts\sectrace-preflight.ps1 -Mode code` | `READY_CODE` |
| `python -m pytest -q -p no:cacheprovider tests/evaluation` | `20 passed` |
| `python -m pytest -q -p no:cacheprovider tests/security/test_repository_hygiene.py` | `16 passed` |
| `python -m pytest -q -p no:cacheprovider` | `164 passed` |
| Formal four-probe report and forced probe-acceptance gate | PASS |
| CLI 0/1/2/3 and non-leakage matrix | PASS |
| Five cases, first/middle/last directed invariants | 15/15 rejected |
| Conflicting contradictory approval, first/middle/last | **3/3 incorrectly accepted** |
| Scenario denominator, duplicates, provenance, nested/result schema, 0/0, unique trace ledger | PASS |
| Two isolated normal CLI runs and JSON/Markdown consistency | PASS |
| `git diff --check` / `git diff --cached --check` | PASS |

## Repository-state audit

Before adding this file, HEAD matched the required base, staged/tracked diff was
empty, and untracked state contained only the Handoff, three preserved FAIL
records, `evaluation/**`, and `tests/evaluation/**`. This cycle writes only the
present QA record. All three historical SHA-256 values are rechecked after the
write.

## Fixed completion report

```text
STATUS: FAIL
PLAN_COMMIT: 9b725e48df05e78b20713d523c1af3f627572a4e
BASE_COMMIT: 9b725e48df05e78b20713d523c1af3f627572a4e
FINAL_COMMIT: NO_COMMIT
FILES_CHANGED: docs/verification/V-OPT2-02-third-corrected-independent-qa.md
HANDOFF: V-OPT2-02 fourth independent repository-only QA
TESTS_RUN: code preflight; focused Eval; repository hygiene; full pytest; formal four-approval-probe gate; CLI 0/1/2/3 and non-leakage probes; every-case first/middle/last semantic mutations; all prior schema/category/duplicate/scenario/trace/ledger/provenance/zero probes; two isolated CLI/hash runs; JSON/Markdown and claim/version/diff/staged/untracked audits
TEST_RESULT: FAIL — conflicting approval semantics are accepted in first, middle, and last positions
NEW_BEHAVIOR: none; fourth independent QA record only
UNCHANGED_SAFETY_BOUNDARIES: synthetic/de-identified local evaluation only; runtime/live unknown; no public Contract, six-tool, canonical ledger/persistence, Matrix, approval action, commit, or push change
KNOWN_LIMITATIONS: no runtime/live/production evidence and no implemented OPT2-04 conflicting terminal
NEXT_HANDOFF: owner 00 should enforce the full conflicting approval/provenance invariant, add reordered conflicting field mutations, and return another uncommitted candidate to owner 05
```
