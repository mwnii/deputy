from __future__ import annotations

import asyncio
from typing import Any

try:
    import httpx
except ImportError:
    httpx = None


class GitHubScanner:
    """Scans GitHub for trending repos, stars, and license info."""

    GITHUB_API = "https://api.github.com"

    async def search_repos(self, query: str, sort: str = "stars", limit: int = 10) -> list[dict]:
        """Search GitHub repos."""
        if httpx is None:
            return []

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{self.GITHUB_API}/search/repositories",
                    params={"q": query, "sort": sort, "per_page": limit},
                    headers={"Accept": "application/vnd.github.v3+json"},
                    timeout=15,
                )
                data = resp.json()
                return [
                    {
                        "name": r["full_name"],
                        "url": r["html_url"],
                        "stars": r["stargazers_count"],
                        "forks": r["forks_count"],
                        "license": r.get("license", {}).get("spdx_id", "None") if r.get("license") else "None",
                        "description": r.get("description", ""),
                        "language": r.get("language", ""),
                        "updated": r.get("updated_at", ""),
                    }
                    for r in data.get("items", [])[:limit]
                ]
            except Exception:
                return []

    async def get_trending(self, language: str = "", since: str = "weekly") -> list[dict]:
        """Get trending repos (uses unofficial endpoint)."""
        if httpx is None:
            return []

        url = f"https://api.gitterapp.com/repositories?since={since}"
        if language:
            url += f"&language={language}"

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(url, timeout=15)
                return resp.json()[:10]
            except Exception:
                return []

    async def compare_tools(self, tools: list[str]) -> list[dict]:
        """Compare multiple tools by searching for each."""
        tasks = [self.search_repos(t, limit=3) for t in tools]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        comparisons = []
        for tool, result in zip(tools, results):
            if isinstance(result, list) and result:
                best = max(result, key=lambda x: x.get("stars", 0))
                comparisons.append({
                    "tool": tool,
                    "top_repo": best.get("name", ""),
                    "stars": best.get("stars", 0),
                    "license": best.get("license", "None"),
                    "url": best.get("url", ""),
                })
        return comparisons
