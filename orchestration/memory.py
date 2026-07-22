from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from langgraph.store.memory import InMemoryStore


_store: Optional[InMemoryStore] = None


def get_store() -> InMemoryStore:
    """Get or create the cross-thread memory store."""
    global _store
    if _store is None:
        _store = InMemoryStore()
    return _store


def save_memory(namespace: tuple[str, ...], key: str, value: dict[str, Any]) -> None:
    """Save a memory item to the store."""
    store = get_store()
    store.put(namespace, key, value)


def recall_memory(namespace: tuple[str, ...], query: str, limit: int = 5) -> list[dict]:
    """Search memories by semantic similarity."""
    store = get_store()
    results = store.search(namespace, query=query, limit=limit)
    return [r.value for r in results] if results else []


def save_reflection(agent_role: str, reflection: str, task_id: str) -> None:
    """Save a verbal reflection (Reflexion pattern)."""
    save_memory(
        ("reflections", agent_role),
        task_id,
        {"reflection": reflection, "task_id": task_id},
    )


def save_skill(skill_name: str, skill_content: str, category: str = "general") -> None:
    """Save a skill to the library."""
    save_memory(
        ("skills", category),
        skill_name,
        {"name": skill_name, "content": skill_content},
    )


def save_lesson(agent_role: str, lesson: str, source_task: str) -> None:
    """Save an extracted lesson (ExpeL pattern)."""
    save_memory(
        ("lessons", agent_role),
        source_task,
        {"lesson": lesson, "source": source_task},
    )
