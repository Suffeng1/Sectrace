# V-OPT2-02 Fourth-Corrected Independent QA

- Owner: 05
- Task: fifth independent QA for `V-OPT2-02`
- Scope: fourth-corrected deterministic offline Eval candidate, repository-only
- Plan/Base/HEAD: `9b725e48df05e78b20713d523c1af3f627572a4e`
- Branch: `codex/adopt-apache-license`
- Preflight: `READY_CODE`
- First FAIL SHA-256: `D54D8A91784824A5FB6777EB61C03C2E29AB2B11E4DE289F6EFCDE5D25F825B8`
- Corrected FAIL SHA-256: `EC5382696CC33F7579D8FBBC8C3498EE7354DF493E72B4633D73E7B04F149164`
- Second-corrected FAIL SHA-256: `0218E42AC07593D80DF791E504B75A238180DDA13392E06B2D5E816EA2E49CE6`
- Third-corrected FAIL SHA-256: `C0350A8EE4578967AEDC482EC3998D98E276F6CA7ECBEEA0D69411370A921AB3`
- Runtime/live status: unknown; no runtime/live activity performed
- Verdict: **PASS**

## Verdict

**PASS**. The fourth correction closes the sole blocker from the fourth QA.
The conflicting case now has an exact approval, provenance, corroboration, and
ledger semantic invariant, independent of dataset position. All four historical
FAIL records remain unchanged, and every earlier blocker was independently
replayed without regression.

This PASS applies only to the local deterministic Eval implementation and
uncommitted working tree at the exact HEAD above. It does not establish current
runtime/live or production state, external approval delivery, latency, cost,
availability, or an implemented OPT2-04 conflicting-evidence terminal.

## Conflicting semantic contract

The accepted fixed case requires exactly:

- approval: `required=false`, `decision=not_requested`,
  `binding_valid=null`;
- provenance: `source_count=2`, `same_subject=true`,
  `ordered_risk_sequence=false`;
- corroboration: `state=conflicting`, `contradictory_claims=true`;
- ledger: `tampered=false`.

Independent first/middle/last probes changed each approval field, multiple
binding values, a combined approval object, and each provenance field. All 24
probes were rejected. Here “two sources” means the explicit
`provenance.source_count`; the three `source_scenarios` values are historical
scenario mappings and are not used to select the oracle.

The other four case kinds also use exact approval triples. Independent
field-level probes covered required, decision, false/true/null binding variants
for normal, insufficient, invalid-approval, and tampered-ledger. All 16
contradictory variants were rejected.

## Historical blocker replay

- The formal invalid-approval result records and actually executes, in fixed
  order, `wrong_trace`, `wrong_plan`, `wrong_decision`, and `unbound_event`
  through `SafeMCPAdapter` approval calls. Artificially accepting one probe
  aborts the Eval before the metric can pass.
- Approval applicability contains invalid, normal, and tampered cases and
  reports `3/3`.
- A predeclared attempted scenario with `scenario_run=false` remains in the
  denominator and reports `0/1 FAIL`.
- CLI classification is fixed and non-leaking: normal PASS returns 0; a metric
  mismatch returns 1; malformed JSON, schema-invalid type, and either output
  I/O failure return 2; internal TypeError, RuntimeError, and AssertionError
  return 3. No traceback or injected internal text was emitted.
- Required five-kind coverage, unique case IDs, unique declared trace IDs,
  nested dataset schema, provenance/corroboration invariants, and semantic
  contradictions are rejected before execution.
- Four executed cases emit four unique trace IDs. Ledger integrity uses
  `unique_trace` aggregation and reports `4/4`. Conflicting remains a
  non-executed boundary with no trace.
- Result schema rejects malformed metric arrays and invalid summary types/exit
  values. All eight metric records retain required fields and stable ordering.
- All eight empty core metrics report denominator 0 and `passed=false`.
- The runner does not select an oracle from source scenario ID, title, or a
  legacy dataset `expected` field.
- Handoff and dataset consistently use dataset version `1.1.0`; the Handoff
  lists exit codes 0/1/2/3, scopes claims to the local repository, and states
  runtime/live unknown.

## Determinism and report consistency

Two isolated CLI executions both returned 0 with summary 8 passed, 0 failed.

- JSON SHA-256, both runs:
  `8010784B33DF82D94C3E54EA00A3B43CC60E511787464C9B89BFB4CE6119C982`
- Markdown SHA-256, both runs:
  `0F1E00C9C6FDB1FCCC64CDB0C6A6194314DE9C02E80099B8DA702F97DBE11819`
- Every JSON metric numerator/denominator matched the corresponding Markdown
  row.
- The invalid case in the JSON report contains all four ordered approval probe
  names and no event content.

## Independent commands and results

| Check | Result |
| --- | --- |
| `pwsh -File .\scripts\sectrace-preflight.ps1 -Mode code` | `READY_CODE` |
| `python -m pytest -q -p no:cacheprovider tests/evaluation` | `52 passed` |
| `python -m pytest -q -p no:cacheprovider tests/security/test_repository_hygiene.py` | `16 passed` |
| `python -m pytest -q -p no:cacheprovider` | `196 passed` |
| Conflicting approval/provenance, first/middle/last | 24/24 invalid variants rejected |
| Other four case approval invariants | 16/16 invalid variants rejected |
| Formal four-probe result and forced-acceptance gate | PASS |
| Scenario failure denominator | `0/1`, FAIL as required |
| CLI 0/1/2/3 and non-leakage | PASS |
| Five kinds, duplicate case/trace, nested schema, provenance/corroboration | PASS |
| Unique-trace ledger and empty core population | `4/4`; all eight `0/0` fail |
| Result-schema negative probes | PASS |
| Two isolated CLI/hash runs and JSON/Markdown consistency | PASS |
| `git diff --check` / `git diff --cached --check` | PASS |

## Repository-state and safety audit

Before adding this file, HEAD matched the required base, tracked/staged diff was
empty, and untracked state contained only the Handoff, four preserved FAIL
records, `evaluation/**`, and `tests/evaluation/**`. This cycle writes only the
present QA record. All four historical hashes are rechecked after the write.

No public Contract, six-tool allowlist, canonical ledger sequence, persistence
code, 01–04 role code, runtime/live resource, Matrix action, credential,
commit, or push was changed or invoked. Evaluation data and probes remained
synthetic and local.

## Fixed completion report

```text
STATUS: PASS
PLAN_COMMIT: 9b725e48df05e78b20713d523c1af3f627572a4e
BASE_COMMIT: 9b725e48df05e78b20713d523c1af3f627572a4e
FINAL_COMMIT: NO_COMMIT
FILES_CHANGED: docs/verification/V-OPT2-02-fourth-corrected-independent-qa.md
HANDOFF: V-OPT2-02 fifth independent repository-only QA
TESTS_RUN: code preflight; focused Eval; repository hygiene; full pytest; conflicting approval/provenance field/combined first-middle-last matrix; other four approval invariant matrix; formal four-probe gate; scenario denominator; CLI 0/1/2/3; all historical schema/category/duplicate/trace/ledger/provenance/zero probes; two isolated CLI/hash runs; JSON/Markdown and claim/version/diff/staged/untracked audits
TEST_RESULT: PASS — all historical blockers and fifth-round semantic invariants independently pass
NEW_BEHAVIOR: none; fifth independent QA record only
UNCHANGED_SAFETY_BOUNDARIES: synthetic/de-identified local evaluation only; runtime/live unknown; no public Contract, six-tool, canonical ledger/persistence, Matrix, approval action, commit, or push change
KNOWN_LIMITATIONS: no runtime/live/production evidence and no implemented OPT2-04 conflicting terminal
NEXT_HANDOFF: owner 00 may proceed with the normal integration/release decision while retaining all four historical FAIL records and this revision-scoped PASS
```
