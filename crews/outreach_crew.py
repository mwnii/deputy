from __future__ import annotations

from crewai import Agent, Crew, Process, Task


STRATEGIST_ROLE = "Outreach Strategist"
STRATEGIST_GOAL = (
    "Design data-backed cold outreach campaigns targeting US businesses "
    "in San Antonio, Miami, Atlanta, Memphis, and Tampa. "
    "Focus on AI-powered freelancing and content services."
)
STRATEGIST_BACKSTORY = (
    "You are an expert at crafting personalized cold outreach that converts. "
    "You understand US small business pain points and can position AI services "
    "as solutions. You never spam - every message is researched and targeted."
)

WRITER_ROLE = "Outreach Copywriter"
WRITER_GOAL = (
    "Write compelling, personalized cold emails and DMs that get responses. "
    "Each message should be under 150 words, reference the prospect specifically, "
    "and include a clear call-to-action."
)
WRITER_BACKSTORY = (
    "You are a skilled copywriter who specializes in cold outreach. "
    "You write concise, warm, personalized messages that feel human "
    "and avoid spam triggers."
)

ANALYST_ROLE = "Outreach Analyst"
ANALYST_GOAL = (
    "Track outreach metrics, analyze response rates, and recommend "
    "optimizations to improve campaign performance."
)
ANALYST_BACKSTORY = (
    "You are a data-driven analyst who monitors outreach KPIs "
    "and uses A/B testing insights to continuously improve results."
)


def create_outreach_crew(target_market: str, message_count: int = 5) -> Crew:
    """Create an outreach crew for cold campaigns."""
    strategist = Agent(
        role=STRATEGIST_ROLE,
        goal=STRATEGIST_GOAL,
        backstory=STRATEGIST_BACKSTORY,
        verbose=True,
        allow_delegation=False,
        max_iter=3,
    )

    writer = Agent(
        role=WRITER_ROLE,
        goal=WRITER_GOAL,
        backstory=WRITER_BACKSTORY,
        verbose=True,
        allow_delegation=False,
        max_iter=3,
    )

    analyst = Agent(
        role=ANALYST_ROLE,
        goal=ANALYST_GOAL,
        backstory=ANALYST_BACKSTORY,
        verbose=True,
        allow_delegation=False,
        max_iter=2,
    )

    strategy_task = Task(
        description=(
            f"Create an outreach strategy for: {target_market}\n\n"
            f"Include:\n"
            f"1. Target audience personas (3-5)\n"
            f"2. Value propositions for each persona\n"
            f"3. Channel selection (email, LinkedIn, Twitter)\n"
            f"4. Timing and frequency recommendations\n"
            f"5. Success metrics and thresholds"
        ),
        expected_output=(
            "A complete outreach strategy document with personas, "
            "value props, channel plan, and success metrics."
        ),
        agent=strategist,
    )

    copy_task = Task(
        description=(
            f"Write {message_count} cold outreach messages for the target market.\n\n"
            "Each message must:\n"
            "- Be under 150 words\n"
            "- Reference a specific pain point\n"
            "- Include a clear CTA\n"
            "- Feel personal, not templated\n"
            "- Include 2 variants for A/B testing"
        ),
        expected_output=(
            f"{message_count} pairs of outreach messages (A/B variants) "
            "with subject lines, body text, and CTA."
        ),
        agent=writer,
    )

    analysis_task = Task(
        description=(
            "Create a tracking spreadsheet template and analysis framework "
            "for outreach campaigns. Include:\n"
            "- Response rate benchmarks\n"
            "- Conversion funnel metrics\n"
            "- A/B test analysis methodology\n"
            "- Weekly reporting template"
        ),
        expected_output=(
            "A complete outreach analytics framework with templates "
            "and benchmark targets."
        ),
        agent=analyst,
    )

    return Crew(
        agents=[strategist, writer, analyst],
        tasks=[strategy_task, copy_task, analysis_task],
        process=Process.sequential,
        verbose=True,
    )
