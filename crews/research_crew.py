from __future__ import annotations

from crewai import Agent, Crew, Process, Task


RESEARCHER_ROLE = "Senior Research Analyst"
RESEARCHER_GOAL = (
    "Conduct thorough research using only free tools and sources. "
    "Apply the evidence hierarchy (Level 5 to Level 1) to all findings. "
    "Use the 1->10->1->5 research protocol for comprehensive analysis."
)
RESEARCHER_BACKSTORY = (
    "You are an expert researcher skilled at finding high-quality, actionable "
    "information from free sources. You specialize in evaluating evidence quality "
    "and synthesizing findings into clear, data-backed recommendations."
)

COMPILER_ROLE = "Research Compiler"
COMPILER_GOAL = (
    "Compile research findings into structured reports with evidence levels, "
    "source credibility ratings, and actionable recommendations."
)
COMPILER_BACKSTORY = (
    "You excel at organizing complex research into clear, prioritized reports "
    "that drive decision-making. You always include source URLs, evidence levels, "
    "and confidence scores."
)

VERIFIER_ROLE = "Research Verifier"
VERIFIER_GOAL = (
    "Verify research findings by cross-referencing multiple sources and "
    "flagging any inconsistencies or low-evidence claims."
)
VERIFIER_BACKSTORY = (
    "You are a meticulous fact-checker who ensures all research claims are "
    "supported by at least two independent sources at Level 3+ evidence."
)


def create_research_crew(topic: str, max_findings: int = 10) -> Crew:
    """Create a research crew for the 1->10->1->5 protocol."""
    researcher = Agent(
        role=RESEARCHER_ROLE,
        goal=RESEARCHER_GOAL,
        backstory=RESEARCHER_BACKSTORY,
        verbose=True,
        allow_delegation=False,
        max_iter=3,
    )

    compiler = Agent(
        role=COMPILER_ROLE,
        goal=COMPILER_GOAL,
        backstory=COMPILER_BACKSTORY,
        verbose=True,
        allow_delegation=False,
        max_iter=2,
    )

    verifier = Agent(
        role=VERIFIER_ROLE,
        goal=VERIFIER_GOAL,
        backstory=VERIFIER_BACKSTORY,
        verbose=True,
        allow_delegation=False,
        max_iter=2,
    )

    research_task = Task(
        description=(
            f"Research the following topic thoroughly: {topic}\n\n"
            f"Use the 1->10->1->5 protocol:\n"
            f"1. Generate 10 search queries\n"
            f"2. Execute all 10 searches in parallel\n"
            f"3. Compile top 10 findings\n"
            f"4. Select top 5 by evidence level\n"
            f"5. Recommend #1 with full reasoning\n\n"
            f"Return findings as structured data with: source URL, title, "
            f"evidence level (1-5), stars (if repo), license, free tier status, summary."
        ),
        expected_output=(
            f"A JSON-structured report with {max_findings} findings, each containing: "
            f"source, url, title, evidence_level (1-5), stars, license, free_tier, summary. "
            f"Plus a final recommendation section."
        ),
        agent=researcher,
    )

    compile_task = Task(
        description=(
            "Compile all research findings into a prioritized report. "
            "Group by evidence level (Level 5 first, then 4, 3, 2, 1). "
            "Include a confidence score for each finding. "
            "Provide a final #1 recommendation with reasoning."
        ),
        expected_output=(
            "A structured research report with: "
            "- Executive summary\n"
            "- Findings by evidence level\n"
            "- Confidence scores\n"
            "- Top 5 ranked recommendations\n"
            "- #1 recommendation with full justification"
        ),
        agent=compiler,
    )

    verify_task = Task(
        description=(
            "Verify the compiled research report. Check that:\n"
            "1. All sources are real and accessible\n"
            "2. Evidence levels are accurately assigned\n"
            "3. No contradictions exist between findings\n"
            "4. Recommendations are supported by evidence\n"
            "Flag any issues found."
        ),
        expected_output=(
            "A verification report noting any issues found, "
            "with a final confidence rating for the overall report."
        ),
        agent=verifier,
    )

    return Crew(
        agents=[researcher, compiler, verifier],
        tasks=[research_task, compile_task, verify_task],
        process=Process.sequential,
        verbose=True,
    )
