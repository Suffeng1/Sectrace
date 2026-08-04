import json
from pathlib import Path

from src.agents.commander.service import build_incident


def test_build_incident_from_s01() -> None:
    scenario_path = Path(__file__).parents[2] / "data" / "scenarios" / "S01.json"
    scenario = json.loads(scenario_path.read_text(encoding="utf-8"))

    incident = build_incident(scenario)

    assert incident.schema_version == "1.0"
    assert incident.scenario_id == "S01"
    assert incident.severity_hint == "high"
    assert incident.raw_event_refs == ["evt_s01_001", "evt_s01_002", "evt_s01_003"]
    assert incident.tasks == ["collect_evidence", "plan_response", "audit"]
    assert incident.status == "open"
    assert incident.trace_id
