# Changelog

## 1.0.0 - 2026-08-14

- Packaged the existing deterministic `create_response_plan` boundary with
  executable input/output schemas, synthetic golden/badcase fixtures, and
  fail-closed boundary tests.
- Preserved advice-only high-risk pending approval and low-risk draft behavior;
  added no MCP tool, public Contract field, ledger action, runtime, or live capability.
- Documented dependencies, release gates, rollback, and revision-scoped
  full-pipeline evaluation limits.

### Corrected owner cycle after V-OPT2-03C QA_FAIL

- Treated Pydantic instances as untrusted by checking their exact serialized
  field set before use and normalizing every boundary failure to one fixed error.
- Enforced a callable-only evidence-ID/source-reference bijection and
  cross-namespace non-overlap invariant; JSON Schema remains structural.
- Extended portable Schema and runtime path checks to embedded Windows, Unix,
  and temporary-directory tokens in Response evidence statements.

### Second corrected owner cycle after corrected QA FAIL

- Required the normal Pydantic object-shape metadata and exact raw field shape
  before serializing any incoming EvidenceItem.
- Rejected same-item evidence-ID/source-reference overlap and non-builtin raw
  related-reference containers before normalization.
