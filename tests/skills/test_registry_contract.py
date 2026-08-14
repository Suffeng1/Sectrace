import importlib
import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator


REPO_ROOT = Path(__file__).parents[2]
REGISTRY_PATH = REPO_ROOT / "docs" / "skills" / "skill-registry.json"
REGISTRY_SCHEMA_PATH = REPO_ROOT / "docs" / "skills" / "skill-registry.schema.json"
EXPECTED_SKILLS = (
    ("sectrace-intake", "1.0.0", "Commander", "src.skills.intake.normalize.normalize_scenario"),
    ("sectrace-evidence", "1.0.0", "Evidence", "src.agents.evidence.service.analyze_case"),
    ("response", "1.0.0", "Response", "src.agents.response.service.create_response_plan"),
    ("audit", "1.0.0", "Audit", "src.agents.audit.service.build_audit_review"),
)
MCP_TOOL_NAMES = {
    "sectrace.intake.create_incident",
    "sectrace.evidence.analyze_case",
    "sectrace.response.create_plan",
    "sectrace.audit.build_bundle",
    "sectrace.ledger.get_trace",
    "sectrace.ledger.log_approval",
}


def _read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def _frontmatter(path: Path) -> dict[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    assert lines and lines[0] == "---"
    end = lines.index("---", 1)
    values = {}
    for line in lines[1:end]:
        key, value = line.split(":", 1)
        values[key] = value.strip()
    assert set(values) == {"name", "description"}
    return values


def _entrypoint(value: str):
    module_name, attribute = value.rsplit(".", 1)
    return getattr(importlib.import_module(module_name), attribute)


def _mutated_registry(index: int, field: str, value: object) -> dict:
    registry = _read_json(REGISTRY_PATH)
    registry["skills"][index][field] = value
    return registry


def _schema_errors(registry: dict) -> list:
    return list(Draft202012Validator(_read_json(REGISTRY_SCHEMA_PATH)).iter_errors(registry))


def _run_checker(tmp_path: Path, registry: dict) -> subprocess.CompletedProcess[str]:
    candidate = tmp_path / "registry.json"
    candidate.write_text(json.dumps(registry), encoding="utf-8")
    return subprocess.run(
        [sys.executable, "scripts/check-skill-registry.py", "--registry", str(candidate)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_skill_registry_is_exact_frozen_and_uses_only_relative_paths() -> None:
    registry = _read_json(REGISTRY_PATH)
    schema = _read_json(REGISTRY_SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    errors = list(Draft202012Validator(schema).iter_errors(registry))
    assert not errors, errors

    assert registry["schema_version"] == "1.0"
    skills = registry["skills"]
    assert tuple((item["name"], item["version"], item["role"], item["entrypoint"]) for item in skills) == EXPECTED_SKILLS
    assert len({item["name"] for item in skills}) == len(skills)
    assert len({item["role"] for item in skills}) == len(skills)
    assert len({item["entrypoint"] for item in skills}) == len(skills)
    for item in skills:
        for path in (item["skill_path"], item["input_schema"], item["output_schema"]):
            assert not Path(path).is_absolute()
            assert ".." not in Path(path).parts
            assert (REPO_ROOT / path).is_file()


def test_registered_skill_metadata_schemas_and_entrypoints_match_source() -> None:
    registry = _read_json(REGISTRY_PATH)
    for item in registry["skills"]:
        frontmatter = _frontmatter(REPO_ROOT / item["skill_path"])
        assert frontmatter["name"] == item["name"]
        assert frontmatter["description"] == item["description"]
        assert callable(_entrypoint(item["entrypoint"]))
        for schema_path in (item["input_schema"], item["output_schema"]):
            schema = _read_json(REPO_ROOT / schema_path)
            assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
            Draft202012Validator.check_schema(schema)
            assert schema["$id"].endswith(f"/{item['version']}/{Path(schema_path).name}")
        changelog = (REPO_ROOT / item["changelog_path"]).read_text(encoding="utf-8")
        assert f"## {item['version']} -" in changelog


def test_registry_preserves_role_chain_mcp_boundary_and_evaluation_limits() -> None:
    registry = _read_json(REGISTRY_PATH)
    assert registry["contract_schema_version"] == "1.0"
    assert registry["role_chain"] == ["Commander", "Evidence", "Response", "Audit"]
    for item in registry["skills"]:
        assert item["mcp_tools"] == []
        assert not set(item["mcp_tools"]) & MCP_TOOL_NAMES
        assert item["lifecycle"]["status"] == "qa_passed_registry_pending_release"
        assert item["evaluation_scope"] == {
            "scope": "full_local_pipeline_only",
            "evidence": "docs/verification/V-OPT2-02-fourth-corrected-independent-qa.md",
            "per_skill_score": "not_claimed",
            "runtime_live_status": "not_claimed",
        }
        assert item["official_skill"] is False
        assert item["installation"] == "not_installed"


@pytest.mark.parametrize("unknown_field", ["current_live", "score", "official_provider"])
def test_registry_schema_rejects_unknown_fields_fail_closed(unknown_field: str) -> None:
    registry = _read_json(REGISTRY_PATH)
    registry["skills"][0][unknown_field] = "invented"
    assert _schema_errors(registry)


@pytest.mark.parametrize(
    ("index", "field", "value"),
    [
        (1, "name", "sectrace-intake"),
        (1, "role", "Commander"),
        (0, "name", "unknown-skill"),
        (0, "role", "Evidence"),
        (0, "entrypoint", "src.agents.evidence.service.analyze_case"),
        (0, "entrypoint", "src.skills.intake.normalize.does_not_exist"),
        (0, "version", "2.0.0"),
        (0, "skill_path", "../outside/SKILL.md"),
        (0, "skill_path", "C:/outside/SKILL.md"),
        (0, "entrypoint", "src.app.mcp_adapter.TOOL_NAMES"),
    ],
)
def test_registry_schema_rejects_frozen_membership_order_and_mapping_mutations(
    index: int, field: str, value: object
) -> None:
    assert _schema_errors(_mutated_registry(index, field, value))


def test_registry_schema_rejects_extra_or_reordered_entries() -> None:
    registry = _read_json(REGISTRY_PATH)
    registry["skills"].append(deepcopy(registry["skills"][0]))
    assert _schema_errors(registry)

    reordered = _read_json(REGISTRY_PATH)
    reordered["skills"][0], reordered["skills"][1] = reordered["skills"][1], reordered["skills"][0]
    assert _schema_errors(reordered)


@pytest.mark.parametrize(
    ("field", "value", "expected_category"),
    [
        ("skill_path", "src/skills/missing/SKILL.md", "path"),
        ("skill_path", "../outside/SKILL.md", "schema"),
        ("skill_path", "C:/outside/SKILL.md", "schema"),
        ("version", "2.0.0", "schema"),
        ("role", "Evidence", "schema"),
        ("entrypoint", "src.skills.intake.normalize.does_not_exist", "schema"),
        ("entrypoint", "src.app.mcp_adapter.TOOL_NAMES", "schema"),
        ("unknown_field", "invented", "schema"),
    ],
)
def test_registry_checker_fails_closed_without_echoing_input(
    tmp_path: Path, field: str, value: object, expected_category: str
) -> None:
    result = _run_checker(tmp_path, _mutated_registry(0, field, value))
    assert result.returncode != 0
    assert result.stdout == ""
    assert result.stderr == f"Skill registry is invalid: {expected_category}.\n"
    assert str(value) not in result.stderr
