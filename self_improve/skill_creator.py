from __future__ import annotations

from pathlib import Path
from typing import Optional

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.language_models import BaseChatModel

from .memory_store import MemoryStore
from .skill_manager import SkillManager


SKILL_CREATION_PROMPT = """Based on the following task outcome and lessons learned, create a new reusable skill.

Task: {task_description}
Result: {task_result}
Success: {success}
Lessons: {lessons}

Create a skill that encapsulates the key knowledge needed to handle similar tasks in the future.

Format the skill as:
# [Skill Name]

## Description
[What this skill does]

## When to Use
[Conditions for applying this skill]

## Steps
1. [Step 1]
2. [Step 2]
...

## Tips
- [Important tip]
...

## Anti-patterns
- [What to avoid]
...

## Quality Checklist
- [ ] [Quality check]
...
"""


async def create_skill(
    llm: BaseChatModel,
    manager: SkillManager,
    task_description: str,
    task_result: str,
    success: bool,
    lessons: str,
    category: str = "general",
) -> str:
    """Create a new skill from task outcomes (Voyager pattern).

    This implements the Voyager skill library idea: successful task
    completions generate reusable skills that can be retrieved and
    applied to future tasks.
    """
    messages = [
        SystemMessage(content="You create reusable skills from task experience."),
        HumanMessage(
            content=SKILL_CREATION_PROMPT.format(
                task_description=task_description,
                task_result=task_result,
                success=str(success),
                lessons=lessons,
            )
        ),
    ]

    response = await llm.ainvoke(messages)
    skill_content = response.content

    # Extract skill name from the content (first heading)
    lines = skill_content.split("\n")
    skill_name = "unnamed_skill"
    for line in lines:
        if line.startswith("# "):
            skill_name = line[2:].strip()
            break

    manager.add_skill(skill_name, skill_content, category)
    return skill_name
