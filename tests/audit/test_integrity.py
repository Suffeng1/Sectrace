from tests.audit.test_service import approved, evidence, high_risk_plan, incident, valid_ledger

from src.agents.audit.service import build_audit_review


def test_tampered_hash_is_a_failed_not_qualified_review() -> None:
    records = valid_ledger()
    records[0]["payload_ref"] = "incident:tampered"

    review = build_audit_review(
        incident(), [evidence()], high_risk_plan(), approved(), records
    )

    assert review.integrity_check == "failed"
    assert review.audit_status == "not_qualified"
    assert "ledger.integrity" in review.missing_requirements
    assert review.ledger_hash == ""

