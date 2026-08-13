# V-OPT2-03A Intake Skill Second-Corrected Independent QA

- Owner: 05
- Date: 2026-08-13 (Asia/Shanghai)
- Scope: second-corrected OPT2-03A Intake Skill uncommitted repository-only candidate
- Plan/Base/HEAD: `7d4f51d1605e69d2d975ad12ced387a9a2b33227`
- Branch: `codex/adopt-apache-license`
- Handoff: `docs/handoffs/H-OPT2-03A-intake-skill.md`
- Preserved first FAIL SHA-256: `C32C1F70E239927B7D01DC08CCB8BDBC3ED08196703DD680F876359220FDAF33`
- Preserved corrected FAIL SHA-256: `AC356AE70FAD772C181A3101B0B2CEAB3CD9CA80995EDE5F5CC13455910C3044`
- Preflight: `READY_CODE`
- Runtime/live activity: none; current runtime/live state remains unknown
- Verdict: **PASS**

## Verdict

**PASS**. The second correction closes every blocker in the first and corrected
independent QA records. Required-field validation is total before indexing;
every expected enum and event type is type-gated before membership; all
schema-invalid historical and expanded probes converge on the documented fixed
non-leaking `ValueError`; and accepted payloads retain Schema/callable parity.

The strict schemas, exact `real_data: false` gate, S01–S24 intake oracle,
allowlisted `unknown` semantic, golden/badcase behavior, deep-copy invariance,
determinism, dependency declaration, Skill claims, Handoff count, and scope
boundaries all pass independent review.

This PASS applies only to the second-corrected uncommitted working tree at the
exact HEAD above. It does not publish a registry entry or establish current
runtime/live, external-system, latency, cost, availability, or production
state.

## Historical blocker closure

### Strict Schema and callable parity

- Root, event, and `expected` objects use `additionalProperties: false`.
- Root requires `scenario_id`, `real_data`, `events`, and `expected`; events
  require `event_ref`, `event_type`, `at`, and `subject`.
- IDs and strings are bounded, event types are enumerated, and `at` requires a
  real UTC `Z` RFC3339 timestamp.
- Independent deletion of each of the eight root/event required fields was
  rejected by the input Schema and raised exactly
  `ValueError("invalid intake payload")`. No field name or value appeared in
  the error.
- Every expected enum/const semantic field was independently injected with a
  JSON list, object, null, number, and boolean. All 65 combinations were
  rejected by Schema and callable with the exact fixed error. The same five
  wrong-type values for `event_type` behaved identically.
- Together with the eight required deletions and eight `real_data` cases, the
  expanded exact-error/parity matrix passed 86/86 cases without `KeyError`,
  `TypeError`, mutation, or input-derived error text.

### Original negative and safety boundaries

- The 13 original extra/path/secret-like, overlength, unsupported event type,
  integer event type, malformed timestamp, non-UTC timestamp, and impossible
  calendar timestamp probes all failed closed with the fixed malformed-payload
  error and were rejected by the input Schema.
- Only exact JSON boolean `false` is accepted for `real_data`. `true`, strings,
  numbers, null, arrays, objects, and absence reject; invalid present values use
  the fixed synthetic/de-identified safety error.
- The real-data badcase raises exactly the safety error without payload
  leakage. The golden fixture produces the declared normalized output exactly.

### Accepted behavior and corpus oracle

- `classification: "unknown"` is a legal allowlisted semantic and is preserved;
  an unknown property is rejected.
- Accepted output is deterministic and deeply independent of the input at root,
  `events`, individual event, and `expected` levels; the caller input remains
  equal to its pre-call deep copy.
- All S01–S24 scenarios match their declared `expected.intake` oracle: S09,
  S10, S11, and S12 reject, while the other 20 accept. Every accepted scenario
  validates against both input and output schemas.

## Documentation, dependency, and scope

- `SKILL.md` consistently states deep-copy behavior and accurately records the
  `jsonschema>=4,<5` development dependency now present in `pyproject.toml`.
- The Skill Evaluation section remains limited to revision-scoped OPT2-02
  full-pipeline evidence and makes no per-Skill score, latency, cost, runtime,
  or current-live claim.
- The current Handoff focused command and `53 passed` count match the
  independent run. Historical chronology and both earlier FAIL records remain
  preserved.
- Owner 00's shared oracle test continues to read all 24 scenarios' declared
  intake result, and the root dependency change remains present. Owner 01 did
  not overwrite either reconciliation.
- No MCP tool, public Contract, canonical ledger, or registry implementation
  changed; staged state remains empty.

The repository focused tests explicitly sample selected expected enum fields
and non-scalar types rather than encoding the complete enum/type Cartesian
matrix. This is not a blocker because the implementation uses one shared
type-first enum validation path and the independent 65-case expected-enum
matrix above exercises every field and required wrong type. This record does
not attribute that full matrix to the focused test file.

## Independent commands and results

| Check | Result |
| --- | --- |
| `scripts/sectrace-preflight.ps1 -Mode code` | `READY_CODE` |
| HEAD gate | exact `7d4f51d1605e69d2d975ad12ced387a9a2b33227` |
| two historical FAIL integrity checks | both SHA-256 values unchanged |
| `python -m pytest -q -p no:cacheprovider tests/commander tests/skills/intake` | `53 passed` |
| `python -m pytest -q -p no:cacheprovider tests/security/test_repository_hygiene.py` | `16 passed` |
| `python -m pytest -q -p no:cacheprovider` | `245 passed` |
| required/enum/event-type/real-data exact-error matrix | `86/86 passed` |
| original extra/path/secret/length/type/timestamp matrix | `13/13 passed` |
| S01–S24 declared intake oracle | `24/24 matched`; 20 accept, 4 reject |
| accepted corpus input/output Schema parity | PASS |
| legal unknown / deep invariance / determinism | PASS / PASS / PASS |
| golden / real-data badcase | exact PASS / fixed non-leaking rejection PASS |
| `git diff --check` / `git diff --cached --check` | PASS / PASS |
| staged audit | 0 staged files |
| dirty audit before this record | OPT2-03A delivery, two preserved FAILs, and owner-00 dependency/shared-oracle reconciliation only |

## Fixed completion report

```text
STATUS: PASS
PLAN_COMMIT: 7d4f51d1605e69d2d975ad12ced387a9a2b33227
BASE_COMMIT: 7d4f51d1605e69d2d975ad12ced387a9a2b33227
FINAL_COMMIT: NO_COMMIT
FILES_CHANGED: docs/verification/V-OPT2-03A-intake-skill-second-corrected-independent-qa.md
HANDOFF: docs/handoffs/H-OPT2-03A-intake-skill.md
TESTS_RUN: code preflight; focused Commander/Intake; repository hygiene; full pytest; all historical negatives; 86-case required/enum/event-type/real-data exact-error and Schema-parity matrix; S01-S24 oracle; legal unknown; golden/badcase; deep non-mutation/determinism; dependency/claims/scope; diff/staged/untracked audits
TEST_RESULT: PASS — 53 focused, 16 hygiene, 245 full; all independent historical and expanded matrices pass
NEW_BEHAVIOR: none; second-corrected independent QA record only
UNCHANGED_SAFETY_BOUNDARIES: synthetic/de-identified local input only; no runtime/live/Matrix/external action; no public Contract, MCP tool, registry, ledger, commit, or push change
KNOWN_LIMITATIONS: repository focused tests sample rather than enumerate the full expected-enum/type Cartesian matrix; current runtime/live remains unknown; registry integration remains owner 00 work
NEXT_HANDOFF: owner 00 may accept V-OPT2-03A second-corrected QA PASS and proceed with separate registry integration/release decisions under existing authorization gates
```
