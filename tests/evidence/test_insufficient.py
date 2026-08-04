import json
from pathlib import Path

from src.agents.evidence.service import analyze_case
from src.app.contracts import IncidentCase


def test_incomplete_case_returns_unknown() -> None:
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

    evidence_items, risk_path = analyze_case(incident, scenario)

    assert risk_path == []
    assert len(evidence_items) == 1
    item = evidence_items[0]
    assert item.trace_id == incident.trace_id
    assert item.classification == "unknown"
    assert item.evidence_level == "insufficient"
    assert "无法确认" in item.statement
    assert item.source_ref == "evt_s05_001"
