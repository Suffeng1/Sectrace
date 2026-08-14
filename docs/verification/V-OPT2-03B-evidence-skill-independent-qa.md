# V-OPT2-03B Evidence Skill independent QA

- Task: `V-OPT2-03B`
- Owner: 05 independent QA
- Date: 2026-08-13
- Status: `QA_FAIL`
- Plan/base/final commit: `21079e03d88bed8f3a5a2066f5d2fe2281000414`
  / `21079e03d88bed8f3a5a2066f5d2fe2281000414` / `NO_COMMIT`
- Branch: `codex/adopt-apache-license`
- Preflight: `READY_CODE`
- Scope: current unstaged and untracked OPT2-03B artifacts; the owner Handoff's
  PASS claims were not used as evidence.

## Conclusion

OPT2-03B is not ready for owner-00 registry integration. The focused and full
test suites pass, but independent adversarial probes reproduce three contract
failures:

1. A secret-like or absolute-path value in the allowed `event.note` field is
   accepted by both the input Schema and `analyze_case`. Accepted probes covered
   a credential-assignment-shaped value and `<local-user-directory>/example-file`. This
   contradicts `SKILL.md`'s claim that path-like or secret-like fields are
   rejected and does not satisfy the requested field-and-value boundary.
2. Duplicate `event_ref` values are accepted by both layers. A syntactically
   valid three-event sequence returned
   `['evt_s01_001', 'evt_s01_001', 'evt_s01_003']` as its risk path. The output
   Schema likewise accepts duplicate `risk_path` and `related_event_refs`
   entries. Source-reference uniqueness and evidence-to-event integrity are
   therefore not enforced.
3. The callable accepts `collections.abc.Mapping`, but an event or `expected`
   Mapping whose iterator yields an unhashable key escapes as raw
   `TypeError: unhashable type: 'list'` from `set(...)`. The documented fixed
   non-leaking `ValueError("invalid evidence payload")` boundary is incomplete.

There is also a lower-severity Schema completeness gap: `trace_id` has no
length or pattern constraint in either the real Pydantic Contract or the Skill
input/output Schemas; the output Schema accepted a 100,000-character value.
This is not the first failing layer because the three failures above already
block release.

## Independent evidence

### Compatibility and scope

- The public function signature remains
  `analyze_case(IncidentCase, dict) -> tuple[list[EvidenceItem], list[str]]` and
  returned objects conform to the existing Contract fields and Evidence Agent
  handoff shape.
- The implementation derives the business result only from ordered event types;
  `scenario_id`, `title`, and `expected` are validated/matched but are not used
  as output or oracle branches.
- No `sufficient | insufficient | conflicting` decision or re-analysis state was
  added. Existing `fact` and `unknown` behavior remains; `inference` is a public
  Contract possibility but is not emitted by the current callable. This is
  consistent with leaving OPT2-04 unimplemented.
- The changed production scope is confined to Evidence service/Skill artifacts.
  No MCP tool, public Contract, canonical ledger, registry, Intake, Response,
  Audit, runtime, or live artifact changed. The only cross-owner artifact in the
  worktree is the owner-02 Handoff supplied for review.

### Skill packaging and claims

- System `skill-creator` quick validation returned `Skill is valid!`.
- `SKILL.md` frontmatter contains exactly `name` and `description`; the
  description accurately targets supplied synthetic SecTrace evidence without
  external access or action. The body is concise and predominantly imperative.
- The frozen OPT2-03 plan explicitly requires a `CHANGELOG.md`, so its presence
  is project-required despite the generic skill-creator preference against
  auxiliary files. README is only a compatibility pointer.
- README/CHANGELOG do not claim an official Alibaba Cloud Skill, current
  runtime/live state, or a per-Skill score. The evaluation link is scoped to a
  local full-pipeline QA record. Version, dependency, release, and rollback text
  is consistent with the frozen plan, subject to resolving this QA failure.

### Schema/callable probes

- All 112 combinations of 14 real enum fields with list, dict, null, number,
  true, false, NaN, and Infinity were rejected by the Schema and callable with
  the fixed invalid-payload error.
- `real_data` accepted only exact boolean `false`; true, strings, integers,
  null, list, and object returned the exact non-leaking real-data error.
- Missing root and nested required fields, unknown fields, invalid timestamps,
  unsupported event types, overlong scalar fields, overlong event lists,
  boolean-as-integer `record_count`, NaN, and Infinity failed closed in the
  tested ordinary-dict paths.
- The S01 golden output matched byte-for-value after JSON parsing. Repeated calls
  were equal and the supplied scenario remained deeply unchanged. Every emitted
  S01 trace/source/related reference was tied to the supplied IncidentCase.
- S05 produced one sourced `unknown`/`insufficient` item containing `无法确认`
  and an empty risk path. The callable currently has no legal inference branch,
  so no inference output was invented for QA.
- Corpus replay accepted 20 scenarios (S01-S08 and S13-S24) and rejected the
  four intake-invalid scenarios S09-S12 at the established boundary. S01 and
  S17-S20/S22 produced the existing three-fact path; the other accepted cases
  produced the existing unknown path. No scenario identifier/title/expected
  oracle branch was observed.

## Gates run

| Gate | Independent result |
| --- | --- |
| `scripts/sectrace-preflight.ps1 -Mode code` | `READY_CODE` |
| focused `tests/evidence tests/skills/evidence` | `40 passed` |
| repository hygiene | `16 passed` |
| complete `pytest -q -p no:cacheprovider` | `282 passed` |
| skill-creator `quick_validate.py src/skills/evidence` | PASS |
| `git diff --check` | PASS |
| `git diff --cached --check` | PASS; index empty |
| staged audit | no staged files |
| untracked audit before this report | 10 Evidence Skill/test files plus the owner-02 Handoff |

Git emitted a read-only warning that the user-level `.config/git/ignore` was
not accessible; explicit `--untracked-files=all` and `git ls-files --others
--exclude-standard` still enumerated the worktree artifacts. No runtime/live,
Matrix, commit, or push action occurred.

## Minimum repair and re-QA

Return to owner 02. Apply one shared, explicit value policy in both the input
Schema and callable for allowed free-text fields, including rejection of
path-like and secret-assignment patterns without echoing the value. Enforce
unique `event_ref` values and unique output references (`uniqueItems: true` plus
callable parity). Normalize all Mapping/set/key-conversion failures to the fixed
invalid-payload `ValueError`, or narrow the accepted runtime type to ordinary
JSON dictionaries before traversal. Add regression tests for each reproduction
and decide a finite `trace_id` bound with owner 00 because it is a shared
Contract concern; do not silently change the public Contract in this owner task.

After repair, rerun the same focused, hygiene, full, diff/staged, and untracked
gates and request owner 05 re-QA. This record preserves the current failure and
must not be replaced by an owner assertion.

## Post-QA hygiene redaction

On 2026-08-14, owner 05 replaced only a local user-directory example and a
credential-assignment-shaped probe literal so repository hygiene could scan this
record safely. The original `QA_FAIL`, reproductions, impact, and repair guidance
remain substantively unchanged; no historical finding was erased.
