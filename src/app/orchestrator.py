"""Deterministic local orchestration for the fixed synthetic demonstration."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from src.agents.audit.service import build_audit_review
from src.agents.commander.service import build_incident
from src.agents.evidence.service import analyze_case
from src.agents.response.service import create_response_plan
from src.app.contracts import ApprovalRecord
from src.app.ledger import AuditLedger


ApprovalStatus = Literal["pending", "approved", "rejected"]


def _approval(scenario: dict, trace_id: str, status: ApprovalStatus) -> ApprovalRecord:
    timestamp = None
    if status in {"approved", "rejected"}:
        timestamp = datetime.fromisoformat(
            scenario["events"][-1]["at"].replace("Z", "+00:00")
        ).astimezone(timezone.utc)
    return ApprovalRecord(
        trace_id=trace_id,
        approver_role="human_operator",
        status=status,
        timestamp=timestamp,
    )


def run_demo(
    scenario_path: str | Path, *, approval_status: ApprovalStatus = "pending"
) -> dict:
    """Run Commander → Evidence → Response → Audit without real-world actions."""
    scenario = json.loads(Path(scenario_path).read_text(encoding="utf-8"))
    incident = build_incident(scenario)
    evidence_items, risk_path = analyze_case(incident, scenario)
    response_plan = create_response_plan(evidence_items)
    approval = _approval(scenario, incident.trace_id, approval_status)

    ledger = AuditLedger(incident.trace_id)
    at = scenario["events"][-1]["at"]
    ledger.append(
        at=at,
        actor="commander",
        event_type="incident.created",
        payload_ref=f"incident:{incident.trace_id}",
    )
    ledger.append(
        at=at,
        actor="evidence",
        event_type="evidence.completed",
        payload_ref="evidence:" + ",".join(item.evidence_id for item in evidence_items),
    )
    ledger.append(
        at=at,
        actor="response",
        event_type="response.pending_approval",
        payload_ref=f"response:{response_plan.plan_id}",
    )
    ledger.append(
        at=at,
        actor="human_operator",
        event_type=f"approval.{approval.status}",
        payload_ref=f"approval:{approval.status}",
    )
    ledger.append(
        at=at,
        actor="audit",
        event_type="audit.projected",
        payload_ref=f"audit:{incident.trace_id}",
    )
    audit = build_audit_review(
        incident, evidence_items, response_plan, approval, ledger.records
    )

    return {
        "trace_id": incident.trace_id,
        "stages": ["commander", "evidence", "response", "audit"],
        "incident": incident.model_dump(mode="json"),
        "evidence_items": [item.model_dump(mode="json") for item in evidence_items],
        "risk_path": risk_path,
        "response_plan": response_plan.model_dump(mode="json"),
        "approval": approval.model_dump(mode="json"),
        "audit": audit.model_dump(mode="json"),
        "ledger": list(ledger.records),
        "safety_notice": "Synthetic exercise only; no real action has been executed.",
    }
