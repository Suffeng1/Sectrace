from copy import deepcopy
from hashlib import sha256
from pathlib import Path

import pytest

from src.app.mcp_adapter import SAFETY_NOTICE, TOOL_NAMES, SafeMCPAdapter
from tests.approval_fakes import APPROVAL_EVENT_ID, StaticApprovalVerifier


REPO_ROOT = Path(__file__).resolve().parents[2]


def _ready_adapter(
    reason: str = "synthetic human approval",
) -> tuple[SafeMCPAdapter, str, str]:
    adapter = SafeMCPAdapter(
        REPO_ROOT / "data" / "scenarios",
        approval_verifier=StaticApprovalVerifier(reason),
    )
    intake = adapter.call_tool("sectrace.intake.create_incident", scenario_id="S01")
    trace_id = intake["trace_id"]
    adapter.call_tool("sectrace.evidence.analyze_case", trace_id=trace_id)
    response = adapter.call_tool("sectrace.response.create_plan", trace_id=trace_id)
    return adapter, trace_id, response["result"]["plan_id"]


def _state_snapshot(adapter: SafeMCPAdapter, trace_id: str) -> tuple[dict, list[dict]]:
    state = adapter.traces[trace_id]
    return state["approval"].model_dump(mode="json"), deepcopy(state["ledger"].records)


def test_mcp_adapter_exposes_exactly_six_safe_tools() -> None:
    assert TOOL_NAMES == (
        "sectrace.intake.create_incident",
        "sectrace.evidence.analyze_case",
        "sectrace.response.create_plan",
        "sectrace.audit.build_bundle",
        "sectrace.ledger.get_trace",
        "sectrace.ledger.log_approval",
    )


def test_mcp_tool_chain_uses_envelopes_and_one_trace() -> None:
    adapter = SafeMCPAdapter(REPO_ROOT / "data" / "scenarios")

    intake = adapter.call_tool("sectrace.intake.create_incident", scenario_id="S01")
    trace_id = intake["trace_id"]
    evidence = adapter.call_tool("sectrace.evidence.analyze_case", trace_id=trace_id)
    response = adapter.call_tool("sectrace.response.create_plan", trace_id=trace_id)
    audit = adapter.call_tool("sectrace.audit.build_bundle", trace_id=trace_id)
    ledger = adapter.call_tool("sectrace.ledger.get_trace", trace_id=trace_id)

    for envelope in (intake, evidence, response, audit, ledger):
        assert envelope["schema_version"] == "1.0"
        assert envelope["trace_id"] == trace_id
        assert envelope["safety_notice"] == SAFETY_NOTICE
    assert response["result"]["status"] == "pending_approval"


def test_log_approval_approved_qualifies_audit_and_hashes_reason() -> None:
    reason = "synthetic reviewer confirmed rollback coverage"
    adapter, trace_id, plan_ref = _ready_adapter(reason)

    approval = adapter.call_tool(
        "sectrace.ledger.log_approval",
        trace_id=trace_id,
        decision="approved",
        plan_ref=plan_ref,
        approval_event_id=APPROVAL_EVENT_ID,
    )
    audit = adapter.call_tool("sectrace.audit.build_bundle", trace_id=trace_id)

    ledger_record = approval["result"]["ledger_record"]
    reason_digest = sha256(reason.encode("utf-8")).hexdigest()
    event_digest = sha256(APPROVAL_EVENT_ID.encode("utf-8")).hexdigest()
    assert approval["result"]["approval"]["status"] == "approved"
    assert approval["result"]["approval"]["timestamp"] is not None
    assert ledger_record["actor"] == "human_operator"
    assert ledger_record["event_type"] == "approval.approved"
    assert ledger_record["payload_ref"] == (
        f"approval:{plan_ref}:event_sha256:{event_digest}:"
        f"reason_sha256:{reason_digest}"
    )
    assert reason not in str(approval["result"])
    assert "approval.required" not in audit["result"]["missing_requirements"]


def test_log_approval_rejected_is_audited_and_does_not_qualify() -> None:
    adapter, trace_id, plan_ref = _ready_adapter("synthetic evidence needs review")

    approval = adapter.call_tool(
        "sectrace.ledger.log_approval",
        trace_id=trace_id,
        decision="rejected",
        plan_ref=plan_ref,
        approval_event_id=APPROVAL_EVENT_ID,
    )
    audit = adapter.call_tool("sectrace.audit.build_bundle", trace_id=trace_id)

    assert approval["result"]["approval"]["status"] == "rejected"
    assert approval["result"]["ledger_record"]["actor"] == "human_operator"
    assert approval["result"]["ledger_record"]["event_type"] == "approval.rejected"
    assert "approval.required" in audit["result"]["missing_requirements"]


@pytest.mark.parametrize(
    ("arguments", "error"),
    [
        ({"plan_ref": "rp_wrong"}, "plan_ref does not match"),
        ({"approval_event_id": "$forged"}, "approval event is not authorized"),
        ({"decision": "pending"}, "decision must be"),
    ],
)
def test_log_approval_rejects_invalid_input_without_mutation(
    arguments: dict[str, str], error: str
) -> None:
    adapter, trace_id, plan_ref = _ready_adapter()
    before_approval, before_ledger = _state_snapshot(adapter, trace_id)
    call_arguments = {
        "trace_id": trace_id,
        "decision": "approved",
        "plan_ref": plan_ref,
        "approval_event_id": APPROVAL_EVENT_ID,
        **arguments,
    }

    with pytest.raises(ValueError, match=error):
        adapter.call_tool("sectrace.ledger.log_approval", **call_arguments)

    after_approval, after_ledger = _state_snapshot(adapter, trace_id)
    assert after_approval == before_approval
    assert after_ledger == before_ledger


@pytest.mark.parametrize(
    ("first_decision", "second_decision"),
    [
        ("approved", "approved"),
        ("approved", "rejected"),
        ("rejected", "rejected"),
        ("rejected", "approved"),
    ],
)
def test_log_approval_rejects_repeat_or_override_without_mutation(
    first_decision: str, second_decision: str
) -> None:
    adapter, trace_id, plan_ref = _ready_adapter()
    adapter.call_tool(
        "sectrace.ledger.log_approval",
        trace_id=trace_id,
        decision=first_decision,
        plan_ref=plan_ref,
        approval_event_id=APPROVAL_EVENT_ID,
    )
    before_approval, before_ledger = _state_snapshot(adapter, trace_id)

    with pytest.raises(ValueError, match="approval is no longer pending"):
        adapter.call_tool(
            "sectrace.ledger.log_approval",
            trace_id=trace_id,
            decision=second_decision,
            plan_ref=plan_ref,
            approval_event_id=APPROVAL_EVENT_ID,
        )

    after_approval, after_ledger = _state_snapshot(adapter, trace_id)
    assert after_approval == before_approval
    assert after_ledger == before_ledger


def test_mcp_adapter_rejects_unknown_or_execution_tools() -> None:
    adapter = SafeMCPAdapter(REPO_ROOT / "data" / "scenarios")

    with pytest.raises(ValueError, match="unsupported safe tool"):
        adapter.call_tool("sectrace.response.execute_action", trace_id="tr_s01")
