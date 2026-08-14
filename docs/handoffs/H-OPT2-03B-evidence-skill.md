# Handoff: OPT2-03B Evidence Skill

- Owner: 02
- Status: `CORRECTED_OWNER_COMPLETE_REQA_PENDING`
- Plan/Base commit: `21079e03d88bed8f3a5a2066f5d2fe2281000414`
- Final commit: `NO_COMMIT`
- Code preflight: `READY_CODE`

## Delivered

- Added Evidence `SKILL.md`, SemVer `1.0.0` changelog, Draft 2020-12 input and
  output schemas, synthetic S01/S05 golden fixtures, and a real-data badcase.
- Hardened only `analyze_case` at its existing function signature. It now
  rejects malformed/missing/unknown fields, type and length bypasses,
  non-boolean `real_data`, unsupported semantics, malformed timestamps, and a
  mismatched `IncidentCase` with fixed non-leaking errors before direct access.
- Preserved deterministic existing output: ordered supplied S01 facts and risk
  path; otherwise one supplied-source `unknown`/`insufficient` item containing
  `无法确认`. Input is not modified.
- Added Evidence Skill contract tests for schema conformance, fixtures,
  extra/path-like/secret-like fields, bounds/enums/types, missing fields,
  KeyError/TypeError/AttributeError avoidance, real-data injection, corpus
  boundary coverage, deterministic behavior, and output serialization.

## RED / GREEN

- RED: `python -m pytest -q -p no:cacheprovider tests/skills/evidence` =
  `33 failed, 2 passed`; it showed the absent schemas/fixtures plus permissive
  entry handling and raw exception paths.
- GREEN: focused Evidence + Skill tests = `40 passed`.

## Verification

| Command | Result |
| --- | --- |
| `pwsh -File .\scripts\sectrace-preflight.ps1 -Mode code` | `READY_CODE` |
| `python -m pytest -q -p no:cacheprovider tests/evidence tests/skills/evidence` | `40 passed` |
| `python -m pytest -q -p no:cacheprovider tests/security/test_repository_hygiene.py` | `16 passed` |
| `python -m pytest -q -p no:cacheprovider` | `282 passed` |
| `git diff --check` | PASS |
| `git diff --cached --check` | PASS; no staged files |
| `git status --porcelain=v1 --untracked-files=all` | only this owner task's 12 untracked Skill/test files, plus two modified owned files |

## Release and scope

- `SKILL.md` requires owner 00 registry integration and owner 05 independent
  QA before any release claim. It records Python/Pydantic runtime dependencies
  and owner-00's test-only `jsonschema>=4,<5` declaration, release gates, and
  a restore-and-rerun rollback procedure.
- Evaluation wording cites only the revision-scoped local OPT2-02 independent
  QA record. It makes no per-Skill score, runtime/live, production, or Alibaba
  Cloud official-Skill claim.

## Unchanged safety boundaries

- No shared Contract, MCP six-tool allowlist, registry, canonical ledger,
  persistence, Intake/Response/Audit code, runtime/live resource, Matrix
  operation, credential, commit, or push changed.
- No OPT2-04 sufficient/insufficient/conflicting branch was implemented.

## Independent QA request (owner 05)

Independently replay RED/GREEN and inspect schema/callable parity for required
fields, extra/path-like/secret-like fields, scalar and enum type bypasses,
lengths, UTC timestamps, exact non-leaking errors, incident/scenario matching,
input non-mutation, deterministic fixtures, corpus behavior, evaluation scope,
and all release gates. Write only under `docs/verification/`.

## Owner 00 handoff

Integrate the Evidence Skill in the shared registry and compatibility/release
artifacts only after independent QA. No shared-contract issue was found.

## Corrected owner cycle after V-OPT2-03B QA_FAIL

`docs/verification/V-OPT2-03B-evidence-skill-independent-qa.md` remains
unchanged. The minimal correction addresses its blockers without touching the
public Contract:

- The callable now accepts only ordinary JSON dictionaries at the scenario,
  event, and expected-object boundaries. Hostile Mapping inputs (including
  unhashable iterated keys) reject with the fixed invalid-payload error.
- Schema and callable share a free-text policy: reject secret-assignment and
  local/absolute/temp-path values without echoing them. Existing synthetic
  corpus fields remain accepted.
- Duplicate event references reject before correlation. `uniqueItems` applies
  to JSON arrays where the standard schema can express uniqueness; the callable
  additionally enforces unique event identities before output.
- Per controller decision, this Evidence Skill now requires a local `trace_id`
  of 1–128 characters matching `^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$` at its
  callable boundary and in both serialized input/output schemas. This is not a
  change to `src/app/contracts.py` or the public Contract.

Correction RED: `tests/skills/evidence` reported `12 failed, 40 passed`.
Correction GREEN: focused Evidence + Skill tests reported `55 passed`; the
system Skill Creator quick validation reported `Skill is valid!`.

### Correction-gate shared blocker

The correction's repository-hygiene gate reported two findings in the
pre-existing, owner-05-only
`docs/verification/V-OPT2-03B-evidence-skill-independent-qa.md`: a local-path
form and a credential-assignment form. The controller instruction requires
that independent QA record remain unchanged, and owner 02 cannot edit
`docs/verification/`; therefore this task cannot truthfully report a passing
hygiene or full-suite gate. Focused Evidence/Skill behavior is GREEN, but the
current handoff status is `BLOCKED_SHARED_HANDOFF` until the controller routes
an authorized preservation/redaction decision to the appropriate owner and
the gates are rerun.

## Second corrected owner cycle after corrected QA_FAIL

Both owner-05 records remain unchanged in this owner task. This minimal schema
repair replaces the three `safe_text_*` inline case-insensitive expressions
with explicit-case portable Draft 2020-12 / ECMA-262 patterns for both
secret-assignment and temporary-path checks. It adds mixed-case probes across
scenario title; event region, subject, and note; and expected conclusion,
report-contains, and report-excludes. The new RED run reported `7 failed, 59
passed`; focused GREEN reported `69 passed`, and `quick_validate.py` reported
`Skill is valid!`.

`SKILL.md` now accurately distinguishes full-object `uniqueItems` validation
from the callable's additional `event_ref` identity validation. The
Evidence-local 1–128 `trace_id` decision remains unchanged. Final broad-gate
status follows the required rerun.

### Second-correction final gates

| Command | Result |
| --- | --- |
| `pwsh -File .\scripts\sectrace-preflight.ps1 -Mode code` | `READY_CODE` |
| `python -m pytest -q -p no:cacheprovider tests/evidence tests/skills/evidence` | `69 passed` |
| `python -m pytest -q -p no:cacheprovider tests/security/test_repository_hygiene.py` | `16 passed` |
| `python -m pytest -q -p no:cacheprovider` | `311 passed` |
| `quick_validate.py src/skills/evidence` | `Skill is valid!` |
| `git diff --check` / `git diff --cached --check` | PASS |
| staged audit | empty index |

The untracked audit contains the two preserved owner-05 QA records, this
owner's Handoff, and the uncommitted Evidence Skill/test artifacts listed
above. No commit, push, runtime, or live activity occurred. Owner 05 should
now independently re-QA the portable Schema patterns, seven-location mixed-case
matrix, full-object versus property-level uniqueness disclosure, trace bound,
and all release gates.
