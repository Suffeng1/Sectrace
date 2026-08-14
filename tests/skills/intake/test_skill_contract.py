import json
from pathlib import Path
from copy import deepcopy

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from src.skills.intake.normalize import normalize_scenario


SKILL_ROOT = Path(__file__).parents[3] / "src" / "skills" / "intake"
_INVALID_PAYLOAD = "invalid intake payload"


def _read_json(relative_path: str) -> dict:
    return json.loads((SKILL_ROOT / relative_path).read_text(encoding="utf-8"))


def _validate(instance: dict, schema_path: str) -> None:
    errors = list(Draft202012Validator(_read_json(schema_path), format_checker=FormatChecker()).iter_errors(instance))
    assert not errors, errors


def test_golden_fixture_conforms_to_executable_intake_contract() -> None:
    scenario = _read_json("fixtures/golden-synthetic-login.json")
    expected = _read_json("fixtures/golden-synthetic-login.normalized.json")

    _validate(scenario, "schema/input.schema.json")
    normalized = normalize_scenario(scenario)
    _validate(normalized, "schema/output.schema.json")

    assert normalized == expected
    assert normalized is not scenario


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
def test_extra_or_sensitive_looking_fields_are_schema_and_runtime_rejected(field_path: tuple[object, ...]) -> None:
    scenario = _read_json("fixtures/golden-synthetic-login.json")
    target = scenario
    for part in field_path[:-1]:
        target = target[part]
    target[field_path[-1]] = "synthetic-value"

    assert list(Draft202012Validator(_read_json("schema/input.schema.json"), format_checker=FormatChecker()).iter_errors(scenario))
    with pytest.raises(ValueError, match="invalid intake payload"):
        normalize_scenario(scenario)


@pytest.mark.parametrize(
    ("field_path", "value"),
    [
        (("scenario_id",), "s" * 65),
        (("events", 0, "event_ref"), "e" * 129),
        (("events", 0, "subject"), "u" * 257),
        (("events", 0, "event_type"), "unsupported_synthetic_event"),
        (("events", 0, "event_type"), 3),
        (("events", 0, "at"), "not-a-timestamp"),
        (("events", 0, "at"), "2026-08-04T09:00:00+00:00"),
        (("events", 0, "at"), "2026-02-30T09:00:00Z"),
    ],
)
def test_schema_and_runtime_fail_closed_on_semantic_or_length_violations(field_path: tuple[object, ...], value: object) -> None:
    scenario = _read_json("fixtures/golden-synthetic-login.json")
    target = scenario
    for part in field_path[:-1]:
        target = target[part]
    target[field_path[-1]] = value

    assert list(Draft202012Validator(_read_json("schema/input.schema.json"), format_checker=FormatChecker()).iter_errors(scenario))
    with pytest.raises(ValueError, match="invalid intake payload"):
        normalize_scenario(scenario)


@pytest.mark.parametrize("value", [True, "true", "false", 0, 1, None, [], {}])
def test_real_data_must_be_json_boolean_false(value: object) -> None:
    scenario = _read_json("fixtures/golden-synthetic-login.json")
    scenario["real_data"] = value

    with pytest.raises(ValueError, match="intake accepts synthetic or de-identified data only"):
        normalize_scenario(scenario)


def test_unknown_is_supported_semantic_value_and_input_is_deeply_unchanged() -> None:
    scenario = _read_json("fixtures/golden-synthetic-login.json")
    scenario["expected"]["classification"] = "unknown"
    original = deepcopy(scenario)

    first = normalize_scenario(scenario)
    second = normalize_scenario(scenario)

    assert scenario == original
    assert first == second
    assert first["expected"]["classification"] == "unknown"
    assert first["events"] is not scenario["events"]
    assert first["events"][0] is not scenario["events"][0]


def test_real_synthetic_corpus_fields_are_allowlisted_except_intentional_intake_rejections() -> None:
    scenarios = Path(__file__).parents[3] / "data" / "scenarios"
    rejected = {"S09.json", "S10.json", "S11.json", "S12.json"}
    for path in sorted(scenarios.glob("*.json")):
        scenario = json.loads(path.read_text(encoding="utf-8"))
        if path.name in rejected:
            with pytest.raises(ValueError):
                normalize_scenario(scenario)
        else:
            _validate(scenario, "schema/input.schema.json")
            _validate(normalize_scenario(scenario), "schema/output.schema.json")


def test_real_data_badcase_is_schema_shaped_but_rejected_before_output() -> None:
    scenario = _read_json("fixtures/badcase-real-data.json")

    assert list(Draft202012Validator(_read_json("schema/input.schema.json"), format_checker=FormatChecker()).iter_errors(scenario))
    with pytest.raises(ValueError, match="synthetic or de-identified"):
        normalize_scenario(scenario)


@pytest.mark.parametrize("field", ["scenario_id", "real_data", "events", "expected"])
def test_missing_required_root_fields_have_a_fixed_nonleaking_error(field: str) -> None:
    scenario = _read_json("fixtures/golden-synthetic-login.json")
    scenario.pop(field)

    with pytest.raises(ValueError) as error:
        normalize_scenario(scenario)

    assert str(error.value) == _INVALID_PAYLOAD


@pytest.mark.parametrize("field", ["event_ref", "event_type", "at", "subject"])
def test_missing_required_event_fields_have_a_fixed_nonleaking_error(field: str) -> None:
    scenario = _read_json("fixtures/golden-synthetic-login.json")
    scenario["events"][0].pop(field)

    with pytest.raises(ValueError) as error:
        normalize_scenario(scenario)

    assert str(error.value) == _INVALID_PAYLOAD


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("intake", []), ("intake", {}), ("intake", None),
        ("severity_hint", []), ("severity_hint", {}), ("severity_hint", None),
        ("classification", []), ("classification", {}), ("classification", None),
    ],
)
def test_expected_enum_non_scalar_values_have_a_fixed_nonleaking_error(field: str, value: object) -> None:
    scenario = _read_json("fixtures/golden-synthetic-login.json")
    scenario["expected"][field] = value

    with pytest.raises(ValueError) as error:
        normalize_scenario(scenario)

    assert str(error.value) == _INVALID_PAYLOAD


@pytest.mark.parametrize("value", [[], {}, None])
def test_event_type_non_scalar_values_have_a_fixed_nonleaking_error(value: object) -> None:
    scenario = _read_json("fixtures/golden-synthetic-login.json")
    scenario["events"][0]["event_type"] = value

    with pytest.raises(ValueError) as error:
        normalize_scenario(scenario)

    assert str(error.value) == _INVALID_PAYLOAD


@pytest.mark.parametrize(
    ("scenario", "message"),
    [
        ({"events": [], "expected": {}}, _INVALID_PAYLOAD),
        ({"scenario_id": "S-invalid", "expected": {}}, _INVALID_PAYLOAD),
        ({"scenario_id": "S-invalid", "events": []}, _INVALID_PAYLOAD),
        ({"scenario_id": "S-invalid", "events": [], "expected": {"severity_hint": "critical"}}, _INVALID_PAYLOAD),
    ],
)
def test_failure_injection_rejects_malformed_or_unsupported_input(scenario: dict, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        normalize_scenario(scenario)
