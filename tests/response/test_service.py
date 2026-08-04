import json
from pathlib import Path

from src.agents.commander.service import build_incident
from src.agents.evidence.service import analyze_case
from src.agents.response.service import create_response_plan
from src.app.contracts import IncidentCase


def test_high_risk_plan_requires_human_approval() -> None:
    scenario_path = Path(__file__).parents[2] / "data" / "scenarios" / "S01.json"
    scenario = json.loads(scenario_path.read_text(encoding="utf-8"))
    incident = build_incident(scenario)
    evidence_items, _ = analyze_case(incident, scenario)

    plan = create_response_plan(evidence_items)

    assert plan.trace_id == incident.trace_id
    assert plan.risk_level == "high"
    assert plan.requires_approval is True
    assert plan.status == "pending_approval"
    assert plan.rollback_steps
    assert all(action.startswith("建议：") for action in plan.actions)
    assert plan.verification_steps


def test_unknown_evidence_does_not_create_high_confidence_response() -> None:
    scenario_path = Path(__file__).parents[2] / "data" / "scenarios" / "S05.json"
    scenario = json.loads(scenario_path.read_text(encoding="utf-8"))
    incident = IncidentCase(
        trace_id="tr_s05",
        schema_version="1.0",
        scenario_id="S05",
        severity_hint="medium",
        raw_event_refs=["evt_s05_001"],
        tasks=["collect_evidence", "plan_response", "audit"],
        status="open",
    )
    evidence_items, _ = analyze_case(incident, scenario)

    plan = create_response_plan(evidence_items)

    assert plan.risk_level == "low"
    assert plan.requires_approval is False
    assert plan.status == "draft"
    assert all(action.startswith("建议：") for action in plan.actions)
    assert any("无法确认" in action for action in plan.actions)

