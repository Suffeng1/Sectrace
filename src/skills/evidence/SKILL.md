---
name: sectrace-evidence
description: Analyze supplied synthetic SecTrace scenario events into sourced EvidenceItem values and a deterministic risk path without external access or actions.
---

# SecTrace Evidence Skill

Use `src.agents.evidence.service.analyze_case(incident: IncidentCase, scenario: dict) -> tuple[list[EvidenceItem], list[str]]` only after Commander has produced the matching Contract v1.0 `IncidentCase`.

- Validate input with [`schema/input.schema.json`](schema/input.schema.json). Pass an ordinary JSON `dict` scenario and the model instance to the callable; it enforces the same scenario boundary before direct field access.
- Require a Skill-local `trace_id` matching `^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$`. This is an Evidence Skill input/output bound, not a public Contract change.
- Accept only a matching synthetic/de-identified scenario with JSON `real_data: false`, unique event references, and safe bounded free text. Reject every malformed, missing, unknown, duplicate, path-like, local/temp-path, or secret-assignment value with `ValueError("invalid evidence payload")`. Reject any non-false `real_data` value with `ValueError("evidence analysis accepts synthetic or de-identified data only")`.
- Preserve the caller input. Return deterministic `EvidenceItem` values and a risk path; validate their serialized wrapper with [`schema/output.schema.json`](schema/output.schema.json).
- Emit sourced `fact` items only for the supplied ordered login → privilege elevation → bulk-access sequence. Keep every emitted path and related reference unique. Schema `uniqueItems` rejects identical event objects; the runtime additionally rejects duplicate `event_ref` values across otherwise different event objects. Otherwise emit one supplied-source `unknown`, `insufficient`, low-confidence item containing `无法确认` and an empty risk path.
- Do not create MCP tools, connect to logs or networks, scan, fabricate evidence/IOC, expose sensitive data, generate remediation, modify the ledger, or approve actions. Do not implement sufficient/insufficient/conflicting branching here; OPT2-04 owns that future work.

Fixtures: [`fixtures/golden-s01.json`](fixtures/golden-s01.json), its deterministic output, [`fixtures/golden-s05.json`](fixtures/golden-s05.json), and [`fixtures/badcase-real-data.json`](fixtures/badcase-real-data.json).

Version: `1.0.0`. Dependencies: Python 3.11+, Pydantic v2 (shared Contract); `jsonschema>=4,<5` is test-only and declared by owner 00. Before release, run focused Evidence/Skill tests, hygiene, full pytest, diff and staged-diff checks, and an untracked audit. Release also requires owner 00 registry integration and owner 05 independent QA. Roll back by restoring this directory and the matching owner-00 registry entry, then rerun the same gates; never rewrite Contract, trace, or ledger history.

Evaluation may cite only the revision-scoped local OPT2-02 QA record at [`docs/verification/V-OPT2-02-fourth-corrected-independent-qa.md`](../../../docs/verification/V-OPT2-02-fourth-corrected-independent-qa.md). It evaluates the full local pipeline, not this Skill in isolation, and establishes neither live/runtime state nor an official Alibaba Cloud Skill.
