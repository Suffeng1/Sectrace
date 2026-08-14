import hashlib
import json
from datetime import datetime, timezone

from src.agents.audit.service import build_audit_review
from src.app.contracts import (
    ApprovalRecord,
    EvidenceItem,
    IncidentCase,
    ResponsePlan,
)


def ledger_record(
    event_id: str,
    trace_id: str,
    event_type: str,
    payload_ref: str,
    prev_hash: str = "",
    actor: str = "test",
) -> dict[str, str]:
    record = {
        "event_id": event_id,
        "trace_id": trace_id,
        "at": "2026-08-04T09:00:00Z",
        "actor": actor,
        "event_type": event_type,
        "payload_ref": payload_ref,
        "prev_hash": prev_hash,
    }
    canonical = json.dumps(record, sort_keys=True, separators=(",", ":")).encode()
    record["hash"] = hashlib.sha256(prev_hash.encode() + canonical).hexdigest()
    return record


def incident(trace_id: str = "tr_audit_001") -> IncidentCase:
    return IncidentCase(
        trace_id=trace_id,
        schema_version="1.0",
        scenario_id="S01",
        severity_hint="high",
        raw_event_refs=["evt_s01_001"],
        tasks=["collect_evidence", "plan_response", "audit"],
        status="awaiting_approval",
    )


def evidence(trace_id: str = "tr_audit_001") -> EvidenceItem:
    return EvidenceItem(
        evidence_id="ev_evt_s01_001",
        trace_id=trace_id,
        source_ref="evt_s01_001",
        statement="Supplied synthetic event records an anomalous login.",
        classification="fact",
        confidence="high",
        evidence_level="strong",
        related_event_refs=["evt_s01_001"],
    )


def high_risk_plan(trace_id: str = "tr_audit_001") -> ResponsePlan:
    return ResponsePlan(
        plan_id="rp_tr_audit_001",
        trace_id=trace_id,
        risk_level="high",
        actions=["建议：等待人工审批后限制高风险会话。"],
        verification_steps=["核对证据引用。"],
        rollback_steps=["建议恢复审批前状态。"],
        requires_approval=True,
        status="pending_approval",
    )


def approved(trace_id: str = "tr_audit_001") -> ApprovalRecord:
    return ApprovalRecord(
        trace_id=trace_id,
        approver_role="human_operator",
        status="approved",
        timestamp=datetime(2026, 8, 4, tzinfo=timezone.utc),
    )


def valid_ledger(trace_id: str = "tr_audit_001") -> list[dict[str, str]]:
    first = ledger_record(
        "led_001", trace_id, "incident.created", f"incident:{trace_id}", actor="commander"
    )
    second = ledger_record(
        "led_002", trace_id, "evidence.completed", "evidence:ev_evt_s01_001", first["hash"], actor="evidence"
    )
    third = ledger_record(
        "led_003", trace_id, "response.pending_approval", f"response:rp_{trace_id}", second["hash"], actor="response"
    )
    fourth = ledger_record(
        "led_004", trace_id, "approval.approved", "approval:approved", third["hash"], actor="human_operator"
    )
    fifth = ledger_record(
        "led_005", trace_id, "audit.projected", f"audit:{trace_id}", fourth["hash"], actor="audit"
    )
    return [first, second, third, fourth, fifth]


def test_high_risk_without_evidence_or_approval_is_not_qualified() -> None:
    review = build_audit_review(
        incident(), [], high_risk_plan(), None, valid_ledger()
    )

    assert review.audit_status == "not_qualified"
    assert review.integrity_check == "passed"
    assert "evidence.required" in review.missing_requirements
    assert "approval.required" in review.missing_requirements
    assert review.trace_id == "tr_audit_001"


def test_complete_high_risk_trace_is_qualified() -> None:
    review = build_audit_review(
        incident(), [evidence()], high_risk_plan(), approved(), valid_ledger()
    )

    assert review.audit_status == "qualified"
    assert review.integrity_check == "passed"
    assert review.missing_requirements == []
    assert review.evidence_refs == ["ev_evt_s01_001"]
    assert review.response_plan_ref == "rp_tr_audit_001"
    assert review.approval_ref == "approval:approved"
    assert review.ledger_hash == valid_ledger()[-1]["hash"]


def test_trace_source_classification_and_rollback_gaps_are_reported() -> None:
    item = evidence("tr_other")
    item.source_ref = "evt_unprovided"
    item.classification = "unknown"
    item.evidence_level = "strong"
    item.statement = "无法确认"
    plan = high_risk_plan()
    plan.rollback_steps = []

    review = build_audit_review(
        incident(), [item], plan, approved(), valid_ledger()
    )

    assert review.audit_status == "not_qualified"
    assert set(review.missing_requirements) >= {
        "trace_id.evidence",
        "evidence.source:ev_evt_s01_001",
        "evidence.classification:ev_evt_s01_001",
        "response.rollback_steps",
    }
