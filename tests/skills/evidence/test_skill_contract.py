from copy import deepcopy
from collections.abc import Mapping
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from src.agents.commander.service import build_incident
from src.agents.evidence.service import analyze_case


SKILL_ROOT = Path(__file__).parents[3] / "src" / "skills" / "evidence"
_INVALID_PAYLOAD = "invalid evidence payload"
_REAL_DATA_ERROR = "evidence analysis accepts synthetic or de-identified data only"


def _read_json(relative_path: str) -> dict:
    return json.loads((SKILL_ROOT / relative_path).read_text(encoding="utf-8"))


def _validate(instance: object, schema_path: str) -> None:
    errors = list(
        Draft202012Validator(
            _read_json(schema_path), format_checker=FormatChecker()
        ).iter_errors(instance)
    )
    assert not errors, errors


def _input(scenario: dict | None = None) -> tuple[object, dict]:
    scenario = scenario or _read_json("fixtures/golden-s01.json")
    return build_incident(scenario), scenario


def _schema_input(incident: object, scenario: dict) -> dict:
    return {"incident": incident.model_dump(mode="json"), "scenario": scenario}


def _schema_output(evidence_items: list[object], risk_path: list[str]) -> dict:
    return {
        "evidence_items": [item.model_dump(mode="json") for item in evidence_items],
        "risk_path": risk_path,
    }


def test_golden_fixture_conforms_to_the_executable_evidence_contract() -> None:
    scenario = _read_json("fixtures/golden-s01.json")
    expected = _read_json("fixtures/golden-s01.output.json")
    incident, scenario = _input(scenario)

    _validate(_schema_input(incident, scenario), "schema/input.schema.json")
    evidence_items, risk_path = analyze_case(incident, scenario)
    output = _schema_output(evidence_items, risk_path)
    _validate(output, "schema/output.schema.json")

    assert output == expected


@pytest.mark.parametrize(
    "field_path",
    [
        ("source_path",),
        ("events", 0, "path"),
        ("events", 0, "api_key"),
        ("expected", "operator_token"),
        ("unknown",),
    ],
)
def test_extra_or_sensitive_looking_scenario_fields_are_schema_and_callable_rejected(
    field_path: tuple[object, ...],
) -> None:
    incident, scenario = _input()
    target = scenario
    for part in field_path[:-1]:
        target = target[part]
    target[field_path[-1]] = "synthetic-value"

    assert list(
        Draft202012Validator(_read_json("schema/input.schema.json"), format_checker=FormatChecker()).iter_errors(
            _schema_input(incident, scenario)
        )
    )
    with pytest.raises(ValueError) as error:
        analyze_case(incident, scenario)
    assert str(error.value) == _INVALID_PAYLOAD


@pytest.mark.parametrize(
    ("field_path", "value"),
    [
        (("scenario_id",), "s" * 65),
        (("events", 0, "event_ref"), "e" * 129),
        (("events", 0, "subject"), "u" * 257),
        (("events", 0, "event_type"), "unsupported_synthetic_event"),
        (("events", 0, "event_type"), []),
        (("events", 0, "at"), "not-a-timestamp"),
        (("events", 0, "at"), "2026-08-04T09:00:00+00:00"),
    ],
)
def test_schema_and_callable_fail_closed_on_bounds_and_semantics(
    field_path: tuple[object, ...], value: object
) -> None:
    incident, scenario = _input()
    target = scenario
    for part in field_path[:-1]:
        target = target[part]
    target[field_path[-1]] = value

    assert list(
        Draft202012Validator(_read_json("schema/input.schema.json"), format_checker=FormatChecker()).iter_errors(
            _schema_input(incident, scenario)
        )
    )
    with pytest.raises(ValueError) as error:
        analyze_case(incident, scenario)
    assert str(error.value) == _INVALID_PAYLOAD


@pytest.mark.parametrize("value", [True, "true", "false", 0, 1, None, [], {}])
def test_real_data_must_be_json_boolean_false(value: object) -> None:
    incident, scenario = _input()
    scenario["real_data"] = value

    with pytest.raises(ValueError) as error:
        analyze_case(incident, scenario)
    assert str(error.value) == _REAL_DATA_ERROR


@pytest.mark.parametrize("field", ["scenario_id", "real_data", "events", "expected"])
def test_missing_root_fields_return_a_fixed_error_not_keyerror(field: str) -> None:
    incident, scenario = _input()
    scenario.pop(field)

    with pytest.raises(ValueError) as error:
        analyze_case(incident, scenario)
    assert str(error.value) == _INVALID_PAYLOAD


@pytest.mark.parametrize("field", ["event_ref", "event_type", "at", "subject"])
def test_missing_event_fields_return_a_fixed_error_not_keyerror(field: str) -> None:
    incident, scenario = _input()
    scenario["events"][0].pop(field)

    with pytest.raises(ValueError) as error:
        analyze_case(incident, scenario)
    assert str(error.value) == _INVALID_PAYLOAD


@pytest.mark.parametrize("value", [[], {}, None])
def test_non_scalar_event_type_returns_a_fixed_error_not_typeerror(value: object) -> None:
    incident, scenario = _input()
    scenario["events"][0]["event_type"] = value

    with pytest.raises(ValueError) as error:
        analyze_case(incident, scenario)
    assert str(error.value) == _INVALID_PAYLOAD


def test_unknown_is_a_supported_evidence_semantic_and_input_is_not_mutated() -> None:
    incident, scenario = _input()
    original = deepcopy(scenario)

    first = analyze_case(incident, scenario)
    second = analyze_case(incident, scenario)

    assert scenario == original
    assert first == second
    assert first[0][0].classification == "fact"


def test_incomplete_golden_fixture_is_schema_valid_and_returns_unknown() -> None:
    scenario = _read_json("fixtures/golden-s05.json")
    incident, scenario = _input(scenario)

    _validate(_schema_input(incident, scenario), "schema/input.schema.json")
    evidence_items, risk_path = analyze_case(incident, scenario)
    _validate(_schema_output(evidence_items, risk_path), "schema/output.schema.json")

    assert risk_path == []
    assert evidence_items[0].classification == "unknown"
    assert evidence_items[0].evidence_level == "insufficient"
    assert "无法确认" in evidence_items[0].statement


def test_real_data_badcase_is_schema_shaped_but_rejected_before_output() -> None:
    scenario = _read_json("fixtures/badcase-real-data.json")
    incident, _ = _input()
    incident = incident.model_copy(
        update={
            "scenario_id": scenario["scenario_id"],
            "raw_event_refs": [scenario["events"][0]["event_ref"]],
        }
    )

    assert list(
        Draft202012Validator(_read_json("schema/input.schema.json"), format_checker=FormatChecker()).iter_errors(
            _schema_input(incident, scenario)
        )
    )
    with pytest.raises(ValueError) as error:
        analyze_case(incident, scenario)
    assert str(error.value) == _REAL_DATA_ERROR


def test_synthetic_corpus_is_accepted_or_rejected_at_the_same_boundary_as_intake() -> None:
    scenario_dir = Path(__file__).parents[3] / "data" / "scenarios"
    rejected = {"S09.json", "S10.json", "S11.json", "S12.json"}
    for path in sorted(scenario_dir.glob("*.json")):
        scenario = json.loads(path.read_text(encoding="utf-8"))
        if path.name in rejected:
            incident = build_incident(_read_json("fixtures/golden-s01.json"))
            with pytest.raises(ValueError):
                analyze_case(incident, scenario)
            continue
        incident = build_incident(scenario)
        _validate(_schema_input(incident, scenario), "schema/input.schema.json")
        evidence_items, risk_path = analyze_case(incident, scenario)
        _validate(_schema_output(evidence_items, risk_path), "schema/output.schema.json")


def test_invalid_incident_is_fixed_error_not_attributeerror() -> None:
    _, scenario = _input()

    with pytest.raises(ValueError) as error:
        analyze_case({"trace_id": "tr_invalid"}, scenario)  # type: ignore[arg-type]

    assert str(error.value) == _INVALID_PAYLOAD


@pytest.mark.parametrize(
    "value_factory",
    [
        lambda: "API" + "_KEY=" + "synthetic-value",
        lambda: "C:" + "/" + "Users" + "/" + "example" + "/" + "artifact.txt",
        lambda: "temp" + "/" + "artifact.txt",
    ],
)
def test_free_text_secret_or_path_values_are_schema_and_callable_rejected(value_factory) -> None:
    incident, scenario = _input()
    scenario["events"][0]["note"] = value_factory()

    assert list(
        Draft202012Validator(_read_json("schema/input.schema.json"), format_checker=FormatChecker()).iter_errors(
            _schema_input(incident, scenario)
        )
    )
    with pytest.raises(ValueError) as error:
        analyze_case(incident, scenario)
    assert str(error.value) == _INVALID_PAYLOAD


def test_duplicate_event_references_are_rejected_before_correlation() -> None:
    incident, scenario = _input()
    scenario["events"][1]["event_ref"] = scenario["events"][0]["event_ref"]
    incident = incident.model_copy(
        update={"raw_event_refs": [event["event_ref"] for event in scenario["events"]]}
    )

    with pytest.raises(ValueError) as error:
        analyze_case(incident, scenario)
    assert str(error.value) == _INVALID_PAYLOAD


def test_schema_rejects_exact_duplicate_events_and_output_references() -> None:
    incident, scenario = _input()
    scenario["events"] = [scenario["events"][0], deepcopy(scenario["events"][0])]
    incident = incident.model_copy(
        update={"raw_event_refs": [event["event_ref"] for event in scenario["events"]]}
    )
    assert list(
        Draft202012Validator(_read_json("schema/input.schema.json"), format_checker=FormatChecker()).iter_errors(
            _schema_input(incident, scenario)
        )
    )

    output = _read_json("fixtures/golden-s01.output.json")
    output["risk_path"] = [output["risk_path"][0], output["risk_path"][0]]
    output["evidence_items"][0]["related_event_refs"] *= 2
    assert list(
        Draft202012Validator(_read_json("schema/output.schema.json"), format_checker=FormatChecker()).iter_errors(output)
    )


class _UnhashableKeyMapping(Mapping):
    def __getitem__(self, key: object) -> object:
        raise KeyError(key)

    def __iter__(self):
        return iter([[]])

    def __len__(self) -> int:
        return 1


@pytest.mark.parametrize("target", ["scenario", "expected", "event"])
def test_hostile_mapping_with_unhashable_keys_has_a_fixed_error(target: str) -> None:
    incident, scenario = _input()
    if target == "scenario":
        candidate = _UnhashableKeyMapping()
    else:
        candidate = scenario
        if target == "expected":
            candidate["expected"] = _UnhashableKeyMapping()
        else:
            candidate["events"][0] = _UnhashableKeyMapping()

    with pytest.raises(ValueError) as error:
        analyze_case(incident, candidate)  # type: ignore[arg-type]
    assert str(error.value) == _INVALID_PAYLOAD


@pytest.mark.parametrize(
    "trace_id",
    ["", "t" * 129, "bad trace", True, 5],
)
def test_skill_local_trace_id_bound_is_schema_and_callable_rejected(trace_id: object) -> None:
    incident, scenario = _input()
    incident = incident.model_copy(update={"trace_id": trace_id})
    schema_input = _schema_input(_input()[0], scenario)
    schema_input["incident"]["trace_id"] = trace_id

    assert list(
        Draft202012Validator(_read_json("schema/input.schema.json"), format_checker=FormatChecker()).iter_errors(
            schema_input
        )
    )
    with pytest.raises(ValueError) as error:
        analyze_case(incident, scenario)
    assert str(error.value) == _INVALID_PAYLOAD

    output = _read_json("fixtures/golden-s01.output.json")
    for item in output["evidence_items"]:
        item["trace_id"] = trace_id
    assert list(
        Draft202012Validator(_read_json("schema/output.schema.json"), format_checker=FormatChecker()).iter_errors(output)
    )


@pytest.mark.parametrize("trace_id", ["t", "t" * 128])
def test_skill_local_trace_id_bound_accepts_one_and_128_characters(trace_id: str) -> None:
    incident, scenario = _input()
    incident = incident.model_copy(update={"trace_id": trace_id})
    _validate(_schema_input(incident, scenario), "schema/input.schema.json")
    evidence_items, risk_path = analyze_case(incident, scenario)
    output = _schema_output(evidence_items, risk_path)
    _validate(output, "schema/output.schema.json")
    assert all(item.trace_id == trace_id for item in evidence_items)


_SAFE_TEXT_LOCATIONS = [
    ("title",),
    ("events", 0, "region_label"),
    ("events", 0, "subject"),
    ("events", 0, "note"),
    ("expected", "conclusion"),
    ("expected", "report_contains"),
    ("expected", "report_excludes"),
]


@pytest.mark.parametrize("field_path", _SAFE_TEXT_LOCATIONS)
@pytest.mark.parametrize(
    "value_factory",
    [
        lambda: "aPi" + "_KeY=" + "synthetic-value",
        lambda: "TeMp" + "/" + "artifact.txt",
    ],
)
def test_mixed_case_safe_text_values_are_schema_and_callable_rejected(
    field_path: tuple[object, ...], value_factory
) -> None:
    incident, scenario = _input()
    target = scenario
    for part in field_path[:-1]:
        target = target[part]
    target[field_path[-1]] = value_factory()

    assert list(
        Draft202012Validator(_read_json("schema/input.schema.json"), format_checker=FormatChecker()).iter_errors(
            _schema_input(incident, scenario)
        )
    )
    with pytest.raises(ValueError) as error:
        analyze_case(incident, scenario)
    assert str(error.value) == _INVALID_PAYLOAD
