from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Iterable


SCANNED_SUFFIXES = {
    ".conf",
    ".ini",
    ".json",
    ".md",
    ".ps1",
    ".py",
    ".sh",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}
HICLAW_LOCAL_PATHS = {"hiclaw/start_hiclaw.py"}
UNTRACKED_RELEASE_ROOTS = {
    "config",
    "docs",
    "hiclaw",
    "outputs",
    "scripts",
    "src",
    "tests",
}
RULES = {
    "windows_user_directory": re.compile(
        r"\b[A-Za-z]:[\\/]Users[\\/](?!<redacted>|<user>|USERNAME\b)[^\\/\s`\"']+",
        re.IGNORECASE,
    ),
    "local_temporary_path": re.compile(
        r"\b[A-Za-z]:[\\/](?:Users[\\/][^\\/\s`\"']+[\\/])?"
        r"(?:AppData[\\/]Local[\\/]Temp|tmp)[\\/]",
        re.IGNORECASE,
    ),
    "openai_key_prefix": re.compile(r"\b" + "s" + "k-", re.IGNORECASE),
    "api_key_assignment": re.compile(
        r"\bAPI"
        + r"_KEY\s*=\s*[`\"']?(?!<redacted|redacted\b|\$\{|\{\{)[^\s`\"']{8,}",
        re.IGNORECASE,
    ),
    "password_assignment": re.compile(
        r"\bPASS"
        + r"WORD\s*=\s*[`\"']?(?!<redacted|redacted\b|\$\{|\{\{)[^\s`\"']{8,}",
        re.IGNORECASE,
    ),
    "token_assignment": re.compile(
        r"\bTO"
        + r"KEN\s*=\s*[`\"']?(?!<redacted|redacted\b|\$\{|\{\{)[^\s`\"']{8,}",
        re.IGNORECASE,
    ),
    "password_literal": re.compile(
        "pass" + r"word\s*[:=]\s*`(?!redacted\b)[^`\r\n]+`", re.IGNORECASE
    ),
    "bearer_credential": re.compile(
        r"\b" + "Bearer" + r"\s+(?!<redacted|redacted\b)[A-Za-z0-9._~+/-]{8,}=*",
        re.IGNORECASE,
    ),
    "bearer_label_literal": re.compile(
        r"\bBearer\s+token\s*:\s*[`\"']?"
        r"(?!<redacted|redacted\b)[A-Za-z0-9._~+/-]{8,}=*",
        re.IGNORECASE,
    ),
    "password_json_literal": re.compile(
        r"[\"']pass" + r"word[\"']\s*:\s*[\"']"
        r"(?!<redacted|redacted\b|\$\{|\{\{)[^\"'\r\n]{8,}",
        re.IGNORECASE,
    ),
    "query_access_token": re.compile(
        r"[?&]access" + r"_token=(?!<redacted|redacted\b)[^&\s`\"']{8,}",
        re.IGNORECASE,
    ),
    "private_key_material": re.compile(
        r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"
    ),
    "github_token_prefix": re.compile(
        r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})"
    ),
    "aws_access_key_prefix": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
}


def _is_hiclaw_local_configuration(relative_path: Path) -> bool:
    normalized = relative_path.as_posix()
    if normalized in HICLAW_LOCAL_PATHS:
        return True
    if relative_path.parts[:1] != ("hiclaw",):
        return False

    name = relative_path.name.lower()
    return (
        (name.endswith(".env") and name != ".env.example")
        or name.startswith(("secrets", "credentials", "tokens"))
        or name.startswith("config.local.")
    )


def _is_scannable(path: Path) -> bool:
    return path.name == ".env.example" or path.suffix.lower() in SCANNED_SUFFIXES


def _git_paths(repo_root: Path, arguments: list[str]) -> set[str]:
    result = subprocess.run(
        arguments,
        cwd=repo_root,
        check=True,
        capture_output=True,
    )
    return {item for item in result.stdout.decode("utf-8").split("\0") if item}


def _git_repository_files(repo_root: Path) -> list[Path]:
    relative_paths = _git_paths(repo_root, ["git", "ls-files", "-z"])
    untracked = _git_paths(
        repo_root,
        ["git", "ls-files", "--others", "--exclude-standard", "-z"],
    )
    relative_paths.update(
        path
        for path in untracked
        if Path(path).parts[:1] in {(root,) for root in UNTRACKED_RELEASE_ROOTS}
    )
    candidates = {repo_root / relative_path for relative_path in relative_paths}
    return sorted(candidates)


def scan_repository(
    repo_root: Path, tracked_files: Iterable[Path] | None = None
) -> list[dict[str, str]]:
    repo_root = repo_root.resolve()
    candidates = (
        list(tracked_files)
        if tracked_files is not None
        else _git_repository_files(repo_root)
    )
    findings: list[dict[str, str]] = []

    for candidate in candidates:
        path = candidate.resolve()
        relative_path = path.relative_to(repo_root)
        if _is_hiclaw_local_configuration(relative_path):
            findings.append(
                {
                    "path": relative_path.as_posix(),
                    "rule": "tracked_local_configuration",
                }
            )
            continue
        if not _is_scannable(path):
            continue

        content = path.read_text(encoding="utf-8", errors="replace")
        for rule_name, pattern in RULES.items():
            if pattern.search(content):
                findings.append({"path": relative_path.as_posix(), "rule": rule_name})

    return findings
