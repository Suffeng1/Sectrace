"""Commander intake service for synthetic SecTrace scenarios."""

from src.app.contracts import IncidentCase
from src.skills.intake.normalize import normalize_scenario


def build_incident(scenario: dict) -> IncidentCase:
    """Build an open incident from a synthetic scenario payload."""
    scenario = normalize_scenario(scenario)
    scenario_id = scenario["scenario_id"]
    return IncidentCase(
        trace_id=f"tr_{scenario_id.lower()}",
        schema_version="1.0",
        scenario_id=scenario_id,
        severity_hint=scenario["expected"]["severity_hint"],
        raw_event_refs=[event["event_ref"] for event in scenario["events"]],
        tasks=["collect_evidence", "plan_response", "audit"],
        status="open",
    )
