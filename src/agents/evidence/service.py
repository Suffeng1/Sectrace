"""Evidence analysis for supplied synthetic SecTrace scenarios."""

from src.app.contracts import EvidenceItem, IncidentCase
from src.skills.evidence.correlate import correlate_risk_path


def analyze_case(
    incident: IncidentCase, scenario: dict
) -> tuple[list[EvidenceItem], list[str]]:
    """Build sourced evidence and a deterministic risk path from supplied events."""
    if scenario.get("real_data") is True:
        raise ValueError("evidence analysis accepts synthetic or de-identified data only")
    events = scenario["events"]
    risk_path = correlate_risk_path(events)
    if not risk_path:
        event = events[0]
        return [
            EvidenceItem(
                evidence_id=f"ev_{event['event_ref']}",
                trace_id=incident.trace_id,
                source_ref=event["event_ref"],
                statement="无法确认存在完整风险路径；当前证据不足。",
                classification="unknown",
                confidence="low",
                evidence_level="insufficient",
                related_event_refs=[event["event_ref"]],
            )
        ], []

    evidence_items = [
        EvidenceItem(
            evidence_id=f"ev_{event['event_ref']}",
            trace_id=incident.trace_id,
            source_ref=event["event_ref"],
            statement=f"Supplied synthetic event records {event['event_type']}.",
            classification="fact",
            confidence="high",
            evidence_level="strong",
            related_event_refs=[event["event_ref"]],
        )
        for event in events
    ]
    return evidence_items, risk_path
