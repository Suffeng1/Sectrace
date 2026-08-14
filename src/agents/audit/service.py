"""Independent, deterministic audit review for synthetic SecTrace traces."""

from __future__ import annotations

import re
from math import isfinite
from typing import Literal

from src.app.contracts import (
    ApprovalRecord,
    AuditBundle,
    EvidenceItem,
    IncidentCase,
    ResponsePlan,
)
from src.skills.audit.verify import LEDGER_FIELDS, redact_reference, verify_ledger


INVALID_AUDIT_INPUT_ERROR = "invalid audit input"
_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")
_TRACE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")
_MODEL_FIELDS = {
    IncidentCase: frozenset({"trace_id", "schema_version", "scenario_id", "severity_hint", "raw_event_refs", "tasks", "status"}),
    EvidenceItem: frozenset({"evidence_id", "trace_id", "source_ref", "statement", "classification", "confidence", "evidence_level", "related_event_refs"}),
    ResponsePlan: frozenset({"plan_id", "trace_id", "risk_level", "actions", "verification_steps", "rollback_steps", "requires_approval", "status"}),
    ApprovalRecord: frozenset({"trace_id", "approver_role", "status", "timestamp"}),
}


class AuditReview(AuditBundle):
    """AuditBundle projection with the review decision required by the Audit role."""

    audit_status: Literal["qualified", "qualified_with_gaps", "not_qualified"]
    integrity_check: Literal["passed", "failed"]


def _add_once(missing: list[str], requirement: str) -> None:
    if requirement not in missing:
        missing.append(requirement)


def _valid_model(value: object, model_type: type[object]) -> bool:
    """Accept only complete, unmodified shared-Contract model instances."""
    if type(value) is not model_type:
        return False
    try:
        fields = _MODEL_FIELDS[model_type]  # type: ignore[index]
        raw = object.__getattribute__(value, "__dict__")
        fields_set = object.__getattribute__(value, "__pydantic_fields_set__")
        private = object.__getattribute__(value, "__pydantic_private__")
        extra = object.__getattribute__(value, "__pydantic_extra__")
        dumped = value.model_dump(mode="python", warnings=False)  # type: ignore[union-attr]
        return (
            type(raw) is dict
            and set(raw) == fields
            and type(fields_set) is set
            and fields_set == fields
            and private is None
            and extra is None
            and type(dumped) is dict
            and set(dumped) == fields
            and _plain_values(raw)
            and model_type.model_validate(raw, strict=True).model_dump(mode="python") == dumped  # type: ignore[union-attr]
        )
    except Exception:
        return False


def _plain_values(value: object) -> bool:
    if type(value) in {str, bool, int} or value is None:
        return True
    if type(value) is float:
        return isfinite(value)
    if type(value) is list:
        return all(_plain_values(item) for item in value)
    if type(value) is dict:
        return all(type(key) is str and _plain_values(item) for key, item in value.items())
    return value.__class__.__name__ == "datetime"


def _valid_ledger_records(records: object) -> bool:
    return (
        type(records) is list
        and len(records) <= 5
        and all(
            type(record) is dict
            and set(record) == LEDGER_FIELDS
            and all(type(value) is str for value in record.values())
            for record in records
        )
    )


def _valid_evidence_bindings(items: list[EvidenceItem], raw_event_refs: list[str]) -> bool:
    evidence_ids: set[str] = set()
    source_refs: set[str] = set()
    for item in items:
        if (
            item.evidence_id in evidence_ids
            or item.source_ref in source_refs
            or item.evidence_id in source_refs
            or item.source_ref in evidence_ids
            or item.evidence_id == item.source_ref
            or len(item.related_event_refs) != len(set(item.related_event_refs))
        ):
            return False
        evidence_ids.add(item.evidence_id)
        source_refs.add(item.source_ref)
    all_evidence_ids = {item.evidence_id for item in items}
    all_references = set(raw_event_refs) | source_refs | {
        reference for item in items for reference in item.related_event_refs
    }
    return all_evidence_ids.isdisjoint(all_references)


def _valid_reference(value: object, pattern: re.Pattern[str] = _IDENTIFIER) -> bool:
    return type(value) is str and pattern.fullmatch(value) is not None


def _has_qualified_ledger_chain(
    records: list[dict[str, str]], trace_id: str, evidence_items: list[EvidenceItem], plan: ResponsePlan, approval: ApprovalRecord
) -> bool:
    expected = [
        ("incident.created", f"incident:{trace_id}"),
        ("evidence.completed", "evidence:" + ",".join(item.evidence_id for item in evidence_items)),
        ("response.pending_approval", f"response:{plan.plan_id}"),
        ("audit.projected", f"audit:{trace_id}"),
    ]
    if len(records) != 5 or any(
        records[index]["event_type"] != event_type
        or records[index]["payload_ref"] != payload_ref
        for index, (event_type, payload_ref) in enumerate(expected[:3])
    ):
        return False
    approval_ref = records[3]["payload_ref"]
    approval_ref_valid = approval_ref == "approval:approved" or re.fullmatch(
        rf"approval:{re.escape(plan.plan_id)}:(?:event_sha256:[0-9a-f]{{64}}:)?reason_sha256:[0-9a-f]{{64}}",
        approval_ref,
    ) is not None
    return (
        records[3]["event_type"] == "approval.approved"
        and approval_ref_valid
        and records[4]["event_type"] == expected[3][0]
        and records[4]["payload_ref"] == expected[3][1]
    )


def build_audit_review(
    incident: IncidentCase,
    evidence_items: list[EvidenceItem],
    response_plan: ResponsePlan | None,
    approval: ApprovalRecord | None,
    ledger_records: list[dict[str, str]],
) -> AuditReview:
    """Validate supplied outputs and project an audit result without filling gaps."""
    if not _valid_model(incident, IncidentCase):
        raise ValueError(INVALID_AUDIT_INPUT_ERROR)
    if type(evidence_items) is not list or len(evidence_items) > 16:
        raise ValueError(INVALID_AUDIT_INPUT_ERROR)
    if any(not _valid_model(item, EvidenceItem) for item in evidence_items):
        raise ValueError(INVALID_AUDIT_INPUT_ERROR)
    if not _valid_evidence_bindings(evidence_items, incident.raw_event_refs):
        raise ValueError(INVALID_AUDIT_INPUT_ERROR)
    if response_plan is not None and not _valid_model(response_plan, ResponsePlan):
        raise ValueError(INVALID_AUDIT_INPUT_ERROR)
    if approval is not None and not _valid_model(approval, ApprovalRecord):
        raise ValueError(INVALID_AUDIT_INPUT_ERROR)
    if not _valid_ledger_records(ledger_records):
        raise ValueError(INVALID_AUDIT_INPUT_ERROR)
    trace_id = incident.trace_id
    missing: list[str] = []

    if not evidence_items:
        _add_once(missing, "evidence.required")
    for item in evidence_items:
        if not _valid_reference(item.evidence_id) or not _valid_reference(item.source_ref):
            _add_once(missing, "evidence.references")
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
        if not _valid_reference(response_plan.plan_id):
            _add_once(missing, "response.reference")
        if response_plan.trace_id != trace_id:
            _add_once(missing, "trace_id.response")
        if not response_plan.rollback_steps:
            _add_once(missing, "response.rollback_steps")
        if response_plan.risk_level == "high":
            if not response_plan.requires_approval or response_plan.status != "pending_approval":
                _add_once(missing, "response.approval_gate")
            if approval is None or approval.status != "approved" or approval.timestamp is None:
                _add_once(missing, "approval.required")

    if approval is not None and approval.trace_id != trace_id:
        _add_once(missing, "trace_id.approval")

    ledger_ok, ledger_hash = verify_ledger(ledger_records)
    if not ledger_ok:
        _add_once(missing, "ledger.integrity")
    if any(record.get("trace_id") != trace_id for record in ledger_records):
        _add_once(missing, "trace_id.ledger")
    if (
        ledger_ok
        and response_plan is not None
        and approval is not None
        and response_plan.risk_level == "high"
        and not _has_qualified_ledger_chain(ledger_records, trace_id, evidence_items, response_plan, approval)
    ):
        _add_once(missing, "ledger.references")

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
