from pathlib import Path

from src.app.mcp_adapter import TOOL_NAMES


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_current_release_documentation_uses_authoritative_facts() -> None:
    requirements = (PROJECT_ROOT / "requirements.md").read_text(encoding="utf-8")
    resource_readme = (
        PROJECT_ROOT / "hiclaw" / "sectrace-agents" / "README.md"
    ).read_text(encoding="utf-8")
    context = (PROJECT_ROOT / "CONTEXT.md").read_text(encoding="utf-8")
    phase_two_plan = (
        PROJECT_ROOT / "docs" / "plans" / "phase-2" / "README.md"
    ).read_text(encoding="utf-8")
    release_facts = (PROJECT_ROOT / "docs" / "release-facts.md").read_text(
        encoding="utf-8"
    )

    assert len(TOOL_NAMES) == 6
    assert "exactly five synthetic/read-only MCP tools" not in requirements
    assert "will contain repository-safe Worker and Team resources" not in resource_readme
    assert "Contract v1.0 is pending" not in context
    assert "`RiskAssessment`" not in phase_two_plan
    assert all(f"`{tool_name}`" in release_facts for tool_name in TOOL_NAMES)


def test_final_records_reference_existing_sanitized_evidence() -> None:
    for relative_path in (
        "docs/verification/S-09-codex-security-scan.md",
        "docs/verification/R-08BG-clean-s01-final-closure.md",
        "docs/verification/R-09B6-mcp-verifier-reload.md",
    ):
        assert (PROJECT_ROOT / relative_path).is_file()
