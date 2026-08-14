import re
from pathlib import Path

import pytest

from tests.security.repository_hygiene import scan_repository


PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMPETITION_ROOT = PROJECT_ROOT / "docs" / "competition"
COMPETITION_DOCS = (
    COMPETITION_ROOT / "value-baseline.md",
    COMPETITION_ROOT / "evidence-manifest.md",
    COMPETITION_ROOT / "portability-matrix.md",
)
METRICS = (
    "Trace completeness rate",
    "Approval binding correctness rate",
    "Invalid-state rejection rate",
    "Audit-chain completeness rate",
    "E2E elapsed time",
    "Manual handoff step count",
)
METRIC_FIELDS = (
    "Formula",
    "Numerator",
    "Denominator/sample population",
    "Applicability",
    "Zero/empty policy",
    "Evidence source",
    "Limits",
)


def _metric_sections(document: str) -> dict[str, str]:
    headings = list(re.finditer(r"(?m)^### (.+)$", document))
    sections: dict[str, str] = {}
    for index, heading in enumerate(headings):
        name = heading.group(1).strip()
        end = headings[index + 1].start() if index + 1 < len(headings) else len(document)
        sections[name] = document[heading.end() : end]
    return sections


def _unsupported_claim_reasons(text: str) -> list[str]:
    reasons: list[str] = []
    statements = re.split(
        r"(?<=[.!?])\s+|[\r\n]+|(?i:\b(?:but|however|yet)\b)", text
    )
    bounded = re.compile(
        r"(?i)\b(?:point-in-time|historical|runtime unknown|unknown|unverified|todo)\b"
        r"|\b(?:no|not|never|neither|without|cannot|isn't|aren't|wasn't|weren't)\b"
    )
    production_state = re.compile(
        r"(?i)\b(?:deployed|running|operational|ready|proven|validated)\b"
        r"(?:\W+\w+){0,5}\W+\bproduction\b"
        r"|\bproduction\b(?:\W+\w+){0,5}\W+"
        r"\b(?:deployment|running|operational|ready|proven|validated)\b"
        r"|\bproduction\s+deployment\b(?:\W+\w+){0,3}\W+\blive\b"
    )
    current_live_state = re.compile(
        r"(?i)(?:\bcurrently\b|\bnow\b|\bcurrent\b(?:\W+\w+){0,3})?"
        r"\blive(?:\W+runtime)?\b(?:\W+\w+){0,5}\W+"
        r"\b(?:healthy|running|ready|available|operational|validated)\b"
    )
    quantified_benefit = re.compile(
        r"(?i)\b(?:cuts?|cutting|reduced?|reducing|saved?|saving|improved?|improving|"
        r"increased?|increasing|accelerated?|accelerating)\b"
        r"(?:\W+\w+){0,8}\W+\d+(?:\.\d+)?\s*"
        r"(?:%|percent|hours?|minutes?|days?)(?=\W|$)"
        r"|\b(?:achieved?|delivered?|realized?|reported?)\b(?:\W+\w+){0,5}\W+"
        r"\d+(?:\.\d+)?\s*(?:%|percent)(?:\W+\w+){0,4}\W+"
        r"\b(?:reduction|improvement|increase|decrease|savings?|gain)\b"
    )

    for statement in statements:
        if not statement.strip() or bounded.search(statement):
            continue
        if production_state.search(statement):
            reasons.append("production_state")
        if current_live_state.search(statement):
            reasons.append("current_live_state")
        if quantified_benefit.search(statement):
            reasons.append("quantified_benefit")
    return reasons


def test_opt2_01_documents_define_required_scope_without_results() -> None:
    value_baseline, evidence_manifest, portability_matrix = (
        path.read_text(encoding="utf-8") for path in COMPETITION_DOCS
    )

    for stage in (
        "synthetic/de-identified event intake",
        "Evidence",
        "Response pending gate",
        "human approval",
        "Audit",
    ):
        assert stage in value_baseline

    metric_sections = _metric_sections(value_baseline)
    assert set(METRICS).issubset(metric_sections)
    for metric in METRICS:
        section = metric_sections[metric]
        for field in METRIC_FIELDS:
            assert re.search(rf"(?m)^- \*\*{re.escape(field)}:\*\*\s+\S", section), (
                metric,
                field,
            )

    assert "SYNTHETIC BENCHMARK PROTOCOL" in value_baseline
    assert "NO RESULTS RECORDED" in value_baseline
    assert "point-in-time" in evidence_manifest
    assert "repository-only" in evidence_manifest
    assert "runtime unknown" in evidence_manifest
    assert "Invariant core" in portability_matrix
    assert "Replaceable adapter layer" in portability_matrix


def test_competition_evidence_manifest_has_no_dangling_repository_links() -> None:
    manifest = (COMPETITION_ROOT / "evidence-manifest.md").read_text(
        encoding="utf-8"
    )
    links = re.findall(r"\[[^]]+\]\(([^)]+)\)", manifest)

    assert links
    for link in links:
        assert not re.match(r"^[a-z]+://", link)
        target = (COMPETITION_ROOT / link.split("#", 1)[0]).resolve()
        assert target.is_relative_to(PROJECT_ROOT.resolve())
        assert target.is_file(), link


def test_competition_documents_reject_unsupported_claims_and_sensitive_content() -> None:
    corpus = "\n".join(path.read_text(encoding="utf-8") for path in COMPETITION_DOCS)
    assert _unsupported_claim_reasons(corpus) == []
    assert scan_repository(PROJECT_ROOT, tracked_files=list(COMPETITION_DOCS)) == []


@pytest.mark.parametrize(
    "claim",
    (
        "SecTrace is deployed in production.",
        "SecTrace reduced mean response time by 40%.",
        "The live runtime is healthy.",
        "SecTrace cuts manual handoffs by 50%.",
        "SecTrace is operational in production.",
        "The current live service is available.",
        "Runtime is unknown, but SecTrace is deployed in production.",
        "SecTrace achieved a 35 percent reduction in review time.",
        "The production deployment is live now.",
    ),
)
def test_unsupported_production_benefit_and_current_live_claims_are_detected(
    claim: str,
) -> None:
    assert _unsupported_claim_reasons(claim)


@pytest.mark.parametrize(
    "bounded_statement",
    (
        "Historical live PASS is point-in-time evidence only.",
        "The current runtime is unknown.",
        "TODO: obtain authorized live evidence before making a current claim.",
        "SecTrace is not deployed in production.",
        "No production benefit has been measured.",
        "The historical service was deployed in production at that point in time.",
        "TODO: test a production deployment before making a release claim.",
    ),
)
def test_bounded_historical_unknown_todo_and_negative_statements_are_allowed(
    bounded_statement: str,
) -> None:
    assert _unsupported_claim_reasons(bounded_statement) == []
