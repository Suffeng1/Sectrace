import pytest
from pydantic import ValidationError

from src.app.contracts import IncidentCase, ResponsePlan


def test_valid_incident_case_parses() -> None:
    incident = IncidentCase(
        trace_id="tr_s01_001",
        schema_version="1.0",
        scenario_id="S01",
        severity_hint="high",
        raw_event_refs=["evt_s01_001", "evt_s01_002", "evt_s01_003"],
        tasks=["collect_evidence", "plan_response", "audit"],
        status="open",
    )

    assert incident.trace_id == "tr_s01_001"


def test_high_risk_response_requires_approval() -> None:
    with pytest.raises(ValidationError):
        ResponsePlan(
            plan_id="plan_s01_001",
            trace_id="tr_s01_001",
            risk_level="high",
            actions=["Escalate the case to a human operator."],
            verification_steps=["Confirm the evidence references."],
            rollback_steps=["Withdraw the advisory recommendation."],
            requires_approval=False,
            status="draft",
        )

    with pytest.raises(ValidationError):
        ResponsePlan(
            plan_id="plan_s01_002",
            trace_id="tr_s01_001",
            risk_level="high",
            actions=["Escalate the case to a human operator."],
            verification_steps=["Confirm the evidence references."],
            rollback_steps=["Withdraw the advisory recommendation."],
            requires_approval=True,
            status="executed",
        )
