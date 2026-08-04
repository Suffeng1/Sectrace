import json
from pathlib import Path

import pytest

from src.agents.commander.service import build_incident
from src.agents.evidence.service import analyze_case


def test_s01_has_sourced_fact_and_risk_path() -> None:
    scenario_path = Path(__file__).parents[2] / "data" / "scenarios" / "S01.json"
    scenario = json.loads(scenario_path.read_text(encoding="utf-8"))
    incident = build_incident(scenario)

    evidence_items, risk_path = analyze_case(incident, scenario)

    assert risk_path == ["evt_s01_001", "evt_s01_002", "evt_s01_003"]
    assert [item.classification for item in evidence_items] == ["fact", "fact", "fact"]
    assert [item.source_ref for item in evidence_items] == risk_path
    assert all(item.trace_id == incident.trace_id for item in evidence_items)
    assert all(item.statement for item in evidence_items)


def test_rejects_real_data_marker() -> None:
    scenario_path = Path(__file__).parents[2] / "data" / "scenarios" / "S01.json"
    scenario = json.loads(scenario_path.read_text(encoding="utf-8"))
    incident = build_incident(scenario)
    scenario["real_data"] = True

    with pytest.raises(
        ValueError,
        match="synthetic or de-identified",
    ):
        analyze_case(incident, scenario)
