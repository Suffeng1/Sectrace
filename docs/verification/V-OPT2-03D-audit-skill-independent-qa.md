# V-OPT2-03D Audit Skill Independent QA

- Owner: 05
- Task: `V-OPT2-03D`
- Scope: current uncommitted OPT2-03D Audit Skill candidate, repository-only
- Plan/Base/HEAD: `2992e75b64b37928d678b004605da4cb8d3a358b`
- Preflight: `READY_CODE`
- Runtime/live status: unknown; no runtime/live activity performed
- Verdict: **QA_FAIL**

## Verdict

**QA_FAIL**. The approved high-risk golden path and the declared pending,
rejected, missing, tampered, reference-mismatch and order-mismatch paths have
the correct deterministic terminal behavior, and the complete repository suite
passes. The candidate is nevertheless not ready for owner-00 registry
integration because its strict input/output boundary, untrusted Python-object
handling and packaged badcase do not satisfy the frozen OPT2-03D acceptance
matrix.

This is a bounded result. It does not request a new MCP tool, public Contract,
ledger algorithm, registry feature, other-role change, runtime or live
capability. The low-risk `not_requested` oracle remains outside the blockers
below and was not redefined.

## Blocking findings

### F1 — Callable does not consistently reject Pydantic/Mapping/hostile inputs

Independent in-memory probes against
`src.agents.audit.service.build_audit_review` reproduced four failures:

- `EvidenceItem.model_copy(update={"statement": float("inf")})` retained the
  exact Pydantic object shape and was accepted as `qualified/passed`. The shape
  check does not revalidate internal values.
- Five `collections.UserDict` ledger records were accepted as a complete
  `qualified/passed` chain although the Skill promises an ordinary built-in
  ledger and fail-closed Mapping handling.
- A built-in ledger list containing `object()` escaped as `TypeError: 'object'
  object is not iterable`, rather than the fixed non-leaking
  `ValueError("invalid audit input")`.
- Two identical `EvidenceItem` objects, with a canonically rehashed matching
  ledger reference, were accepted as `qualified/passed`; duplicate evidence
  identity is not rejected.

Minimal repair: before relational or hash work, validate exact built-in
containers and record dictionaries without invoking hostile overrides;
revalidate every shared-Contract field value/type after `model_copy` or
`model_construct` bypasses; reject duplicate evidence identities/references;
map every invalid-input path to the one fixed error. Add focused regression
tests for these four probes and ordinary valid controls. Do not change the
public Contract or callable signature.

### F2 — Schemas are not strict and no acceptance guard protects forged reviews

The input Schema produced zero errors for each of these independently mutated
documents: an empty Incident object, an unexpected Incident property, invalid
`severity_hint="critical"`, and a duplicated Evidence item. Its Incident,
Evidence, Response and Approval definitions are only `type: object`; they omit
the Contract field sets, nested `required`, nested `additionalProperties`,
types, enums, identifier/text bounds and duplicate constraints. Conversely,
`response_plan: null` is rejected even though the frozen callable signature
explicitly accepts `ResponsePlan | None`; the same mismatch applies to
Approval.

The output Schema also accepted a structurally valid forged `qualified` review
with a substituted 64-hex terminal hash. Independently substituting every one
of the nine declared `AuditReview` fields was accepted by
`AuditReview.model_validate`; all nine values differed from the deterministic
rebuild. The current package has no output-acceptance guard requiring exact
equality with a rebuild from Incident, Evidence, Response, Approval and ledger.

Minimal repair: define the frozen nested Contract structures in the input
Schema with exact required/additional-property, type, enum, length/capacity and
duplicate rules, while matching the callable's nullable arguments. Tighten
the output structural bounds. At any local AuditReview acceptance point,
rebuild from the five supplied inputs and require field-for-field equality;
add one mutation test per declared field and state explicitly that Schema or
Pydantic shape validation alone is not semantic acceptance. Keep canonical
hash recomputation and cross-object/order binding callable-side as already
disclosed; do not add a public tool or Contract field.

### F3 — The packaged Badcase is a valid copy of the golden ledger

`src/skills/audit/fixtures/badcase-ledger.json` is byte-for-value equal to the
`ledger_records` array in the golden approved-chain input. Direct use of the
advertised Badcase therefore supplies a valid qualified chain; the focused test
only becomes negative because it mutates the fixture after loading it.

Minimal repair: make the Badcase artifact independently invalid in one named,
stable way (for example one bad hash or one reference mismatch) and assert that
the fixture itself fails closed. Keep additional mutation tests separate.

## Passing independent checks

- The golden approved chain matched the expected serialized review,
  `qualified/passed`, with the canonical terminal hash.
- Pending and rejected Approval were `not_qualified`; missing Response and
  Approval were `not_qualified`.
- A reference mismatch and an order mismatch remained `not_qualified` after
  recomputing a valid hash chain, proving the relational checks are not merely
  hash-failure aliases.
- A hash mismatch was `not_qualified/failed` with an empty exported terminal
  hash.
- Repeated golden calls were deterministic and all five supplied input objects
  remained deeply equal after the calls.
- Static Audit/Skill review found no scenario-title, expected-field or
  scenario-ID oracle selection. The S01-S24 Evaluation tests passed.
- Static and diff review found no evidence creation, plan creation, approval,
  execution, input or ledger mutation, MCP/Contract/ledger-algorithm/registry/
  other-role/runtime/live expansion.
- `quick_validate.py` accepted the Skill metadata and layout. This does not
  validate the JSON Schema semantics or the callable boundary failures above.

## Commands and results

| Check | Result |
| --- | --- |
| `scripts/sectrace-preflight.ps1 -Mode code` | `READY_CODE` |
| `python -m pytest -q -p no:cacheprovider tests/audit tests/skills/audit` | `12 passed` |
| `quick_validate.py src/skills/audit` | `Skill is valid!` |
| `python -m pytest -q -p no:cacheprovider tests/security/test_repository_hygiene.py` | `16 passed` |
| `python -m pytest -q -p no:cacheprovider tests/evaluation` | `52 passed` |
| `python -m pytest -q -p no:cacheprovider` | `364 passed` |
| Golden, fail-closed relation/hash, determinism and deep non-mutation probes | PASS |
| Strict input/output Schema negative matrix | FAIL (F2) |
| Pydantic/Mapping/hostile-container/duplicate probes | FAIL (F1) |
| Packaged Badcase identity check | FAIL (F3) |

## Repository-state and safety audit

Before this report, tracked changes were limited to
`src/agents/audit/service.py` and `tests/audit/test_service.py`. Untracked
content was limited to the owner-04 Handoff, the Audit Skill package and the
focused Audit Skill tests; the index was empty. This QA adds only the present
verification record and modifies no owner-04 artifact.

All probes were local, synthetic and in-memory. No secret value, real-system
connection, Matrix action, approval action, runtime/live mutation, commit or
push occurred.

## Fixed completion report

```text
STATUS: QA_FAIL
PLAN_COMMIT: 2992e75b64b37928d678b004605da4cb8d3a358b
BASE_COMMIT: 2992e75b64b37928d678b004605da4cb8d3a358b
FINAL_COMMIT: NO_COMMIT
FILES_CHANGED: docs/verification/V-OPT2-03D-audit-skill-independent-qa.md
HANDOFF: V-OPT2-03D bounded repository-only independent QA
TESTS_RUN: code preflight; focused Audit+Skill; quick_validate; hygiene; S01-S24 Evaluation; full pytest; golden/fail-closed/determinism/deep-nonmutation; strict Schema; Pydantic/Mapping/hostile-container/non-finite/duplicates; forged-review field reconstruction; badcase identity; diff/cached/staged/untracked/static scope audits
TEST_RESULT: QA_FAIL — F1 callable untrusted-input bypasses, F2 non-strict/misaligned Schemas and missing forged-review acceptance guard, F3 valid packaged Badcase
NEW_BEHAVIOR: none; independent QA record only
UNCHANGED_SAFETY_BOUNDARIES: synthetic/de-identified repository-only checks; read-only Audit; advice only; runtime/live unknown; no execution, Contract, tool, ledger algorithm/history, registry, other-role, Matrix, approval, commit or push activity
KNOWN_LIMITATIONS: no runtime/live/production evidence; this verdict is revision-scoped to the current uncommitted candidate
NEXT_HANDOFF: owner 04 should apply only the minimal F1-F3 repairs and rerun the same gates before owner 05 corrected independent QA; owner 00 should not integrate this revision
CONTROLLER_NOTIFIED: true
```
