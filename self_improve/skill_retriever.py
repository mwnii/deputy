from __future__ import annotations

from .memory_store import MemoryStore


class SkillRetriever:
    """Retrieves skills from the library for use in task execution."""

    def __init__(self, store: MemoryStore | None = None):
        self.store = store or MemoryStore()

    def retrieve(self, query: str, limit: int = 3) -> list[str]:
        """Retrieve skills relevant to a query."""
        results = self.store.search("skills", query, limit)
        return [r["text"] for r in results]

    def retrieve_for_agent(self, agent_role: str, task_type: str) -> list[str]:
        """Retrieve skills for a specific agent and task type."""
        query = f"{agent_role} {task_type}"
        return self.retrieve(query)


def retrieve_skills(store: MemoryStore, query: str, limit: int = 3) -> list[str]:
    """Convenience function for skill retrieval."""
    retriever = SkillRetriever(store)
    return retriever.retrieve(query, limit)
