from collections.abc import Mapping
from itertools import product
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from src.agents.commander.service import build_incident
from src.agents.evidence.service import analyze_case
from src.agents.response.service import create_response_plan
from src.app.contracts import EvidenceItem
from src.skills.response.plan import has_corroborated_risk


SKILL_ROOT = Path(__file__).parents[3] / "src" / "skills" / "response"
_INVALID_EVIDENCE = "invalid response evidence"


class _RelatedRefsList(list):
    pass


class _RelatedRefsIterable:
    def __iter__(self):
        return iter(("evt_s01_001",))


def _read_json(relative_path: str) -> object:
    return json.loads((SKILL_ROOT / relative_path).read_text(encoding="utf-8"))


def _validate(instance: object, schema_path: str) -> None:
    errors = list(Draft202012Validator(_read_json(schema_path)).iter_errors(instance))
    assert not errors, errors


def _items(payload: object | None = None) -> list[EvidenceItem]:
    source = payload if payload is not None else _read_json("fixtures/golden-s01.evidence.json")
    assert isinstance(source, list)
    return [EvidenceItem.model_validate(item) for item in source]


def _output(plan: object) -> dict[str, object]:
    return plan.model_dump(mode="json")  # type: ignore[union-attr]


def test_golden_fixture_conforms_to_executable_response_contract() -> None:
    payload = _read_json("fixtures/golden-s01.evidence.json")
    expected = _read_json("fixtures/golden-s01.plan.json")

    _validate(payload, "schema/input.schema.json")
    plan = create_response_plan(_items(payload))
    _validate(_output(plan), "schema/output.schema.json")

    assert _output(plan) == expected


def test_low_risk_evidence_preserves_existing_draft_semantics() -> None:
    evidence = EvidenceItem(
        evidence_id="ev_s05_001",
        trace_id="tr_s05",
        source_ref="evt_s05_001",
        statement="无法确认存在完整风险路径；当前证据不足。",
        classification="unknown",
        confidence="low",
        evidence_level="insufficient",
        related_event_refs=["evt_s05_001"],
    )

    plan = create_response_plan([evidence])

    assert plan.risk_level == "low"
    assert plan.requires_approval is False
    assert plan.status == "draft"
    assert plan.status != "executed"
    assert all(action.startswith("建议：") for action in plan.actions)


@pytest.mark.parametrize("levels", list(product(("strong", "corroborated"), repeat=3)))
def test_every_legal_high_risk_variant_stays_advice_only_pending_approval(
    levels: tuple[str, str, str],
) -> None:
    items = [item.model_copy(update={"evidence_level": level}) for item, level in zip(_items(), levels)]

    plan = create_response_plan(items)

    assert plan.risk_level == "high"
    assert plan.requires_approval is True
    assert plan.status == "pending_approval"
    assert plan.status != "executed"
    assert all(action.startswith("建议：") for action in plan.actions)


def test_empty_evidence_has_the_fixed_nonleaking_error() -> None:
    with pytest.raises(ValueError) as error:
        create_response_plan([])
    assert str(error.value) == _INVALID_EVIDENCE


@pytest.mark.parametrize(
    "field_path",
    [
        (0, "extra"),
        (0, "source_path"),
        (0, "api_key"),
        (0, "real_data"),
    ],
)
def test_extra_sensitive_or_real_data_fields_are_schema_and_callable_rejected(
    field_path: tuple[object, ...],
) -> None:
    payload = _read_json("fixtures/golden-s01.evidence.json")
    assert isinstance(payload, list)
    payload[field_path[0]][field_path[1]] = True  # type: ignore[index]

    assert list(Draft202012Validator(_read_json("schema/input.schema.json")).iter_errors(payload))
    with pytest.raises(ValueError) as error:
        create_response_plan(payload)  # type: ignore[arg-type]
    assert str(error.value) == _INVALID_EVIDENCE


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("evidence_id", "e" * 129),
        ("trace_id", "bad trace"),
        ("source_ref", "s" * 129),
        ("statement", "x" * 513),
        ("classification", "unsupported"),
        ("classification", []),
        ("confidence", {}),
        ("evidence_level", None),
    ],
)
def test_schema_and_callable_fail_closed_on_bounds_enums_and_types(field: str, value: object) -> None:
    payload = _read_json("fixtures/golden-s01.evidence.json")
    assert isinstance(payload, list)
    payload[0][field] = value

    assert list(Draft202012Validator(_read_json("schema/input.schema.json")).iter_errors(payload))
    candidate = _items()[0].model_copy(update={field: value})
    with pytest.raises(ValueError) as error:
        create_response_plan([candidate])
    assert str(error.value) == _INVALID_EVIDENCE


@pytest.mark.parametrize(
    "value_factory",
    [
        lambda: "API" + "_KEY=" + "synthetic-value",
        lambda: "C:" + "/" + "Users" + "/" + "example" + "/" + "artifact.txt",
        lambda: "TeMp" + "/" + "artifact.txt",
    ],
)
def test_free_text_secret_or_path_values_are_schema_and_callable_rejected(value_factory) -> None:
    payload = _read_json("fixtures/golden-s01.evidence.json")
    assert isinstance(payload, list)
    payload[0]["statement"] = value_factory()

    assert list(Draft202012Validator(_read_json("schema/input.schema.json")).iter_errors(payload))
    with pytest.raises(ValueError) as error:
        create_response_plan(_items(payload))
    assert str(error.value) == _INVALID_EVIDENCE


@pytest.mark.parametrize(
    "value_factory",
    [
        lambda: "ordinary text " + "C:" + chr(92) + "Users" + chr(92) + "synthetic",
        lambda: "ordinary text /" + "var/tmp/synthetic",
        lambda: "ordinary text TeMp" + chr(92) + "synthetic",
    ],
)
def test_embedded_path_tokens_are_schema_and_callable_rejected(value_factory) -> None:
    payload = _read_json("fixtures/golden-s01.evidence.json")
    assert isinstance(payload, list)
    payload[0]["statement"] = value_factory()

    assert list(Draft202012Validator(_read_json("schema/input.schema.json")).iter_errors(payload))
    with pytest.raises(ValueError) as error:
        create_response_plan(_items(payload))
    assert str(error.value) == _INVALID_EVIDENCE


def test_trace_and_reference_continuity_and_duplicates_fail_closed() -> None:
    items = _items()
    mismatched_trace = items[1].model_copy(update={"trace_id": "tr_other"})
    duplicate_source = items[1].model_copy(update={"source_ref": items[0].source_ref})
    missing_source_link = items[1].model_copy(update={"related_event_refs": [items[0].source_ref]})

    for candidate in ([items[0], mismatched_trace], [items[0], duplicate_source], [items[0], missing_source_link]):
        with pytest.raises(ValueError) as error:
            create_response_plan(candidate)
        assert str(error.value) == _INVALID_EVIDENCE


def test_pydantic_bypasses_with_missing_or_extra_fields_fail_closed() -> None:
    item = _items()[0]
    missing_statement = EvidenceItem.model_construct(
        **{key: value for key, value in item.model_dump(mode="python").items() if key != "statement"}
    )
    injected_extra = item.model_copy()
    injected_extra.__dict__["undeclared"] = "synthetic"
    injected_pydantic_extra = item.model_copy()
    object.__setattr__(injected_pydantic_extra, "__pydantic_extra__", {"undeclared": "synthetic"})

    for candidate in ([missing_statement], [injected_extra], [injected_pydantic_extra]):
        with pytest.raises(ValueError) as error:
            create_response_plan(candidate)
        assert str(error.value) == _INVALID_EVIDENCE


def test_pydantic_internal_metadata_shape_is_checked_before_serialization() -> None:
    item = _items()[0]
    all_fields = set(item.model_dump(mode="python"))
    empty_fields_set = item.model_copy()
    object.__setattr__(empty_fields_set, "__pydantic_fields_set__", set())
    wrong_type_fields_set = item.model_copy()
    object.__setattr__(wrong_type_fields_set, "__pydantic_fields_set__", frozenset(all_fields))
    overdeclared_fields_set = item.model_copy()
    object.__setattr__(overdeclared_fields_set, "__pydantic_fields_set__", all_fields | {"undeclared"})
    empty_private = item.model_copy()
    object.__setattr__(empty_private, "__pydantic_private__", {})
    populated_private = item.model_copy()
    object.__setattr__(populated_private, "__pydantic_private__", {"injected": "synthetic"})
    empty_extra = item.model_copy()
    object.__setattr__(empty_extra, "__pydantic_extra__", {})

    for candidate in (
        empty_fields_set,
        wrong_type_fields_set,
        overdeclared_fields_set,
        empty_private,
        populated_private,
        empty_extra,
    ):
        with pytest.raises(ValueError) as error:
            create_response_plan([candidate])
        assert str(error.value) == _INVALID_EVIDENCE


def test_normal_pydantic_validate_copy_and_construct_controls_remain_accepted() -> None:
    item = _items()[0]
    constructed = EvidenceItem.model_construct(**item.model_dump(mode="python"))

    for candidate in (item, item.model_copy(), constructed):
        plan = create_response_plan([candidate])
        assert plan.status == "pending_approval"
        assert plan.requires_approval is True


def test_evidence_source_bijection_and_cross_namespace_collisions_fail_closed() -> None:
    items = _items()
    duplicate_evidence = items[1].model_copy(update={"evidence_id": items[0].evidence_id})
    duplicate_source = items[1].model_copy(update={"source_ref": items[0].source_ref})
    evidence_id_matches_other_source = items[1].model_copy(update={"evidence_id": items[0].source_ref})
    source_matches_other_evidence = items[1].model_copy(
        update={"source_ref": items[0].evidence_id, "related_event_refs": [items[0].evidence_id]}
    )

    for candidate in (
        [items[0], duplicate_evidence],
        [items[0], duplicate_source],
        [items[0], evidence_id_matches_other_source],
        [items[0], source_matches_other_evidence],
    ):
        with pytest.raises(ValueError) as error:
            create_response_plan(candidate)
        assert str(error.value) == _INVALID_EVIDENCE

    assert create_response_plan(items).status == "pending_approval"


def test_same_item_evidence_source_namespace_overlap_fails_closed() -> None:
    item = _items()[0]
    overlapping = item.model_copy(
        update={"source_ref": item.evidence_id, "related_event_refs": [item.evidence_id]}
    )

    with pytest.raises(ValueError) as error:
        create_response_plan([overlapping])
    assert str(error.value) == _INVALID_EVIDENCE


@pytest.mark.parametrize(
    "related_refs",
    [
        ("evt_s01_001",),
        _RelatedRefsList(["evt_s01_001"]),
        _RelatedRefsIterable(),
    ],
)
def test_raw_related_references_require_an_exact_builtin_list(related_refs: object) -> None:
    item = _items()[0].model_copy(update={"related_event_refs": related_refs})

    with pytest.raises(ValueError) as error:
        create_response_plan([item])
    assert str(error.value) == _INVALID_EVIDENCE


@pytest.mark.parametrize("related_refs", [[True], ["r" * 129]])
def test_raw_related_reference_elements_require_exact_bounded_strings(related_refs: list[object]) -> None:
    item = _items()[0].model_copy(update={"related_event_refs": related_refs})

    with pytest.raises(ValueError) as error:
        create_response_plan([item])
    assert str(error.value) == _INVALID_EVIDENCE


def test_missing_nested_fields_and_capacity_fail_closed() -> None:
    payload = _read_json("fixtures/golden-s01.evidence.json")
    assert isinstance(payload, list)
    payload[0].pop("related_event_refs")
    assert list(Draft202012Validator(_read_json("schema/input.schema.json")).iter_errors(payload))
    with pytest.raises(ValueError) as error:
        create_response_plan(payload)  # type: ignore[arg-type]
    assert str(error.value) == _INVALID_EVIDENCE

    item = _items()[0]
    oversized = [
        item.model_copy(
            update={
                "evidence_id": f"ev_{index}",
                "source_ref": f"evt_{index}",
                "related_event_refs": [f"evt_{index}"],
            }
        )
        for index in range(17)
    ]
    with pytest.raises(ValueError) as error:
        create_response_plan(oversized)
    assert str(error.value) == _INVALID_EVIDENCE


def test_bool_nan_and_hostile_mapping_never_leak_raw_exceptions() -> None:
    item = _items()[0]
    bad_boolean = item.model_copy(update={"statement": True})
    bad_nan = item.model_copy(update={"statement": float("nan")})
    bad_infinity = item.model_copy(update={"statement": float("inf")})

    for candidate in ([bad_boolean], [bad_nan], [bad_infinity], _HostileMapping()):
        with pytest.raises(ValueError) as error:
            create_response_plan(candidate)  # type: ignore[arg-type]
        assert str(error.value) == _INVALID_EVIDENCE


def test_input_is_not_mutated_and_plans_are_deterministic() -> None:
    items = _items()
    before = [item.model_dump(mode="json") for item in items]

    first = create_response_plan(items)
    second = create_response_plan(items)

    assert [item.model_dump(mode="json") for item in items] == before
    assert first == second
    assert first.trace_id == items[0].trace_id
    assert first.plan_id == f"rp_{items[0].trace_id}"
    assert has_corroborated_risk(items) is True


def test_s01_to_s24_traversal_preserves_response_safety_without_an_oracle_selector() -> None:
    scenario_dir = Path(__file__).parents[3] / "data" / "scenarios"
    rejected = 0
    plans = []
    for path in sorted(scenario_dir.glob("S*.json")):
        scenario = json.loads(path.read_text(encoding="utf-8"))
        try:
            incident = build_incident(scenario)
            evidence_items, _ = analyze_case(incident, scenario)
        except ValueError:
            rejected += 1
            continue
        plans.append(create_response_plan(evidence_items))

    assert rejected == 4
    assert len(plans) == 20
    assert sum(plan.risk_level == "high" for plan in plans) == 6
    assert sum(plan.risk_level == "low" for plan in plans) == 14
    assert all(plan.status != "executed" for plan in plans)


def test_badcase_raw_mapping_is_schema_shaped_but_rejected_before_output() -> None:
    badcase = _read_json("fixtures/badcase-raw-mapping.json")

    assert list(Draft202012Validator(_read_json("schema/input.schema.json")).iter_errors(badcase))
    with pytest.raises(ValueError) as error:
        create_response_plan(badcase)  # type: ignore[arg-type]
    assert str(error.value) == _INVALID_EVIDENCE


def test_output_schema_rejects_execution_approval_type_and_extra_fields() -> None:
    output = _output(create_response_plan(_items()))
    invalid_outputs = []
    executed = dict(output)
    executed["status"] = "executed"
    invalid_outputs.append(executed)
    unapproved = dict(output)
    unapproved["requires_approval"] = False
    invalid_outputs.append(unapproved)
    bool_as_int = dict(output)
    bool_as_int["requires_approval"] = 1
    invalid_outputs.append(bool_as_int)
    extra = dict(output)
    extra["execution_ref"] = "none"
    invalid_outputs.append(extra)

    validator = Draft202012Validator(_read_json("schema/output.schema.json"))
    assert all(list(validator.iter_errors(candidate)) for candidate in invalid_outputs)


class _HostileMapping(Mapping):
    def __getitem__(self, key: object) -> object:
        raise KeyError(key)

    def __iter__(self):
        return iter([[]])

    def __len__(self) -> int:
        return 1
