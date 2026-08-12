import asyncio
import json
from copy import deepcopy
from hashlib import sha256
from pathlib import Path

import pytest

from src.app.approval_verifier import (
    MatrixApprovalVerifier,
    matrix_approval_verifier_from_environment,
)
from src.app.mcp_adapter import create_mcp_server
from tests.approval_fakes import StaticApprovalVerifier


REPO_ROOT = Path(__file__).resolve().parents[2]
EVENT_ID = "$verified-event"
ROOM_ID = "!approval-room:matrix.local"
USER_ID = "@admin:matrix.local"
MATRIX_TEST_VALUE = "synthetic-" + "server-token"


def _approval_body(**overrides: object) -> str:
    body = {
        "schema_version": "1.0",
        "action": "sectrace.approval",
        "trace_id": "tr_s01_secure",
        "plan_ref": "rp_tr_s01_secure",
        "decision": "approved",
        "reason": "synthetic operator review",
        **overrides,
    }
    return json.dumps(body, sort_keys=True)


def _matrix_event(**overrides: object) -> dict:
    event = {
        "event_id": EVENT_ID,
        "sender": USER_ID,
        "type": "m.room.message",
        "origin_server_ts": 1786437000000,
        "content": {"msgtype": "m.text", "body": _approval_body()},
    }
    event.update(overrides)
    return event


def _verifier(event: dict, observed: dict | None = None) -> MatrixApprovalVerifier:
    def load_event(url: str, authorization: str, timeout: float) -> dict:
        if observed is not None:
            observed.update(
                {"url": url, "authorization": authorization, "timeout": timeout}
            )
        return event

    return MatrixApprovalVerifier(
        homeserver_url="http://matrix.local",
        access_token=MATRIX_TEST_VALUE,
        room_id=ROOM_ID,
        approver_user_id=USER_ID,
        event_loader=load_event,
    )


def test_matching_matrix_event_produces_plan_bound_server_facts() -> None:
    observed: dict = {}

    verified = _verifier(_matrix_event(), observed).verify(
        approval_event_id=EVENT_ID,
        trace_id="tr_s01_secure",
        plan_ref="rp_tr_s01_secure",
        decision="approved",
    )

    assert verified.reason == "synthetic operator review"
    assert verified.decided_at.isoformat() == "2026-08-11T08:30:00+00:00"
    assert verified.event_digest == sha256(EVENT_ID.encode("utf-8")).hexdigest()
    assert "%21approval-room%3Amatrix.local" in observed["url"]
    assert "%24verified-event" in observed["url"]
    assert observed["authorization"] == "Bear" + "er " + MATRIX_TEST_VALUE
    assert observed["timeout"] == 5.0


@pytest.mark.parametrize(
    "mutation",
    [
        {"sender": "@worker:matrix.local"},
        {"event_id": "$different-event"},
        {"type": "m.room.member"},
        {"origin_server_ts": "1786437000000"},
        {"content": {"msgtype": "m.notice", "body": _approval_body()}},
        {
            "content": {
                "msgtype": "m.text",
                "body": _approval_body(trace_id="tr_other"),
            }
        },
        {
            "content": {
                "msgtype": "m.text",
                "body": _approval_body(plan_ref="rp_other"),
            }
        },
        {
            "content": {
                "msgtype": "m.text",
                "body": _approval_body(decision="rejected"),
            }
        },
        {"content": {"msgtype": "m.text", "body": "approved"}},
    ],
)
def test_untrusted_or_unbound_matrix_event_is_rejected_without_detail_leak(
    mutation: dict,
) -> None:
    event = _matrix_event()
    event.update(deepcopy(mutation))

    with pytest.raises(ValueError, match="approval event is not authorized") as error:
        _verifier(event).verify(
            approval_event_id=EVENT_ID,
            trace_id="tr_s01_secure",
            plan_ref="rp_tr_s01_secure",
            decision="approved",
        )

    assert USER_ID not in str(error.value)
    assert "tr_other" not in str(error.value)


def test_environment_configuration_is_absent_or_complete() -> None:
    assert matrix_approval_verifier_from_environment({}) is None

    with pytest.raises(ValueError, match="incomplete Matrix approval"):
        matrix_approval_verifier_from_environment(
            {"SECTRACE_MATRIX_HOMESERVER_URL": "http://matrix.local"}
        )


def test_mcp_schema_accepts_only_event_reference_and_plan_decision() -> None:
    server = create_mcp_server(
        REPO_ROOT / "data" / "scenarios",
        approval_verifier=StaticApprovalVerifier(),
    )

    tools = asyncio.run(server.list_tools())
    approval_tool = next(
        tool for tool in tools if tool.name == "sectrace.ledger.log_approval"
    )

    assert set(approval_tool.inputSchema["properties"]) == {
        "trace_id",
        "decision",
        "plan_ref",
        "approval_event_id",
    }
    assert set(approval_tool.inputSchema["required"]) == {
        "trace_id",
        "decision",
        "plan_ref",
        "approval_event_id",
    }
