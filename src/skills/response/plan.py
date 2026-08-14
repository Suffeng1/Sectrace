"""Fail-closed deterministic rules for advice-only response planning."""

from __future__ import annotations

import re

from src.app.contracts import EvidenceItem


INVALID_EVIDENCE_ERROR = "invalid response evidence"
_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")
_TRACE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")
_SECRET_ASSIGNMENT = re.compile(
    r"\b(?:api[_-]?key|secret|token|password|passwd|authorization|credential)\b\s*[:=]",
    re.IGNORECASE,
)
_PATH_TOKEN = re.compile(
    r"(?:[A-Za-z]:[\\/]|\\\\[^\s\\/]+|(?:^|[\s\"'=(:])/(?:[^\s\\/]+)|(?:^|[\s\"'=(:])(?:\.{1,2}|tmp|temp)[\\/])",
    re.IGNORECASE,
)
_CLASSIFICATIONS = {"fact", "inference", "unknown"}
_CONFIDENCES = {"low", "medium", "high"}
_EVIDENCE_LEVELS = {"insufficient", "corroborated", "strong"}
_EVIDENCE_FIELDS = frozenset(
    {
        "evidence_id",
        "trace_id",
        "source_ref",
        "statement",
        "classification",
        "confidence",
        "evidence_level",
        "related_event_refs",
    }
)


def _is_identifier(value: object, pattern: re.Pattern[str]) -> bool:
    return type(value) is str and pattern.fullmatch(value) is not None


def _is_safe_statement(value: object) -> bool:
    return (
        type(value) is str
        and 1 <= len(value) <= 512
        and _SECRET_ASSIGNMENT.search(value) is None
        and _PATH_TOKEN.search(value) is None
    )


def _has_valid_evidence_values(data: dict[str, object]) -> bool:
    evidence_id = data["evidence_id"]
    trace_id = data["trace_id"]
    source_ref = data["source_ref"]
    statement = data["statement"]
    classification = data["classification"]
    confidence = data["confidence"]
    evidence_level = data["evidence_level"]
    related_refs = data["related_event_refs"]
    return (
        _is_identifier(evidence_id, _IDENTIFIER)
        and _is_identifier(trace_id, _TRACE_ID)
        and _is_identifier(source_ref, _IDENTIFIER)
        and _is_safe_statement(statement)
        and type(classification) is str
        and classification in _CLASSIFICATIONS
        and type(confidence) is str
        and confidence in _CONFIDENCES
        and type(evidence_level) is str
        and evidence_level in _EVIDENCE_LEVELS
        and type(related_refs) is list
        and 1 <= len(related_refs) <= 16
        and all(_is_identifier(ref, _IDENTIFIER) for ref in related_refs)
    )


def _normalized_evidence_item(item: object) -> dict[str, object]:
    if type(item) is not EvidenceItem:
        raise ValueError(INVALID_EVIDENCE_ERROR)
    raw_fields = object.__getattribute__(item, "__dict__")
    fields_set = object.__getattribute__(item, "__pydantic_fields_set__")
    pydantic_private = object.__getattribute__(item, "__pydantic_private__")
    pydantic_extra = object.__getattribute__(item, "__pydantic_extra__")
    if (
        type(raw_fields) is not dict
        or set(raw_fields) != _EVIDENCE_FIELDS
        or type(fields_set) is not set
        or fields_set != _EVIDENCE_FIELDS
        or pydantic_private is not None
        or pydantic_extra is not None
        or not _has_valid_evidence_values(raw_fields)
    ):
        raise ValueError(INVALID_EVIDENCE_ERROR)
    serialized = EvidenceItem.model_dump(item, mode="python", warnings=False)
    if (
        type(serialized) is not dict
        or set(serialized) != _EVIDENCE_FIELDS
        or not _has_valid_evidence_values(serialized)
    ):
        raise ValueError(INVALID_EVIDENCE_ERROR)
    return serialized


def validate_evidence_items(evidence_items: list[EvidenceItem]) -> list[dict[str, object]]:
    """Return normalized evidence only when every boundary invariant holds."""
    try:
        return _validate_evidence_items(evidence_items)
    except Exception:
        raise ValueError(INVALID_EVIDENCE_ERROR) from None


def _validate_evidence_items(evidence_items: list[EvidenceItem]) -> list[dict[str, object]]:
    if type(evidence_items) is not list or not 1 <= len(evidence_items) <= 16:
        raise ValueError(INVALID_EVIDENCE_ERROR)

    trace_id: str | None = None
    evidence_ids: set[str] = set()
    source_refs: set[str] = set()
    related_refs: list[list[str]] = []
    for item in evidence_items:
        normalized = _normalized_evidence_item(item)
        evidence_id = normalized["evidence_id"]
        item_trace_id = normalized["trace_id"]
        source_ref = normalized["source_ref"]
        statement = normalized["statement"]
        classification = normalized["classification"]
        confidence = normalized["confidence"]
        evidence_level = normalized["evidence_level"]
        item_related_refs = normalized["related_event_refs"]
        if trace_id is None:
            trace_id = item_trace_id
        if (
            item_trace_id != trace_id
            or evidence_id in evidence_ids
            or source_ref in source_refs
            or evidence_id in source_refs
            or source_ref in evidence_ids
            or evidence_id == source_ref
        ):
            raise ValueError(INVALID_EVIDENCE_ERROR)
        if source_ref not in item_related_refs or len(item_related_refs) != len(set(item_related_refs)):
            raise ValueError(INVALID_EVIDENCE_ERROR)
        evidence_ids.add(evidence_id)
        source_refs.add(source_ref)
        related_refs.append(item_related_refs)

    if any(not set(refs).issubset(source_refs) for refs in related_refs):
        raise ValueError(INVALID_EVIDENCE_ERROR)
    return [_normalized_evidence_item(item) for item in evidence_items]


def has_corroborated_risk(evidence_items: list[EvidenceItem]) -> bool:
    """Return whether validated evidence supports a high-risk advice plan."""
    normalized_items = validate_evidence_items(evidence_items)
    return all(
        item["classification"] == "fact"
        and item["confidence"] == "high"
        and item["evidence_level"] in {"corroborated", "strong"}
        for item in normalized_items
    )
