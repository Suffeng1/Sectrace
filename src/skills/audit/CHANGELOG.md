# Changelog

## 1.0.0 - 2026-08-14

- Packaged the existing read-only Audit callable with structural schemas, deterministic synthetic golden/badcase fixtures, and focused fail-closed tests.
- Required an approved, reference-bound canonical ledger chain before `qualified`; pending, missing, tampered, and out-of-order chains remain `not_qualified`.
- Added fixed-error validation for altered shared-Contract models and invalid outer containers. No public Contract, MCP tool, ledger hash algorithm, registry, runtime, or live behavior changed.

### Corrected owner cycle after V-OPT2-03D QA_FAIL

- Revalidated model-copy/construct values, rejected non-finite values and exact unsupported ledger container shapes, and rejected duplicate or ambiguous Evidence references before qualification.
- Replaced placeholder input/output Schema objects with bounded Contract-shaped Draft 2020-12 definitions, including nullable Response/Approval inputs.
- Replaced the copied ledger badcase with a standalone malformed synthetic record and covered it directly.
