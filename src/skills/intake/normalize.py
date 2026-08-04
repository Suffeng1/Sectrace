"""Safety normalization for Commander intake payloads."""


def normalize_scenario(scenario: dict) -> dict:
    """Reject real data and return an accepted synthetic scenario."""
    if scenario.get("real_data") is True:
        raise ValueError("intake accepts synthetic or de-identified data only")
    return scenario
