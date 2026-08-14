import json
import hashlib
from collections import UserDict
from copy import deepcopy
from math import inf, nan
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from src.agents.audit.service import INVALID_AUDIT_INPUT_ERROR, build_audit_review
from src.app.contracts import ApprovalRecord, EvidenceItem, IncidentCase, ResponsePlan


SKILL_ROOT = Path(__file__).parents[3] / "src" / "skills" / "audit"


def _read(relative_path: str) -> dict:
    return json.loads((SKILL_ROOT / relative_path).read_text(encoding="utf-8"))


def _models(payload: dict) -> tuple[IncidentCase, list[EvidenceItem], ResponsePlan | None, ApprovalRecord | None, list[dict[str, str]]]:
    return (
        IncidentCase.model_validate(payload["incident"]),
        [EvidenceItem.model_validate(item) for item in payload["evidence_items"]],
        ResponsePlan.model_validate(payload["response_plan"]) if payload["response_plan"] is not None else None,
        ApprovalRecord.model_validate(payload["approval"]) if payload["approval"] is not None else None,
        payload["ledger_records"],
    )


def test_golden_pair_conforms_and_is_deterministic() -> None:
    payload = _read("fixtures/golden-approved-chain.json")
    expected = _read("fixtures/golden-approved-chain.review.json")
    assert not list(Draft202012Validator(_read("schema/input.schema.json")).iter_errors(payload))

    review = build_audit_review(*_models(payload))

    serialized = review.model_dump(mode="json")
    assert serialized == expected
    assert not list(Draft202012Validator(_read("schema/output.schema.json")).iter_errors(serialized))
    assert build_audit_review(*_models(deepcopy(payload))).model_dump(mode="json") == expected


def test_pending_approval_and_bad_ledger_reference_fail_closed() -> None:
    payload = _read("fixtures/golden-approved-chain.json")
    payload["approval"]["status"] = "pending"
    payload["approval"]["timestamp"] = None
    review = build_audit_review(*_models(payload))
    assert review.audit_status == "not_qualified"
    assert "approval.required" in review.missing_requirements

    payload = _read("fixtures/golden-approved-chain.json")
    payload["ledger_records"][2]["payload_ref"] = "response:wrong"
    review = build_audit_review(*_models(payload))
    assert review.audit_status == "not_qualified"
    assert "ledger.integrity" in review.missing_requirements


@pytest.mark.parametrize("response_present,approval_status", [(False, None), (True, "rejected")])
def test_missing_or_rejected_high_risk_chain_is_not_qualified(response_present: bool, approval_status: str | None) -> None:
    payload = _read("fixtures/golden-approved-chain.json")
    if not response_present:
        payload["response_plan"] = None
        payload["approval"] = None
    else:
        payload["approval"]["status"] = approval_status
    review = build_audit_review(*_models(payload))
    assert review.audit_status == "not_qualified"


def test_rehashed_reference_mismatch_is_not_qualified_without_hash_failure() -> None:
    payload = _read("fixtures/golden-approved-chain.json")
    records = payload["ledger_records"]
    records[2]["payload_ref"] = "response:wrong"
    previous = ""
    for record in records:
        record["prev_hash"] = previous
        unsigned = {key: value for key, value in record.items() if key != "hash"}
        canonical = json.dumps(unsigned, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        record["hash"] = hashlib.sha256(previous.encode("utf-8") + canonical).hexdigest()
        previous = record["hash"]
    review = build_audit_review(*_models(payload))
    assert review.integrity_check == "passed"
    assert "ledger.references" in review.missing_requirements


@pytest.mark.parametrize("mutation", ["tampered", "order"])
def test_badcase_ledger_shapes_and_order_are_not_qualified(mutation: str) -> None:
    payload = _read("fixtures/golden-approved-chain.json")
    records = payload["ledger_records"]
    if mutation == "tampered":
        records[1]["payload_ref"] = "evidence:tampered"
    else:
        records[1], records[2] = records[2], records[1]
    incident, items, plan, approval, ledger = _models(payload)
    review = build_audit_review(incident, items, plan, approval, ledger)
    assert review.audit_status == "not_qualified"
    assert review.integrity_check == "failed"


def test_raw_mappings_and_pydantic_shape_bypasses_have_one_fixed_error() -> None:
    payload = _read("fixtures/golden-approved-chain.json")
    incident, items, plan, approval, ledger = _models(payload)
    injected = incident.model_copy()
    injected.__dict__["undeclared"] = "synthetic"

    for candidate in ({}, injected, [incident], True):
        with pytest.raises(ValueError, match=INVALID_AUDIT_INPUT_ERROR):
            build_audit_review(candidate, items, plan, approval, ledger)  # type: ignore[arg-type]


@pytest.mark.parametrize("value", [nan, inf, -inf])
def test_nonfinite_pydantic_bypasses_fail_with_one_error(value: float) -> None:
    payload = _read("fixtures/golden-approved-chain.json")
    incident, items, plan, approval, ledger = _models(payload)
    for item in (
        items[0].model_copy(update={"statement": value}),
        EvidenceItem.model_construct(**{**items[0].model_dump(), "confidence": value}),
    ):
        with pytest.raises(ValueError, match=f"^{INVALID_AUDIT_INPUT_ERROR}$"):
            build_audit_review(incident, [item], plan, approval, ledger)


def test_hostile_and_nonplain_ledger_containers_have_one_error() -> None:
    payload = _read("fixtures/golden-approved-chain.json")
    incident, items, plan, approval, ledger = _models(payload)
    for candidate in (
        UserDict({"records": ledger}),
        [UserDict(record) for record in ledger],
        [object()],
    ):
        with pytest.raises(ValueError, match=f"^{INVALID_AUDIT_INPUT_ERROR}$"):
            build_audit_review(incident, items, plan, approval, candidate)  # type: ignore[arg-type]


def test_duplicate_or_ambiguous_evidence_references_fail_before_qualification() -> None:
    payload = _read("fixtures/golden-approved-chain.json")
    incident, items, plan, approval, ledger = _models(payload)
    duplicate = items[0].model_copy()
    for candidate in ([items[0], duplicate], [items[0], items[0].model_copy(update={"source_ref": items[0].evidence_id, "related_event_refs": [items[0].evidence_id]})]):
        with pytest.raises(ValueError, match=f"^{INVALID_AUDIT_INPUT_ERROR}$"):
            build_audit_review(incident, candidate, plan, approval, ledger)


def test_evidence_ids_are_disjoint_from_incident_and_related_references() -> None:
    payload = _read("fixtures/golden-approved-chain.json")
    incident, items, plan, approval, ledger = _models(payload)
    assert plan is not None and approval is not None
    incident = incident.model_copy(update={"raw_event_refs": ["evt_first", "evt_second", "evt_related"]})
    first = items[0].model_copy(update={"evidence_id": "ev_first", "source_ref": "evt_first", "related_event_refs": ["evt_first", "evt_related"]})
    benign = items[0].model_copy(update={"evidence_id": "ev_second", "source_ref": "evt_second", "related_event_refs": ["evt_second"]})
    assert build_audit_review(incident, [first, benign], plan, approval, ledger).audit_status == "not_qualified"

    incident_collision = benign.model_copy(update={"evidence_id": "evt_first"})
    related_collision = benign.model_copy(update={"evidence_id": "evt_related"})
    for candidate in (incident_collision, related_collision):
        with pytest.raises(ValueError, match=f"^{INVALID_AUDIT_INPUT_ERROR}$"):
            build_audit_review(incident, [first, candidate], plan, approval, ledger)


def test_packaged_badcase_itself_fails_closed() -> None:
    payload = _read("fixtures/golden-approved-chain.json")
    payload["ledger_records"] = _read("fixtures/badcase-ledger.json")["ledger_records"]
    review = build_audit_review(*_models(payload))
    assert review.audit_status == "not_qualified"
    assert review.integrity_check == "failed"


def test_strict_schemas_reject_contract_mutations_and_nullable_inputs() -> None:
    payload = _read("fixtures/golden-approved-chain.json")
    schema = Draft202012Validator(_read("schema/input.schema.json"))
    assert not list(schema.iter_errors(payload))
    nullable = deepcopy(payload)
    nullable["response_plan"] = None
    nullable["approval"] = None
    assert not list(schema.iter_errors(nullable))
    for mutation in (
        lambda value: value["incident"].clear(),
        lambda value: value["incident"].update({"unknown": "synthetic"}),
        lambda value: value["incident"].update({"severity_hint": "critical"}),
        lambda value: value["evidence_items"].append(deepcopy(value["evidence_items"][0])),
    ):
        candidate = deepcopy(payload)
        mutation(candidate)
        assert list(schema.iter_errors(candidate))


def test_forged_review_is_not_an_authoritative_callable_input() -> None:
    payload = _read("fixtures/golden-approved-chain.json")
    rebuilt = build_audit_review(*_models(payload))
    forged = rebuilt.model_copy(update={"ledger_hash": "0" * 64})
    assert forged != rebuilt
    assert build_audit_review(*_models(payload)) == rebuilt
