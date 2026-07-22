from __future__ import annotations

import json
from typing import Any
from pathlib import Path

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage


REPORT_TEMPLATE = """# Research Report: {topic}

**Generated:** {date}
**Evidence Levels:** 5=Best, 1=Weakest

## Executive Summary

{summary}

## Top Findings

{findings}

## Recommendations

{recommendations}

## Source Details

{sources}
"""


class ReportCompiler:
    """Compiles research findings into structured reports."""

    def __init__(self, llm: BaseChatModel):
        self.llm = llm

    async def compile(self, research_data: dict, evidence_evaluations: list[dict]) -> str:
        """Compile research data and evidence evaluations into a report."""
        from datetime import datetime

        findings_text = self._format_findings(research_data.get("results", []), evidence_evaluations)
        summary = await self._generate_summary(research_data)
        recommendations = await self._generate_recommendations(research_data, evidence_evaluations)

        report = REPORT_TEMPLATE.format(
            topic=research_data.get("topic", "Unknown"),
            date=datetime.now().isoformat(),
            summary=summary,
            findings=findings_text,
            recommendations=recommendations,
            sources=self._format_sources(research_data.get("results", [])),
        )
        return report

    async def _generate_summary(self, data: dict) -> str:
        from datetime import datetime
        messages = [
            SystemMessage(content="You write concise research summaries."),
            HumanMessage(content=f"Summarize this research in 3-5 sentences:\n{json.dumps(data.get('results', [])[:5], indent=2)}"),
        ]
        resp = await self.llm.ainvoke(messages)
        return resp.content

    async def _generate_recommendations(self, data: dict, evaluations: list[dict]) -> str:
        messages = [
            SystemMessage(content="You generate data-backed recommendations."),
            HumanMessage(
                content=(
                    f"Based on this research and evidence evaluation, "
                    f"provide 3-5 prioritized recommendations:\n\n"
                    f"Research: {json.dumps(data.get('results', [])[:5], indent=2)}\n\n"
                    f"Evidence: {json.dumps(evaluations[:5], indent=2)}"
                )
            ),
        ]
        resp = await self.llm.ainvoke(messages)
        return resp.content

    def _format_findings(self, results: list[dict], evaluations: list[dict]) -> str:
        lines = []
        for i, r in enumerate(results[:10]):
            ev = evaluations[i] if i < len(evaluations) else {}
            level = ev.get("evidence_level", "?")
            lines.append(f"### {i+1}. {r.get('title', 'Untitled')}")
            lines.append(f"- **URL:** {r.get('url', 'N/A')}")
            lines.append(f"- **Evidence Level:** {level}/5")
            lines.append(f"- **Summary:** {r.get('body', r.get('summary', 'N/A'))[:200]}")
            lines.append("")
        return "\n".join(lines) if lines else "No findings compiled."

    def _format_sources(self, results: list[dict]) -> str:
        lines = []
        for i, r in enumerate(results[:10], 1):
            lines.append(f"{i}. [{r.get('title', 'Untitled')}]({r.get('url', '#')})")
        return "\n".join(lines) if lines else "No sources."

    def save(self, report: str, filename: str) -> str:
        """Save report to vault."""
        path = Path(__file__).parent.parent / "vault" / "03-REPORTS" / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(report, encoding="utf-8")
        return str(path)
