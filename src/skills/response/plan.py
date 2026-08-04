"""Deterministic advice-only response planning rules."""

from src.app.contracts import EvidenceItem


def has_corroborated_risk(evidence_items: list[EvidenceItem]) -> bool:
    """Return whether supplied evidence supports a high-risk response plan."""
    return bool(evidence_items) and all(
        item.classification == "fact"
        and item.confidence == "high"
        and item.evidence_level in {"corroborated", "strong"}
        for item in evidence_items
    )

