from __future__ import annotations

from typing import Any


EVIDENCE_LEVELS = {
    5: "Peer-reviewed + production system",
    4: "Published benchmark + multi-source validated",
    3: "Community adoption + documentation",
    2: "Individual reports + blog posts",
    1: "Anecdotal / single source",
}


class EvidenceEvaluator:
    """Evaluates evidence quality using the 5-level evidence hierarchy."""

    def evaluate_tool(self, tool_data: dict) -> dict[str, Any]:
        """Evaluate a tool's evidence level."""
        score = 1
        reasons = []

        stars = tool_data.get("stars", 0)
        if stars > 10000:
            score = max(score, 4)
            reasons.append(f"High community adoption ({stars} stars)")
        elif stars > 1000:
            score = max(score, 3)
            reasons.append(f"Moderate community adoption ({stars} stars)")

        license_type = tool_data.get("license", "None")
        if license_type not in ("None", "PROPRIETARY", "CC-BY-NC-4.0"):
            score = max(score, 3)
            reasons.append(f"Open source license: {license_type}")

        if tool_data.get("free_tier"):
            score = max(score, 2)
            reasons.append("Has free tier")

        if tool_data.get("peer_reviewed"):
            score = 5
            reasons.append("Peer-reviewed")

        if tool_data.get("production_use"):
            score = max(score, 4)
            reasons.append("Used in production")

        return {
            "evidence_level": min(score, 5),
            "level_description": EVIDENCE_LEVELS[min(score, 5)],
            "reasons": reasons,
            "confidence": self._confidence(score),
        }

    def evaluate_methodology(self, claim: dict) -> dict[str, Any]:
        """Evaluate a methodology claim."""
        sources = claim.get("sources", [])
        score = 1
        reasons = []

        if len(sources) >= 3:
            score = max(score, 3)
            reasons.append(f"Multiple sources ({len(sources)})")

        if any(s.get("peer_reviewed") for s in sources):
            score = max(score, 5)
            reasons.append("At least one peer-reviewed source")

        if any(s.get("production_use") for s in sources):
            score = max(score, 4)
            reasons.append("At least one production source")

        return {
            "evidence_level": min(score, 5),
            "level_description": EVIDENCE_LEVELS[min(score, 5)],
            "reasons": reasons,
        }

    def _confidence(self, level: int) -> str:
        if level >= 4:
            return "high"
        if level >= 3:
            return "medium"
        return "low"
