# Handoff: OPT2-03A Intake Skill engineering

STATUS: SECOND_CORRECTED_OWNER_COMPLETE_REQA_PENDING
PLAN_COMMIT: 7d4f51d1605e69d2d975ad12ced387a9a2b33227
BASE_COMMIT: 7d4f51d1605e69d2d975ad12ced387a9a2b33227
FINAL_COMMIT: NO_COMMIT

## Delivered

- Versioned the existing `normalize_scenario` boundary as Intake Skill `1.0.0`.
- Added executable Draft 2020-12 input/output schemas, a golden fixture, a
  real-data badcase, and schema/safety/failure-injection tests.
- Hardened the existing boundary to reject malformed inputs and unsupported
  severity hints with `ValueError`; valid behavior remains a non-mutating
  default of missing `severity_hint` to `low`.
- Added lifecycle documentation: dependency scope, release gates, rollback,
  safety limits, and an evaluation section which references only the real,
  revision-scoped OPT2-02 evidence.

## RED to GREEN

- RED: `tests/skills/intake/test_skill_contract.py` failed because schemas did
  not exist and the former normalization function did not reject malformed or
  unsupported values (`6 failed`).
- GREEN: the schemas and boundary validation satisfy the golden, badcase, and
  failure-injection contract tests.

## Files changed

- `src/skills/intake/normalize.py`
- `src/skills/intake/SKILL.md`
- `src/skills/intake/CHANGELOG.md`
- `src/skills/intake/schema/input.schema.json`
- `src/skills/intake/schema/output.schema.json`
- `src/skills/intake/fixtures/golden-synthetic-login.json`
- `src/skills/intake/fixtures/golden-synthetic-login.normalized.json`
- `src/skills/intake/fixtures/badcase-real-data.json`
- `tests/skills/intake/test_skill_contract.py`
- `docs/handoffs/H-OPT2-03A-intake-skill.md`

## Safety and scope

No public Contract, shared registry, six-tool allowlist, ledger, runtime/live
resource, Matrix action, credential, commit, or push was changed or used.
The Skill remains synthetic/de-identified only and does not make findings or
take security action.

## Next handoff

Owner 00: integrate the independently reviewed registry entry only; this task
does not modify the shared registry. Owner 05: independently run the listed
quality gates and validate the documentation claims and schemas. No per-Skill
evaluation score is claimed; OPT2-02 is cited strictly as full-pipeline local
evidence.

## Corrected owner cycle after V-OPT2-03A FAIL

The first independent QA FAIL at
`docs/verification/V-OPT2-03A-intake-skill-independent-qa.md` is preserved and
unchanged. This correction addresses only its four blocking findings.

- Root, event, and `expected` schemas now use `additionalProperties: false`.
  Their allowed fields, required fields, types, bounds, and semantic enumerated
  values are frozen from the existing synthetic S01–S24 corpus. The four
  established malformed/rejection fixtures S09–S12 remain rejected.
- Events now require a bounded `event_ref`, a supported `event_type`, strict
  UTC RFC3339 `at`, and bounded `subject`; optional corpus fields are bounded
  and allowlisted. `scenario_id` is bounded to 64 characters.
- `normalize_scenario` independently applies the same effective contract and
  returns only a deep copy of accepted data. Extra/path-like/secret-like field
  names, malformed semantics, unknown fields, and unsupported values are
  rejected with fixed non-leaking errors before output.
- Only JSON boolean `false` is accepted for `real_data`; `true`, absent,
  strings, numbers, arrays, and objects all reject. `classification: "unknown"`
  remains a valid semantic value rather than a permitted unknown field.
- Corrected RED tests first produced 24 failures against the permissive
  candidate. GREEN now covers every QA counterexample plus S01–S24 corpus,
  determinism, and deep input invariance.

## Dependency handoff to owner 00

Resolved by owner 00: `jsonschema>=4,<5` is now declared in the root
development dependency set. This owner task did not modify `pyproject.toml`.

## Corrected QA request

Owner 05 should retain the original FAIL record and independently verify: all
three schema object levels reject extra properties; runtime/schema parity for
every QA counterexample; strict `real_data` handling; bounded ID/event/timestamp
contract; `unknown` semantics versus unknown fields; deep-copy determinism;
S01–S24 coverage; focused/hygiene/full/diff/staged/untracked audits; and the
00-owned dependency follow-up. Runtime/live remain unknown and out of scope.

## Blocking full-suite reconciliation

Resolved by owner 00. The shared security test now reads each scenario's
`expected.intake` oracle: S09, S10, and S12 reject with the fixed malformed
payload error, while S11 rejects via the fixed real-data error. This exactly
matches the frozen fail-closed Intake boundary. Owner 00 also added the
requested `jsonschema>=4,<5` development dependency. Both changes were read
only verified by owner 01; neither shared file was modified in this task.

Corrected owner gates after reconciliation: focused Commander/Intake `33
passed`; repository hygiene `16 passed`; full suite `225 passed`; `git diff
--check` and `git diff --cached --check` passed; staged audit remains empty.
The initial independent QA FAIL record remains preserved and unchanged.

## Second corrected owner cycle after corrected QA FAIL

The first and corrected independent QA FAIL records are preserved unchanged.
This minimal follow-up closes their remaining callable/Schema error-parity and
documentation findings:

- Required-key checks now use total subset semantics before every direct field
  access. Missing root (`scenario_id`, `real_data`, `events`, `expected`) and
  event (`event_ref`, `event_type`, `at`, `subject`) fields raise exactly
  `ValueError("invalid intake payload")`, never `KeyError`.
- Every enum membership check now first requires the appropriate JSON scalar
  type. Lists, objects, and null in `event_type` or expected enum fields raise
  exactly the same fixed `ValueError`, never `TypeError`.
- Focused tests add all required-field deletions and list/dict/null enum
  counterexamples, with exact-error assertions. They retain Schema strictness,
  S01–S24 oracle alignment, `classification: "unknown"`, determinism, and deep
  non-mutation coverage.
- `SKILL.md` now consistently describes deep-copy behavior and records that 00
  has already declared `jsonschema>=4,<5` for tests.

Second corrected owner gate result: `python -m pytest -q -p no:cacheprovider
tests/commander tests/skills/intake` = `53 passed` (the current focused command
and count; supersedes the prior 33), plus hygiene/full/diff/staged/untracked
reruns below. No shared file was modified by owner 01.

## Second corrected QA request

Owner 05 should retain both earlier FAIL records and independently verify total
required-key handling, non-scalar enum handling, exact non-leaking error
messages, strict Schema/runtime parity, S01–S24 oracle behavior, deep-copy
determinism, dependencies, and all release gates before recording a new QA
verdict.
