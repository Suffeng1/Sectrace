from datetime import datetime, timezone
from hashlib import sha256

from src.app.approval_verifier import VerifiedApproval


APPROVAL_EVENT_ID = "$synthetic-verified-approval"


class StaticApprovalVerifier:
    def __init__(self, reason: str = "synthetic human approval") -> None:
        self.reason = reason

    def verify(
        self,
        *,
        approval_event_id: str,
        trace_id: str,
        plan_ref: str,
        decision: str,
    ) -> VerifiedApproval:
        if approval_event_id != APPROVAL_EVENT_ID:
            raise ValueError("approval event is not authorized")
        assert trace_id
        assert plan_ref
        assert decision in {"approved", "rejected"}
        return VerifiedApproval(
            decided_at=datetime(2026, 8, 11, 8, 30, tzinfo=timezone.utc),
            reason=self.reason,
            event_digest=sha256(approval_event_id.encode("utf-8")).hexdigest(),
        )
