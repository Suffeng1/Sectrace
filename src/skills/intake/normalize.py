"""Fail-closed safety normalization for Commander intake payloads."""

from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from datetime import datetime
import re
from typing import Any


_ERROR = "invalid intake payload"
_REAL_DATA_ERROR = "intake accepts synthetic or de-identified data only"
_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")
_EVENT_REF = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")
_RFC3339_UTC = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
_EVENT_TYPES = {"anomalous_login", "privilege_elevation", "bulk_sensitive_data_access"}
_ROOT_FIELDS = {"scenario_id", "title", "real_data", "events", "expected"}
_EVENT_FIELDS = {"event_ref", "event_type", "at", "region_label", "subject", "record_count", "note"}
_REQUIRED_ROOT_FIELDS = {"scenario_id", "real_data", "events", "expected"}
_REQUIRED_EVENT_FIELDS = {"event_ref", "event_type", "at", "subject"}
_EXPECTED_FIELDS = {
    "intake", "severity_hint", "risk_path", "response_status", "requires_approval",
    "classification", "evidence_level", "conclusion", "reason", "risk_level",
    "contract", "approval_status", "audit", "missing_requirement", "report_contains",
    "report_excludes", "tampered_hash", "valid_replay",
}
_STRING_LIMITS = {"title": 256, "region_label": 128, "subject": 256, "note": 512}
_EXPECTED_ENUMS = {
    "intake": {"accept", "reject"},
    "severity_hint": {"low", "medium", "high"},
    "response_status": {"draft", "pending_approval", "executed"},
    "classification": {"inference", "unknown"},
    "evidence_level": {"insufficient"},
    "contract": {"reject"},
    "approval_status": {"rejected"},
    "audit": {"integrity_check", "missing_requirements", "redact"},
    "missing_requirement": {"approval", "evidence"},
    "reason": {"invalid_timestamp", "missing_required_event_type", "real_data_marker", "unsupported_event_type"},
    "risk_level": {"low", "medium", "high"},
    "tampered_hash": {"reject"},
    "valid_replay": {"stable"},
}
_FREE_EXPECTED_STRINGS = {"conclusion", "report_contains", "report_excludes"}


def _is_string(value: object, maximum: int) -> bool:
    return isinstance(value, str) and 1 <= len(value) <= maximum


def _is_rfc3339_utc(value: object) -> bool:
    if not isinstance(value, str) or not _RFC3339_UTC.fullmatch(value):
        return False
    try:
        datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return False
    return True


def _valid_expected(expected: Mapping[str, Any]) -> bool:
    if set(expected) - _EXPECTED_FIELDS:
        return False
    for key, value in expected.items():
        if key in _EXPECTED_ENUMS and (not isinstance(value, str) or value not in _EXPECTED_ENUMS[key]):
            return False
        if key == "requires_approval" and type(value) is not bool:
            return False
        if key == "risk_path" and (
            not isinstance(value, list)
            or len(value) > 16
            or any(not _EVENT_REF.fullmatch(item) for item in value if isinstance(item, str))
            or any(not isinstance(item, str) for item in value)
        ):
            return False
        if key in _FREE_EXPECTED_STRINGS and not _is_string(value, 512):
            return False
    return True


def _valid_event(event: object) -> bool:
    if not isinstance(event, Mapping) or set(event) - _EVENT_FIELDS:
        return False
    if not _REQUIRED_EVENT_FIELDS.issubset(event):
        return False
    if not isinstance(event["event_ref"], str) or not _EVENT_REF.fullmatch(event["event_ref"]):
        return False
    if not isinstance(event["event_type"], str) or event["event_type"] not in _EVENT_TYPES or not _is_rfc3339_utc(event["at"]):
        return False
    if not _is_string(event["subject"], _STRING_LIMITS["subject"]):
        return False
    for key in {"region_label", "note"} & set(event):
        if not _is_string(event[key], _STRING_LIMITS[key]):
            return False
    return "record_count" not in event or (type(event["record_count"]) is int and 0 <= event["record_count"] <= 1_000_000)


def _valid_payload(scenario: object) -> bool:
    if not isinstance(scenario, Mapping) or set(scenario) - _ROOT_FIELDS:
        return False
    if not _REQUIRED_ROOT_FIELDS.issubset(scenario):
        return False
    if not isinstance(scenario["scenario_id"], str) or not _IDENTIFIER.fullmatch(scenario["scenario_id"]):
        return False
    if "title" in scenario and not _is_string(scenario["title"], _STRING_LIMITS["title"]):
        return False
    if not isinstance(scenario["events"], list) or not 1 <= len(scenario["events"]) <= 16:
        return False
    return all(_valid_event(event) for event in scenario["events"]) and isinstance(scenario["expected"], Mapping) and _valid_expected(scenario["expected"])


def normalize_scenario(scenario: dict) -> dict:
    """Return a deep-copied, normalized synthetic scenario or a fixed rejection."""
    if not isinstance(scenario, Mapping) or "real_data" not in scenario:
        raise ValueError(_ERROR)
    if type(scenario["real_data"]) is not bool or scenario["real_data"] is not False:
        raise ValueError(_REAL_DATA_ERROR)
    if not _valid_payload(scenario):
        raise ValueError(_ERROR)
    normalized = deepcopy(dict(scenario))
    normalized["expected"]["severity_hint"] = normalized["expected"].get("severity_hint", "low")
    return normalized
