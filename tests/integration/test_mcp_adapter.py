from pathlib import Path

import pytest

from src.app.mcp_adapter import SAFETY_NOTICE, TOOL_NAMES, SafeMCPAdapter


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_mcp_adapter_exposes_exactly_five_safe_tools() -> None:
    assert TOOL_NAMES == (
        "sectrace.intake.create_incident",
        "sectrace.evidence.analyze_case",
        "sectrace.response.create_plan",
        "sectrace.audit.build_bundle",
        "sectrace.ledger.get_trace",
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


def test_mcp_adapter_rejects_unknown_or_execution_tools() -> None:
    adapter = SafeMCPAdapter(REPO_ROOT / "data" / "scenarios")

    with pytest.raises(ValueError, match="unsupported safe tool"):
        adapter.call_tool("sectrace.response.execute_action", trace_id="tr_s01")
