"""Deterministic correlation over supplied synthetic scenario events."""


RISK_SEQUENCE = ["anomalous_login", "privilege_elevation", "bulk_sensitive_data_access"]


def correlate_risk_path(events: list[dict]) -> list[str]:
    """Return the event references when the supplied events match the risk sequence."""
    if [event.get("event_type") for event in events] != RISK_SEQUENCE:
        return []
    return [event["event_ref"] for event in events]
