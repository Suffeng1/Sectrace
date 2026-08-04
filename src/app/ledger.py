"""Append-only canonical JSON ledger for the local synthetic demo."""

from __future__ import annotations

import hashlib
import json


class AuditLedger:
    """Build canonical, hash-chained records without external persistence."""

    def __init__(self, trace_id: str) -> None:
        self.trace_id = trace_id
        self.records: list[dict[str, str]] = []

    def append(
        self, *, at: str, actor: str, event_type: str, payload_ref: str
    ) -> dict[str, str]:
        prev_hash = self.records[-1]["hash"] if self.records else ""
        unsigned = {
            "event_id": f"ledger_{len(self.records) + 1:03d}",
            "trace_id": self.trace_id,
            "at": at,
            "actor": actor,
            "event_type": event_type,
            "payload_ref": payload_ref,
            "prev_hash": prev_hash,
        }
        canonical = json.dumps(
            unsigned, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
        record_hash = hashlib.sha256(prev_hash.encode() + canonical).hexdigest()
        record = {**unsigned, "hash": record_hash}
        self.records.append(record)
        return record
