from copy import deepcopy
import json
from pathlib import Path

import pytest

from src.app.mcp_adapter import SafeMCPAdapter


REPO_ROOT = Path(__file__).resolve().parents[2]
SCENARIOS = REPO_ROOT / "data" / "scenarios"


def _evidence_adapter() -> tuple[SafeMCPAdapter, str]:
    adapter = SafeMCPAdapter(SCENARIOS)
    intake = adapter.call_tool("sectrace.intake.create_incident", scenario_id="S01")
    trace_id = intake["trace_id"]
    adapter.call_tool("sectrace.evidence.analyze_case", trace_id=trace_id)
    return adapter, trace_id


def _pending_adapter() -> tuple[SafeMCPAdapter, str, str]:
    adapter, trace_id = _evidence_adapter()
    response = adapter.call_tool("sectrace.response.create_plan", trace_id=trace_id)
    return adapter, trace_id, response["result"]["plan_id"]


@pytest.mark.parametrize(
    "operation",
    [
        "repeat_evidence",
        "evidence_after_response",
        "repeat_response",
        "repeat_audit",
        "approval_after_audit",
    ],
)
def test_repeated_or_out_of_order_stage_is_rejected_without_mutation(
    operation: str,
) -> None:
    if operation == "repeat_evidence":
        adapter, trace_id = _evidence_adapter()
        plan_id = ""
        tool, arguments = "sectrace.evidence.analyze_case", {"trace_id": trace_id}
    else:
        adapter, trace_id, plan_id = _pending_adapter()
        if operation == "evidence_after_response":
            tool, arguments = "sectrace.evidence.analyze_case", {"trace_id": trace_id}
        elif operation == "repeat_response":
            tool, arguments = "sectrace.response.create_plan", {"trace_id": trace_id}
        else:
            adapter.call_tool("sectrace.audit.build_bundle", trace_id=trace_id)
            if operation == "repeat_audit":
                tool, arguments = "sectrace.audit.build_bundle", {"trace_id": trace_id}
            else:
                tool = "sectrace.ledger.log_approval"
                arguments = {
                    "trace_id": trace_id,
                    "decision": "approved",
                    "plan_ref": plan_id,
                    "approval_event_id": "$synthetic-audit-complete",
                }

    before = deepcopy(adapter._serialize_state(trace_id))
    with pytest.raises(ValueError):
        adapter.call_tool(tool, **arguments)
    assert adapter._serialize_state(trace_id) == before


def test_scenario_id_cannot_escape_the_approved_scenario_directory(
    tmp_path: Path,
) -> None:
    scenario_dir = tmp_path / "scenarios"
    scenario_dir.mkdir()
    (tmp_path / "outside.json").write_text("{}", encoding="utf-8")
    adapter = SafeMCPAdapter(scenario_dir)

    with pytest.raises(ValueError, match="invalid scenario_id"):
        adapter.call_tool(
            "sectrace.intake.create_incident", scenario_id="../outside"
        )


@pytest.mark.parametrize("scenario_id", [f"S{index:02d}" for index in range(1, 25)])
def test_all_scenario_ids_follow_their_declared_intake_oracle(scenario_id: str) -> None:
    adapter = SafeMCPAdapter(SCENARIOS)
    scenario = json.loads((SCENARIOS / f"{scenario_id}.json").read_text(encoding="utf-8"))

    if scenario["expected"].get("intake") == "reject":
        expected_error = (
            "synthetic or de-identified"
            if scenario.get("real_data") is True
            else "invalid intake payload"
        )
        with pytest.raises(ValueError, match=expected_error):
            adapter.call_tool(
                "sectrace.intake.create_incident", scenario_id=scenario_id
            )
        return

    result = adapter.call_tool(
        "sectrace.intake.create_incident", scenario_id=scenario_id
    )

    assert result["result"]["scenario_id"] == scenario_id


def test_trace_capacity_is_enforced_before_new_state_is_created(
    tmp_path: Path,
) -> None:
    state_dir = tmp_path / "state"
    adapter = SafeMCPAdapter(SCENARIOS, state_dir=state_dir, max_traces=1)
    adapter.call_tool("sectrace.intake.create_incident", scenario_id="S01")

    with pytest.raises(ValueError, match="trace capacity reached"):
        adapter.call_tool("sectrace.intake.create_incident", scenario_id="S02")

    assert sorted(path.name for path in state_dir.glob("*.json")) == ["tr_s01.json"]


def test_unconfigured_adapter_rejects_self_asserted_human_approval_without_mutation(
) -> None:
    adapter, trace_id, plan_id = _pending_adapter()
    before = deepcopy(adapter._serialize_state(trace_id))

    with pytest.raises(ValueError, match="trusted approval verification"):
        adapter.call_tool(
            "sectrace.ledger.log_approval",
            trace_id=trace_id,
            decision="approved",
            plan_ref=plan_id,
            approval_event_id="$caller-controlled-event",
            approver="human_operator",
            reason="caller-controlled reason",
        )

    assert adapter._serialize_state(trace_id) == before
