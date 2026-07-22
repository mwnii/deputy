from __future__ import annotations

from pathlib import Path
from typing import Any, Optional
import json

from .memory_store import MemoryStore


SKILLS_DIR = Path(__file__).parent.parent / "vault" / "04-SKILLS"


class SkillManager:
    """Manages the Voyager-style skill library.

    Skills are stored as markdown files in vault/04-SKILLS/ and indexed
    in LanceDB for semantic retrieval.
    """

    def __init__(self, store: MemoryStore | None = None):
        self.store = store or MemoryStore()
        SKILLS_DIR.mkdir(parents=True, exist_ok=True)

    def add_skill(self, name: str, content: str, category: str = "general") -> None:
        """Add a new skill to the library."""
        # Save to LanceDB for semantic search
        self.store.save_skill(name, content, category)

        # Save as markdown file
        skill_file = SKILLS_DIR / f"{name.lower().replace(' ', '_')}.md"
        skill_file.write_text(
            f"# {name}\n\n"
            f"**Category:** {category}\n\n"
            f"## Content\n\n{content}\n",
            encoding="utf-8",
        )

    def get_skill(self, name: str) -> Optional[dict]:
        """Retrieve a skill by name."""
        results = self.store.search("skills", name, limit=1)
        return results[0] if results else None

    def search_skills(self, query: str, limit: int = 5) -> list[dict]:
        """Search skills by semantic similarity."""
        return self.store.search("skills", query, limit)

    def list_all_skills(self) -> list[str]:
        """List all skill names."""
        all_skills = self.store.get_all("skills")
        return [s["key"] for s in all_skills]

    def count(self) -> int:
        """Count total skills."""
        return len(self.store.get_all("skills"))
