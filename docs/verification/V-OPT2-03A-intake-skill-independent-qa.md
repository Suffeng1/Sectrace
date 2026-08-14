# V-OPT2-03A Intake Skill Independent QA

- Owner: 05
- Date: 2026-08-13 (Asia/Shanghai)
- Scope: OPT2-03A Intake Skill uncommitted repository-only candidate
- Plan/Base/HEAD: `7d4f51d1605e69d2d975ad12ced387a9a2b33227`
- Branch: `codex/adopt-apache-license`
- Handoff: `docs/handoffs/H-OPT2-03A-intake-skill.md`
- Preflight: `READY_CODE`
- Runtime/live activity: none; current runtime/live state remains unknown
- Verdict: **FAIL**

## Verdict

**FAIL**. The version, entrypoint, bounded evaluation disclosure, golden output,
real-data marker rejection, determinism, and non-mutation claims are supported.
However, the executable boundary and both schemas are not fail-closed for the
strict input contract required by this ticket. They accept and preserve
unbounded identifiers, malformed or missing event semantics, path-like fields,
secret-like fields, and arbitrary extra properties. The production Commander
path calls `normalize_scenario` directly and does not enforce the JSON Schema,
which also exposes a `real_data` type bypass.

This verdict applies only to the uncommitted candidate and exact HEAD above. It
does not attest runtime/live, external systems, latency, cost, availability, or
registry publication.

## Blocking findings

### F-01: schemas accept extra, path-like, and secret-like fields

Both schemas set `additionalProperties: true` at the root, event-item, and
`expected` object levels:

- `src/skills/intake/schema/input.schema.json`: lines 16, 22, 25
- `src/skills/intake/schema/output.schema.json`: lines 16, 23, 26

Because `normalize_scenario` returns shallow copies that preserve all fields
(`src/skills/intake/normalize.py:31`), independently injected `source_path`,
event `path`, `api_key`, `operator_token`, and arbitrary `unknown` content were
schema-valid and were returned unchanged. This violates the ticket's strict
`additionalProperties` and no-secret/no-real-system-field acceptance gate.

Impact: a schema-valid Skill invocation can carry undeclared sensitive-looking
or system-location content across the intake boundary and into downstream
callers.

### F-02: required event semantics and length bounds are absent

The schemas and callable require only a non-empty `scenario_id`, an array, a
non-empty `event_ref`, an `expected` object, and a supported severity hint.
They do not bound identifier lengths, require/enum-check `event_type`, or
require/format-check the corpus timestamp field `at`.

Independent probes confirmed acceptance of:

- a 10,001-character `scenario_id`;
- an integer `event_type`;
- a missing `event_type`;
- `at: "not-a-time"` (and an undeclared malformed `timestamp`).

This also conflicts with the repository's existing intake rejection oracles:
`data/scenarios/S09.json` requires rejection for missing `event_type`, S10 for
an invalid timestamp, and S12 for an unsupported event type.

### F-03: runtime validation diverges from the declared schema

The input schema types `real_data` as boolean, but production
`src/agents/commander/service.py:9` invokes the callable without schema
validation. `src/skills/intake/normalize.py:13` rejects only
`scenario.get("real_data") is True`; schema-invalid values such as the string
`"true"` are accepted and preserved. Therefore the published Schema is not the
effective production boundary.

### F-04: focused tests do not cover the release-critical boundary

`tests/skills/intake/test_skill_contract.py:42-53` covers missing coarse fields
and unsupported severity only. It does not assert extra-property rejection,
path/secret-like rejection and non-leakage, maximum lengths, `real_data` type
bypasses, event type/timestamp validation, determinism, or complete input
invariance. Consequently the reported GREEN result does not establish the
strict contract required for release.

The tests also import `jsonschema`, while `pyproject.toml` does not declare it
in project or `dev` dependencies. The suite passes in the current environment,
but a clean environment is not guaranteed to reproduce it.

## Passing checks and bounded claims

- `SKILL.md` identifies Intake Skill `1.0.0`, the actual function entrypoint,
  Python 3.11+, the production Commander consumer, lifecycle gates, rollback,
  and current ownership.
- The golden fixture exactly equals the current normalize output and the input
  object remains unchanged.
- The `real_data: true` badcase fails before output with the fixed non-leaking
  error `intake accepts synthetic or de-identified data only`.
- Repeated calls over accepted probes were deterministic.
- `SKILL.md` correctly says this is not a new MCP tool, registry integration is
  still pending owner 00, and OPT2-02's dataset `1.1.0` / eight metrics are
  revision-scoped full-pipeline evidence rather than a per-Skill score.
- The working-tree diff contains no MCP adapter, public Contract, registry, or
  ledger change; no files are staged.

## Independent commands and results

| Check | Result |
| --- | --- |
| `scripts/sectrace-preflight.ps1 -Mode code` | `READY_CODE` |
| HEAD gate | exact `7d4f51d1605e69d2d975ad12ced387a9a2b33227` |
| `python -m pytest -q -p no:cacheprovider tests/commander tests/skills/intake` | `10 passed` |
| `python -m pytest -q -p no:cacheprovider tests/security/test_repository_hygiene.py` | `16 passed` |
| `python -m pytest -q -p no:cacheprovider` | `202 passed` |
| Golden exact output / badcase rejection | PASS / PASS, no payload leakage |
| Empty ID / missing required top-level fields | rejected |
| Long ID / bad or missing event type / bad timestamp | incorrectly accepted |
| Path / secret-like / extra-field probes | incorrectly schema-valid, accepted, and preserved |
| Input invariance / determinism | PASS |
| `git diff --check` / `git diff --cached --check` | PASS / PASS |
| staged audit | 0 staged files |
| dirty audit before this record | only OPT2-03A delivery files |

## Minimum repair recommendation

1. Freeze the actual supported scenario, event, and expected properties needed
   by the synthetic corpus; set `additionalProperties: false` at every object
   level without discarding legitimate corpus fields.
2. Add bounded string constraints and patterns for IDs, a supported
   `event_type` enum, and RFC 3339 validation for the canonical `at` field.
3. Make the production callable enforce the same effective contract as the
   schemas, including strict boolean handling and fixed non-leaking rejection
   for undeclared/path/secret-like content.
4. Add focused negative tests for every counterexample above, plus determinism,
   deep input invariance, and error non-leakage. Declare `jsonschema` in the
   appropriate test/development dependency set.
5. Re-run owner GREEN, focused/hygiene/full pytest and all Git audits, then
   request corrected independent QA. Owner 05 must not implement these fixes.

## Fixed completion report

```text
STATUS: FAIL
PLAN_COMMIT: 7d4f51d1605e69d2d975ad12ced387a9a2b33227
BASE_COMMIT: 7d4f51d1605e69d2d975ad12ced387a9a2b33227
FINAL_COMMIT: NO_COMMIT
FILES_CHANGED: docs/verification/V-OPT2-03A-intake-skill-independent-qa.md
HANDOFF: docs/handoffs/H-OPT2-03A-intake-skill.md
TESTS_RUN: code preflight; focused Commander/Intake; repository hygiene; full pytest; golden/badcase; independent strict schema, length, event type/timestamp, path/secret/extra-field, type-bypass, invariance and determinism probes; diff/staged/untracked audits
TEST_RESULT: FAIL — standard suites pass (10 focused, 16 hygiene, 202 full), but release-critical independent counterexamples are accepted
NEW_BEHAVIOR: none; independent QA record only
UNCHANGED_SAFETY_BOUNDARIES: no runtime/live/Matrix/external action; no public Contract, MCP tool, registry, ledger, commit, or push change
KNOWN_LIMITATIONS: permissive schemas and callable allow undeclared, path-like, secret-like, malformed and unbounded input; current runtime/live unknown
NEXT_HANDOFF: owner 01 applies the minimum fail-closed contract/test/dependency repair; owner 00 must not integrate or publish the registry entry until corrected owner GREEN and owner 05 PASS
```
