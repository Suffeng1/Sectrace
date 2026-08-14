# V-OPT2-03A Intake Skill Corrected Independent QA

- Owner: 05
- Date: 2026-08-13 (Asia/Shanghai)
- Scope: corrected OPT2-03A Intake Skill uncommitted repository-only candidate
- Plan/Base/HEAD: `7d4f51d1605e69d2d975ad12ced387a9a2b33227`
- Branch: `codex/adopt-apache-license`
- Handoff: `docs/handoffs/H-OPT2-03A-intake-skill.md`
- Preserved first FAIL: `docs/verification/V-OPT2-03A-intake-skill-independent-qa.md`
- Preserved first FAIL SHA-256: `C32C1F70E239927B7D01DC08CCB8BDBC3ED08196703DD680F876359220FDAF33`
- Preflight: `READY_CODE`
- Runtime/live activity: none; current runtime/live state remains unknown
- Verdict: **FAIL**

## Verdict

**FAIL**. The correction closes the original permissive-schema, ordinary
length/type/timestamp, strict `real_data`, dependency, corpus-oracle, deep-copy,
and scope blockers. It does not yet provide full callable/Schema parity or the
documented fixed non-leaking `ValueError` for all schema-invalid inputs.

Missing required fields can escape as raw `KeyError`, while list/dict values in
enum positions can escape as raw `TypeError`. Both are independently
reproducible through the production callable and are absent from the focused
test matrix. The corrected candidate therefore remains blocked from registry
integration or publication.

This verdict applies only to this uncommitted working tree at the exact HEAD
above. It does not establish runtime/live, external-system, latency, cost,
availability, or production state.

## Remaining blocking findings

### F-01: missing required properties escape as `KeyError`

`src/skills/intake/normalize.py:82` and line 99 use proper-subset checks:

```python
if set(event) < {"event_ref", "event_type", "at", "subject"}:
if set(scenario) < {"scenario_id", "real_data", "events", "expected"}:
```

When an input omits a required property but retains an optional property, its
key set is not a proper subset of the required set. Validation continues and
direct indexing at lines 84–88 or 101–107 raises a raw key-derived exception.

Independent probes produced:

- missing root `scenario_id`, `events`, or `expected` -> `KeyError` naming the
  missing property;
- missing event `event_ref`, `event_type`, `at`, or `subject` -> `KeyError`
  naming the missing property.

The input Schema rejects every probe, so callable/Schema error parity is not
met. This also contradicts `SKILL.md:49-52`, which says absent fields fail with
a fixed error before output.

### F-02: non-scalar enum values escape as `TypeError`

`src/skills/intake/normalize.py:63` and line 86 perform set membership before
checking that enum values are strings. JSON arrays and objects are unhashable.

Independent probes placed list/dict values in `event_type`,
`expected.severity_hint`, `expected.classification`, and `expected.intake`.
The Schema rejected all of them, but the callable raised
`TypeError: unhashable type` instead of `ValueError("invalid intake payload")`.

These messages expose input type details and violate the fixed non-leaking
failure contract. Existing focused tests cover an integer `event_type`, but do
not cover list/dict values in any enum field.

### F-03: current documentation and Handoff facts drift

- `src/skills/intake/SKILL.md:13` says the function returns a shallow copy,
  while the implementation uses `deepcopy` and line 40 correctly says deep
  copy.
- `SKILL.md:6-8` says the `jsonschema` declaration is still requested from
  owner 00, although `pyproject.toml` now declares `jsonschema>=4,<5`.
- The Handoff reports focused Commander/Intake `63 passed` at lines 106–108.
  Independently running the release command documented in `SKILL.md:59`,
  `tests/commander tests/skills/intake`, collected and passed 33 tests.

These are claim/documentation defects rather than evidence that the dependency
or deep-copy implementation is absent, but must be corrected before a PASS
record can affirm the Skill documentation and Handoff as accurate.

## Original blockers independently closed

- Root, event, and `expected` schemas all use
  `additionalProperties: false`; required properties, types, bounded IDs and
  strings, event-type enums, and UTC `Z` RFC3339 timestamps are declared.
- Callable and Schema both reject the original extra/path/secret-like fields,
  overlong IDs/event refs/subjects, unsupported or integer event types,
  malformed/non-UTC/impossible timestamps, and the 65-character ID boundary.
- `real_data` accepts only the exact JSON boolean `false`. `true`, strings,
  numbers, null, arrays, objects, and absence are rejected.
- The legal semantic value `classification: "unknown"` is accepted and
  preserved; an unknown property remains rejected.
- All 24 synthetic scenarios agree with their declared intake oracle. S09,
  S10, S11, and S12 reject; the other 20 accept and validate against both
  input/output schemas.
- Golden output is exact. The real-data badcase rejects with the fixed safety
  error. Accepted input is deeply unchanged and repeated output is
  deterministic.
- `pyproject.toml` declares `jsonschema>=4,<5` in the dev dependency set.
- No MCP tool, public Contract, canonical ledger, or registry implementation
  changed. Evaluation language remains limited to full-pipeline OPT2-02
  evidence and makes no per-Skill score or current-live claim.

## Independent commands and results

| Check | Result |
| --- | --- |
| `scripts/sectrace-preflight.ps1 -Mode code` | `READY_CODE` |
| HEAD gate | exact `7d4f51d1605e69d2d975ad12ced387a9a2b33227` |
| first FAIL integrity | SHA-256 unchanged: `C32C...F33` |
| `python -m pytest -q -p no:cacheprovider tests/commander tests/skills/intake` | `33 passed` |
| `python -m pytest -q -p no:cacheprovider tests/security/test_repository_hygiene.py` | `16 passed` |
| `python -m pytest -q -p no:cacheprovider` | `225 passed` |
| original negative matrix | 25/25 rejected; fixed errors except missing-field cases |
| missing required root/event matrix | 7/7 incorrectly raised raw `KeyError` |
| list/dict enum-type matrix | 8/8 incorrectly raised raw `TypeError` |
| legal unknown / deep invariance / determinism | PASS / PASS / PASS |
| golden / real-data badcase | exact PASS / fixed rejection PASS |
| S01-S24 declared oracle | 24/24 match; 20 accept, 4 reject |
| accepted corpus input/output Schema parity | PASS |
| `git diff --check` / `git diff --cached --check` | PASS / PASS |
| staged audit | 0 staged files |
| untracked/dirty audit before this record | corrected OPT2-03A, preserved first FAIL, and reconciled owner-00 dependency/shared test only |

An initial parallel command batch exceeded its 10-second outer orchestration
window. Each required gate was immediately rerun independently and completed
with the explicit results above; this was not a pytest failure.

## Minimum repair recommendation

1. Replace the proper-subset checks with explicit missing-key checks, such as
   `REQUIRED_FIELDS - set(payload)`, before all direct indexing.
2. Require enum values to be strings before set membership, or otherwise make
   membership total for all JSON types.
3. Add parameterized missing root/event and list/dict enum counterexamples that
   assert the exact fixed `ValueError` and absence of payload-derived content.
4. Correct the shallow/deep-copy statement, dependency status, and focused test
   count in current documentation/Handoff.
5. Re-run owner GREEN, focused/hygiene/full pytest and Git audits, then request
   another corrected independent QA. Owner 05 must not implement these fixes.

## Fixed completion report

```text
STATUS: FAIL
PLAN_COMMIT: 7d4f51d1605e69d2d975ad12ced387a9a2b33227
BASE_COMMIT: 7d4f51d1605e69d2d975ad12ced387a9a2b33227
FINAL_COMMIT: NO_COMMIT
FILES_CHANGED: docs/verification/V-OPT2-03A-intake-skill-corrected-independent-qa.md
HANDOFF: docs/handoffs/H-OPT2-03A-intake-skill.md
TESTS_RUN: code preflight; focused Commander/Intake; repository hygiene; full pytest; original blocker matrix; missing-required and unhashable-enum matrices; exact real_data; schema parity; legal unknown; S01-S24 oracle; deterministic deep invariance; golden/badcase; claims/scope; diff/staged/untracked audits
TEST_RESULT: FAIL — 33 focused, 16 hygiene, and 225 full tests pass, but independent schema-invalid probes escape as KeyError/TypeError instead of fixed ValueError
NEW_BEHAVIOR: none; corrected independent QA record only
UNCHANGED_SAFETY_BOUNDARIES: no runtime/live/Matrix/external action; no public Contract, MCP tool, registry, ledger, commit, or push change
KNOWN_LIMITATIONS: callable error parity remains incomplete for missing required properties and unhashable enum values; documentation facts drift; current runtime/live unknown
NEXT_HANDOFF: owner 01 corrects total fail-closed validation/tests/docs; owner 00 must not integrate or publish the registry entry until owner GREEN and a subsequent owner 05 PASS
```
