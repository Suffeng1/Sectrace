"""Safe MCP boundary over the deterministic SecTrace services."""

from __future__ import annotations

import hashlib
import json
import os
import re
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from src.agents.audit.service import AuditReview, build_audit_review
from src.agents.commander.service import build_incident
from src.agents.evidence.service import analyze_case
from src.agents.response.service import create_response_plan
from src.app.approval_verifier import ApprovalVerifier
from src.app.contracts import ApprovalRecord, EvidenceItem, IncidentCase, ResponsePlan
from src.app.ledger import AuditLedger
from src.skills.audit.verify import verify_ledger


SAFETY_NOTICE = "Synthetic exercise only; no real action has been executed."
TOOL_NAMES = (
    "sectrace.intake.create_incident",
    "sectrace.evidence.analyze_case",
    "sectrace.response.create_plan",
    "sectrace.audit.build_bundle",
    "sectrace.ledger.get_trace",
    "sectrace.ledger.log_approval",
)
STATE_SCHEMA_VERSION = "1.0"
TRACE_ID_PATTERN = re.compile(r"[A-Za-z0-9_.-]+")
RUN_ID_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,31}")
SCENARIO_ID_PATTERN = re.compile(r"S(?:0[1-9]|1[0-9]|2[0-4])")
DEFAULT_MAX_TRACES = 256


class SafeMCPAdapter:
    """Synthetic trace state used by the six side-effect-free tools."""

    def __init__(
        self,
        scenario_dir: str | Path,
        *,
        state_dir: str | Path | None = None,
        max_traces: int = DEFAULT_MAX_TRACES,
        approval_verifier: ApprovalVerifier | None = None,
    ) -> None:
        if max_traces < 1:
            raise ValueError("max_traces must be positive")
        self.scenario_dir = Path(scenario_dir).resolve()
        self.state_dir = Path(state_dir) if state_dir is not None else None
        self.max_traces = max_traces
        self.approval_verifier = approval_verifier
        self.traces: dict[str, dict] = {}
        self._lock = threading.RLock()
        self._load_persisted_traces()

    def _state_path(self, trace_id: str) -> Path:
        if self.state_dir is None or TRACE_ID_PATTERN.fullmatch(trace_id) is None:
            raise ValueError("invalid trace_id for persistence")
        return self.state_dir / f"{trace_id}.json"

    def _serialize_state(self, trace_id: str) -> dict:
        state = self.traces[trace_id]
        payload = {
            "schema_version": STATE_SCHEMA_VERSION,
            "trace_id": trace_id,
            "scenario": state["scenario"],
            "incident": state["incident"].model_dump(mode="json"),
            "ledger": list(state["ledger"].records),
        }
        if "evidence_items" in state:
            payload["evidence_items"] = [
                item.model_dump(mode="json") for item in state["evidence_items"]
            ]
            payload["risk_path"] = state["risk_path"]
        if "response_plan" in state:
            payload["response_plan"] = state["response_plan"].model_dump(mode="json")
            payload["approval"] = state["approval"].model_dump(mode="json")
        if "audit" in state:
            payload["audit"] = state["audit"].model_dump(mode="json")
        return payload

    def _deserialize_state(self, payload: dict, expected_trace_id: str) -> dict:
        if not isinstance(payload, dict):
            raise ValueError("persisted state must be an object")
        if payload.get("schema_version") != STATE_SCHEMA_VERSION:
            raise ValueError("unsupported persisted state schema")
        if payload.get("trace_id") != expected_trace_id:
            raise ValueError("persisted trace identity mismatch")
        if ("evidence_items" in payload) != ("risk_path" in payload):
            raise ValueError("persisted evidence stage is incomplete")
        if ("response_plan" in payload) != ("approval" in payload):
            raise ValueError("persisted response stage is incomplete")
        if "response_plan" in payload and "evidence_items" not in payload:
            raise ValueError("persisted response requires evidence")
        if "audit" in payload and "response_plan" not in payload:
            raise ValueError("persisted audit requires response")

        incident = IncidentCase.model_validate(payload["incident"])
        scenario = payload["scenario"]
        if not isinstance(scenario, dict):
            raise ValueError("persisted scenario must be an object")
        if incident.trace_id != expected_trace_id:
            raise ValueError("persisted incident trace mismatch")
        if scenario.get("scenario_id") != incident.scenario_id:
            raise ValueError("persisted scenario mismatch")

        records = payload["ledger"]
        if not isinstance(records, list):
            raise ValueError("persisted ledger must be a list")
        ledger_ok, _ = verify_ledger(records)
        if not ledger_ok or any(
            record.get("trace_id") != expected_trace_id for record in records
        ):
            raise ValueError("persisted ledger integrity failure")
        ledger = AuditLedger(expected_trace_id)
        ledger.records = records
        state = {"scenario": scenario, "incident": incident, "ledger": ledger}

        if "evidence_items" in payload:
            evidence_items = [
                EvidenceItem.model_validate(item) for item in payload["evidence_items"]
            ]
            if any(item.trace_id != expected_trace_id for item in evidence_items):
                raise ValueError("persisted evidence trace mismatch")
            state["evidence_items"] = evidence_items
            state["risk_path"] = payload["risk_path"]
        if "response_plan" in payload:
            response_plan = ResponsePlan.model_validate(payload["response_plan"])
            approval = ApprovalRecord.model_validate(payload["approval"])
            if (
                response_plan.trace_id != expected_trace_id
                or approval.trace_id != expected_trace_id
            ):
                raise ValueError("persisted response trace mismatch")
            state["response_plan"] = response_plan
            state["approval"] = approval
        if "audit" in payload:
            audit = AuditReview.model_validate(payload["audit"])
            if audit.trace_id != expected_trace_id:
                raise ValueError("persisted audit trace mismatch")
            state["audit"] = audit
        self._validate_state_semantics(state)
        return state

    def _validate_state_semantics(self, state: dict) -> None:
        trace_id = state["incident"].trace_id
        expected_events = [
            ("commander", "incident.created", f"incident:{trace_id}")
        ]
        if "evidence_items" in state:
            evidence_ref = "evidence:" + ",".join(
                item.evidence_id for item in state["evidence_items"]
            )
            expected_events.append(
                ("evidence", "evidence.completed", evidence_ref)
            )

        if "response_plan" in state:
            approval = state["approval"]
            plan = state["response_plan"]
            if approval.status == "not_requested":
                raise ValueError("response stage requires an approval decision state")
            expected_events.append(
                (
                    "response",
                    "response.pending_approval",
                    f"response:{plan.plan_id}",
                )
            )
            approval_events = [
                record
                for record in state["ledger"].records
                if record["event_type"].startswith("approval.")
            ]
            if approval.status == "pending":
                if approval.timestamp is not None or approval_events:
                    raise ValueError("pending approval has a decision event")
            else:
                if approval.timestamp is None or len(approval_events) != 1:
                    raise ValueError("decided approval requires one ledger event")
                event = approval_events[0]
                legacy_pattern = re.compile(
                    rf"approval:{re.escape(plan.plan_id)}:reason_sha256:[0-9a-f]{{64}}"
                )
                attested_pattern = re.compile(
                    rf"approval:{re.escape(plan.plan_id)}:event_sha256:"
                    rf"[0-9a-f]{{64}}:reason_sha256:[0-9a-f]{{64}}"
                )
                if (
                    event["actor"] != "human_operator"
                    or event["event_type"] != f"approval.{approval.status}"
                    or (
                        legacy_pattern.fullmatch(event["payload_ref"]) is None
                        and attested_pattern.fullmatch(event["payload_ref"]) is None
                    )
                    or datetime.fromisoformat(event["at"]).astimezone(timezone.utc)
                    != approval.timestamp.astimezone(timezone.utc)
                ):
                    raise ValueError(
                        "approval ledger event does not match approval state"
                    )
                expected_events.append(
                    (event["actor"], event["event_type"], event["payload_ref"])
                )

        if "audit" in state:
            expected_events.append(
                ("audit", "audit.projected", f"audit:{trace_id}")
            )

        actual_events = [
            (record["actor"], record["event_type"], record["payload_ref"])
            for record in state["ledger"].records
        ]
        if actual_events != expected_events:
            raise ValueError("persisted ledger state machine mismatch")

        if "audit" in state:
            expected_audit = build_audit_review(
                state["incident"],
                state["evidence_items"],
                state["response_plan"],
                state["approval"],
                state["ledger"].records,
            )
            if (
                state["audit"].model_dump(mode="json")
                != expected_audit.model_dump(mode="json")
            ):
                raise ValueError("persisted audit projection mismatch")

    def _load_persisted_traces(self) -> None:
        if self.state_dir is None or not self.state_dir.exists():
            return
        paths = sorted(self.state_dir.glob("*.json"))
        if len(paths) > self.max_traces:
            raise ValueError("persisted trace capacity exceeded")
        for path in paths:
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
                state = self._deserialize_state(payload, path.stem)
            except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError):
                raise ValueError(f"invalid persisted trace: {path.name}") from None
            self.traces[path.stem] = state

    def _persist_trace(self, trace_id: str) -> None:
        if self.state_dir is None:
            return
        self.state_dir.mkdir(parents=True, exist_ok=True)
        target = self._state_path(trace_id)
        temporary = target.with_name(f".{target.name}.{uuid.uuid4().hex}.tmp")
        try:
            with temporary.open("w", encoding="utf-8") as stream:
                json.dump(
                    self._serialize_state(trace_id),
                    stream,
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                )
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, target)
        finally:
            temporary.unlink(missing_ok=True)

    def _envelope(self, trace_id: str, result: object) -> dict:
        return {
            "schema_version": "1.0",
            "trace_id": trace_id,
            "result": result,
            "safety_notice": SAFETY_NOTICE,
        }

    def call_tool(self, name: str, **arguments: str) -> dict:
        with self._lock:
            return self._call_tool(name, **arguments)

    def _call_tool(self, name: str, **arguments: str) -> dict:
        if name not in TOOL_NAMES:
            raise ValueError(f"unsupported safe tool: {name}")
        if name == TOOL_NAMES[0]:
            return self._create_incident(
                arguments["scenario_id"], arguments.get("run_id")
            )

        trace_id = arguments["trace_id"]
        if trace_id not in self.traces:
            raise ValueError("unknown trace_id")
        if name == TOOL_NAMES[1]:
            return self._analyze(trace_id)
        if name == TOOL_NAMES[2]:
            return self._plan(trace_id)
        if name == TOOL_NAMES[3]:
            return self._audit(trace_id)
        if name == TOOL_NAMES[5]:
            return self._log_approval(
                trace_id=trace_id,
                decision=arguments["decision"],
                plan_ref=arguments["plan_ref"],
                approval_event_id=arguments["approval_event_id"],
            )
        return self._envelope(trace_id, list(self.traces[trace_id]["ledger"].records))

    def _create_incident(
        self, scenario_id: str, run_id: str | None = None
    ) -> dict:
        if SCENARIO_ID_PATTERN.fullmatch(scenario_id) is None:
            raise ValueError("invalid scenario_id")
        if len(self.traces) >= self.max_traces:
            raise ValueError("trace capacity reached")
        path = (self.scenario_dir / f"{scenario_id}.json").resolve()
        if path.parent != self.scenario_dir:
            raise ValueError("invalid scenario_id")
        scenario = json.loads(path.read_text(encoding="utf-8"))
        incident = build_incident(scenario)
        if run_id is not None:
            if RUN_ID_PATTERN.fullmatch(run_id) is None:
                raise ValueError("invalid run_id")
            incident = incident.model_copy(
                update={"trace_id": f"{incident.trace_id}_{run_id.lower()}"}
            )
        if incident.trace_id in self.traces:
            raise ValueError("trace already exists")
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
        self._persist_trace(incident.trace_id)
        return self._envelope(incident.trace_id, incident.model_dump(mode="json"))

    def _analyze(self, trace_id: str) -> dict:
        state = self.traces[trace_id]
        if "evidence_items" in state:
            raise ValueError("evidence stage already completed")
        items, risk_path = analyze_case(state["incident"], state["scenario"])
        state["evidence_items"] = items
        state["risk_path"] = risk_path
        state["ledger"].append(
            at=state["scenario"]["events"][-1]["at"],
            actor="evidence",
            event_type="evidence.completed",
            payload_ref="evidence:" + ",".join(item.evidence_id for item in items),
        )
        self._persist_trace(trace_id)
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
        if "response_plan" in state:
            raise ValueError("response stage already completed")
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
        self._persist_trace(trace_id)
        return self._envelope(trace_id, plan.model_dump(mode="json"))

    def _audit(self, trace_id: str) -> dict:
        state = self.traces[trace_id]
        if "response_plan" not in state:
            raise ValueError("response planning is required before audit")
        if "audit" in state:
            raise ValueError("audit stage already completed")
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
        self._persist_trace(trace_id)
        return self._envelope(trace_id, review.model_dump(mode="json"))

    def _log_approval(
        self,
        *,
        trace_id: str,
        decision: str,
        plan_ref: str,
        approval_event_id: str,
    ) -> dict:
        if trace_id not in self.traces:
            raise ValueError("unknown trace_id")
        state = self.traces[trace_id]
        if "approval" not in state:
            raise ValueError("no pending approval to log; create_plan first")
        if "audit" in state:
            raise ValueError("audit is already completed")
        if state["approval"].status != "pending":
            raise ValueError("approval is no longer pending")
        if decision not in ("approved", "rejected"):
            raise ValueError("decision must be 'approved' or 'rejected'")
        if plan_ref != state["response_plan"].plan_id:
            raise ValueError("plan_ref does not match current response plan")
        if self.approval_verifier is None:
            raise ValueError("trusted approval verification is not configured")

        verified = self.approval_verifier.verify(
            approval_event_id=approval_event_id,
            trace_id=trace_id,
            plan_ref=plan_ref,
            decision=decision,
        )
        reason_digest = hashlib.sha256(verified.reason.encode("utf-8")).hexdigest()
        decided_at = verified.decided_at
        approval = state["approval"].model_copy(
            update={
                "status": decision,
                "timestamp": decided_at,
            }
        )
        ledger_record = state["ledger"].append(
            at=decided_at.isoformat(),
            actor="human_operator",
            event_type=f"approval.{decision}",
            payload_ref=(
                f"approval:{plan_ref}:event_sha256:{verified.event_digest}:"
                f"reason_sha256:{reason_digest}"
            ),
        )
        state["approval"] = approval
        self._persist_trace(trace_id)
        return self._envelope(
            trace_id,
            {
                "approval": approval.model_dump(mode="json"),
                "ledger_record": ledger_record,
            },
        )


def create_mcp_server(
    scenario_dir: str | Path,
    *,
    state_dir: str | Path | None = None,
    approval_verifier: ApprovalVerifier | None = None,
) -> FastMCP:
    """Create an MCP server exposing exactly the six documented safe tools."""
    adapter = SafeMCPAdapter(
        scenario_dir,
        state_dir=state_dir,
        approval_verifier=approval_verifier,
    )
    server = FastMCP("SecTrace Safe Tools")

    @server.tool(name=TOOL_NAMES[0])
    def create_incident(scenario_id: str, run_id: str | None = None) -> dict:
        return adapter.call_tool(
            TOOL_NAMES[0], scenario_id=scenario_id, run_id=run_id
        )

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

    @server.tool(name=TOOL_NAMES[5])
    def log_approval(
        trace_id: str,
        decision: str,
        plan_ref: str,
        approval_event_id: str,
    ) -> dict:
        return adapter.call_tool(
            TOOL_NAMES[5],
            trace_id=trace_id,
            decision=decision,
            plan_ref=plan_ref,
            approval_event_id=approval_event_id,
        )

    return server
