from pathlib import Path
import tomllib


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_project_metadata_describes_completed_initial_release() -> None:
    metadata = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8"))[
        "project"
    ]

    assert metadata["version"] == "1.0.0"
    assert metadata["description"] == (
        "Safe multi-Agent security incident analysis and audit demo"
    )
