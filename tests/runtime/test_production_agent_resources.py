from pathlib import Path
import re

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
AGENT_DIR = REPO_ROOT / "hiclaw" / "sectrace-agents"
PROMPT_DIR = AGENT_DIR / "prompts"
WORKERS = (
    "sectrace-commander",
    "sectrace-evidence",
    "sectrace-response",
    "sectrace-audit",
)


def _load(path: Path) -> dict:
    assert path.is_file(), f"missing production resource: {path.name}"
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_four_workers_match_proven_crd_and_prompt_sources() -> None:
    for name in WORKERS:
        resource = _load(AGENT_DIR / f"{name}.yaml")
        prompt = (PROMPT_DIR / f"{name}.md").read_text(encoding="utf-8").strip()

        assert resource["apiVersion"] == "agentteams.io/v1beta1"
        assert resource["kind"] == "Worker"
        assert resource["metadata"]["name"] == name
        assert resource["spec"]["model"] == "qwen3.6-plus"
        assert resource["spec"]["runtime"] == "openclaw"
        assert resource["spec"]["state"] == "Running"
        assert resource["spec"]["agents"].strip() == prompt
        assert resource["spec"]["mcpServers"] == [
            {
                "name": "sectrace",
                "url": "http://host.docker.internal:19090/mcp",
                "transport": "http",
            }
        ]


def test_production_team_has_exact_role_order() -> None:
    team = _load(AGENT_DIR / "sectrace-audit-team.yaml")

    assert team["apiVersion"] == "agentteams.io/v1beta1"
    assert team["kind"] == "Team"
    assert team["metadata"]["name"] == "sectrace-audit-team"
    assert team["spec"]["workerMembers"] == [
        {"name": "sectrace-commander", "role": "team_leader"},
        {"name": "sectrace-evidence", "role": "worker"},
        {"name": "sectrace-response", "role": "worker"},
        {"name": "sectrace-audit", "role": "worker"},
    ]


def test_production_resources_have_no_credential_values() -> None:
    pattern = re.compile(
        r"(?i)(?:api[_-]?key|password|token|credential|secret)\s*[:=]\s*\S+"
        r"|\b[0-9a-f]{32,}\b"
    )
    paths = [*(AGENT_DIR.glob("sectrace-*.yaml")), *(PROMPT_DIR.glob("*.md"))]

    assert paths
    for path in paths:
        assert pattern.search(path.read_text(encoding="utf-8")) is None
