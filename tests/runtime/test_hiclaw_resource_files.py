from pathlib import Path
import re

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
RESOURCE_DIR = REPO_ROOT / "hiclaw" / "sectrace-agents"


def _load_resource(filename: str) -> dict:
    path = RESOURCE_DIR / filename
    assert path.is_file(), f"missing H-01 smoke resource: {filename}"
    resource = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(resource, dict)
    return resource


def test_smoke_worker_resource_exists_and_is_named() -> None:
    worker = _load_resource("smoke-worker.yaml")

    assert worker["metadata"]["name"] == "sectrace-smoke"


def test_smoke_team_resource_exists_and_is_named() -> None:
    team = _load_resource("smoke-team.yaml")

    assert team["metadata"]["name"] == "sectrace-smoke-team"


def test_smoke_resources_contain_no_credential_like_values() -> None:
    credential_pattern = re.compile(
        r"(?i)(?:api[_-]?key|password|token|credential|secret)\s*[:=]\s*\S+"
        r"|\b[0-9a-f]{32,}\b"
    )

    for filename in ("smoke-worker.yaml", "smoke-team.yaml"):
        path = RESOURCE_DIR / filename
        assert path.is_file(), f"missing H-01 smoke resource: {filename}"
        assert credential_pattern.search(path.read_text(encoding="utf-8")) is None
