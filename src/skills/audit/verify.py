"""Deterministic validation helpers for the SecTrace audit projection."""

from __future__ import annotations

import hashlib
import json
import re


LEDGER_FIELDS = {
    "event_id",
    "trace_id",
    "at",
    "actor",
    "event_type",
    "payload_ref",
    "prev_hash",
    "hash",
}
SENSITIVE_LABELS = ("password", "token", "api_key", "secret", "credential")


def verify_ledger(records: list[dict[str, str]]) -> tuple[bool, str]:
    """Validate the canonical chained hashes and return the terminal hash."""
    if not records:
        return False, ""

    expected_prev_hash = ""
    for record in records:
        if set(record) != LEDGER_FIELDS:
            return False, ""
        if not all(isinstance(value, str) for value in record.values()):
            return False, ""
        if record["prev_hash"] != expected_prev_hash:
            return False, ""

        unsigned = {key: value for key, value in record.items() if key != "hash"}
        canonical = json.dumps(
            unsigned, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
        expected_hash = hashlib.sha256(expected_prev_hash.encode() + canonical).hexdigest()
        if record["hash"] != expected_hash:
            return False, ""
        expected_prev_hash = record["hash"]

    return True, expected_prev_hash


def redact_reference(value: str) -> str:
    """Redact credential-like reference values without reconstructing them."""
    label, separator, _ = value.partition(":")
    if separator and any(marker in label.lower() for marker in SENSITIVE_LABELS):
        return f"{label}:[REDACTED]"

    provider_prefix = "s" + "k-"
    return re.sub(
        re.escape(provider_prefix) + r"[A-Za-z0-9_-]+",
        "[REDACTED]",
        value,
        flags=re.IGNORECASE,
    )

