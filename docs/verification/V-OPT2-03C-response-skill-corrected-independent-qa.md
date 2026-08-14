# V-OPT2-03C Response Skill Corrected Independent QA

- Owner: 05
- Task: corrected independent QA for `V-OPT2-03C`
- Scope: corrected Response Skill uncommitted candidate, repository-only
- Plan/Base/HEAD: `5df7316f858adef0b6a6cb76c904cd61d7ade05e`
- Branch: `codex/adopt-apache-license`
- Preflight: `READY_CODE`
- Prior FAIL record SHA-256: `A73D73E0B25771C16477BF91D3150C0A18C5DDEDBAF5470BC2B0591AE65EA6A6`
- Runtime/live status: unknown; no runtime/live activity performed
- Verdict: **QA_FAIL**

## Verdict

**QA_FAIL**. The correction closes the four concrete reproductions recorded in
the first QA: missing/extra Pydantic fields now use the fixed error, both
cross-object namespace collision directions fail closed, and embedded path
tokens have matching callable/Schema rejection. Independent expansion of the
explicit corrected acceptance criteria still finds three substantive bypasses.
The current candidate must not be released or integrated into the registry.

The first QA file remains byte-for-byte unchanged at the hash above. This
corrected result applies only to the uncommitted working tree at the exact HEAD
above and establishes no runtime/live or production fact.

## Blocking findings

### C1 — abnormal Pydantic fields-set/private metadata is accepted

All required-field omissions, wrong internal field values/types, injected
`__dict__` extras, and abnormal Pydantic-extra storage now fail with the exact
non-leaking `ValueError("invalid response evidence")`. However, seven abnormal
fields-set/private metadata shapes are silently accepted and create plans.
There is no exception leak, but the corrected requirement says abnormal
private/internal shapes must fail closed, and the implementation already claims
an exact genuine-model internal shape boundary.

Minimal owner-03 fix: for this Contract model, require an exact ordinary
fields-set equal to the eight declared evidence fields and the normal absence
of private storage before serialization. Normalize access/type failures to the
fixed error. Add empty, wrong-type, over-declared fields-set and empty/non-empty
private-storage tests, while retaining valid validated, copied, and fully
populated constructed controls.

### C2 — same-item cross-namespace overlap violates the declared invariant

Duplicate evidence IDs, duplicate source references, and both cross-object
evidence/source collision directions now fail before plan creation. A single
otherwise valid item whose evidence ID equals its own source reference is still
accepted. This contradicts the SKILL's “non-overlapping evidence-ID/source-
reference binding” statement and leaves the global namespace intersection
non-empty.

Minimal owner-03 fix: reject `evidence_id == source_ref` for the current item,
or equivalently build both complete identifier sets and reject any intersection
before returning normalized evidence. Keep the benign disjoint bijection
control.

### C3 — nested list subclasses are normalized into acceptance

Top-level list subclasses, mappings, mapping items, unhashable nested values,
and duplicate items fail with the fixed error. A `related_event_refs` list
subclass is converted by `model_dump` into an ordinary list before the explicit
type check and is accepted. This misses the delegated requirement to replay all
prior abnormal-list/hostile-container negatives at fields relevant to the real
signature.

Minimal owner-03 fix: validate the exact raw type of every declared field before
Pydantic serialization, especially `type(related_event_refs) is list`; then
validate the normalized copy as defense in depth. Add benign ordinary-list and
nested-list-subclass controls and assert exact fixed errors without input echo.

## Passing corrected coverage

- Missing required attributes passed 8/8 fixed-error probes; wrong internal
  values/types passed 48/48; injected extra stores passed 2/2. No raw
  `AttributeError`, `KeyError`, `TypeError`, Pydantic detail, cause chain, or
  rejected value leaked. Valid validated, copied, and fully populated
  constructed instances passed 3/3 and remained unmodified.
- Four cross-object identity cases now fail closed: duplicate evidence ID with
  a distinct source, duplicate source with a distinct evidence ID, and both
  evidence/source collision directions. The benign bijection remains accepted,
  deterministic, and correctly plan-bound. The SKILL honestly states that the
  portable JSON Schema is structural and the callable adds relational checks.
- Embedded Windows user-directory, Windows absolute/UNC, Unix absolute, and
  mixed-case temporary path categories passed 18/18 Schema rejections, 18/18
  fixed callable rejections, and 18/18 agreement checks across start, middle,
  and end placement. No probe value was printed or persisted. Node successfully
  compiled the JSON Schema pattern as ECMAScript.
- Every ordinary legal classification/confidence/evidence-level combination
  preserved the real high/low branch truth table. All eight multi-item
  strong/corroborated high-risk variants stayed advice-only,
  `requires_approval=true`, `status=pending_approval`, and never `executed`.
  Low-risk branches remained drafts without new authority.
- Determinism, deep non-mutation, trace/reference/plan continuity, output Schema
  conformance, action advice prefix, golden equality, raw-mapping badcase,
  required fields, additional properties, enum list/dict/null/number/bool,
  bool-as-int, empty/duplicate/over-capacity values, bad charset, secret-like
  assignments, NaN/Infinity, and fixed-error cases otherwise passed.
- All 72 independent malformed-output Schema cases were rejected.
- S01–S24 synthetic traversal produced 20 Response plans (6 high and 14 low),
  four upstream fail-closed cases, zero malformed outputs, zero executed plans,
  and zero unexpected leaks. Static Response review found no scenario ID,
  title, or expected-field oracle selector.
- `quick_validate.py`, focused tests, hygiene, full pytest, diff checks, and
  cached/staged/untracked audits passed. No OPT2-04 state, MCP/public Contract,
  canonical ledger, registry, other-role, runtime/live, commit, or push
  expansion was found.

## Commands and results

| Check | Result |
| --- | --- |
| `scripts/sectrace-preflight.ps1 -Mode code` | `READY_CODE` |
| `python -m pytest -q -p no:cacheprovider tests/response tests/skills/response` | `40 passed` |
| `quick_validate.py src/skills/response` | `Skill is valid!` |
| `python -m pytest -q -p no:cacheprovider tests/security/test_repository_hygiene.py` | `16 passed` |
| `python -m pytest -q -p no:cacheprovider` | `348 passed` |
| Pydantic missing/wrong/extra and valid-control matrices | PASS |
| Pydantic abnormal fields-set/private metadata | FAIL: C1 |
| Cross-object collisions and benign bijection | PASS |
| Complete cross-namespace non-overlap | FAIL: C2 |
| Top-level hostile containers | PASS |
| Nested list subclass | FAIL: C3 |
| Embedded path Schema/callable/ECMAScript checks | PASS |
| Legal risk, determinism, continuity, and output negatives | PASS |
| S01–S24 and no-oracle-selector audit | PASS |
| `git diff --check` / `git diff --cached --check` | PASS |

## Repository-state and safety audit

Before this report, tracked changes remained limited to
`src/agents/response/service.py` and `src/skills/response/plan.py`; the index was
empty. Untracked content remained the owner-03 Handoff, unchanged first QA
record, Response Skill package, and focused tests. This cycle adds only the
present corrected QA record. It did not modify the first QA record or any
owner-03 artifact.

No public Contract, six-tool allowlist, canonical ledger, registry, Intake,
Evidence, Audit, runtime/live resource, Matrix action, approval action,
credential, commit, or push was changed or invoked. All probes were in-memory,
local, synthetic, and intentionally absent from output artifacts.

## Fixed completion report

```text
STATUS: QA_FAIL
PLAN_COMMIT: 5df7316f858adef0b6a6cb76c904cd61d7ade05e
BASE_COMMIT: 5df7316f858adef0b6a6cb76c904cd61d7ade05e
FINAL_COMMIT: NO_COMMIT
FILES_CHANGED: docs/verification/V-OPT2-03C-response-skill-corrected-independent-qa.md
HANDOFF: owner 03 minimal correction required for C1-C3, then owner 05 re-QA
TESTS_RUN: code preflight; focused Response+Skill; quick_validate; hygiene; full pytest; Pydantic construct/copy missing/extra/wrong/internal/private matrices; cross-object and complete namespace collision probes; embedded Windows/Unix/temp path Schema/callable/ECMAScript matrix; legal high/low variants; deterministic golden/badcase/deep non-mutation; enum/type/bounds/NaN/Infinity/hostile-container negatives; 72 output Schema negatives; S01-S24/no-oracle-selector; diff/cached/staged/untracked/static scope audits
TEST_RESULT: QA_FAIL — three substantive fail-closed/invariant blockers remain
NEW_BEHAVIOR: none; corrected independent QA record only
UNCHANGED_SAFETY_BOUNDARIES: synthetic/de-identified repository-only checks; advice only; runtime/live unknown; no execution, Contract, tool, ledger, registry, other-role, Matrix, approval, commit, or push activity
KNOWN_LIMITATIONS: no runtime/live/production evidence; portable Schema remains structural and callable relational validation remains authoritative
NEXT_HANDOFF: owner 03 applies only C1-C3 and requests another revision-scoped independent QA; owner 00 must not integrate this candidate
```
