from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.language_models import BaseChatModel


EVALUATION_PROMPT = """Evaluate the quality of a task result.

Task: {task_description}
Result: {task_result}
Success Criteria: {success_criteria}

Rate on a scale of 1-10:
1. Completeness (did it cover everything?)
2. Quality (is it well-executed?)
3. Accuracy (is it correct?)
4. Timeliness (was it on time?)
5. Innovation (did it go above and beyond?)

Provide:
- Score for each dimension (1-10)
- Overall score (average)
- Specific improvements needed
- Pass/Fail recommendation (pass >= 7)"""


async def evaluate_task(
    llm: BaseChatModel,
    task_description: str,
    task_result: str,
    success_criteria: str = "Complete the task accurately and on time",
) -> dict:
    """Evaluate a task result against success criteria."""
    messages = [
        SystemMessage(content="You are a quality evaluator for task results."),
        HumanMessage(
            content=EVALUATION_PROMPT.format(
                task_description=task_description,
                task_result=task_result,
                success_criteria=success_criteria,
            )
        ),
    ]

    response = await llm.ainvoke(messages)
    return {
        "evaluation": response.content,
        "task_description": task_description,
    }
