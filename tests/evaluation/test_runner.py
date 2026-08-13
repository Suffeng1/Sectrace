from __future__ import annotations

import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

import pytest

from evaluation.metrics import build_metrics
from evaluation.runner import (
    EXIT_EVALUATION_FAILURE,
    EXIT_INTERNAL_FAILURE,
    EXIT_INPUT_FAILURE,
    EXIT_SUCCESS,
    _LocalApprovalVerifier,
    _result,
    main,
    render_markdown,
    run_evaluation,
)


ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = ROOT / "evaluation" / "dataset.json"


def dataset() -> dict:
    return json.loads(DATASET_PATH.read_text(encoding="utf-8"))


def write_dataset(tmp_path: Path, payload: dict) -> Path:
    path = tmp_path / "dataset.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_dataset_has_fixed_semantics_and_all_required_kinds() -> None:
    payload = dataset()
    assert {case["case_kind"] for case in payload["cases"]} == {
        "normal", "insufficient", "conflicting", "invalid_approval", "tampered_ledger"
    }
    assert len({case["case_id"] for case in payload["cases"]}) == 5
    assert len({case["trace_id"] for case in payload["cases"]}) == 5
    for case in payload["cases"]:
        assert "expected" not in case and "title" not in case


@pytest.mark.parametrize(
    ("case_kind", "approval"),
    [
        ("normal", {"required": True, "decision": "approved", "binding_valid": True}),
        ("insufficient", {"required": False, "decision": "not_requested", "binding_valid": None}),
        ("conflicting", {"required": False, "decision": "not_requested", "binding_valid": None}),
        ("invalid_approval", {"required": True, "decision": "approved", "binding_valid": False}),
        ("tampered_ledger", {"required": True, "decision": "approved", "binding_valid": True}),
    ],
)
def test_all_case_approval_invariants_are_structured_and_stable(case_kind: str, approval: dict) -> None:
    case = next(item for item in dataset()["cases"] if item["case_kind"] == case_kind)
    assert case["approval"] == approval


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("required", True),
        ("decision", "approved"),
        ("decision", "rejected"),
        ("binding_valid", True),
        ("binding_valid", False),
    ],
)
@pytest.mark.parametrize("position", [0, 2, 4])
def test_conflicting_approval_field_mutations_are_rejected_in_any_position(
    tmp_path: Path, field: str, value: object, position: int
) -> None:
    payload = dataset()
    case_index = next(index for index, item in enumerate(payload["cases"]) if item["case_kind"] == "conflicting")
    case = payload["cases"].pop(case_index)
    case["approval"][field] = value
    payload["cases"].insert(position, case)
    with pytest.raises(ValueError, match="invalid evaluation dataset"):
        run_evaluation(write_dataset(tmp_path, payload), ROOT)


@pytest.mark.parametrize("position", [0, 2, 4])
def test_conflicting_approval_combined_mutation_is_rejected_in_any_position(
    tmp_path: Path, position: int
) -> None:
    payload = dataset()
    case_index = next(index for index, item in enumerate(payload["cases"]) if item["case_kind"] == "conflicting")
    case = payload["cases"].pop(case_index)
    case["approval"] = {"required": True, "decision": "approved", "binding_valid": True}
    payload["cases"].insert(position, case)
    with pytest.raises(ValueError, match="invalid evaluation dataset"):
        run_evaluation(write_dataset(tmp_path, payload), ROOT)


@pytest.mark.parametrize(
    ("field", "value"),
    [("same_subject", False), ("ordered_risk_sequence", True), ("source_count", 1)],
)
@pytest.mark.parametrize("position", [0, 2, 4])
def test_conflicting_provenance_mutations_are_rejected_in_any_position(
    tmp_path: Path, field: str, value: object, position: int
) -> None:
    payload = dataset()
    case_index = next(index for index, item in enumerate(payload["cases"]) if item["case_kind"] == "conflicting")
    case = payload["cases"].pop(case_index)
    case["provenance"][field] = value
    payload["cases"].insert(position, case)
    with pytest.raises(ValueError, match="invalid evaluation dataset"):
        run_evaluation(write_dataset(tmp_path, payload), ROOT)


@pytest.mark.parametrize("mutation", ["missing_kind", "duplicate_case", "duplicate_trace", "nested_field", "semantic_mismatch"])
def test_dataset_rejects_coverage_identity_nested_and_semantic_errors(tmp_path: Path, mutation: str) -> None:
    payload = dataset()
    if mutation == "missing_kind":
        payload["cases"][2]["case_kind"] = "normal"
    elif mutation == "duplicate_case":
        payload["cases"][1]["case_id"] = payload["cases"][0]["case_id"]
    elif mutation == "duplicate_trace":
        payload["cases"][1]["trace_id"] = payload["cases"][0]["trace_id"]
    elif mutation == "nested_field":
        del payload["cases"][0]["approval"]["decision"]
    else:
        payload["cases"][0]["provenance"]["source_count"] = 1
    with pytest.raises(ValueError, match="invalid evaluation dataset"):
        run_evaluation(write_dataset(tmp_path, payload), ROOT)


def test_runner_real_execution_binding_trace_metrics_and_boundary() -> None:
    result = run_evaluation(DATASET_PATH, ROOT)
    cases = {case["case_id"]: case for case in result["case_results"]}
    metrics = {metric["name"]: metric for metric in result["metrics"]}

    assert result["summary"]["exit_code"] == EXIT_SUCCESS
    assert cases["normal-corroborated"]["execution_status"] == "executed"
    assert cases["invalid-high-risk-approval"]["execution_status"] == "executed"
    assert cases["invalid-high-risk-approval"]["approval_applicable"] is True
    assert cases["invalid-high-risk-approval"]["approval_binding"] is True
    assert cases["invalid-high-risk-approval"]["approval_probe_results"] == [
        "wrong_trace", "wrong_plan", "wrong_decision", "unbound_event"
    ]
    assert cases["conflicting-evidence-boundary"]["execution_status"] == "expected_fail_closed"
    assert cases["conflicting-evidence-boundary"]["scenario_run"] is False
    assert cases["conflicting-evidence-boundary"]["capability_boundary"] is True
    assert metrics["approval_binding_rate"]["denominator"] == 3
    assert metrics["ledger_integrity_rate"]["denominator"] == len(
        {case["trace_id"] for case in result["case_results"] if case["trace_applicable"]}
    )
    assert metrics["ledger_integrity_rate"]["aggregation"] == "unique_trace"


def test_approval_verifier_requires_all_four_exact_binding_probes() -> None:
    verifier = _LocalApprovalVerifier("tr_expected", "rp_expected")
    for event_id, trace_id, plan_ref, decision in (
        (verifier.valid_event_id, "tr_wrong", "rp_expected", "approved"),
        (verifier.valid_event_id, "tr_expected", "rp_wrong", "approved"),
        (verifier.valid_event_id, "tr_expected", "rp_expected", "rejected"),
        ("$unbound-event", "tr_expected", "rp_expected", "approved"),
    ):
        with pytest.raises(ValueError, match="approval event is not authorized"):
            verifier.verify(
                approval_event_id=event_id,
                trace_id=trace_id,
                plan_ref=plan_ref,
                decision=decision,
            )


def test_failed_attempt_stays_in_predeclared_scenario_run_denominator() -> None:
    case = next(case for case in dataset()["cases"] if case["case_kind"] == "normal")
    failed = _result(
        case, "tr_failed", "executed", False, "high", "qualified",
        True, True, True, True, True, True, "allow_plan",
    )
    metric = next(item for item in build_metrics([failed]) if item["name"] == "scenario_run_rate")
    assert metric["denominator"] == 1
    assert metric["numerator"] == 0
    assert metric["passed"] is False


def test_provenance_changes_fixture_or_is_rejected(tmp_path: Path) -> None:
    payload = dataset()
    payload["cases"][0]["provenance"]["ordered_risk_sequence"] = False
    with pytest.raises(ValueError, match="invalid evaluation dataset"):
        run_evaluation(write_dataset(tmp_path, payload), ROOT)


def test_schema_validates_real_result_and_rejects_malformed_result() -> None:
    from evaluation.runner import _validate_result

    result = run_evaluation(DATASET_PATH, ROOT)
    _validate_result(result)
    broken = deepcopy(result)
    broken["metrics"] = [{}]
    with pytest.raises(ValueError, match="invalid evaluation result"):
        _validate_result(broken)
    broken = deepcopy(result)
    broken["summary"] = {"passed": "8", "failed": 0, "exit_code": 99}
    with pytest.raises(ValueError, match="invalid evaluation result"):
        _validate_result(broken)


def test_nonzero_oracle_exit_and_zero_core_denominator_failure(tmp_path: Path) -> None:
    payload = dataset()
    payload["cases"][0]["oracle"]["terminal"] = "rejected"
    assert run_evaluation(write_dataset(tmp_path, payload), ROOT)["summary"]["exit_code"] == EXIT_EVALUATION_FAILURE

    metrics = build_metrics([])
    assert all(not metric["passed"] for metric in metrics if metric["zero_denominator_policy"] == "fail")


@pytest.mark.parametrize("failure", ["malformed", "missing_json_parent", "missing_markdown_parent"])
def test_cli_input_and_output_failures_are_nonleaking_exit_two(tmp_path: Path, failure: str) -> None:
    dataset_path = DATASET_PATH
    json_out = tmp_path / "result.json"
    markdown_out = tmp_path / "report.md"
    if failure == "malformed":
        dataset_path = tmp_path / "bad.json"
        dataset_path.write_text('{"schema_version":"1.0"}', encoding="utf-8")
    elif failure == "missing_json_parent":
        json_out = tmp_path / "missing" / "result.json"
    else:
        markdown_out = tmp_path / "missing" / "report.md"
    completed = subprocess.run(
        [sys.executable, "-m", "evaluation.runner", "--dataset", str(dataset_path), "--json-out", str(json_out), "--markdown-out", str(markdown_out)],
        cwd=ROOT, text=True, capture_output=True, check=False,
    )
    assert completed.returncode == EXIT_INPUT_FAILURE
    assert completed.stderr == "evaluation failed: invalid input or output\n"
    assert "Traceback" not in completed.stderr


@pytest.mark.parametrize("exception_type", [RuntimeError, AssertionError, TypeError])
def test_cli_internal_failure_is_not_mislabeled_as_input_output(exception_type: type[Exception], monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    def boom(_: Path) -> dict:
        raise exception_type("synthetic evaluator defect")

    monkeypatch.setattr("evaluation.runner.run_evaluation", boom)
    monkeypatch.setattr(sys, "argv", ["evaluation.runner", "--json-out", str(tmp_path / "result.json"), "--markdown-out", str(tmp_path / "report.md")])

    assert main() == EXIT_INTERNAL_FAILURE
    assert capsys.readouterr().err == "evaluation failed: internal error\n"


def test_schema_validation_type_error_is_expected_input_boundary(tmp_path: Path) -> None:
    payload = dataset()
    payload["cases"] = "not-an-array"
    completed = subprocess.run(
        [sys.executable, "-m", "evaluation.runner", "--dataset", str(write_dataset(tmp_path, payload)), "--json-out", str(tmp_path / "result.json"), "--markdown-out", str(tmp_path / "report.md")],
        cwd=ROOT, text=True, capture_output=True, check=False,
    )
    assert completed.returncode == EXIT_INPUT_FAILURE
    assert completed.stderr == "evaluation failed: invalid input or output\n"


def test_determinism_and_markdown_json_metric_consistency() -> None:
    first = run_evaluation(DATASET_PATH, ROOT)
    second = run_evaluation(DATASET_PATH, ROOT)
    assert first == second
    markdown = render_markdown(first)
    for metric in first["metrics"]:
        assert f"| {metric['name']} | {metric['numerator']} | {metric['denominator']} |" in markdown
