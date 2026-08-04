"""Command-line replay entry point for judges and local verification."""

import json
from pathlib import Path

from src.app.orchestrator import run_demo


if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parents[2]
    result = run_demo(repo_root / "data" / "scenarios" / "S01.json")
    print(json.dumps(result, ensure_ascii=False, indent=2))
