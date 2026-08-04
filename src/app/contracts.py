"""Version 1.0 shared domain contracts for the synthetic SecTrace demo."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, model_validator


class IncidentCase(BaseModel):
    trace_id: str
    schema_version: Literal["1.0"]
    scenario_id: str
    severity_hint: Literal["low", "medium", "high"]
    raw_event_refs: list[str]
    tasks: list[Literal["collect_evidence", "plan_response", "audit"]]
    status: Literal["open", "analyzing", "awaiting_approval", "closed"]


class EvidenceItem(BaseModel):
    evidence_id: str
    trace_id: str
    source_ref: str
    statement: str
    classification: Literal["fact", "inference", "unknown"]
    confidence: Literal["low", "medium", "high"]
    evidence_level: Literal["insufficient", "corroborated", "strong"]
    related_event_refs: list[str]


class ResponsePlan(BaseModel):
    plan_id: str
    trace_id: str
    risk_level: Literal["low", "medium", "high"]
    actions: list[str]
    verification_steps: list[str]
    rollback_steps: list[str]
    requires_approval: bool
    status: Literal["draft", "pending_approval", "executed"]

    @model_validator(mode="after")
    def require_human_approval_for_high_risk(self) -> "ResponsePlan":
        if self.risk_level == "high" and not self.requires_approval:
            raise ValueError("high-risk response plans require human approval")
        if self.risk_level == "high" and self.status == "executed":
            raise ValueError("high-risk response plans cannot be executed in the MVP")
        return self


class ApprovalRecord(BaseModel):
    trace_id: str
    approver_role: Literal["human_operator"]
    status: Literal["not_requested", "pending", "approved", "rejected"]
    timestamp: datetime | None


class AuditBundle(BaseModel):
    trace_id: str
    evidence_refs: list[str]
    response_plan_ref: str | None
    approval_ref: str | None
    missing_requirements: list[str]
    report_markdown: str
    ledger_hash: str
