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
