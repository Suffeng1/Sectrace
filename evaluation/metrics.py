"""Metric definitions for the deterministic, offline evaluation harness."""

from __future__ import annotations


METRIC_SPECS = (
    ("scenario_run_rate", "scenario", "case", "fail", "pipeline completion", "pipeline_execution", "scenario_run"),
    ("expected_risk_terminal_accuracy", "all", "case", "fail", "semantic oracle and executed/boundary result", "oracle_mismatch", "risk_terminal"),
    ("trace_continuity_rate", "trace", "unique_trace", "fail", "executed trace fields", "trace_mismatch", "trace_continuity"),
    ("stage_order_validity_rate", "trace", "unique_trace", "fail", "executed canonical stage order", "stage_order", "stage_order"),
    ("approval_binding_rate", "approval", "case", "fail", "SafeMCPAdapter approval verifier and plan binding", "approval_binding", "approval_binding"),
    ("ledger_integrity_rate", "ledger", "unique_trace", "fail", "hash-chain verifier by trace", "ledger_integrity", "ledger_integrity"),
    ("fail_closed_rejection_rate", "fail_closed", "case", "fail", "rejection or declared current boundary", "fail_closed", "fail_closed"),
    ("branch_gate_accuracy", "all", "case", "fail", "semantic branch oracle", "branch_gate", "branch_gate"),
)


def _applicable(result: dict, selector: str) -> bool:
    return selector == "all" or bool(result[f"{selector}_applicable"])


def build_metrics(case_results: list[dict]) -> list[dict]:
    """Build fixed metrics; per-trace metrics deduplicate on emitted trace IDs."""
    metrics: list[dict] = []
    for name, selector, aggregation, zero_policy, evidence, failure_class, key in METRIC_SPECS:
        applicable = [result for result in case_results if _applicable(result, selector)]
        if aggregation == "unique_trace":
            by_trace = {result["trace_id"]: result for result in applicable}
            applicable = [by_trace[trace_id] for trace_id in sorted(by_trace)]
        numerator = sum(bool(result[key]) for result in applicable)
        denominator = len(applicable)
        passed = numerator == denominator if denominator else zero_policy == "not_applicable_pass"
        metrics.append({
            "name": name,
            "applicable_cases": [result["case_id"] for result in applicable],
            "numerator": numerator,
            "denominator": denominator,
            "zero_denominator_policy": zero_policy,
            "evidence_source": evidence,
            "failure_class": failure_class,
            "aggregation": aggregation,
            "passed": passed,
        })
    return metrics
