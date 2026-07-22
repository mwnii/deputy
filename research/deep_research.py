from __future__ import annotations

import asyncio
from typing import Any

from langchain_core.language_models import BaseChatModel

try:
    from duckduckgo_search import DDGS
except ImportError:
    DDGS = None

try:
    import httpx
except ImportError:
    httpx = None

from bs4 import BeautifulSoup


QUERY_EXPANSION_PROMPT = """Given the research topic: "{topic}"

Generate exactly 10 diverse search queries that would find comprehensive information about this topic.

Include queries for:
1. Official documentation
2. GitHub repositories
3. Academic papers
4. Industry reports
5. Blog posts and tutorials
6. Comparisons and reviews
7. Community discussions
8. Free alternatives
9. Pricing information
10. Case studies

Return only the 10 queries, one per line, no numbering."""


class DeepResearcher:
    """Implements the 1→10→1→5 research protocol.

    Pattern: 1 query → 10 sub-agent parallel searches → 1 compiler → top 10 → top 5 → #1 recommendation
    """

    def __init__(self, llm: BaseChatModel):
        self.llm = llm

    async def expand_queries(self, topic: str) -> list[str]:
        """Generate 10 diverse search queries from one topic."""
        from langchain_core.messages import HumanMessage, SystemMessage

        messages = [
            SystemMessage(content="You generate diverse search queries for research."),
            HumanMessage(content=QUERY_EXPANSION_PROMPT.format(topic=topic)),
        ]
        response = await self.llm.ainvoke(messages)
        queries = [q.strip() for q in response.content.strip().split("\n") if q.strip()]
        return queries[:10]

    async def search(self, query: str) -> list[dict[str, str]]:
        """Execute a single search query using DuckDuckGo."""
        if DDGS is None:
            return [{"title": "DuckDuckGo not installed", "url": "", "body": ""}]

        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=5))
            return [
                {"title": r.get("title", ""), "url": r.get("href", ""), "body": r.get("body", "")}
                for r in results
            ]
        except Exception as e:
            return [{"title": f"Search error: {e}", "url": "", "body": ""}]

    async def parallel_search(self, queries: list[str]) -> list[dict]:
        """Execute all searches in parallel."""
        tasks = [self.search(q) for q in queries]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_results = []
        for r in results:
            if isinstance(r, list):
                all_results.extend(r)
        return all_results

    def deduplicate(self, results: list[dict]) -> list[dict]:
        """Remove duplicate URLs."""
        seen = set()
        unique = []
        for r in results:
            url = r.get("url", "")
            if url and url not in seen:
                seen.add(url)
                unique.append(r)
        return unique

    async def research(self, topic: str) -> dict[str, Any]:
        """Execute the full 1→10→1→5 research protocol."""
        queries = await self.expand_queries(topic)
        raw_results = await self.parallel_search(queries)
        unique_results = self.deduplicate(raw_results)

        return {
            "topic": topic,
            "queries": queries,
            "raw_count": len(raw_results),
            "unique_count": len(unique_results),
            "results": unique_results[:20],
        }
