from __future__ import annotations

from crewai import Agent, Crew, Process, Task


SCOUT_ROLE = "Platform Scout"
SCOUT_GOAL = (
    "Find and evaluate microtask and AI training platforms "
    "(Outlier, DataAnnotation, etc.) for earning opportunities."
)
SCOUT_BACKSTORY = (
    "You are an expert at identifying legitimate microtask platforms "
    "and evaluating their pay rates, requirements, and reliability. "
    "You prioritize platforms with consistent work and fair compensation."
)

TASKER_ROLE = "Task Executor"
TASKER_GOAL = (
    "Efficiently complete platform tasks (data annotation, AI training) "
    "while maintaining high quality scores."
)
TASKER_BACKSTORY = (
    "You are skilled at completing AI training tasks quickly and accurately. "
    "You understand quality requirements and maintain high ratings."
)

TRACKER_ROLE = "Earnings Tracker"
TRACKER_GOAL = (
    "Track earnings across all platforms, calculate hourly rates, "
    "and recommend which platforms to prioritize."
)
TRACKER_BACKSTORY = (
    "You are a meticulous tracker who monitors earnings, time investment, "
    "and ROI across platforms to maximize income efficiency."
)


def create_automation_crew(platforms: list[str] | None = None) -> Crew:
    """Create a microtask/automation crew."""
    if platforms is None:
        platforms = ["outlier", "dataannotation"]

    scout = Agent(
        role=SCOUT_ROLE,
        goal=SCOUT_GOAL,
        backstory=SCOUT_BACKSTORY,
        verbose=True,
        allow_delegation=False,
        max_iter=3,
    )

    tasker = Agent(
        role=TASKER_ROLE,
        goal=TASKER_GOAL,
        backstory=TASKER_BACKSTORY,
        verbose=True,
        allow_delegation=False,
        max_iter=3,
    )

    tracker = Agent(
        role=TRACKER_ROLE,
        goal=TRACKER_GOAL,
        backstory=TRACKER_BACKSTORY,
        verbose=True,
        allow_delegation=False,
        max_iter=2,
    )

    scout_task = Task(
        description=(
            f"Research and evaluate these platforms: {', '.join(platforms)}\n\n"
            "For each platform:\n"
            "1. Current pay rates and task types\n"
            "2. Availability of tasks\n"
            "3. Quality requirements\n"
            "4. Payment methods available in Botswana\n"
            "5. Optimal strategy for maximizing earnings"
        ),
        expected_output=(
            "Platform evaluation reports with pay rates, strategies, "
            "and Botswana-specific considerations."
        ),
        agent=scout,
    )

    task_task = Task(
        description=(
            "Create standard operating procedures for completing tasks on each platform:\n"
            "1. Quality checklist per task type\n"
            "2. Time optimization strategies\n"
            "3. Common pitfalls to avoid\n"
            "4. Quality score maintenance tips\n"
            "5. Escalation procedures for issues"
        ),
        expected_output=(
            "SOPs for each platform with quality checklists and optimization tips."
        ),
        agent=tasker,
    )

    tracking_task = Task(
        description=(
            "Build an earnings tracking system:\n"
            "1. Daily earnings log template\n"
            "2. Platform comparison dashboard\n"
            "3. Hourly rate calculator\n"
            "4. Weekly/monthly reporting templates\n"
            "5. KPI targets by platform"
        ),
        expected_output=(
            "Complete tracking templates and KPI framework for microtask platforms."
        ),
        agent=tracker,
    )

    return Crew(
        agents=[scout, tasker, tracker],
        tasks=[scout_task, task_task, tracking_task],
        process=Process.sequential,
        verbose=True,
    )
