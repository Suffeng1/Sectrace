from pathlib import Path

import pytest

from tests.security.repository_hygiene import _git_repository_files, scan_repository


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_tracked_repository_has_no_credential_like_values() -> None:
    assert scan_repository(REPO_ROOT) == []


def test_findings_disclose_only_path_and_rule_name(tmp_path: Path) -> None:
    tracked = tmp_path / "unsafe.md"
    tracked.write_text("PASS" + "WORD=" + "synthetic-value", encoding="utf-8")

    findings = scan_repository(tmp_path, tracked_files=[tracked])

    assert findings == [{"path": "unsafe.md", "rule": "password_assignment"}]
    assert "synthetic-value" not in repr(findings)



def test_tracked_hiclaw_worker_yaml_is_scanned(tmp_path: Path) -> None:
    worker = tmp_path / "hiclaw" / "sectrace-agents" / "worker.yaml"
    worker.parent.mkdir(parents=True)
    worker.write_text("TO" + "KEN=" + "synthetic-value", encoding="utf-8")

    findings = scan_repository(tmp_path, tracked_files=[worker])

    assert findings == [
        {"path": "hiclaw/sectrace-agents/worker.yaml", "rule": "token_assignment"}
    ]


def test_hiclaw_local_configuration_is_not_read(tmp_path: Path) -> None:
    local_config = tmp_path / "hiclaw" / "worker" / "config.local.yaml"

    findings = scan_repository(tmp_path, tracked_files=[local_config])

    assert findings == [
        {"path": "hiclaw/worker/config.local.yaml", "rule": "tracked_local_configuration"}
    ]


def test_untracked_nonignored_release_candidate_is_scanned(
    tmp_path: Path,
) -> None:
    import subprocess

    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    candidate = tmp_path / "docs" / "handoff.md"
    candidate.parent.mkdir()
    candidate.write_text("PASS" + "WORD=" + "synthetic-value", encoding="utf-8")

    assert _git_repository_files(tmp_path) == [candidate]
    assert scan_repository(tmp_path) == [
        {"path": "docs/handoff.md", "rule": "password_assignment"}
    ]


@pytest.mark.parametrize(
    ("content", "rule"),
    [
        ("Admin pass" + "word: `synthetic-value`", "password_literal"),
        ("Authorization: " + "Bear" + "er synthetic-token-value", "bearer_credential"),
        ("?access" + "_token=synthetic-token-value", "query_access_token"),
    ],
)
def test_credential_forms_are_reported_without_disclosing_values(
    tmp_path: Path, content: str, rule: str
) -> None:
    candidate = tmp_path / "handoff.md"
    candidate.write_text(content, encoding="utf-8")

    findings = scan_repository(tmp_path, tracked_files=[candidate])

    assert findings == [{"path": "handoff.md", "rule": rule}]
    assert "synthetic-token-value" not in repr(findings)
