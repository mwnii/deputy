# Agent Hierarchy

## CEO (Chief Executive Officer)

**Role:** Strategic decisions, delegation, verification
**Model:** Groq Llama 3.3 70B
**Delegates to:** EA

The CEO never executes tasks directly. It analyzes the current state, makes strategic decisions, and delegates to the EA for task routing.

## EA (Executive Assistant)

**Role:** Task routing and coordination
**Model:** Groq Llama 3.3 70B
**Delegates to:** CMO, CFO, CTO, COO

The EA routes tasks based on type:
- Marketing/outreach → CMO
- Financial/platform → CFO
- Technical/automation → CTO
- Operations/client → COO

## CMO (Chief Marketing Officer)

**Role:** Marketing, outreach, content strategy
**Delegates to:** Outreach Agent, Content Agent

## CFO (Chief Financial Officer)

**Role:** Finance, invoicing, platform management
**Direct reports:** None (handles directly)

## CTO (Chief Technology Officer)

**Role:** Automation, tools, self-improvement
**Delegates to:** Automation Agent, Research Agent

## COO (Chief Operations Officer)

**Role:** Client work, operations, quality
**Delegates to:** Freelance Agent, Microtask Agent

## Worker Agents

| Agent | Role | Model |
|-------|------|-------|
| Outreach Agent | Cold email/DM campaigns | Groq Llama 3.1 8B |
| Content Agent | Blog posts, social media | Groq Llama 3.1 8B |
| Freelance Agent | Client deliverables | Groq Llama 3.1 8B |
| Microtask Agent | Platform tasks | Groq Llama 3.1 8B |
| Automation Agent | Script maintenance | Groq Llama 3.1 8B |
| Research Agent | Deep research | Groq Llama 3.1 8B |

## Adding New Agents

1. Create agent definition in `agents/`
2. Add to `.opencode/opencode.json`
3. Add routing in `orchestration/supervisor.py`
4. Update `AGENTS.md` if universal
