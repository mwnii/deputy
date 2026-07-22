from __future__ import annotations

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field
from langgraph.graph import MessagesState


class AgentRole(str, Enum):
    CEO = "ceo"
    EA = "ea"
    CMO = "cmo"
    CFO = "cfo"
    CTO = "cto"
    COO = "coo"
    OUTREACH = "outreach"
    CONTENT = "content"
    FREELANCE = "freelance"
    MICROTASK = "microtask"
    AUTOMATION = "automation"
    RESEARCH = "research"


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    BLOCKED = "blocked"
    FAILED = "failed"


class TaskRecord(BaseModel):
    task_id: str
    description: str
    assigned_to: AgentRole
    priority: str = "medium"
    status: TaskStatus = TaskStatus.PENDING
    deadline: Optional[str] = None
    success_criteria: Optional[str] = None
    context: Optional[str] = None
    result: Optional[str] = None
    blockers: list[str] = Field(default_factory=list)


class ResearchFinding(BaseModel):
    source: str
    url: str
    title: str
    evidence_level: int = 1
    stars: int = 0
    license: str = "unknown"
    free_tier: bool = False
    summary: str = ""


class SystemState(MessagesState):
    """Main state schema for the income system graph."""

    current_task: Optional[TaskRecord] = None
    task_queue: list[TaskRecord] = Field(default_factory=list)
    completed_tasks: list[TaskRecord] = Field(default_factory=list)

    active_agent: AgentRole = AgentRole.CEO
    active_crew: Optional[str] = None

    research_findings: list[ResearchFinding] = Field(default_factory=list)
    research_report: Optional[str] = None

    kpis: dict[str, Any] = Field(default_factory=dict)
    decisions: list[dict[str, Any]] = Field(default_factory=list)

    skills_created: list[str] = Field(default_factory=list)
    reflections: list[str] = Field(default_factory=list)

    error: Optional[str] = None
    human_input_needed: bool = False
    human_input: Optional[str] = None
