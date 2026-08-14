# V-OPT2-03C Response Skill Independent QA

- Owner: 05
- Task: `V-OPT2-03C`
- Scope: Response Skill uncommitted candidate, repository-only
- Plan/Base/HEAD: `5df7316f858adef0b6a6cb76c904cd61d7ade05e`
- Branch: `codex/adopt-apache-license`
- Preflight: `READY_CODE`
- Runtime/live status: unknown; no runtime/live activity performed
- Verdict: **QA_FAIL**

## Verdict

**QA_FAIL**. The normal Response and Skill suites, repository hygiene, full
pytest, quick validation, deterministic golden pair, all ordinary legal risk
variants, and advice-only high-risk gate pass. Independent model-bypass and
cross-object probes nevertheless expose fail-closed and input-contract defects.
The candidate must not be released or integrated into the registry at this
revision.

This result is scoped to the uncommitted working tree at the exact HEAD above.
It establishes no runtime/live, production, Matrix, external approval, or
official cloud-Skill fact.

## Blocking findings

### F1 — fixed-error boundary leaks a raw exception

A genuine `EvidenceItem` created through Pydantic's construction bypass with a
required attribute absent reaches direct attribute access in
`validate_evidence_items`. The public callable raises raw `AttributeError`
instead of the exact `ValueError("invalid response evidence")`. This violates
the fixed non-leaking boundary and means the current required-field tests cover
only raw mappings, not the callable's declared Pydantic signature.

Minimal owner-03 fix: put the complete validation path behind one exception
normalization boundary, explicitly inspect the model field set before attribute
access, and convert all validation/access/container failures to the fixed error.
Add a regression test using a real `EvidenceItem` construction bypass; assert
exception type and exact message only.

### F2 — callable silently accepts a Pydantic object with an extra field

A genuine `EvidenceItem` carrying an injected extra attribute is accepted and
produces a plan. The input Schema rejects the equivalent additional property,
so Schema and callable are not fail-closed peers. This is also a silent
capability widening at the model boundary.

Minimal owner-03 fix: require the exact declared `EvidenceItem` field set,
including no injected or Pydantic-extra attributes, before reading values. Add
a regression test that proves both the Schema and callable reject the same
extra-field category with the fixed callable error.

### F3 — cross-object identity namespaces are not collision-safe

The callable rejects trace mismatch, duplicate evidence IDs, duplicate source
references, missing self-links, empty links, and duplicate links. It still
accepts both cross-object collision directions where one item's evidence ID is
another item's source reference. That breaks unambiguous evidence/source object
binding. Separately, the Draft 2020-12 Schema accepts all tested relationally
invalid cross-object payloads that the callable rejects, so strict semantic
Schema/callable parity is not established.

Minimal owner-03 fix: reject intersection between the complete evidence-ID and
source-reference sets, with the fixed error. Add both collision directions.
For Schema parity, either provide an executable semantic validation layer for
serialized inputs and document its required use alongside the structural
Schema, or hand off any serialized-contract redesign to owner 00; do not claim
Schema-only relational parity that standard `uniqueItems` does not enforce.

### F4 — embedded local/absolute/temporary paths bypass the text guard

The path expression is start-anchored. All independently tested path categories
were rejected when they occupied the whole/start of the statement, but all were
accepted when embedded after ordinary text. The task requires secret-like,
local, absolute, and temporary path values to fail closed, not merely strings
that begin with them.

Minimal owner-03 fix: detect unsafe path tokens anywhere in bounded free text,
keep the Python and JSON Schema rules equivalent, and add start/middle/end
tests without echoing rejected content.

## Passing independent coverage

- Every ordinary legal combination of `classification`, `confidence`, and
  `evidence_level` was exercised. Only high-confidence corroborated/strong
  facts produced high risk; those plans were always advice-only,
  `requires_approval=true`, `status=pending_approval`, and never `executed`.
  All other supported combinations remained low-risk drafts without authority
  expansion.
- The 24 synthetic scenario files were traversed without using
  `scenario_id`, title, or expected fields as Response oracle selectors. Twenty
  reached Response (6 high, 14 low), four failed closed upstream, every emitted
  plan conformed to the output Schema, and none was executed or leaked an
  unexpected exception.
- Golden input/output equality, raw-mapping badcase, deterministic repeated
  output, deep input non-mutation, trace continuity, deterministic plan binding,
  advice prefix, action/verification/rollback capacity, and output conditional
  risk/approval/status rules passed.
- Required-field deletion, nested/root additional-property cases applicable to
  each Schema shape, enum wrong-type matrices, booleans as integers, empty and
  over-capacity collections, duplicate items/references, bad charset, secret
  assignment, start-position path, non-finite numbers, hostile mapping,
  unhashable nested values, and abnormal list subclasses were exercised.
- All 68 independent malformed-output Schema cases were rejected, covering
  every required field, extra fields, enums, booleans, list/dict/null/number
  types, bounds, duplicates, identifiers, advice-only actions, and the high/low
  approval/status coupling.
- `quick_validate.py` accepted the Skill frontmatter and name. The trigger and
  body accurately describe the real callable, advice-only boundary, no MCP
  execution, version `1.0.0`, Python/shared-Contract dependencies, test-only
  `jsonschema` dependency, release gate, rollback procedure, and revision-scoped
  OPT2-02 limitation.
- Static and diff review found no OPT2-04 state, new public Contract, new MCP
  tool, canonical-ledger/registry mutation, other-role change, runtime/live
  expansion, network/execution import, commit, or push.

## Commands and results

| Check | Result |
| --- | --- |
| `scripts/sectrace-preflight.ps1 -Mode code` | `READY_CODE` |
| `python -m pytest -q -p no:cacheprovider tests/response tests/skills/response` | `27 passed` |
| `quick_validate.py src/skills/response` | `Skill is valid!` |
| `python -m pytest -q -p no:cacheprovider tests/security/test_repository_hygiene.py` | `16 passed` |
| `python -m pytest -q -p no:cacheprovider` | `335 passed` |
| Legal risk-branch matrix and output conformance | PASS |
| S01–S24 synthetic traversal and no-oracle-selector audit | PASS |
| Output Schema negative matrix | 68/68 rejected |
| Pydantic bypass, cross-object identity, and embedded-path probes | FAIL: F1–F4 |
| `git diff --check` / `git diff --cached --check` | PASS |

## Repository-state and safety audit

Before this report, tracked changes were limited to
`src/agents/response/service.py` and `src/skills/response/plan.py`; the index was
empty. Untracked content was limited to the owner-03 Handoff, Response Skill
CHANGELOG/SKILL/Schemas/fixtures, and focused Response Skill tests. This QA adds
only the present verification record. No owner-03 artifact was modified.

No public Contract, six-tool allowlist, canonical ledger, registry, Intake,
Evidence, Audit, runtime/live resource, Matrix action, approval action,
credential, commit, or push was changed or invoked. Probe inputs remained local
and synthetic and are intentionally not reproduced in this report.

## Fixed completion report

```text
STATUS: QA_FAIL
PLAN_COMMIT: 5df7316f858adef0b6a6cb76c904cd61d7ade05e
BASE_COMMIT: 5df7316f858adef0b6a6cb76c904cd61d7ade05e
FINAL_COMMIT: NO_COMMIT
FILES_CHANGED: docs/verification/V-OPT2-03C-response-skill-independent-qa.md
HANDOFF: owner 03 minimal correction required for F1-F4, then owner 05 re-QA
TESTS_RUN: code preflight; focused Response+Skill; quick_validate; repository hygiene; full pytest; required/additionalProperties/type/enum/bounds/duplicate/charset/secret/path/non-finite/hostile-container matrices; Pydantic bypass and cross-object probes; all legal risk variants; deterministic golden/badcase/non-mutation; S01-S24 traversal; no-oracle-selector; output Schema negatives; diff/staged/untracked/static scope audits
TEST_RESULT: QA_FAIL — four substantive fail-closed/parity blockers
NEW_BEHAVIOR: none; independent QA record only
UNCHANGED_SAFETY_BOUNDARIES: synthetic/de-identified repository-only checks; advice only; runtime/live unknown; no execution, Contract, tool, ledger, registry, other-role, Matrix, approval, commit, or push activity
KNOWN_LIMITATIONS: no runtime/live/production evidence; Schema-alone relational parity is not established
NEXT_HANDOFF: owner 03 applies only the minimal F1-F4 correction and requests revision-scoped independent re-QA; owner 00 must not integrate this candidate yet
```
