from pathlib import Path

from src.app.orchestrator import run_demo


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_s01_flow_keeps_one_trace_id_and_waits_for_human() -> None:
    result = run_demo(REPO_ROOT / "data" / "scenarios" / "S01.json")

    trace_ids = {
        result["incident"]["trace_id"],
        *(item["trace_id"] for item in result["evidence_items"]),
        result["response_plan"]["trace_id"],
        result["approval"]["trace_id"],
        result["audit"]["trace_id"],
        *(record["trace_id"] for record in result["ledger"]),
    }
    assert trace_ids == {"tr_s01"}
    assert result["stages"] == ["commander", "evidence", "response", "audit"]
    assert result["response_plan"]["status"] == "pending_approval"
    assert result["approval"]["status"] == "pending"
    assert result["audit"]["integrity_check"] == "passed"
    assert "approval.required" in result["audit"]["missing_requirements"]


def test_s01_human_approval_qualifies_without_executing_plan() -> None:
    result = run_demo(
        REPO_ROOT / "data" / "scenarios" / "S01.json",
        approval_status="approved",
    )

    assert result["approval"]["status"] == "approved"
    assert result["response_plan"]["status"] == "pending_approval"
    assert result["audit"]["audit_status"] == "qualified"
    assert result["audit"]["integrity_check"] == "passed"
