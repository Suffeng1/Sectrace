# V-OPT2-03D Audit Skill Corrected Independent QA

- Owner: 05
- Task: corrected bounded QA for `V-OPT2-03D`
- Scope: current uncommitted corrected OPT2-03D Audit Skill candidate, repository-only
- Plan/Base/HEAD: `2992e75b64b37928d678b004605da4cb8d3a358b`
- Preflight: `READY_CODE`
- Preserved first FAIL SHA-256: `2DE5D535E8E3AAD4030F51181B9DB4B3EF808115050FD9DDBD7596A79C57B0B3`
- Runtime/live status: unknown; no runtime/live activity performed
- Verdict: **QA_FAIL**

## Verdict

**QA_FAIL**. The correction closes the original non-finite Pydantic,
plain-container, fixed-error, strict-Schema and copied-Badcase failures. One
minimal F1 blocker remains: an Evidence identity can still collide with a
supplied Incident/related event reference and a fully rehashed matching ledger
is then accepted as `qualified/passed`. This violates the explicitly frozen
ambiguous evidence/source/ref binding rejection requirement.

No new feature or broader namespace rule is requested. The blocker is limited
to identifiers already supplied to this callable. The existing low-risk
OPT2-02 oracle was not redefined.

## Minimal reproducible blocker

Two independent synthetic controls reproduced the same missing invariant:

1. An Incident supplied `raw_event_refs=["evt_s01_001", "evt_other"]`.
   Evidence used `evidence_id="evt_other"` and
   `source_ref="evt_s01_001"`. After changing the evidence ledger payload to
   `evidence:evt_other` and canonically recomputing all hashes, Audit returned
   `qualified/passed` with no missing requirement.
2. With two legal event sources, the first Evidence `related_event_refs`
   contained `ev_other` while the second Evidence used
   `evidence_id="ev_other"`. A canonically rehashed matching five-event ledger
   again returned `qualified/passed` with no missing requirement.

The corrected `_valid_evidence_bindings` rejects duplicate Evidence IDs,
duplicate source refs, direct evidence/source collisions and duplicate related
refs, but it does not compare Evidence IDs with Incident raw-event refs or the
complete related-event-ref namespace.

Minimal repair: before qualification, require the set of all Evidence IDs to
be disjoint from the union of Incident `raw_event_refs`, all Evidence
`source_ref` values and all `related_event_refs`; reject either collision with
the existing exact `ValueError("invalid audit input")`. Add the two controls
above plus one ordinary disjoint control. This is a callable-only cross-object
invariant and requires no Schema, Contract, ledger, tool or registry change.

## Closed original findings

### F1 closed except for the blocker above

- Four model-copy/construct non-finite probes spanning Incident, Evidence,
  Response and Approval were rejected 4/4 with the exact fixed error.
- UserDict, custom iterable, list subclass, dict-record subclass, UserDict
  records, and a hostile object record were rejected 6/6 with the exact fixed
  error. A hostile Evidence list subclass was also rejected. Overridden
  iteration/length/index/value methods were called zero times.
- Duplicate Evidence ID, duplicate source ref, direct evidence/source namespace
  collision and duplicate related refs were rejected 4/4 with the exact fixed
  error.
- Ordinary built-in lists/dicts/records remained accepted; the golden call was
  deterministic and deeply non-mutating.

### F2 strict structural Schema and rebuild disclosure closed

- The golden input and nullable `response_plan`/`approval` input each produced
  zero Schema errors.
- Sixty-four bounded negative cases covering top-level and nested required
  fields, additional properties, enum/type errors, date-time format, identifier
  and text bounds, array capacities, and identity/reference duplicates were
  rejected 64/64.
- Seventeen output negative cases covering every required field, additional
  properties, enum/type/bound errors and duplicate reference/requirement arrays
  were rejected 17/17; the golden review conformed.
- Duplicate free-text Response actions/verification/rollback strings were not
  promoted into a new rejection requirement because the frozen shared Contract
  permits them. Identity and reference duplicates remain rejected as required.
- Each of the nine declared `AuditReview` fields was independently substituted
  with a different Pydantic-valid value. Every forged object differed from the
  deterministic rebuild, while repeated rebuilds remained identical.
- `SKILL.md` accurately limits JSON Schema to supported serialized structure
  and states that model internals, canonical hash computation, cross-object and
  ordered binding, and exact derived-review reconstruction are callable-only
  invariants. It does not present Schema/Pydantic shape validation as
  authoritative review acceptance.

### F3 packaged Badcase closed

The packaged Badcase is materially different from the golden five-record
ledger. Its standalone non-canonical hash makes `verify_ledger` return
`(False, "")`, and the callable returns `not_qualified/failed` when it replaces
the golden ledger.

## Frozen Audit matrix

- The complete approved, reference-bound, canonical high-risk chain alone
  returned `qualified/passed` with the verified terminal hash.
- Pending Approval, rejected Approval, and missing Response/Approval returned
  `not_qualified`.
- Reference mismatch and order mismatch remained `not_qualified` after their
  complete chains were canonically rehashed, proving relational rejection
  independently of hash integrity.
- Tampered payload and hash mismatch returned `not_qualified/failed` with an
  empty exported terminal hash.
- Golden output equality, repeated determinism and deep non-mutation passed.
- S01-S24 Evaluation passed. Static Audit/Skill review found no scenario-ID,
  title, expected-field or source-scenario oracle selector.
- Static and diff review found no evidence/plan creation, approval, execution,
  input or ledger mutation, MCP/public Contract/canonical ledger algorithm/
  registry/other-role/runtime/live expansion.

## Commands and results

| Check | Result |
| --- | --- |
| `scripts/sectrace-preflight.ps1 -Mode code` | `READY_CODE` |
| `python -m pytest -q -p no:cacheprovider tests/audit tests/skills/audit tests/evaluation` | `73 passed` |
| `python -m pytest -q -p no:cacheprovider tests/audit tests/skills/audit` | `21 passed` |
| `quick_validate.py src/skills/audit` | `Skill is valid!` |
| `python -m pytest -q -p no:cacheprovider tests/security/test_repository_hygiene.py` | `16 passed` |
| `python -m pytest -q -p no:cacheprovider` | `373 passed` |
| Non-finite/exact-container/hostile/fixed-error controls | PASS |
| Duplicate and direct evidence/source binding controls | PASS |
| Incident/related-ref namespace collision controls | FAIL — minimal blocker |
| Input/output strict structural Schema matrices | PASS |
| Nine-field deterministic rebuild comparison | PASS |
| Badcase material-difference/direct fail-closed check | PASS |
| Pending/rejected/missing/tamper/ref/order/hash matrix | PASS |
| `git diff --check` / `git diff --cached --check` | PASS; index empty |

## Repository-state and safety audit

Before this corrected report, tracked changes were limited to
`src/agents/audit/service.py` and `tests/audit/test_service.py`. Untracked
content was limited to the owner-04 Handoff, the Audit Skill package, focused
Audit Skill tests, and the preserved first FAIL. The first FAIL remained
byte-for-byte unchanged at the SHA-256 recorded above. This QA adds only the
present corrected verification record and modifies no owner-04 artifact.

All probes were local, synthetic and in-memory. No secret value, real-system
connection, Matrix action, approval action, runtime/live mutation, commit or
push occurred.

## Fixed completion report

```text
STATUS: QA_FAIL
PLAN_COMMIT: 2992e75b64b37928d678b004605da4cb8d3a358b
BASE_COMMIT: 2992e75b64b37928d678b004605da4cb8d3a358b
FINAL_COMMIT: NO_COMMIT
FILES_CHANGED: docs/verification/V-OPT2-03D-audit-skill-corrected-independent-qa.md
HANDOFF: V-OPT2-03D corrected bounded repository-only independent QA
TESTS_RUN: code preflight; focused Audit+Skill+Evaluation; quick_validate; hygiene; full pytest; non-finite Pydantic; exact built-in/UserDict/custom/hostile containers; fixed-error/no-invocation; evidence/source/ref namespace and duplicates; strict input/output Schema; nine-field deterministic rebuild; Badcase identity/direct failure; pending/rejected/missing/tampered/rehashed-ref/rehashed-order/hash; determinism/deep non-mutation; S01-S24/no-oracle; diff/cached/staged/untracked/static scope
TEST_RESULT: QA_FAIL — Evidence IDs can still collide with Incident raw-event or related-event references and qualify on a valid matching canonical chain
NEW_BEHAVIOR: none; corrected independent QA record only
UNCHANGED_SAFETY_BOUNDARIES: synthetic/de-identified repository-only checks; read-only Audit; advice only; runtime/live unknown; no execution, Contract, tool, ledger algorithm/history, registry, other-role, Matrix, approval, commit or push activity
KNOWN_LIMITATIONS: no runtime/live/production evidence; result is revision-scoped to the current uncommitted corrected candidate
NEXT_HANDOFF: owner 04 should add only the minimal cross-object Evidence-ID/event-ref disjointness guard and two regression controls, then request another bounded owner-05 QA; owner 00 should not integrate this revision
CONTROLLER_NOTIFIED: true
```
