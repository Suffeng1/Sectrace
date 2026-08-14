"""Read-only deterministic validation for the local Skill registry."""

import argparse
import importlib
import json
import re
import sys
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).parents[1]
SCHEMA_PATH = ROOT / "docs" / "skills" / "skill-registry.schema.json"
REGISTRY_PATH = ROOT / "docs" / "skills" / "skill-registry.json"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
ENTRYPOINTS = {
    "Commander": "src.skills.intake.normalize.normalize_scenario",
    "Evidence": "src.agents.evidence.service.analyze_case",
    "Response": "src.agents.response.service.create_response_plan",
    "Audit": "src.agents.audit.service.build_audit_review",
}
CHANGELOG_VERSION = re.compile(r"^## (\d+\.\d+\.\d+) - \d{4}-\d{2}-\d{2}$", re.MULTILINE)


class RegistryError(Exception):
    def __init__(self, category: str) -> None:
        self.category = category


def _read_json(path: Path, category: str) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise RegistryError(category) from error


def _resolve_path(value: object) -> Path:
    if not isinstance(value, str):
        raise RegistryError("path")
    candidate = Path(value)
    if candidate.is_absolute():
        raise RegistryError("path")
    resolved = (ROOT / candidate).resolve()
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError as error:
        raise RegistryError("path") from error
    if not resolved.is_file():
        raise RegistryError("path")
    return resolved


def _frontmatter(path: Path) -> dict[str, str]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
        if not lines or lines[0] != "---":
            raise ValueError
        end = lines.index("---", 1)
        values = {}
        for line in lines[1:end]:
            key, value = line.split(":", 1)
            if key in values:
                raise ValueError
            values[key] = value.strip()
        if set(values) != {"name", "description"}:
            raise ValueError
        return values
    except (OSError, UnicodeError, ValueError) as error:
        raise RegistryError("frontmatter") from error


def _changelog_version(path: Path) -> str:
    try:
        match = CHANGELOG_VERSION.search(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError) as error:
        raise RegistryError("version") from error
    if match is None:
        raise RegistryError("version")
    return match.group(1)


def _check_entrypoint(role: object, value: object) -> None:
    if not isinstance(role, str) or not isinstance(value, str) or ENTRYPOINTS.get(role) != value:
        raise RegistryError("entrypoint")
    try:
        module_name, attribute = value.rsplit(".", 1)
        target = getattr(importlib.import_module(module_name), attribute)
    except (ImportError, AttributeError, ValueError) as error:
        raise RegistryError("entrypoint") from error
    if not callable(target):
        raise RegistryError("entrypoint")


def _check_registry(registry: dict, schema: dict) -> None:
    try:
        Draft202012Validator.check_schema(schema)
        if list(Draft202012Validator(schema).iter_errors(registry)):
            raise RegistryError("schema")
    except RegistryError:
        raise
    except Exception as error:
        raise RegistryError("schema") from error

    for item in registry["skills"]:
        skill_path = _resolve_path(item["skill_path"])
        changelog_path = _resolve_path(item["changelog_path"])
        input_schema_path = _resolve_path(item["input_schema"])
        output_schema_path = _resolve_path(item["output_schema"])
        frontmatter = _frontmatter(skill_path)
        if frontmatter["name"] != item["name"] or frontmatter["description"] != item["description"]:
            raise RegistryError("frontmatter")
        if _changelog_version(changelog_path) != item["version"]:
            raise RegistryError("version")
        for schema_path in (input_schema_path, output_schema_path):
            loaded_schema = _read_json(schema_path, "skill_schema")
            try:
                if loaded_schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
                    raise RegistryError("skill_schema")
                if not loaded_schema.get("$id", "").endswith(f"/{item['version']}/{schema_path.name}"):
                    raise RegistryError("skill_schema")
                Draft202012Validator.check_schema(loaded_schema)
            except RegistryError:
                raise
            except Exception as error:
                raise RegistryError("skill_schema") from error
        _check_entrypoint(item["role"], item["entrypoint"])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--registry", type=Path, default=REGISTRY_PATH)
    arguments = parser.parse_args(argv)
    try:
        _check_registry(_read_json(arguments.registry, "registry"), _read_json(SCHEMA_PATH, "schema"))
    except RegistryError as error:
        print(f"Skill registry is invalid: {error.category}.", file=sys.stderr)
        return 1
    print("Skill registry is valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
