import json
from pathlib import Path

from src.agents.commander.service import build_incident
from src.agents.evidence.service import analyze_case
from src.agents.response.service import create_response_plan


def test_no_approval_can_never_be_executed() -> None:
    scenario_path = Path(__file__).parents[2] / "data" / "scenarios" / "S01.json"
    scenario = json.loads(scenario_path.read_text(encoding="utf-8"))
    incident = build_incident(scenario)
    evidence_items, _ = analyze_case(incident, scenario)

    plan = create_response_plan(evidence_items)

    assert plan.requires_approval is True
    assert plan.status == "pending_approval"
    assert plan.status != "executed"
