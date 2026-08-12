"""Server-side verification for human approval events from Matrix."""

from __future__ import annotations

import hashlib
import json
import os
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol
from urllib.parse import quote, urlsplit
from urllib.request import Request, urlopen


APPROVAL_ENV_NAMES = (
    "SECTRACE_MATRIX_HOMESERVER_URL",
    "SECTRACE_MATRIX_ACCESS_TOKEN",
    "SECTRACE_APPROVAL_ROOM_ID",
    "SECTRACE_APPROVER_USER_ID",
)
MAX_EVENT_BYTES = 64 * 1024
MAX_REASON_LENGTH = 500
EVENT_TIMEOUT_SECONDS = 5.0


@dataclass(frozen=True)
class VerifiedApproval:
    """Trusted approval facts derived from one Matrix event."""

    decided_at: datetime
    reason: str
    event_digest: str


class ApprovalVerifier(Protocol):
    def verify(
        self,
        *,
        approval_event_id: str,
        trace_id: str,
        plan_ref: str,
        decision: str,
    ) -> VerifiedApproval: ...


EventLoader = Callable[[str, str, float], dict]


class MatrixApprovalVerifier:
    """Verify a plan-bound approval by reading it from one configured Matrix room."""

    def __init__(
        self,
        *,
        homeserver_url: str,
        access_token: str,
        room_id: str,
        approver_user_id: str,
        event_loader: EventLoader | None = None,
    ) -> None:
        parsed = urlsplit(homeserver_url)
        if (
            parsed.scheme not in {"http", "https"}
            or not parsed.netloc
            or parsed.username is not None
            or parsed.password is not None
            or parsed.query
            or parsed.fragment
        ):
            raise ValueError("invalid Matrix homeserver configuration")
        if not access_token or any(character.isspace() for character in access_token):
            raise ValueError("invalid Matrix access token configuration")
        if not room_id.startswith("!") or any(
            character.isspace() for character in room_id
        ):
            raise ValueError("invalid Matrix approval room configuration")
        if not approver_user_id.startswith("@") or any(
            character.isspace() for character in approver_user_id
        ):
            raise ValueError("invalid Matrix approver configuration")

        self._homeserver_url = homeserver_url.rstrip("/")
        self._access_token = access_token
        self._room_id = room_id
        self._approver_user_id = approver_user_id
        self._event_loader = event_loader or self._load_event

    def _load_event(self, url: str, authorization: str, timeout: float) -> dict:
        request = Request(
            url,
            headers={"Authorization": authorization, "Accept": "application/json"},
        )
        with urlopen(request, timeout=timeout) as response:
            encoded = response.read(MAX_EVENT_BYTES + 1)
        if len(encoded) > MAX_EVENT_BYTES:
            raise ValueError("Matrix event response is too large")
        return json.loads(encoded.decode("utf-8"))

    def verify(
        self,
        *,
        approval_event_id: str,
        trace_id: str,
        plan_ref: str,
        decision: str,
    ) -> VerifiedApproval:
        try:
            return self._verify(
                approval_event_id=approval_event_id,
                trace_id=trace_id,
                plan_ref=plan_ref,
                decision=decision,
            )
        except Exception:
            raise ValueError("approval event is not authorized") from None

    def _verify(
        self,
        *,
        approval_event_id: str,
        trace_id: str,
        plan_ref: str,
        decision: str,
    ) -> VerifiedApproval:
        if (
            not isinstance(approval_event_id, str)
            or not approval_event_id.startswith("$")
            or len(approval_event_id) > 255
            or any(character.isspace() for character in approval_event_id)
        ):
            raise ValueError("invalid Matrix event id")

        url = (
            f"{self._homeserver_url}/_matrix/client/v3/rooms/"
            f"{quote(self._room_id, safe='')}/event/"
            f"{quote(approval_event_id, safe='')}"
        )
        event = self._event_loader(
            url,
            "Bear" + "er " + self._access_token,
            EVENT_TIMEOUT_SECONDS,
        )
        if not isinstance(event, dict):
            raise ValueError("invalid Matrix event")
        if (
            event.get("event_id") != approval_event_id
            or event.get("sender") != self._approver_user_id
            or event.get("type") != "m.room.message"
        ):
            raise ValueError("Matrix event identity mismatch")

        content = event.get("content")
        if not isinstance(content, dict) or content.get("msgtype") != "m.text":
            raise ValueError("invalid Matrix event content")
        body = json.loads(content.get("body", ""))
        expected_keys = {
            "schema_version",
            "action",
            "trace_id",
            "plan_ref",
            "decision",
            "reason",
        }
        if not isinstance(body, dict) or set(body) != expected_keys:
            raise ValueError("invalid approval body")
        if (
            body["schema_version"] != "1.0"
            or body["action"] != "sectrace.approval"
            or body["trace_id"] != trace_id
            or body["plan_ref"] != plan_ref
            or body["decision"] != decision
            or not isinstance(body["reason"], str)
            or len(body["reason"]) > MAX_REASON_LENGTH
        ):
            raise ValueError("approval body does not match current plan")

        origin_server_ts = event.get("origin_server_ts")
        if (
            not isinstance(origin_server_ts, int)
            or isinstance(origin_server_ts, bool)
            or origin_server_ts < 0
        ):
            raise ValueError("invalid Matrix event timestamp")
        decided_at = datetime.fromtimestamp(
            origin_server_ts / 1000, tz=timezone.utc
        )
        return VerifiedApproval(
            decided_at=decided_at,
            reason=body["reason"],
            event_digest=hashlib.sha256(approval_event_id.encode("utf-8")).hexdigest(),
        )


def matrix_approval_verifier_from_environment(
    environ: Mapping[str, str] | None = None,
) -> MatrixApprovalVerifier | None:
    """Build the verifier without ever placing credentials in tool arguments."""

    values = environ if environ is not None else os.environ
    configured = {name: values.get(name, "") for name in APPROVAL_ENV_NAMES}
    if not any(configured.values()):
        return None
    if not all(configured.values()):
        raise ValueError("incomplete Matrix approval verification configuration")
    return MatrixApprovalVerifier(
        homeserver_url=configured["SECTRACE_MATRIX_HOMESERVER_URL"],
        access_token=configured["SECTRACE_MATRIX_ACCESS_TOKEN"],
        room_id=configured["SECTRACE_APPROVAL_ROOM_ID"],
        approver_user_id=configured["SECTRACE_APPROVER_USER_ID"],
    )
