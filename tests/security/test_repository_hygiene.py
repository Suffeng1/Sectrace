from pathlib import Path
import subprocess

import pytest

from tests.security.repository_hygiene import _git_repository_files, scan_repository


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_tracked_repository_has_no_credential_like_values() -> None:
    assert scan_repository(REPO_ROOT) == []


def test_local_secret_and_runtime_paths_are_ignored() -> None:
    candidates = {
        ".env.local",
        "service.env",
        "server.pem",
        "server.key",
        "server.pfx",
        "server.p12",
        "logs/server.log",
        "secrets/service.json",
        "credentials/matrix.json",
        "tokens/mcp.txt",
        "secrets.json",
        "credentials.json",
        "tokens.json",
        "service.secret",
        "service.secrets",
        "id_rsa",
        "id_ed25519",
        "config/config.local.json",
        ".codex-security-scans/run/report.json",
        "outputs/demo/recordings/event.json",
        "runtime/state.json",
        "tmp/scan.json",
        "temp/scan.txt",
        "data/mcp-state/tr_local.json",
    }
    result = subprocess.run(
        [
            "git",
            "-c",
            "core.quotePath=false",
            "-c",
            "core.excludesFile=NUL",
            "check-ignore",
            "--no-index",
            "--",
            *sorted(candidates),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert set(result.stdout.splitlines()) == candidates
    assert result.stderr == ""


@pytest.mark.parametrize(
    ("content", "rule"),
    [
        ("C:" + "\\Users\\local-user\\project", "windows_user_directory"),
        ("C:" + "\\tmp\\scan-output", "local_temporary_path"),
        ("-----BEGIN " + "PRIVATE KEY-----", "private_key_material"),
        ("gh" + "p_" + "a" * 24, "github_token_prefix"),
        ("AK" + "IA" + "A" * 16, "aws_access_key_prefix"),
    ],
)
def test_public_release_privacy_and_credential_forms_are_reported(
    tmp_path: Path, content: str, rule: str
) -> None:
    candidate = tmp_path / "public.md"
    candidate.write_text(content, encoding="utf-8")

    findings = scan_repository(tmp_path, tracked_files=[candidate])

    assert findings == [{"path": "public.md", "rule": rule}]
    assert content not in repr(findings)


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
        ("Bear" + "er token: `synthetic-token-value`", "bearer_label_literal"),
        ('{"pass' + 'word": "synthetic-value"}', "password_json_literal"),
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
