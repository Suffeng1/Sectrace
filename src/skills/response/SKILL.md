---
name: response
description: Create deterministic, advice-only SecTrace ResponsePlan objects from validated synthetic EvidenceItem lists. Use when turning existing Response-stage evidence into a bounded high-risk pending-approval plan or low-risk draft without executing actions, altering approvals, or calling MCP tools.
---

# SecTrace Response Skill

Use `src.agents.response.service.create_response_plan(evidence_items: list[EvidenceItem]) -> ResponsePlan`.

- Supply only a non-empty, ordinary Python `list` of 1–16 shared-Contract `EvidenceItem` instances. Treat incoming model instances as untrusted: the callable performs pre-serialization object-shape checks before validating a normalized plain object. Do not supply scenarios, dictionaries, mappings, live data, MCP payloads, or real-system references.
- Preserve a single bounded `trace_id`; use a one-to-one, non-overlapping evidence-ID/source-reference binding; include each source reference exactly once in its related references. Keep statements bounded, synthetic, and free of secret assignments or embedded Windows, Unix, or temporary-directory path tokens.
- Fail closed with `ValueError("invalid response evidence")`. Do not expose validation internals or echo rejected input.
- Return a deterministic plan only. Corroborated/strong high-confidence facts produce `risk_level="high"`, `requires_approval=true`, and `status="pending_approval"`. Other valid evidence produces `risk_level="low"`, `requires_approval=false`, and `status="draft"`.
- Keep every action advice-only (`建议：`). Include verification and rollback guidance. Never generate `executed`, perform remediation, write the ledger, approve, connect to a network, or add an MCP tool.

Validate serialized inputs and outputs with [`schema/input.schema.json`](schema/input.schema.json) and [`schema/output.schema.json`](schema/output.schema.json). The input Schema is structural: it cannot express Python object internals or portable cross-object bijection/non-overlap relations. `create_response_plan` adds those stronger fail-closed callable invariants. Use [`fixtures/golden-s01.evidence.json`](fixtures/golden-s01.evidence.json) and its expected plan as the deterministic golden pair; use [`fixtures/badcase-raw-mapping.json`](fixtures/badcase-raw-mapping.json) to confirm direct raw input fails closed.

Version: `1.0.0`. Runtime dependencies are Python 3.11+ and the shared Pydantic v2 Contract; `jsonschema>=4,<5` is test-only and declared in the root development dependency set. Before release, run:

```powershell
python -m pytest -q -p no:cacheprovider tests/response tests/skills/response
python -m pytest -q -p no:cacheprovider tests/security/test_repository_hygiene.py
python -m pytest -q -p no:cacheprovider
git diff --check
git diff --cached --check
git status --porcelain=v1 --untracked-files=all
```

Require owner 00 registry integration and owner 05 independent QA before release. Roll back by restoring the last released `src/skills/response/` directory and matching owner-00 registry entry, then rerun these gates. Do not alter public Contracts, traces, ledger history, or runtime state.

OPT2-02 is revision-scoped, full-local-pipeline evidence only: [`V-OPT2-02-fourth-corrected-independent-qa.md`](../../../docs/verification/V-OPT2-02-fourth-corrected-independent-qa.md). Do not claim a per-Skill score, current runtime/live status, production outcome, or Alibaba Cloud official Skill.
