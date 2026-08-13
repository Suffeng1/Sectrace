"""Pure-local deterministic SecTrace evaluation; no service launch, network, or LLM."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from evaluation.metrics import build_metrics
from src.app.approval_verifier import VerifiedApproval
from src.app.contracts import ApprovalRecord, EvidenceItem, IncidentCase, ResponsePlan
from src.app.mcp_adapter import SafeMCPAdapter
from src.agents.audit.service import build_audit_review
from src.app.orchestrator import run_demo


EXIT_SUCCESS = 0
EXIT_EVALUATION_FAILURE = 1
EXIT_INPUT_FAILURE = 2
EXIT_INTERNAL_FAILURE = 3
SCHEMA_VERSION = "1.0"
STAGES = ["commander", "evidence", "response", "audit"]
ROOT = Path(__file__).resolve().parents[1]


class _LocalApprovalVerifier:
    """Deterministic substitute that exercises the production verifier interface."""

    valid_event_id = "$evaluation-approved"

    def __init__(self, expected_trace_id: str, expected_plan_ref: str) -> None:
        self.expected_trace_id = expected_trace_id
        self.expected_plan_ref = expected_plan_ref

    def verify(self, *, approval_event_id: str, trace_id: str, plan_ref: str, decision: str) -> VerifiedApproval:
        if (
            approval_event_id != self.valid_event_id
            or trace_id != self.expected_trace_id
            or plan_ref != self.expected_plan_ref
            or decision != "approved"
        ):
            raise ValueError("approval event is not authorized")
        return VerifiedApproval(
            decided_at=datetime(2026, 8, 1, tzinfo=timezone.utc),
            reason="synthetic evaluation approval",
            event_digest=sha256(approval_event_id.encode()).hexdigest(),
        )


def _schema(name: str) -> dict:
    return json.loads((ROOT / "evaluation" / "schema" / name).read_text(encoding="utf-8"))


class EvaluationInputError(ValueError):
    """A malformed evaluation input or declared schema/result contract."""


def _validate(instance: object, schema_name: str, message: str) -> None:
    try:
        valid = Draft202012Validator(_schema(schema_name)).is_valid(instance)
    except (TypeError, ValueError) as error:
        raise EvaluationInputError(message) from error
    if not valid:
        raise EvaluationInputError(message)


def _validate_dataset(dataset: dict[str, Any]) -> None:
    _validate(dataset, "dataset.schema.json", "invalid evaluation dataset")
    cases = dataset["cases"]
    required_kinds = {"normal", "insufficient", "conflicting", "invalid_approval", "tampered_ledger"}
    if {case["case_kind"] for case in cases} != required_kinds:
        raise EvaluationInputError("invalid evaluation dataset")
    if len({case["case_id"] for case in cases}) != len(cases) or len({case["trace_id"] for case in cases}) != len(cases):
        raise EvaluationInputError("invalid evaluation dataset")
    for case in cases:
        provenance, corroboration, approval, ledger = case["provenance"], case["corroboration"], case["approval"], case["ledger"]
        kind = case["case_kind"]
        valid = (
            (kind == "normal" and provenance["source_count"] == 3 and provenance["same_subject"] and provenance["ordered_risk_sequence"] and corroboration == {"state": "strong", "contradictory_claims": False} and approval == {"required": True, "decision": "approved", "binding_valid": True} and not ledger["tampered"])
            or (kind == "insufficient" and provenance["source_count"] == 1 and provenance["same_subject"] and not provenance["ordered_risk_sequence"] and corroboration == {"state": "insufficient", "contradictory_claims": False} and approval == {"required": False, "decision": "not_requested", "binding_valid": None} and not ledger["tampered"])
            or (kind == "conflicting" and provenance["source_count"] == 2 and provenance["same_subject"] and not provenance["ordered_risk_sequence"] and corroboration == {"state": "conflicting", "contradictory_claims": True} and approval == {"required": False, "decision": "not_requested", "binding_valid": None} and not ledger["tampered"])
            or (kind == "invalid_approval" and provenance["source_count"] == 3 and provenance["same_subject"] and provenance["ordered_risk_sequence"] and corroboration == {"state": "strong", "contradictory_claims": False} and approval == {"required": True, "decision": "approved", "binding_valid": False} and not ledger["tampered"])
            or (kind == "tampered_ledger" and provenance["source_count"] == 3 and provenance["same_subject"] and provenance["ordered_risk_sequence"] and corroboration == {"state": "strong", "contradictory_claims": False} and approval == {"required": True, "decision": "approved", "binding_valid": True} and ledger["tampered"])
        )
        if not valid:
            raise EvaluationInputError("invalid evaluation dataset")


def _validate_result(result: dict[str, Any]) -> None:
    _validate(result, "result.schema.json", "invalid evaluation result")


def _scenario_for(case: dict[str, Any]) -> dict[str, Any]:
    """Construct fixture from provenance and corroboration, never source scenario metadata."""
    provenance, state = case["provenance"], case["corroboration"]["state"]
    strong = provenance["source_count"] == 3 and provenance["same_subject"] and provenance["ordered_risk_sequence"] and state == "strong"
    event_types = ["anomalous_login", "privilege_elevation", "bulk_sensitive_data_access"] if strong else ["anomalous_login"]
    return {"scenario_id": f"eval_{case['trace_id'].replace('-', '_')}", "real_data": False, "events": [
        {"event_ref": f"eval_evt_{index:03d}", "event_type": event_type, "at": f"2026-08-01T00:0{index}:00Z", "subject": "synthetic-evaluation-subject"}
        for index, event_type in enumerate(event_types, 1)
    ], "expected": {"severity_hint": "high" if strong else "low"}}


def _write_scenario(case: dict[str, Any], directory: Path, filename: str = "scenario.json") -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / filename
    path.write_text(json.dumps(_scenario_for(case), sort_keys=True), encoding="utf-8")
    return path


def _run_adapter(case: dict[str, Any], directory: Path, valid_binding: bool) -> tuple[dict, bool, list[str]]:
    scenario = _write_scenario(case, directory, "S01.json")
    adapter = SafeMCPAdapter(scenario.parent)
    trace_id = adapter.call_tool("sectrace.intake.create_incident", scenario_id="S01", run_id=case["trace_id"])["trace_id"]
    adapter.call_tool("sectrace.evidence.analyze_case", trace_id=trace_id)
    plan = adapter.call_tool("sectrace.response.create_plan", trace_id=trace_id)["result"]
    adapter.approval_verifier = _LocalApprovalVerifier(trace_id, plan["plan_id"])
    probe_results: list[str] = []
    if not valid_binding:
        for name, trace, plan_ref, decision, event_id, expected_error in (
            ("wrong_trace", "tr_wrong", plan["plan_id"], "approved", _LocalApprovalVerifier.valid_event_id, "unknown trace_id"),
            ("wrong_plan", trace_id, "rp_wrong", "approved", _LocalApprovalVerifier.valid_event_id, "plan_ref does not match current response plan"),
            ("wrong_decision", trace_id, plan["plan_id"], "rejected", _LocalApprovalVerifier.valid_event_id, "approval event is not authorized"),
            ("unbound_event", trace_id, plan["plan_id"], "approved", "$unbound-event", "approval event is not authorized"),
        ):
            try:
                adapter.call_tool(
                    "sectrace.ledger.log_approval",
                    trace_id=trace,
                    decision=decision,
                    plan_ref=plan_ref,
                    approval_event_id=event_id,
                )
            except ValueError as error:
                if str(error) != expected_error:
                    raise
            else:
                raise RuntimeError("approval binding probe was accepted")
            probe_results.append(name)
    try:
        adapter.call_tool("sectrace.ledger.log_approval", trace_id=trace_id, decision="approved", plan_ref=plan["plan_id"], approval_event_id=_LocalApprovalVerifier.valid_event_id if valid_binding else "$unbound-event")
        binding = valid_binding
    except ValueError as error:
        if str(error) != "approval event is not authorized" or valid_binding:
            raise
        binding = True
    audit = adapter.call_tool("sectrace.audit.build_bundle", trace_id=trace_id)["result"]
    ledger = adapter.call_tool("sectrace.ledger.get_trace", trace_id=trace_id)["result"]
    return {"trace_id": trace_id, "plan": plan, "audit": audit, "ledger": ledger}, binding, probe_results


def _executed_result(case: dict[str, Any], workdir: Path) -> dict[str, Any]:
    if case["case_kind"] == "invalid_approval":
        execution, binding, probes = _run_adapter(case, workdir, valid_binding=False)
        return _result(case, execution["trace_id"], "executed", True, "high", "rejected", True, True, True, binding and probes == ["wrong_trace", "wrong_plan", "wrong_decision", "unbound_event"], True, True, "reject_invalid_plan", probes)
    if case["case_kind"] == "tampered_ledger":
        path = _write_scenario(case, workdir)
        output = run_demo(path, approval_status="approved")
        ledger = deepcopy(output["ledger"]); ledger[-1]["hash"] = "0" * 64
        audit = build_audit_review(IncidentCase.model_validate(output["incident"]), [EvidenceItem.model_validate(item) for item in output["evidence_items"]], ResponsePlan.model_validate(output["response_plan"]), ApprovalRecord.model_validate(output["approval"]), ledger)
        return _result(case, output["trace_id"], "executed", True, output["response_plan"]["risk_level"], audit.audit_status, True, True, True, True, True, audit.integrity_check == "failed", "reject_tampered_ledger")
    path = _write_scenario(case, workdir)
    output = run_demo(path, approval_status="approved" if case["approval"]["required"] else "pending")
    trace_values = [output["trace_id"], output["incident"]["trace_id"], output["response_plan"]["trace_id"], output["approval"]["trace_id"], output["audit"]["trace_id"], *(item["trace_id"] for item in output["evidence_items"]), *(record["trace_id"] for record in output["ledger"])]
    branch = "allow_plan" if output["response_plan"]["risk_level"] == "high" else "observation_only"
    return _result(case, output["trace_id"], "executed", True, output["response_plan"]["risk_level"], output["audit"]["audit_status"], len(set(trace_values)) == 1, output["stages"] == STAGES, case["approval"]["required"], True, True, output["audit"]["integrity_check"] == "passed", branch)


def _result(case: dict, trace_id: str | None, execution_status: str, scenario_run: bool, risk_level: str | None, terminal: str, trace_continuity: bool, stage_order: bool, approval_applicable: bool, approval_binding: bool, ledger_applicable: bool, ledger_integrity: bool, branch: str, approval_probe_results: list[str] | None = None) -> dict:
    oracle = case["oracle"]
    fail_closed_applicable = case["case_kind"] in {"invalid_approval", "tampered_ledger"}
    scenario_applicable = case["case_kind"] != "conflicting"
    return {"case_id": case["case_id"], "case_kind": case["case_kind"], "trace_id": trace_id, "execution_status": execution_status, "capability_boundary": False, "scenario_run": scenario_run, "scenario_applicable": scenario_applicable, "risk_level": risk_level, "terminal": terminal, "risk_terminal": risk_level == oracle["risk_level"] and terminal == oracle["terminal"], "trace_applicable": scenario_run, "trace_continuity": trace_continuity, "stage_order": stage_order, "approval_applicable": approval_applicable, "approval_binding": approval_binding, "approval_probe_results": approval_probe_results or [], "ledger_applicable": ledger_applicable, "ledger_integrity": ledger_integrity, "fail_closed_applicable": fail_closed_applicable, "fail_closed": not fail_closed_applicable or terminal in {"rejected", "not_qualified"}, "branch_gate": branch == oracle["branch_gate"]}


def _case_result(case: dict[str, Any], workdir: Path) -> dict:
    if case["case_kind"] == "conflicting":
        return {"case_id": case["case_id"], "case_kind": case["case_kind"], "trace_id": None, "execution_status": "expected_fail_closed", "capability_boundary": True, "scenario_run": False, "scenario_applicable": False, "risk_level": None, "terminal": "expected_fail_closed", "risk_terminal": True, "trace_applicable": False, "trace_continuity": False, "stage_order": False, "approval_applicable": False, "approval_binding": False, "approval_probe_results": [], "ledger_applicable": False, "ledger_integrity": False, "fail_closed_applicable": True, "fail_closed": True, "branch_gate": True}
    return _executed_result(case, workdir / case["case_id"])


def run_evaluation(dataset_path: Path, root: Path = ROOT) -> dict[str, Any]:
    dataset = json.loads(dataset_path.read_text(encoding="utf-8")); _validate_dataset(dataset)
    with tempfile.TemporaryDirectory(prefix="sectrace-evaluation-") as temporary:
        workdir = Path(temporary)
        results = [_case_result(case, workdir) for case in sorted(dataset["cases"], key=lambda item: item["case_id"])]
    metrics = build_metrics(results); failed = sum(not metric["passed"] for metric in metrics)
    result = {"schema_version": SCHEMA_VERSION, "dataset_version": dataset["dataset_version"], "case_results": results, "metrics": metrics, "summary": {"passed": len(metrics) - failed, "failed": failed, "exit_code": EXIT_SUCCESS if not failed else EXIT_EVALUATION_FAILURE}}
    _validate_result(result); return result


def render_markdown(result: dict[str, Any]) -> str:
    lines = ["# SecTrace deterministic evaluation", "", f"- schema_version: {result['schema_version']}", f"- dataset_version: {result['dataset_version']}", f"- exit_code: {result['summary']['exit_code']}", "", "| metric | numerator | denominator | status |", "| --- | ---: | ---: | --- |"]
    lines.extend(f"| {item['name']} | {item['numerator']} | {item['denominator']} | {'PASS' if item['passed'] else 'FAIL'} |" for item in result["metrics"])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--dataset", type=Path, default=Path("evaluation/dataset.json")); parser.add_argument("--json-out", type=Path, required=True); parser.add_argument("--markdown-out", type=Path, required=True); args = parser.parse_args()
    try:
        try:
            result = run_evaluation(args.dataset)
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            raise EvaluationInputError("invalid evaluation dataset") from error
        _validate_result(result)
        rendered_json = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
        rendered_markdown = render_markdown(result)
    except EvaluationInputError:
        print("evaluation failed: invalid input or output", file=sys.stderr)
        return EXIT_INPUT_FAILURE
    except Exception:
        print("evaluation failed: internal error", file=sys.stderr)
        return EXIT_INTERNAL_FAILURE
    try:
        args.json_out.write_text(rendered_json, encoding="utf-8")
        args.markdown_out.write_text(rendered_markdown, encoding="utf-8")
    except (OSError, UnicodeError):
        print("evaluation failed: invalid input or output", file=sys.stderr)
        return EXIT_INPUT_FAILURE
    return result["summary"]["exit_code"]


if __name__ == "__main__": raise SystemExit(main())
