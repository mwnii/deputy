from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.language_models import BaseChatModel

from .memory_store import MemoryStore


OPRO_PROMPT = """You are optimizing a prompt for better performance.

## Current Prompt
{current_prompt}

## Performance Context
{performance_context}

## Lessons Learned
{lessons}

Optimize the prompt by:
1. Making instructions clearer and more specific
2. Adding examples where helpful
3. Removing unnecessary instructions
4. Improving output format specifications
5. Adding constraints that improve quality

Return the optimized prompt only, no explanation."""


async def optimize_prompt(
    llm: BaseChatModel,
    store: MemoryStore,
    current_prompt: str,
    performance_context: str,
    prompt_name: str = "default",
) -> str:
    """Optimize a prompt using the OPRO pattern.

    Google DeepMind's OPRO (Optimization by PROmpting) approach:
    use an LLM to optimize prompts based on performance feedback.
    """
    # Get past lessons for this prompt
    past_lessons = store.search("lessons", prompt_name, limit=5)
    lessons_text = "\n".join([l["text"] for l in past_lessons]) if past_lessons else "No past lessons yet."

    messages = [
        SystemMessage(content="You optimize prompts for better LLM performance."),
        HumanMessage(
            content=OPRO_PROMPT.format(
                current_prompt=current_prompt,
                performance_context=performance_context,
                lessons=lessons_text,
            )
        ),
    ]

    response = await llm.ainvoke(messages)
    optimized = response.content

    # Store the optimization as a lesson
    store.save_lesson(
        "prompt_optimizer",
        f"Optimized prompt '{prompt_name}': {optimized[:200]}...",
        f"opt_{prompt_name}",
    )

    return optimized
