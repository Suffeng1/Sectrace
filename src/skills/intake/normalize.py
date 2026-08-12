"""Safety normalization for Commander intake payloads."""


def normalize_scenario(scenario: dict) -> dict:
    """Reject real data and return an accepted synthetic scenario."""
    if scenario.get("real_data") is True:
        raise ValueError("intake accepts synthetic or de-identified data only")

    expected = scenario["expected"]
    if "severity_hint" not in expected:
        scenario = {**scenario, "expected": {**expected, "severity_hint": "low"}}
    return scenario
