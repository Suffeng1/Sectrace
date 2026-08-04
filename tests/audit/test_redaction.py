from tests.audit.test_service import approved, evidence, high_risk_plan, incident, valid_ledger

from src.agents.audit.service import build_audit_review


def test_report_redacts_credential_like_payload_values() -> None:
    records = valid_ledger()
    sensitive_value = "synthetic-sensitive-value"
    records[1]["payload_ref"] = "credential:" + sensitive_value

    review = build_audit_review(
        incident(), [evidence()], high_risk_plan(), approved(), records
    )

    assert sensitive_value not in review.report_markdown
    assert "[REDACTED]" in review.report_markdown
