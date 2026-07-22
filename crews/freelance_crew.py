from __future__ import annotations

from crewai import Agent, Crew, Process, Task


ANALYST_ROLE = "Platform Analyst"
ANALYST_GOAL = (
    "Analyze freelance platform opportunities (Fiverr, Upwork) "
    "and identify high-value gigs that match our skills."
)
ANALYST_BACKSTORY = (
    "You are an expert at finding profitable freelance opportunities. "
    "You know which gig categories pay well, how to optimize profiles, "
    "and how to price services competitively."
)

PROPOSAL_ROLE = "Proposal Writer"
PROPOSAL_ROLE = "Proposal Writer"
PROPOSAL_GOAL = (
    "Write compelling proposals and gig descriptions that win clients. "
    "Each proposal should be personalized, demonstrate value, and include "
    "relevant portfolio samples."
)
PROPOSAL_BACKSTORY = (
    "You are a skilled proposal writer who understands client psychology. "
    "You write proposals that address client pain points directly and "
    "demonstrate clear value propositions."
)

DELIVERABLE_ROLE = "Deliverable Manager"
DELIVERABLE_GOAL = (
    "Ensure all client deliverables meet quality standards, "
    "are delivered on time, and include proper documentation."
)
DELIVERABLE_BACKSTORY = (
    "You are a project manager who ensures flawless execution. "
    "You track deadlines, manage revisions, and maintain client satisfaction."
)


def create_freelance_crew(platform: str = "fiverr", gig_count: int = 3) -> Crew:
    """Create a freelance operations crew."""
    analyst = Agent(
        role=ANALYST_ROLE,
        goal=ANALYST_GOAL,
        backstory=ANALYST_BACKSTORY,
        verbose=True,
        allow_delegation=False,
        max_iter=3,
    )

    proposal_writer = Agent(
        role=PROPOSAL_ROLE,
        goal=PROPOSAL_GOAL,
        backstory=PROPOSAL_BACKSTORY,
        verbose=True,
        allow_delegation=False,
        max_iter=3,
    )

    deliverable_mgr = Agent(
        role=DELIVERABLE_ROLE,
        goal=DELIVERABLE_GOAL,
        backstory=DELIVERABLE_BACKSTORY,
        verbose=True,
        allow_delegation=False,
        max_iter=2,
    )

    analysis_task = Task(
        description=(
            f"Analyze {platform} for profitable gig opportunities.\n\n"
            "1. Identify top-paying categories\n"
            "2. Analyze competitor pricing\n"
            "3. Find underserved niches\n"
            "4. Calculate expected earnings per gig\n"
            f"5. Select top {gig_count} opportunities"
        ),
        expected_output=(
            "A ranked list of gig opportunities with pricing, "
            "competition analysis, and expected earnings."
        ),
        agent=analyst,
    )

    proposal_task = Task(
        description=(
            f"Write {gig_count} gig descriptions/proposals for {platform}.\n\n"
            "Each must:\n"
            "- Have an attention-grabbing title\n"
            "- Clearly state the value proposition\n"
            "- Include relevant examples\n"
            "- Be competitively priced\n"
            "- Have tiered pricing (basic/standard/premium)"
        ),
        expected_output=(
            f"{gig_count} complete gig listings with titles, descriptions, "
            "pricing tiers, and FAQ sections."
        ),
        agent=proposal_writer,
    )

    deliverable_task = Task(
        description=(
            "Create a deliverable management system:\n"
            "1. Quality checklist for each service type\n"
            "2. Delivery timeline template\n"
            "3. Revision handling protocol\n"
            "4. Client communication templates\n"
            "5. Post-delivery follow-up sequence"
        ),
        expected_output=(
            "A complete operational playbook for managing client deliverables."
        ),
        agent=deliverable_mgr,
    )

    return Crew(
        agents=[analyst, proposal_writer, deliverable_mgr],
        tasks=[analysis_task, proposal_task, deliverable_task],
        process=Process.sequential,
        verbose=True,
    )
