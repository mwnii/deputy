from __future__ import annotations

from typing import Any

from langchain_core.language_models import BaseChatModel

try:
    import httpx
except ImportError:
    httpx = None

from bs4 import BeautifulSoup


class AcademicResearcher:
    """Searches arxiv, Google Scholar, and Semantic Scholar for papers."""

    ARXIV_API = "http://export.arxiv.org/api/query"
    SEMANTIC_API = "https://api.semanticscholar.org/graph/v1/paper/search"

    def __init__(self, llm: BaseChatModel):
        self.llm = llm

    async def search_arxiv(self, query: str, max_results: int = 5) -> list[dict]:
        """Search arxiv for papers."""
        if httpx is None:
            return []

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    self.ARXIV_API,
                    params={"search_query": f"all:{query}", "max_results": max_results, "sortBy": "relevance"},
                    timeout=15,
                )
                return self._parse_arxiv(resp.text)
            except Exception:
                return []

    def _parse_arxiv(self, xml_text: str) -> list[dict]:
        """Parse arxiv Atom XML."""
        soup = BeautifulSoup(xml_text, "html.parser")
        papers = []
        for entry in soup.find_all("entry"):
            title = entry.find("title").get_text(strip=True) if entry.find("title") else ""
            summary = entry.find("summary").get_text(strip=True) if entry.find("summary") else ""
            link = entry.find("id").get_text(strip=True) if entry.find("id") else ""
            authors = [a.get_text(strip=True) for a in entry.find_all("author")]
            papers.append({
                "title": title,
                "url": link,
                "summary": summary[:300],
                "authors": authors[:3],
                "source": "arxiv",
            })
        return papers

    async def search_semantic(self, query: str, max_results: int = 5) -> list[dict]:
        """Search Semantic Scholar."""
        if httpx is None:
            return []

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    self.SEMANTIC_API,
                    params={"query": query, "limit": max_results, "fields": "title,abstract,url,year,citationCount"},
                    timeout=15,
                )
                data = resp.json()
                return [
                    {
                        "title": p.get("title", ""),
                        "url": p.get("url", ""),
                        "summary": (p.get("abstract") or "")[:300],
                        "year": p.get("year"),
                        "citations": p.get("citationCount", 0),
                        "source": "semantic_scholar",
                    }
                    for p in data.get("data", [])
                ]
            except Exception:
                return []

    async def search_all(self, query: str, max_results: int = 5) -> list[dict]:
        """Search both arxiv and Semantic Scholar."""
        import asyncio
        arxiv_task = self.search_arxiv(query, max_results)
        semantic_task = self.search_semantic(query, max_results)
        arxiv_results, semantic_results = await asyncio.gather(arxiv_task, semantic_task)
        return arxiv_results + semantic_results
