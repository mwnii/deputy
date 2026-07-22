from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.language_models import BaseChatModel

from .memory_store import MemoryStore


EXPEL_PROMPT = """You are analyzing task outcomes to extract reusable lessons.

Recent task outcomes:
{task_outcomes}

For each task, extract:
1. What worked well (positive patterns)
2. What failed (anti-patterns)
3. A generalizable lesson that can be applied to future tasks

Format each lesson as:
- Pattern: [description]
- Type: positive/negative
- Applicability: [when to use this lesson]
- Confidence: [high/medium/low] based on how many times you've seen this pattern

Return a structured list of lessons."""


async def extract_lessons(
    llm: BaseChatModel,
    store: MemoryStore,
    task_outcomes: list[dict],
    agent_role: str = "general",
) -> list[dict]:
    """Extract lessons from task outcomes using the ExpeL pattern.

    Analyzes both successful and failed tasks to identify patterns
    that can inform future decisions.
    """
    outcomes_text = "\n".join(
        f"Task: {o.get('description', 'N/A')}\n"
        f"Result: {o.get('result', 'N/A')}\n"
        f"Success: {o.get('success', False)}\n"
        f"Blockers: {', '.join(o.get('blockers', []))}\n"
        for o in task_outcomes
    )

    messages = [
        SystemMessage(content="You extract actionable lessons from task outcomes."),
        HumanMessage(content=EXPEL_PROMPT.format(task_outcomes=outcomes_text)),
    ]

    response = await llm.ainvoke(messages)
    lesson_text = response.content

    # Store the extracted lessons
    for i, outcome in enumerate(task_outcomes):
        task_id = outcome.get("task_id", f"task_{i}")
        store.save_lesson(agent_role, lesson_text, task_id)

    return [{"lessons": lesson_text, "source_tasks": [o.get("task_id") for o in task_outcomes]}]
