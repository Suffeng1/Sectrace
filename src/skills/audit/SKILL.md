---
name: audit
description: Independently validate supplied synthetic SecTrace Incident, Evidence, Response, Approval, and canonical ledger outputs into a deterministic AuditReview. Use when checking a complete approved chain for trace continuity, reference binding, and ledger integrity without creating, approving, executing, or modifying anything.
---

# SecTrace Audit Skill

Use `src.agents.audit.service.build_audit_review(incident: IncidentCase, evidence_items: list[EvidenceItem], response_plan: ResponsePlan | None, approval: ApprovalRecord | None, ledger_records: list[dict[str, str]]) -> AuditReview`.

- Supply only complete shared-Contract Pydantic v2 instances and an ordinary built-in ledger `list` containing ordinary `dict` records. Treat every object as untrusted: the callable revalidates fields after `model_copy`/`model_construct`, rejects non-finite values, duplicate or ambiguous evidence bindings, raw mappings, list/dict subclasses, hostile records, malformed ledger records, and capacity violations with `ValueError("invalid audit input")`.
- Audit is read-only and independent. It never creates Evidence or Response, changes approvals, appends a ledger event, executes advice, calls MCP, accesses a network, or contacts a real system.
- A high-risk review is `qualified` only for the exact approved chain: incident → evidence → pending-approval Response → approved human Approval → Audit projection. Each object and ledger reference must bind to one trace and the canonical hash chain must validate. Pending, rejected, missing, tampered, mismatched, or out-of-order high-risk inputs are always `not_qualified`.
- Preserve supplied values. Reports redact credential-like ledger references. Do not infer missing evidence or disclose rejected input.

Validate structural JSON wrappers with [`schema/input.schema.json`](schema/input.schema.json) and serialized reviews with [`schema/output.schema.json`](schema/output.schema.json). The schemas precisely bound supported JSON structure, including nullable Response/Approval inputs; they do not accept a review as an authoritative input. Python model internals, canonical hash recomputation, cross-object/ordered reference binding, and equality to the deterministically rebuilt review are callable-only fail-closed invariants. Use [`fixtures/golden-approved-chain.json`](fixtures/golden-approved-chain.json) and its expected review for the deterministic golden pair; [`fixtures/badcase-ledger.json`](fixtures/badcase-ledger.json) is independently malformed and must fail closed.

Version: `1.0.0`. Dependencies are Python 3.11+ and the shared Pydantic v2 Contract; `jsonschema>=4,<5` is test-only. Before release, run focused Audit tests, `quick_validate.py`, hygiene, full pytest, both diff checks, and an untracked audit. Release requires owner 00 registry integration and owner 05 independent QA. Roll back by restoring the released `src/skills/audit/` directory and matching owner-00 registry entry, then rerun the same gates. Never alter Contracts, ledger history, registry, runtime, or live state.

OPT2-02 evidence is revision-scoped and local only: [`V-OPT2-02-fourth-corrected-independent-qa.md`](../../../docs/verification/V-OPT2-02-fourth-corrected-independent-qa.md). It is not a per-Skill score, current runtime/live state, production result, or official Skill claim.
