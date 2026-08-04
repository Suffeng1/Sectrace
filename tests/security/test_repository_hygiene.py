from pathlib import Path

from tests.security.repository_hygiene import scan_repository


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

    assert findings == []
