"""Safe MCP boundary over the deterministic SecTrace services."""

from __future__ import annotations

import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from src.agents.audit.service import build_audit_review
from src.agents.commander.service import build_incident
from src.agents.evidence.service import analyze_case
from src.agents.response.service import create_response_plan
from src.app.contracts import ApprovalRecord
from src.app.ledger import AuditLedger


SAFETY_NOTICE = "Synthetic exercise only; no real action has been executed."
TOOL_NAMES = (
    "sectrace.intake.create_incident",
    "sectrace.evidence.analyze_case",
    "sectrace.response.create_plan",
    "sectrace.audit.build_bundle",
    "sectrace.ledger.get_trace",
)


class SafeMCPAdapter:
    """In-memory synthetic trace state used by the five side-effect-free tools."""

    def __init__(self, scenario_dir: str | Path) -> None:
        self.scenario_dir = Path(scenario_dir)
        self.traces: dict[str, dict] = {}

    def _envelope(self, trace_id: str, result: object) -> dict:
        return {
            "schema_version": "1.0",
            "trace_id": trace_id,
            "result": result,
            "safety_notice": SAFETY_NOTICE,
        }

    def call_tool(self, name: str, **arguments: str) -> dict:
        if name not in TOOL_NAMES:
            raise ValueError(f"unsupported safe tool: {name}")
        if name == TOOL_NAMES[0]:
            return self._create_incident(arguments["scenario_id"])

        trace_id = arguments["trace_id"]
        if trace_id not in self.traces:
            raise ValueError("unknown trace_id")
        if name == TOOL_NAMES[1]:
            return self._analyze(trace_id)
        if name == TOOL_NAMES[2]:
            return self._plan(trace_id)
        if name == TOOL_NAMES[3]:
            return self._audit(trace_id)
        return self._envelope(trace_id, list(self.traces[trace_id]["ledger"].records))

    def _create_incident(self, scenario_id: str) -> dict:
        path = self.scenario_dir / f"{scenario_id}.json"
        scenario = json.loads(path.read_text(encoding="utf-8"))
        incident = build_incident(scenario)
        ledger = AuditLedger(incident.trace_id)
        ledger.append(
            at=scenario["events"][-1]["at"],
            actor="commander",
            event_type="incident.created",
            payload_ref=f"incident:{incident.trace_id}",
        )
        self.traces[incident.trace_id] = {
            "scenario": scenario,
            "incident": incident,
            "ledger": ledger,
        }
        return self._envelope(incident.trace_id, incident.model_dump(mode="json"))

    def _analyze(self, trace_id: str) -> dict:
        state = self.traces[trace_id]
        items, risk_path = analyze_case(state["incident"], state["scenario"])
        state["evidence_items"] = items
        state["risk_path"] = risk_path
        state["ledger"].append(
            at=state["scenario"]["events"][-1]["at"],
            actor="evidence",
            event_type="evidence.completed",
            payload_ref="evidence:" + ",".join(item.evidence_id for item in items),
        )
        return self._envelope(
            trace_id,
            {
                "evidence_items": [item.model_dump(mode="json") for item in items],
                "risk_path": risk_path,
            },
        )

    def _plan(self, trace_id: str) -> dict:
        state = self.traces[trace_id]
        if "evidence_items" not in state:
            raise ValueError("evidence analysis is required before response planning")
        plan = create_response_plan(state["evidence_items"])
        state["response_plan"] = plan
        state["approval"] = ApprovalRecord(
            trace_id=trace_id,
            approver_role="human_operator",
            status="pending",
            timestamp=None,
        )
        state["ledger"].append(
            at=state["scenario"]["events"][-1]["at"],
            actor="response",
            event_type="response.pending_approval",
            payload_ref=f"response:{plan.plan_id}",
        )
        return self._envelope(trace_id, plan.model_dump(mode="json"))

    def _audit(self, trace_id: str) -> dict:
        state = self.traces[trace_id]
        if "response_plan" not in state:
            raise ValueError("response planning is required before audit")
        state["ledger"].append(
            at=state["scenario"]["events"][-1]["at"],
            actor="audit",
            event_type="audit.projected",
            payload_ref=f"audit:{trace_id}",
        )
        review = build_audit_review(
            state["incident"],
            state["evidence_items"],
            state["response_plan"],
            state["approval"],
            state["ledger"].records,
        )
        state["audit"] = review
        return self._envelope(trace_id, review.model_dump(mode="json"))


def create_mcp_server(scenario_dir: str | Path) -> FastMCP:
    """Create an MCP server exposing exactly the five documented safe tools."""
    adapter = SafeMCPAdapter(scenario_dir)
    server = FastMCP("SecTrace Safe Tools")

    @server.tool(name=TOOL_NAMES[0])
    def create_incident(scenario_id: str) -> dict:
        return adapter.call_tool(TOOL_NAMES[0], scenario_id=scenario_id)

    @server.tool(name=TOOL_NAMES[1])
    def analyze_case(trace_id: str) -> dict:
        return adapter.call_tool(TOOL_NAMES[1], trace_id=trace_id)

    @server.tool(name=TOOL_NAMES[2])
    def create_plan(trace_id: str) -> dict:
        return adapter.call_tool(TOOL_NAMES[2], trace_id=trace_id)

    @server.tool(name=TOOL_NAMES[3])
    def build_bundle(trace_id: str) -> dict:
        return adapter.call_tool(TOOL_NAMES[3], trace_id=trace_id)

    @server.tool(name=TOOL_NAMES[4])
    def get_trace(trace_id: str) -> dict:
        return adapter.call_tool(TOOL_NAMES[4], trace_id=trace_id)

    return server
