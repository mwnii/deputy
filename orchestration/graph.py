from __future__ import annotations

from typing import Literal, Optional

from langchain_core.language_models import BaseChatModel
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command

from .state import SystemState, AgentRole, TaskStatus
from .supervisor import create_supervisor
from .checkpoint import get_checkpointer


def build_system_graph(llm: BaseChatModel) -> StateGraph:
    """Build the main system orchestration graph."""

    builder = StateGraph(SystemState)

    # Supervisor nodes
    builder.add_node("ceo", create_supervisor(llm, AgentRole.CEO))
    builder.add_node("ea", create_supervisor(llm, AgentRole.EA))
    builder.add_node("cmo", create_supervisor(llm, AgentRole.CMO))
    builder.add_node("cfo", create_supervisor(llm, AgentRole.CFO))
    builder.add_node("cto", create_supervisor(llm, AgentRole.CTO))
    builder.add_node("coo", create_supervisor(llm, AgentRole.COO))

    # Processing nodes
    builder.add_node("route_task", _route_task)
    builder.add_node("execute_task", _execute_task)
    builder.add_node("verify_result", _verify_result)
    builder.add_node("handle_error", _handle_error)

    # CEO routes to EA for delegation
    builder.add_edge(START, "ceo")
    builder.add_conditional_edges(
        "ceo",
        _ceo_router,
        {
            "ea": "ea",
            "end": END,
        },
    )

    # EA routes to C-suite
    builder.add_conditional_edges(
        "ea",
        _ea_router,
        {
            "cmo": "cmo",
            "cfo": "cfo",
            "cto": "cto",
            "coo": "coo",
            "end": END,
        },
    )

    # C-suite routes to execution
    for role in ["cmo", "cfo", "cto", "coo"]:
        builder.add_conditional_edges(
            role,
            _csuite_router,
            {
                "route_task": "route_task",
                "end": END,
            },
        )

    # Execution flow
    builder.add_edge("route_task", "execute_task")
    builder.add_conditional_edges(
        "execute_task",
        _execution_router,
        {
            "verify": "verify_result",
            "error": "handle_error",
        },
    )

    # Verification flow
    builder.add_conditional_edges(
        "verify_result",
        _verification_router,
        {
            "accept": "ceo",
            "retry": "route_task",
            "escalate": END,
        },
    )

    # Error handling
    builder.add_conditional_edges(
        "handle_error",
        _error_router,
        {
            "retry": "route_task",
            "escalate": "ceo",
            "end": END,
        },
    )

    return builder


def compile_system_graph(llm: BaseChatModel):
    """Build and compile the system graph with checkpointing."""
    builder = build_system_graph(llm)
    checkpointer = get_checkpointer()
    return builder.compile(checkpointer=checkpointer)


# --- Router Functions ---

def _ceo_router(state: SystemState) -> Literal["ea", "end"]:
    """CEO decides whether to delegate or end."""
    if state.get("error"):
        return "ea"
    if state.get("task_queue") or state.get("current_task"):
        return "ea"
    return "end"


def _ea_router(state: SystemState) -> Literal["cmo", "cfo", "cto", "coo", "end"]:
    """EA routes to appropriate C-suite agent."""
    task = state.get("current_task")
    if not task:
        return "end"

    role = task.assigned_to
    routing = {
        AgentRole.CMO: "cmo",
        AgentRole.CFO: "cfo",
        AgentRole.CTO: "cto",
        AgentRole.COO: "coo",
    }
    return routing.get(role, "coo")


def _csuite_router(state: SystemState) -> Literal["route_task", "end"]:
    """C-suite agent decides whether to execute or end."""
    task = state.get("current_task")
    if task and task.status == TaskStatus.PENDING:
        return "route_task"
    return "end"


def _execution_router(state: SystemState) -> Literal["verify", "error"]:
    """Check if execution succeeded."""
    if state.get("error"):
        return "error"
    return "verify"


def _verification_router(state: SystemState) -> Literal["accept", "retry", "escalate"]:
    """Verify result quality."""
    task = state.get("current_task")
    if not task:
        return "escalate"
    if task.status == TaskStatus.COMPLETE:
        return "accept"
    if len(task.blockers) > 2:
        return "escalate"
    return "retry"


def _error_router(state: SystemState) -> Literal["retry", "escalate", "end"]:
    """Handle errors with retry logic."""
    task = state.get("current_task")
    if task and len(task.blockers) < 3:
        return "retry"
    if state.get("human_input_needed"):
        return "escalate"
    return "end"


# --- Processing Nodes ---

def _route_task(state: SystemState) -> dict:
    """Route the current task for execution."""
    task = state.get("current_task")
    if task:
        return {"active_agent": task.assigned_to}
    return {}


def _execute_task(state: SystemState) -> dict:
    """Execute the current task (placeholder for actual execution)."""
    task = state.get("current_task")
    if not task:
        return {"error": "No task to execute"}

    # In production, this would call the appropriate CrewAI crew
    # For now, mark as complete
    task.status = TaskStatus.COMPLETE
    task.result = "Task executed successfully (placeholder)"
    return {"current_task": task}


def _verify_result(state: SystemState) -> dict:
    """Verify task result quality."""
    task = state.get("current_task")
    if task and task.status == TaskStatus.COMPLETE:
        return {
            "completed_tasks": [*state.get("completed_tasks", []), task],
            "current_task": None,
        }
    return {}


def _handle_error(state: SystemState) -> dict:
    """Handle execution errors."""
    error = state.get("error", "Unknown error")
    task = state.get("current_task")
    if task:
        task.blockers.append(error)
        task.status = TaskStatus.BLOCKED
        return {
            "current_task": task,
            "error": None,
            "human_input_needed": True,
        }
    return {"error": None}
