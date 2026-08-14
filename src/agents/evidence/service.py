"""Evidence analysis for supplied synthetic SecTrace scenarios."""

from __future__ import annotations

from datetime import datetime
import re

from src.app.contracts import EvidenceItem, IncidentCase
from src.skills.evidence.correlate import correlate_risk_path


_ERROR = "invalid evidence payload"
_REAL_DATA_ERROR = "evidence analysis accepts synthetic or de-identified data only"
_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")
_EVENT_REF = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")
_TRACE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")
_RFC3339_UTC = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
_SECRET_ASSIGNMENT = re.compile(
    r"\b(?:api[_-]?key|secret|token|password|passwd|authorization|credential)\b\s*[:=]",
    re.IGNORECASE,
)
_LOCAL_PATH = re.compile(
    r"^(?:[A-Za-z]:[\\/]|/|\\\\|\.{1,2}[\\/]|(?:tmp|temp)[\\/])",
    re.IGNORECASE,
)
_EVENT_TYPES = {"anomalous_login", "privilege_elevation", "bulk_sensitive_data_access"}
_ROOT_FIELDS = {"scenario_id", "title", "real_data", "events", "expected"}
_EVENT_FIELDS = {"event_ref", "event_type", "at", "region_label", "subject", "record_count", "note"}
_EXPECTED_FIELDS = {
    "intake", "severity_hint", "risk_path", "response_status", "requires_approval",
    "classification", "evidence_level", "conclusion", "reason", "risk_level",
    "contract", "approval_status", "audit", "missing_requirement", "report_contains",
    "report_excludes", "tampered_hash", "valid_replay",
}
_REQUIRED_ROOT_FIELDS = {"scenario_id", "real_data", "events", "expected"}
_REQUIRED_EVENT_FIELDS = {"event_ref", "event_type", "at", "subject"}
_EXPECTED_ENUMS = {
    "intake": {"accept", "reject"},
    "severity_hint": {"low", "medium", "high"},
    "response_status": {"draft", "pending_approval", "executed"},
    "classification": {"inference", "unknown"},
    "evidence_level": {"insufficient"},
    "reason": {"invalid_timestamp", "missing_required_event_type", "real_data_marker", "unsupported_event_type"},
    "risk_level": {"low", "medium", "high"},
    "contract": {"reject"},
    "approval_status": {"rejected"},
    "audit": {"integrity_check", "missing_requirements", "redact"},
    "missing_requirement": {"approval", "evidence"},
    "tampered_hash": {"reject"},
    "valid_replay": {"stable"},
}


def _is_string(value: object, maximum: int) -> bool:
    return isinstance(value, str) and 1 <= len(value) <= maximum


def _is_safe_text(value: object, maximum: int) -> bool:
    return (
        _is_string(value, maximum)
        and _SECRET_ASSIGNMENT.search(value) is None
        and _LOCAL_PATH.search(value) is None
    )


def _is_rfc3339_utc(value: object) -> bool:
    if not isinstance(value, str) or not _RFC3339_UTC.fullmatch(value):
        return False
    try:
        datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return False
    return True


def _valid_expected(expected: object) -> bool:
    if type(expected) is not dict or set(expected) - _EXPECTED_FIELDS:
        return False
    for key, value in expected.items():
        if key in _EXPECTED_ENUMS and (not isinstance(value, str) or value not in _EXPECTED_ENUMS[key]):
            return False
        if key == "requires_approval" and type(value) is not bool:
            return False
        if key == "risk_path" and (
            not isinstance(value, list)
            or len(value) > 16
            or any(not isinstance(item, str) or not _EVENT_REF.fullmatch(item) for item in value)
        ):
            return False
        if key in {"conclusion", "report_contains", "report_excludes"} and not _is_safe_text(value, 512):
            return False
    return True


def _valid_event(event: object) -> bool:
    if type(event) is not dict or set(event) - _EVENT_FIELDS or not _REQUIRED_EVENT_FIELDS.issubset(event):
        return False
    if not isinstance(event["event_ref"], str) or not _EVENT_REF.fullmatch(event["event_ref"]):
        return False
    if not isinstance(event["event_type"], str) or event["event_type"] not in _EVENT_TYPES:
        return False
    if not _is_rfc3339_utc(event["at"]) or not _is_safe_text(event["subject"], 256):
        return False
    for key, maximum in {"region_label": 128, "note": 512}.items():
        if key in event and not _is_safe_text(event[key], maximum):
            return False
    return "record_count" not in event or (type(event["record_count"]) is int and 0 <= event["record_count"] <= 1_000_000)


def _valid_payload(incident: object, scenario: object) -> bool:
    if not isinstance(incident, IncidentCase) or type(scenario) is not dict:
        return False
    if not isinstance(incident.trace_id, str) or not _TRACE_ID.fullmatch(incident.trace_id):
        return False
    if set(scenario) - _ROOT_FIELDS or not _REQUIRED_ROOT_FIELDS.issubset(scenario):
        return False
    if not isinstance(scenario["scenario_id"], str) or not _IDENTIFIER.fullmatch(scenario["scenario_id"]):
        return False
    if "title" in scenario and not _is_safe_text(scenario["title"], 256):
        return False
    if not isinstance(scenario["events"], list) or not 1 <= len(scenario["events"]) <= 16:
        return False
    if not _valid_expected(scenario["expected"]) or not all(_valid_event(event) for event in scenario["events"]):
        return False
    refs = [event["event_ref"] for event in scenario["events"]]
    return (
        len(refs) == len(set(refs))
        and incident.scenario_id == scenario["scenario_id"]
        and incident.raw_event_refs == refs
    )


def analyze_case(
    incident: IncidentCase, scenario: dict
) -> tuple[list[EvidenceItem], list[str]]:
    """Build sourced evidence and a deterministic risk path from supplied events."""
    if type(scenario) is not dict or "real_data" not in scenario:
        raise ValueError(_ERROR)
    if type(scenario["real_data"]) is not bool or scenario["real_data"] is not False:
        raise ValueError(_REAL_DATA_ERROR)
    if not _valid_payload(incident, scenario):
        raise ValueError(_ERROR)

    events = scenario["events"]
    risk_path = correlate_risk_path(events)
    if not risk_path:
        event = events[0]
        return [
            EvidenceItem(
                evidence_id=f"ev_{event['event_ref']}", trace_id=incident.trace_id,
                source_ref=event["event_ref"], statement="无法确认存在完整风险路径；当前证据不足。",
                classification="unknown", confidence="low", evidence_level="insufficient",
                related_event_refs=[event["event_ref"]],
            )
        ], []

    evidence_items = [
        EvidenceItem(
            evidence_id=f"ev_{event['event_ref']}", trace_id=incident.trace_id,
            source_ref=event["event_ref"], statement=f"Supplied synthetic event records {event['event_type']}.",
            classification="fact", confidence="high", evidence_level="strong",
            related_event_refs=[event["event_ref"]],
        )
        for event in events
    ]
    return evidence_items, risk_path
