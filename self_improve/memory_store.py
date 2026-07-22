from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from lancedb import connect
from lancedb.table import Table


DB_DIR = Path(__file__).parent.parent / "config"
DB_PATH = DB_DIR / "memory.lance"


class MemoryStore:
    """Persistent memory store using LanceDB for semantic search.

    Supports multiple namespaces: reflections, lessons, skills, decisions.
    """

    def __init__(self, db_path: str | Path | None = None):
        self._db_path = Path(db_path) if db_path else DB_PATH
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._db = connect(str(self._db_path))
        self._tables: dict[str, Table] = {}

    def _get_table(self, namespace: str) -> Table:
        if namespace not in self._tables:
            try:
                self._tables[namespace] = self._db.open_table(namespace)
            except Exception:
                self._tables[namespace] = self._db.create_table(
                    namespace,
                    data=[{"text": "init", "metadata": "{}", "key": "init"}],
                )
        return self._tables[namespace]

    def save(self, namespace: str, key: str, text: str, metadata: dict[str, Any] | None = None) -> None:
        table = self._get_table(namespace)
        record = {
            "text": text,
            "key": key,
            "metadata": json.dumps(metadata or {}),
        }
        table.add([record])

    def search(self, namespace: str, query: str, limit: int = 5) -> list[dict]:
        table = self._get_table(namespace)
        try:
            results = table.search(query).limit(limit).to_list()
            return [
                {
                    "text": r["text"],
                    "key": r["key"],
                    "metadata": json.loads(r.get("metadata", "{}")),
                }
                for r in results
            ]
        except Exception:
            return []

    def get_all(self, namespace: str) -> list[dict]:
        table = self._get_table(namespace)
        try:
            results = table.to_pandas().to_dict("records")
            return [
                {
                    "text": r["text"],
                    "key": r["key"],
                    "metadata": json.loads(r.get("metadata", "{}")),
                }
                for r in results
            ]
        except Exception:
            return []

    def save_reflection(self, agent_role: str, reflection: str, task_id: str) -> None:
        self.save("reflections", task_id, reflection, {"agent": agent_role})

    def save_lesson(self, agent_role: str, lesson: str, source: str) -> None:
        self.save("lessons", source, lesson, {"agent": agent_role})

    def save_skill(self, name: str, content: str, category: str = "general") -> None:
        self.save("skills", name, content, {"category": category})

    def save_decision(self, decision: str, reasoning: str, task_id: str) -> None:
        self.save("decisions", task_id, decision, {"reasoning": reasoning})
