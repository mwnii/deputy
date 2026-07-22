from __future__ import annotations

from typing import Optional

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.language_models import BaseChatModel

from .memory_store import MemoryStore
from .skill_manager import SkillManager


SKILL_EVOLUTION_PROMPT = """You have an existing skill and a new task outcome. Evolve the skill based on the new experience.

## Existing Skill
{existing_skill}

## New Task
{task_description}

## Result
{task_result}

## New Lessons
{lessons}

Evolve the skill by:
1. Adding new patterns discovered
2. Removing patterns that proved ineffective
3. Updating the quality checklist
4. Refining the steps based on what actually worked
5. Updating anti-patterns

Return the improved skill in the same format."""


async def evolve_skill(
    llm: BaseChatModel,
    manager: SkillManager,
    skill_name: str,
    task_description: str,
    task_result: str,
    lessons: str,
) -> str:
    """Evolve an existing skill based on new experience.

    This implements the SkillForge pattern: skills evolve through
    experience, with failures driving refinement.
    """
    existing = manager.get_skill(skill_name)
    if not existing:
        return skill_name

    messages = [
        SystemMessage(content="You evolve skills based on experience."),
        HumanMessage(
            content=SKILL_EVOLUTION_PROMPT.format(
                existing_skill=existing.get("text", ""),
                task_description=task_description,
                task_result=task_result,
                lessons=lessons,
            )
        ),
    ]

    response = await llm.ainvoke(messages)
    evolved_content = response.content

    manager.add_skill(skill_name, evolved_content, "evolved")
    return skill_name
