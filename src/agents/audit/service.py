"""Independent, deterministic audit review for synthetic SecTrace traces."""

from __future__ import annotations

from typing import Literal

from src.app.contracts import (
    ApprovalRecord,
    AuditBundle,
    EvidenceItem,
    IncidentCase,
    ResponsePlan,
)
from src.skills.audit.verify import redact_reference, verify_ledger


class AuditReview(AuditBundle):
    """AuditBundle projection with the review decision required by the Audit role."""

    audit_status: Literal["qualified", "qualified_with_gaps", "not_qualified"]
    integrity_check: Literal["passed", "failed"]


def _add_once(missing: list[str], requirement: str) -> None:
    if requirement not in missing:
        missing.append(requirement)


def build_audit_review(
    incident: IncidentCase,
    evidence_items: list[EvidenceItem],
    response_plan: ResponsePlan | None,
    approval: ApprovalRecord | None,
    ledger_records: list[dict[str, str]],
) -> AuditReview:
    """Validate supplied outputs and project an audit result without filling gaps."""
    trace_id = incident.trace_id
    missing: list[str] = []

    if not evidence_items:
        _add_once(missing, "evidence.required")
    for item in evidence_items:
        if item.trace_id != trace_id:
            _add_once(missing, "trace_id.evidence")
        if (
            item.source_ref not in incident.raw_event_refs
            or item.source_ref not in item.related_event_refs
        ):
            _add_once(missing, f"evidence.source:{item.evidence_id}")
        if item.classification == "unknown":
            if item.evidence_level != "insufficient" or "无法确认" not in item.statement:
                _add_once(missing, f"evidence.classification:{item.evidence_id}")
        elif not item.source_ref:
            _add_once(missing, f"evidence.classification:{item.evidence_id}")

    if response_plan is None:
        _add_once(missing, "response.required")
    else:
        if response_plan.trace_id != trace_id:
            _add_once(missing, "trace_id.response")
        if not response_plan.rollback_steps:
            _add_once(missing, "response.rollback_steps")
        if response_plan.risk_level == "high":
            if not response_plan.requires_approval or response_plan.status != "pending_approval":
                _add_once(missing, "response.approval_gate")
            if approval is None or approval.status != "approved":
                _add_once(missing, "approval.required")

    if approval is not None and approval.trace_id != trace_id:
        _add_once(missing, "trace_id.approval")

    ledger_ok, ledger_hash = verify_ledger(ledger_records)
    if not ledger_ok:
        _add_once(missing, "ledger.integrity")
    if any(record.get("trace_id") != trace_id for record in ledger_records):
        _add_once(missing, "trace_id.ledger")

    integrity_check: Literal["passed", "failed"] = "passed" if ledger_ok else "failed"
    audit_status: Literal["qualified", "qualified_with_gaps", "not_qualified"]
    audit_status = "qualified" if not missing else "not_qualified"

    safe_refs = [
        redact_reference(str(record.get("payload_ref", "")))
        for record in ledger_records
    ]
    report_lines = [
        "# SecTrace Audit Review",
        f"- trace_id: {trace_id}",
        f"- audit_status: {audit_status}",
        f"- integrity_check: {integrity_check}",
        "- ledger_payload_refs: " + ", ".join(safe_refs),
        "- missing_requirements: " + (", ".join(missing) if missing else "none"),
    ]

    return AuditReview(
        trace_id=trace_id,
        evidence_refs=[item.evidence_id for item in evidence_items],
        response_plan_ref=response_plan.plan_id if response_plan else None,
        approval_ref=f"approval:{approval.status}" if approval else None,
        missing_requirements=missing,
        report_markdown="\n".join(report_lines),
        ledger_hash=ledger_hash if ledger_ok else "",
        audit_status=audit_status,
        integrity_check=integrity_check,
    )

