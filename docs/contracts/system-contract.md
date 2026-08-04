# SecTrace System Contract v1.0

## Contract boundary

`src/app/contracts.py` is the single source of truth for the five Pydantic v2 models. Producers validate synthetic external input at their boundary; consumers receive validated model instances. The contract version is fixed at `schema_version: "1.0"` for `IncidentCase`.

| Model | Producer | Consumer | Required purpose |
| --- | --- | --- | --- |
| `IncidentCase` | Commander | Evidence, Response, Audit | Case scope, task routing, and event references |
| `EvidenceItem` | Evidence | Response, Audit | Sourced fact, inference, or uncertainty |
| `ResponsePlan` | Response | Audit, human operator | Advice-only action proposal and approval gate |
| `ApprovalRecord` | Human interaction | Audit | Explicit human approval state |
| `AuditBundle` | Audit | UI/export | Deterministic audit projection |

## Models

```python
IncidentCase(trace_id, schema_version, scenario_id, severity_hint,
             raw_event_refs, tasks, status)
EvidenceItem(evidence_id, trace_id, source_ref, statement, classification,
             confidence, evidence_level, related_event_refs)
ResponsePlan(plan_id, trace_id, risk_level, actions, verification_steps,
             rollback_steps, requires_approval, status)
ApprovalRecord(trace_id, approver_role, status, timestamp)
AuditBundle(trace_id, evidence_refs, response_plan_ref, approval_ref,
            missing_requirements, report_markdown, ledger_hash)
```

Allowed enum values and field types are exactly those declared by the Pydantic models. Invalid types or enum members raise Pydantic `ValidationError` at the boundary.

## Safety invariants

- `ResponsePlan(risk_level="high", requires_approval=False)` is invalid.
- A high-risk `ResponsePlan` with `status="executed"` is invalid even when approval is requested.
- `ApprovalRecord.approver_role` is only `human_operator`; an Agent cannot approve a plan.
- Model fields do not carry credentials, live endpoint data, or execution instructions.

## Inter-Agent handoff contract

Every handoff has the common `trace_id`, Contract v1.0, and ledger references. The process order is `IncidentCase` → `list[EvidenceItem]` → `ResponsePlan` + `ApprovalRecord` → `AuditBundle`. A downstream Worker must reject a mismatched trace ID and record the mismatch as a missing requirement; it must not repair or guess one.

## Ledger contract

Each JSONL record has exactly this logical shape:

```json
{"event_id":"evt_001","trace_id":"tr_demo_001","at":"2026-08-04T09:00:00Z","actor":"commander","event_type":"incident.created","payload_ref":"incident:tr_demo_001","prev_hash":"","hash":"sha256..."}
```

Canonical JSON uses UTF-8, lexicographically sorted object keys, compact separators `,` and `:`, and no insignificant whitespace. `hash` is the SHA-256 hex digest of `prev_hash` concatenated with the canonical JSON bytes of the record excluding `hash`. The first record uses the empty string as `prev_hash`; each subsequent record must equal the previous record's `hash`. Replay validates this chain before projecting a report.
