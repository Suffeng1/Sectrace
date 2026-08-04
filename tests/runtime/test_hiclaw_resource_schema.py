from pathlib import Path

import yaml


RESOURCE_DIR = Path(__file__).resolve().parents[2] / "hiclaw" / "sectrace-agents"


def _resource(filename: str) -> dict:
    return yaml.safe_load((RESOURCE_DIR / filename).read_text(encoding="utf-8"))


def test_smoke_worker_matches_installed_crd() -> None:
    worker = _resource("smoke-worker.yaml")

    assert worker == {
        "apiVersion": "agentteams.io/v1beta1",
        "kind": "Worker",
        "metadata": {"name": "sectrace-smoke"},
        "spec": {
            "model": "qwen3.6-plus",
            "runtime": "openclaw",
            "state": "Running",
        },
    }


def test_smoke_team_matches_installed_crd() -> None:
    team = _resource("smoke-team.yaml")

    assert team == {
        "apiVersion": "agentteams.io/v1beta1",
        "kind": "Team",
        "metadata": {"name": "sectrace-smoke-team"},
        "spec": {
            "workerMembers": [
                {"name": "sectrace-smoke", "role": "team_leader"}
            ]
        },
    }
