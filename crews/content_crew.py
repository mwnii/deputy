from __future__ import annotations

from crewai import Agent, Crew, Process, Task


PLANNER_ROLE = "Content Strategist"
PLANNER_GOAL = (
    "Develop a content calendar and strategy for LinkedIn, blog, "
    "and social media that showcases AI writing skills and attracts clients."
)
PLANNER_BACKSTORY = (
    "You are a content strategist who understands how to position "
    "AI-assisted writing services to attract clients organically. "
    "You focus on demonstrating expertise, not just talking about it."
)

WRITER_ROLE = "Content Writer"
WRITER_GOAL = (
    "Produce high-quality blog posts, LinkedIn articles, and social media "
    "content that demonstrates writing skill and attracts inbound leads."
)
WRITER_BACKSTORY = (
    "You are a skilled writer who produces engaging, well-researched content. "
    "You write in a clear, authoritative voice that builds trust. "
    "You never sound robotic or templated."
)

EDITOR_ROLE = "Content Editor"
EDITOR_GOAL = (
    "Review all content for quality, consistency, SEO, and brand voice. "
    "Ensure every piece meets professional publishing standards."
)
EDITOR_BACKSTORY = (
    "You are a meticulous editor who catches grammar issues, "
    "improves flow, optimizes for SEO, and ensures brand consistency. "
    "You use language tools and readability analysis."
)


def create_content_crew(content_type: str = "linkedin", count: int = 5) -> Crew:
    """Create a content creation crew."""
    planner = Agent(
        role=PLANNER_ROLE,
        goal=PLANNER_GOAL,
        backstory=PLANNER_BACKSTORY,
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

    editor = Agent(
        role=EDITOR_ROLE,
        goal=EDITOR_GOAL,
        backstory=EDITOR_BACKSTORY,
        verbose=True,
        allow_delegation=False,
        max_iter=2,
    )

    plan_task = Task(
        description=(
            f"Create a content plan for {count} {content_type} posts.\n\n"
            "Include:\n"
            "- Topic angles that showcase AI writing expertise\n"
            "- Hook strategies for each post\n"
            "- Key points to cover\n"
            "- CTAs that drive inbound leads\n"
            "- Optimal posting schedule"
        ),
        expected_output=(
            "A content plan with topics, hooks, key points, CTAs, "
            "and a posting schedule."
        ),
        agent=planner,
    )

    write_task = Task(
        description=(
            f"Write {count} {content_type} posts based on the content plan.\n\n"
            "Each post must:\n"
            "- Have a compelling hook in the first line\n"
            "- Be well-structured with short paragraphs\n"
            "- Include relevant data or examples\n"
            "- End with engagement-driving CTA\n"
            "- Be 100-300 words (platform appropriate)"
        ),
        expected_output=(
            f"{count} polished {content_type} posts ready for publication."
        ),
        agent=writer,
    )

    edit_task = Task(
        description=(
            "Review all content for:\n"
            "1. Grammar and spelling (use language tools)\n"
            "2. Flow and readability\n"
            "3. SEO optimization (if applicable)\n"
            "4. Brand voice consistency\n"
            "5. Engagement potential\n\n"
            "Provide a quality score (1-10) for each piece and edits."
        ),
        expected_output=(
            "Edited content with quality scores and improvement notes."
        ),
        agent=editor,
    )

    return Crew(
        agents=[planner, writer, editor],
        tasks=[plan_task, write_task, edit_task],
        process=Process.sequential,
        verbose=True,
    )
