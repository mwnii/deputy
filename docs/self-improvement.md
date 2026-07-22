# Self-Improvement Engine

## Overview

The system implements 5 training-free learning patterns that allow it to improve over time without fine-tuning.

## 1. Reflexion (Verbal Reflection)

After each task, the agent generates a verbal reflection covering:
- What went well
- What went wrong
- What to do differently
- Specific lessons for future tasks

**File:** `self_improve/reflection.py`

## 2. Voyager (Skill Library)

Successful task completions generate reusable skills stored in:
- `vault/04-SKILLS/` (markdown files)
- LanceDB (semantic search index)

Skills are retrieved before task execution to inform decisions.

**Files:** `self_improve/skill_manager.py`, `self_improve/skill_retriever.py`

## 3. SkillForge (Failure-Driven Evolution)

Skills evolve through experience:
- Failures trigger skill refinement
- Anti-patterns are identified and removed
- Quality checklists are updated

**File:** `self_improve/skill_evolver.py`

## 4. ExpeL (Insight Extraction)

After batches of tasks, the system extracts:
- Positive patterns (what worked)
- Negative patterns (what failed)
- Generalizable lessons

**File:** `self_improve/lesson_extractor.py`

## 5. OPRO (Prompt Optimization)

Prompts are optimized based on performance feedback:
- Current prompt + performance context → optimized prompt
- Lessons from past optimizations inform future ones

**File:** `self_improve/prompt_optimizer.py`

## Memory Store

All learning artifacts are stored in LanceDB with semantic search:

| Namespace | Content |
|-----------|---------|
| reflections | Task reflections |
| lessons | Extracted lessons |
| skills | Reusable skills |
| decisions | Strategic decisions |

**File:** `self_improve/memory_store.py`
