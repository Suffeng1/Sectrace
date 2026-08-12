import pytest

from src.skills.intake.normalize import normalize_scenario


def test_rejects_real_data_marker() -> None:
    scenario = {
        "scenario_id": "S-real",
        "real_data": True,
        "events": [],
        "expected": {"severity_hint": "high"},
    }

    with pytest.raises(ValueError, match="synthetic or de-identified"):
        normalize_scenario(scenario)


def test_defaults_missing_severity_hint_to_low() -> None:
    scenario = {
        "scenario_id": "S-incomplete",
        "real_data": False,
        "events": [],
        "expected": {},
    }

    assert normalize_scenario(scenario)["expected"]["severity_hint"] == "low"
