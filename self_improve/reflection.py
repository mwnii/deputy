from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.language_models import BaseChatModel


REFLEXION_PROMPT = """You are an AI agent reflecting on a completed task.

Task: {task_description}
Result: {task_result}
Success: {success}
Blockers: {blockers}

Provide a verbal reflection (not code) covering:
1. What went well?
2. What went wrong?
3. What would you do differently next time?
4. What specific lesson can be applied to future tasks?

Be concise and actionable. This reflection will be stored and used to improve future performance."""


async def verbal_reflection(
    llm: BaseChatModel,
    task_description: str,
    task_result: str,
    success: bool,
    blockers: list[str] | None = None,
) -> str:
    """Generate a verbal reflection on a completed task (Reflexion pattern).

    This implements the core Reflexion idea: agents improve by verbally
    reflecting on failures/successes rather than updating weights.
    """
    prompt = REFLEXION_PROMPT.format(
        task_description=task_description,
        task_result=task_result,
        success=str(success),
        blockers=", ".join(blockers) if blockers else "None",
    )

    messages = [
        SystemMessage(content="You are a self-reflective AI agent focused on continuous improvement."),
        HumanMessage(content=prompt),
    ]

    response = await llm.ainvoke(messages)
    return response.content


async def batch_reflect(
    llm: BaseChatModel,
    tasks: list[dict],
) -> list[str]:
    """Reflect on multiple tasks and return reflections."""
    reflections = []
    for task in tasks:
        reflection = await verbal_reflection(
            llm,
            task_description=task.get("description", ""),
            task_result=task.get("result", ""),
            success=task.get("success", False),
            blockers=task.get("blockers", []),
        )
        reflections.append(reflection)
    return reflections
