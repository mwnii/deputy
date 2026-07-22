from __future__ import annotations

import os
from pathlib import Path

from langgraph.checkpoint.sqlite import SqliteSaver


DB_DIR = Path(__file__).parent.parent / "config"
DB_PATH = DB_DIR / "checkpoints.db"


def get_checkpointer() -> SqliteSaver:
    """Create and configure SQLite checkpointer for LangGraph."""
    DB_DIR.mkdir(parents=True, exist_ok=True)

    checkpointer = SqliteSaver.from_conn_string(str(DB_PATH))
    checkpointer.setup()
    return checkpointer


def get_thread_config(thread_id: str = "default") -> dict:
    """Get LangGraph config with thread ID for checkpointing."""
    return {"configurable": {"thread_id": thread_id}}
