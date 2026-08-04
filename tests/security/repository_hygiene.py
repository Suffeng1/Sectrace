from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Iterable


SCANNED_SUFFIXES = {".py", ".md", ".yaml", ".yml", ".json"}
HICLAW_LOCAL_PATHS = {"hiclaw/start_hiclaw.py"}
SAFE_PENDING_PATHS = {
    ".gitignore",
    "README.md",
    "requirements.md",
    "docs/status.md",
    "docs/runtime/hiClaw-inventory.redacted.md",
    "docs/runtime/secret-handling.md",
    "hiclaw/.env.example",
    "hiclaw/sectrace-agents/README.md",
    "tests/security/repository_hygiene.py",
    "tests/security/test_repository_hygiene.py",
}
RULES = {
    "openai_key_prefix": re.compile(r"\b" + "s" + "k-", re.IGNORECASE),
    "api_key_assignment": re.compile("API" + r"_KEY\s*=", re.IGNORECASE),
    "password_assignment": re.compile("PASS" + r"WORD\s*=", re.IGNORECASE),
    "token_assignment": re.compile("TO" + r"KEN\s*=", re.IGNORECASE),
    "long_hex_secret": re.compile(r"(?<![0-9a-f])[0-9a-f]{32,}(?![0-9a-f])", re.IGNORECASE),
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


def _git_tracked_files(repo_root: Path) -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=repo_root,
        check=True,
        capture_output=True,
    )
    relative_paths = [item for item in result.stdout.decode("utf-8").split("\0") if item]
    candidates = {repo_root / relative_path for relative_path in relative_paths}
    candidates.update(
        repo_root / relative_path
        for relative_path in SAFE_PENDING_PATHS
        if (repo_root / relative_path).is_file()
    )
    return sorted(candidates)


def scan_repository(
    repo_root: Path, tracked_files: Iterable[Path] | None = None
) -> list[dict[str, str]]:
    repo_root = repo_root.resolve()
    candidates = list(tracked_files) if tracked_files is not None else _git_tracked_files(repo_root)
    findings: list[dict[str, str]] = []

    for candidate in candidates:
        path = candidate.resolve()
        relative_path = path.relative_to(repo_root)
        if _is_hiclaw_local_configuration(relative_path):
            continue
        if not _is_scannable(path):
            continue

        content = path.read_text(encoding="utf-8", errors="replace")
        for rule_name, pattern in RULES.items():
            if pattern.search(content):
                findings.append({"path": relative_path.as_posix(), "rule": rule_name})

    return findings
