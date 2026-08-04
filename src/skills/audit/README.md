# Audit verification skill

The Audit role validates only supplied, already-modelled SecTrace outputs. It
checks trace continuity, evidence provenance and uncertainty labels, the
high-risk human-approval gate, rollback coverage, and the canonical JSONL hash
chain before projecting an `AuditReview` compatible with `AuditBundle` v1.0.

Missing inputs are listed in `missing_requirements`; they are never inferred or
reconstructed. A broken ledger chain always yields `integrity_check=failed`,
`audit_status=not_qualified`, and an empty terminal ledger hash. Credential-like
reference values are replaced with `[REDACTED]` in the report.
