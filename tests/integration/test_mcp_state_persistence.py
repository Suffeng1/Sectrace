import json
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

import pytest

from src.app.mcp_adapter import SafeMCPAdapter
from tests.approval_fakes import APPROVAL_EVENT_ID, StaticApprovalVerifier


REPO_ROOT = Path(__file__).resolve().parents[2]
SCENARIOS = REPO_ROOT / "data" / "scenarios"


def _rehash_ledger(records: list[dict[str, str]]) -> None:
    previous_hash = ""
    for index, record in enumerate(records, start=1):
        record["event_id"] = f"ledger_{index:03d}"
        record["prev_hash"] = previous_hash
        unsigned = {key: value for key, value in record.items() if key != "hash"}
        canonical = json.dumps(
            unsigned, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
        record["hash"] = sha256(previous_hash.encode() + canonical).hexdigest()
        previous_hash = record["hash"]


def _pending_adapter(state_dir: Path) -> tuple[SafeMCPAdapter, str, str]:
    adapter = SafeMCPAdapter(
        SCENARIOS,
        state_dir=state_dir,
        approval_verifier=StaticApprovalVerifier(),
    )
    intake = adapter.call_tool(
        "sectrace.intake.create_incident", scenario_id="S01"
    )
    trace_id = intake["trace_id"]
    adapter.call_tool("sectrace.evidence.analyze_case", trace_id=trace_id)
    plan = adapter.call_tool("sectrace.response.create_plan", trace_id=trace_id)
    return adapter, trace_id, plan["result"]["plan_id"]


def test_pending_trace_survives_restart_and_can_be_human_approved(
    tmp_path: Path,
) -> None:
    state_dir = tmp_path / "mcp-state"
    _, trace_id, plan_id = _pending_adapter(state_dir)

    restarted = SafeMCPAdapter(
        SCENARIOS,
        state_dir=state_dir,
        approval_verifier=StaticApprovalVerifier(),
    )
    ledger = restarted.call_tool("sectrace.ledger.get_trace", trace_id=trace_id)
    approval = restarted.call_tool(
        "sectrace.ledger.log_approval",
        trace_id=trace_id,
        decision="approved",
        plan_ref=plan_id,
        approval_event_id=APPROVAL_EVENT_ID,
    )
    audit = restarted.call_tool("sectrace.audit.build_bundle", trace_id=trace_id)

    assert len(ledger["result"]) == 3
    assert approval["result"]["approval"]["status"] == "approved"
    assert audit["result"]["audit_status"] == "qualified"
    state_file = state_dir / f"{trace_id}.json"
    assert json.loads(state_file.read_text(encoding="utf-8"))["incident"]["trace_id"] == trace_id
    assert not any(".tmp" in path.name for path in state_dir.iterdir())


def test_completed_trace_and_audit_survive_another_restart(tmp_path: Path) -> None:
    state_dir = tmp_path / "mcp-state"
    adapter, trace_id, plan_id = _pending_adapter(state_dir)
    adapter.call_tool(
        "sectrace.ledger.log_approval",
        trace_id=trace_id,
        decision="approved",
        plan_ref=plan_id,
        approval_event_id=APPROVAL_EVENT_ID,
    )
    adapter.call_tool("sectrace.audit.build_bundle", trace_id=trace_id)

    restarted = SafeMCPAdapter(SCENARIOS, state_dir=state_dir)
    ledger = restarted.call_tool("sectrace.ledger.get_trace", trace_id=trace_id)

    assert len(ledger["result"]) == 5
    assert restarted.traces[trace_id]["audit"].audit_status == "qualified"


def test_tampered_persisted_ledger_refuses_to_load_without_leaking_content(
    tmp_path: Path,
) -> None:
    state_dir = tmp_path / "mcp-state"
    _, trace_id, _ = _pending_adapter(state_dir)
    state_file = state_dir / f"{trace_id}.json"
    payload = json.loads(state_file.read_text(encoding="utf-8"))
    payload["ledger"][-1]["hash"] = "0" * 64
    state_file.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="invalid persisted trace") as error:
        SafeMCPAdapter(SCENARIOS, state_dir=state_dir)

    assert "0" * 64 not in str(error.value)


def test_decided_approval_without_matching_ledger_event_refuses_to_load(
    tmp_path: Path,
) -> None:
    state_dir = tmp_path / "mcp-state"
    _, trace_id, _ = _pending_adapter(state_dir)
    state_file = state_dir / f"{trace_id}.json"
    payload = json.loads(state_file.read_text(encoding="utf-8"))
    payload["approval"]["status"] = "approved"
    payload["approval"]["timestamp"] = datetime.now(timezone.utc).isoformat()
    state_file.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="invalid persisted trace"):
        SafeMCPAdapter(SCENARIOS, state_dir=state_dir)


def test_response_without_evidence_stage_refuses_to_load(tmp_path: Path) -> None:
    state_dir = tmp_path / "mcp-state"
    _, trace_id, _ = _pending_adapter(state_dir)
    state_file = state_dir / f"{trace_id}.json"
    payload = json.loads(state_file.read_text(encoding="utf-8"))
    del payload["evidence_items"]
    del payload["risk_path"]
    state_file.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="invalid persisted trace"):
        SafeMCPAdapter(SCENARIOS, state_dir=state_dir)


def test_approval_before_response_event_refuses_even_with_valid_hashes(
    tmp_path: Path,
) -> None:
    state_dir = tmp_path / "mcp-state"
    adapter, trace_id, plan_id = _pending_adapter(state_dir)
    adapter.call_tool(
        "sectrace.ledger.log_approval",
        trace_id=trace_id,
        decision="approved",
        plan_ref=plan_id,
        approval_event_id=APPROVAL_EVENT_ID,
    )
    state_file = state_dir / f"{trace_id}.json"
    payload = json.loads(state_file.read_text(encoding="utf-8"))
    payload["ledger"][2], payload["ledger"][3] = (
        payload["ledger"][3],
        payload["ledger"][2],
    )
    _rehash_ledger(payload["ledger"])
    state_file.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="invalid persisted trace"):
        SafeMCPAdapter(SCENARIOS, state_dir=state_dir)


def test_missing_response_event_refuses_even_with_valid_hashes(
    tmp_path: Path,
) -> None:
    state_dir = tmp_path / "mcp-state"
    adapter, trace_id, plan_id = _pending_adapter(state_dir)
    adapter.call_tool(
        "sectrace.ledger.log_approval",
        trace_id=trace_id,
        decision="approved",
        plan_ref=plan_id,
        approval_event_id=APPROVAL_EVENT_ID,
    )
    state_file = state_dir / f"{trace_id}.json"
    payload = json.loads(state_file.read_text(encoding="utf-8"))
    payload["ledger"] = [
        record
        for record in payload["ledger"]
        if record["event_type"] != "response.pending_approval"
    ]
    _rehash_ledger(payload["ledger"])
    state_file.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="invalid persisted trace"):
        SafeMCPAdapter(SCENARIOS, state_dir=state_dir)


def test_forged_qualified_audit_refuses_with_valid_ledger(tmp_path: Path) -> None:
    state_dir = tmp_path / "mcp-state"
    adapter, trace_id, _ = _pending_adapter(state_dir)
    adapter.call_tool("sectrace.audit.build_bundle", trace_id=trace_id)
    state_file = state_dir / f"{trace_id}.json"
    payload = json.loads(state_file.read_text(encoding="utf-8"))
    payload["audit"]["audit_status"] = "qualified"
    payload["audit"]["missing_requirements"] = []
    payload["audit"]["report_markdown"] = payload["audit"][
        "report_markdown"
    ].replace("not_qualified", "qualified").replace(
        "approval.required", "none"
    )
    state_file.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="invalid persisted trace"):
        SafeMCPAdapter(SCENARIOS, state_dir=state_dir)


def test_response_stage_not_requested_approval_refuses_with_valid_hashes(
    tmp_path: Path,
) -> None:
    state_dir = tmp_path / "mcp-state"
    _, trace_id, plan_id = _pending_adapter(state_dir)
    state_file = state_dir / f"{trace_id}.json"
    payload = json.loads(state_file.read_text(encoding="utf-8"))
    decided_at = datetime.now(timezone.utc).isoformat()
    payload["approval"]["status"] = "not_requested"
    payload["approval"]["timestamp"] = decided_at
    event = dict(payload["ledger"][-1])
    event.update(
        {
            "at": decided_at,
            "actor": "human_operator",
            "event_type": "approval.not_requested",
            "payload_ref": (
                f"approval:{plan_id}:reason_sha256:{sha256(b'').hexdigest()}"
            ),
        }
    )
    payload["ledger"].append(event)
    _rehash_ledger(payload["ledger"])
    state_file.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="invalid persisted trace"):
        SafeMCPAdapter(SCENARIOS, state_dir=state_dir)


def test_distinct_run_id_preserves_existing_trace_state(tmp_path: Path) -> None:
    state_dir = tmp_path / "mcp-state"
    adapter = SafeMCPAdapter(SCENARIOS, state_dir=state_dir)
    original = adapter.call_tool(
        "sectrace.intake.create_incident", scenario_id="S01"
    )
    original_path = state_dir / f"{original['trace_id']}.json"
    original_bytes = original_path.read_bytes()

    clean = adapter.call_tool(
        "sectrace.intake.create_incident",
        scenario_id="S01",
        run_id="R08BD",
    )

    assert original["trace_id"] == "tr_s01"
    assert clean["trace_id"] == "tr_s01_r08bd"
    assert original_path.read_bytes() == original_bytes
    assert (state_dir / "tr_s01_r08bd.json").is_file()
    assert clean["result"]["scenario_id"] == "S01"


def test_duplicate_trace_creation_refuses_without_overwrite(tmp_path: Path) -> None:
    state_dir = tmp_path / "mcp-state"
    adapter = SafeMCPAdapter(SCENARIOS, state_dir=state_dir)
    intake = adapter.call_tool(
        "sectrace.intake.create_incident", scenario_id="S01"
    )
    state_path = state_dir / f"{intake['trace_id']}.json"
    before = state_path.read_bytes()

    with pytest.raises(ValueError, match="trace already exists"):
        adapter.call_tool("sectrace.intake.create_incident", scenario_id="S01")

    assert state_path.read_bytes() == before


def test_run_id_rejects_path_like_value_without_creating_state(
    tmp_path: Path,
) -> None:
    state_dir = tmp_path / "mcp-state"
    adapter = SafeMCPAdapter(SCENARIOS, state_dir=state_dir)

    with pytest.raises(ValueError, match="invalid run_id"):
        adapter.call_tool(
            "sectrace.intake.create_incident",
            scenario_id="S01",
            run_id="../R08BD",
        )

    assert not state_dir.exists()
