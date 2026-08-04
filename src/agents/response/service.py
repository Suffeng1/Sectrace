"""Advice-only response planning for synthetic SecTrace evidence."""

from src.app.contracts import EvidenceItem, ResponsePlan
from src.skills.response.plan import has_corroborated_risk


def create_response_plan(evidence_items: list[EvidenceItem]) -> ResponsePlan:
    """Create a deterministic plan without executing or simulating any action."""
    if not evidence_items:
        raise ValueError("response planning requires supplied evidence")
    trace_ids = {item.trace_id for item in evidence_items}
    if len(trace_ids) != 1:
        raise ValueError("response evidence must share one trace_id")

    trace_id = trace_ids.pop()
    if has_corroborated_risk(evidence_items):
        return ResponsePlan(
            plan_id=f"rp_{trace_id}",
            trace_id=trace_id,
            risk_level="high",
            actions=[
                "建议：在人工审批后限制受影响合成账号的高风险会话。",
                "建议：保全当前合成证据并核验受影响范围。",
                "建议：在验证完成后恢复经确认的正常访问并记录审批结果。",
                "建议：复核最小权限与异常访问监测规则。",
            ],
            verification_steps=[
                "核对每项建议均引用当前 trace_id 的已提供证据。",
                "确认高风险建议仍处于人工审批等待状态。",
            ],
            rollback_steps=[
                "若人工审批后实施限制产生误判，建议恢复审批前的合成账号状态。",
                "建议保留审批与回滚记录供独立审计复核。",
            ],
            requires_approval=True,
            status="pending_approval",
        )

    return ResponsePlan(
        plan_id=f"rp_{trace_id}",
        trace_id=trace_id,
        risk_level="low",
        actions=[
            "建议：当前证据不足，无法确认高风险事件；先补充同一 trace_id 的合成证据。",
            "建议：在获得可核验来源前仅保持观察，不提出高风险处置。",
        ],
        verification_steps=["复核新增证据的来源、分类与置信度后再评估风险。"],
        rollback_steps=["无需回滚；当前计划不包含任何执行动作。"],
        requires_approval=False,
        status="draft",
    )

