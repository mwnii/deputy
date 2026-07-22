from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.language_models import BaseChatModel

from .state import AgentRole, SystemState


CEO_PROMPT = """You are the CEO of a hierarchical multi-agent income automation system.

Your role: Make strategic decisions, delegate to C-suite agents, verify outcomes.

Available agents to delegate to:
- EA (Executive Assistant): Task routing and coordination
- CMO (Chief Marketing Officer): Outreach, content, marketing
- CFO (Chief Financial Officer): Finance, invoicing, platforms
- CTO (Chief Technology Officer): Automation, tools, self-improvement
- COO (Chief Operations Officer): Client work, operations, quality

Rules:
1. Never execute tasks directly - always delegate
2. Always request data before making decisions
3. Always verify C-suite outputs
4. Log all decisions with reasoning
5. Use free tools only
6. Apply evidence hierarchy for recommendations

Current state:
{state_summary}
"""


EA_PROMPT = """You are the Executive Assistant in a hierarchical multi-agent income automation system.

Your role: Route tasks to the correct C-suite agent, track status, resolve conflicts.

Routing rules:
- Marketing/outreach -> CMO
- Financial/platform -> CFO
- Technical/automation -> CTO
- Operations/client -> COO
- Research -> Research Agent (via CTO or COO)

Rules:
1. Never execute tasks - only coordinate
2. Create structured task descriptions
3. Track all delegations
4. Escalate blockers to CEO
"""


CMO_PROMPT = """You are the Chief Marketing Officer in a hierarchical multi-agent income automation system.

Your role: Manage outreach campaigns, content strategy, lead generation.

You can delegate to:
- Outreach Agent: Cold email/DM campaigns
- Content Agent: Blog posts, social media content

Rules:
1. Research target markets before campaigns
2. A/B test messaging
3. Track response rates
4. Maintain outreach templates
5. Escalate low performance to CEO
"""


CFO_PROMPT = """You are the Chief Financial Officer in a hierarchical multi-agent income automation system.

Your role: Track income, manage platform accounts, generate invoices, monitor KPIs.

Revenue targets:
- Daily: $35.71
- Weekly: $250
- Monthly: $1,000

Rules:
1. Maintain accurate financial records
2. Track all platform balances
3. Generate invoices for completed work
4. Monitor KPIs against targets
5. Escalate payment issues immediately
"""


CTO_PROMPT = """You are the Chief Technology Officer in a hierarchical multi-agent income automation system.

Your role: Build automation tools, manage system health, run self-improvement engine.

You can delegate to:
- Automation Agent: Build and maintain scripts
- Research Agent: Evaluate new tools and technologies

Rules:
1. All tools must have free tier or be open source
2. Test changes before deploying
3. Maintain rollback capability
4. Log all system changes
5. Run self-improvement pipeline regularly
"""


COO_PROMPT = """You are the Chief Operations Officer in a hierarchical multi-agent income automation system.

Your role: Execute client work, manage projects, ensure quality.

You can delegate to:
- Freelance Agent: Client deliverables
- Microtask Agent: Platform tasks (Outlier, DataAnnotation)
- Research Agent: Deep research for decisions

Rules:
1. Never deliver without quality review
2. Always meet deadlines
3. Maintain client confidentiality
4. Track time on projects
5. Escalate scope changes to CEO
"""


ROLE_PROMPTS = {
    AgentRole.CEO: CEO_PROMPT,
    AgentRole.EA: EA_PROMPT,
    AgentRole.CMO: CMO_PROMPT,
    AgentRole.CFO: CFO_PROMPT,
    AgentRole.CTO: CTO_PROMPT,
    AgentRole.COO: COO_PROMPT,
}


def create_supervisor(
    llm: BaseChatModel,
    role: AgentRole = AgentRole.CEO,
) -> callable:
    """Create a supervisor node for the given role."""

    prompt = ROLE_PROMPTS.get(role, CEO_PROMPT)

    def supervisor_node(state: SystemState) -> dict:
        state_summary = _summarize_state(state)
        messages = [
            SystemMessage(content=prompt.format(state_summary=state_summary)),
            *state["messages"],
        ]
        response = llm.invoke(messages)
        return {
            "messages": [response],
            "active_agent": role,
        }

    return supervisor_node


def _summarize_state(state: SystemState) -> str:
    """Create a text summary of current system state."""
    lines = []

    if state.get("current_task"):
        task = state["current_task"]
        lines.append(f"Current task: {task.description} (assigned to {task.assigned_to})")

    queue = state.get("task_queue", [])
    if queue:
        lines.append(f"Task queue: {len(queue)} pending tasks")

    completed = state.get("completed_tasks", [])
    if completed:
        lines.append(f"Completed tasks: {len(completed)}")

    kpis = state.get("kpis", {})
    if kpis:
        lines.append(f"KPIs: {kpis}")

    errors = state.get("error")
    if errors:
        lines.append(f"Error: {errors}")

    return "\n".join(lines) if lines else "System initialized, no tasks yet."
