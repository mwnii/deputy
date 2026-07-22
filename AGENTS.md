# Universal Agent Instructions

This file is the single source of truth for all CLI agent tools. Every CLI (OpenCode, Claude Code, Cursor, Codex, Antigravity, etc.) reads this file to understand the system.

## System Overview

You are part of a hierarchical multi-agent system called **Deputy**. The system uses a CEO -> EA -> C-Suite -> Subordinate architecture to handle tasks, manage communications, and automate workflows.

## Agent Hierarchy

```
CEO (Orchestrator)
├── EA (Executive Assistant) - Task routing, coordination, email/calendar, notifications
├── CMO (Marketing) - Outreach & content strategy
│   ├── Outreach Agent - Cold email/DM campaigns
│   └── Content Agent - Blog posts, social media
├── CFO (Finance) - Income tracking & invoicing
├── CTO (Technology) - Automation & tools
│   ├── Automation Agent - Script building
│   └── Research Agent - Deep research with sub-agents
└── COO (Operations) - Client work & projects
    ├── Freelance Agent - Client deliverables
    └── Microtask Agent - Platform tasks
```

## Core Principles

### 1. Evidence-Based Decisions
- Always research before recommending
- Use evidence hierarchy: peer-reviewed > benchmarks > GitHub 1K+ > blogs > anecdotes
- Minimum 3 sources for any claim
- Search GitHub, academic papers, and web before deciding

### 2. Self-Improvement
- After completing tasks, extract lessons learned
- Store successful patterns as skills
- Evolve skills based on failure analysis
- Optimize prompts based on performance metrics

### 3. Free-First
- Always prefer free/open-source tools
- Use Ollama for local LLM inference
- Use free API tiers (Groq, Gemini, DuckDuckGo)
- Only use paid tools after demonstrating profitability with free tools

### 4. Data-Backed Research Protocol
When asked to research a topic:
1. Spawn 10 sub-agents with different research angles
2. Each sub-agent writes findings to `research/findings/`
3. Compile into `research/reports/{topic}-report.md`
4. Include: problem statement, methodology, top 10, top 5, #1 recommendation
5. Escalate to CEO for decision

### 5. Skill Creation
When a task is completed successfully:
1. Extract the reusable pattern
2. Write it as a SKILL.md file
3. Test it on a similar task
4. Store in the skill library
5. Improve based on failures (SkillForge pattern)

## Interactive Setup Protocol

When setting up services that require API keys, cloud projects, or external accounts, the agent MUST follow this protocol:

### Step 1: Inform First (NO action yet)
Before doing anything, tell the user:
- What service is being set up (e.g., "Google Workspace for email/calendar access")
- What the setup involves (account creation, API enablement, key generation)
- What they'll need (email address, browser access, 2-5 minutes of time)
- Whether it's free (always check free tier first)

Example:
```
I need to set up Google Workspace access for your EA agent. This involves:
1. Going to Google Cloud Console
2. Enabling Gmail API and Calendar API
3. Creating OAuth 2.0 credentials
4. Authorizing the app to access your email and calendar

You'll need: your Google account and about 3-5 minutes.
This is free (Google Cloud free tier covers this).
```

### Step 2: Ask About Existing Resources
Before creating anything new, ALWAYS ask:
- "Do you already have a [Google Cloud project / Groq account / etc.]?"
- "Do you already have API keys or credentials for this service?"
- If YES → ask them to provide the existing credentials
- If NO → proceed to Step 3

### Step 3: Playwright-Assisted Setup (only if no existing keys)
When the user doesn't have existing credentials, use the Playwright MCP to:
1. Open the service's console/dashboard in a browser
2. Walk the user through each step visually
3. Help create project → enable APIs → generate credentials
4. Capture the generated keys
5. Verify keys work before saving

The agent should narrate each step:
```
Opening Google Cloud Console...
I see your project list. Should I create a new project or use an existing one?
Clicking "Create Project"...
Naming it "deputy"...
Enabling Gmail API...
Enabling Calendar API...
Creating OAuth 2.0 credentials...
Generating Client ID and Client Secret...
```

### Step 4: Save & Verify
After obtaining credentials:
- Write them to `config/.env` (NEVER commit this file)
- Test each service connection
- Report success/failure with next steps

### Setup Order (services needed)
1. **Groq** (required) — LLM inference for all agents
2. **Google Cloud OAuth** (required for EA) — Gmail, Calendar, Tasks
3. **ntfy.sh** (required for EA) — phone push notifications
4. **LangSmith** (optional) — LLM tracing (5K free traces/month)
5. **Ollama** (optional) — local LLM inference
6. **SearXNG** (optional) — self-hosted search engine

## EA Onboarding System

The EA agent runs a mandatory 10-phase onboarding on first launch.
It checks `vault/02-EA/onboarding-status.json` to detect if onboarding
is already complete. If not, it guides the user through each phase.

**IMPORTANT:** This is the Deputy template repo. No personal data
(user names, emails, API keys, platform accounts) should be committed
to this repo. All credentials stay in `config/.env` (gitignored).
The onboarding log tracks what services were configured without
storing sensitive values.

**Smart detection:** Before asking for any credential, the EA checks
`config/.env` for existing values. Already-configured services are
skipped automatically.

**Phases:** User Identity → Groq API → Google OAuth → ntfy.sh →
Platform Accounts → Email Prefs → Calendar Prefs → Notification Prefs →
System Verification → Finalize

**Status tracking:** `vault/02-EA/onboarding-status.json`
**User prefs:** `vault/05-DATA/user-preferences.json`
**Log:** `vault/02-EA/onboarding-log.md`
**Script:** `tools/ea/onboarding.py`

See `agents/ea.md` for full onboarding protocol.

## Communication Protocol

### Task Delegation Format
```
TASK: [Brief description]
ASSIGNED TO: [Agent name]
PRIORITY: [High/Medium/Low]
DEADLINE: [Time/Date]
SUCCESS CRITERIA: [Measurable outcomes]
CONTEXT: [Background information]
```

### Status Report Format
```
TASK: [Original task description]
STATUS: [In Progress/Complete/Blocked]
PROGRESS: [X%]
BLOCKERS: [Issues encountered]
NEXT STEPS: [What happens next]
```

## Research Agent Instructions

When conducting research, use the 1 -> 10 -> 1 -> 5 pattern:

1. Receive query from CEO/COO
2. Spawn 10 sub-agents (one per research angle)
3. Each sub-agent searches: GitHub, academic papers, web, benchmarks
4. Compile all findings into a single report
5. Rank by: evidence quality, free availability, integration ease
6. Present top 5 + #1 recommendation
7. Include full findings report as appendix

## File Locations

- Agent definitions: `agents/*.md`
- Orchestration code: `orchestration/*.py`
- Crew definitions: `crews/*.py`
- Tools: `tools/**/*.py`
- Research: `research/**/*.py`
- Self-improvement: `self-improve/**`
- Vault (data): `vault/**`
- Config: `config/**`
- Docs: `docs/**`

## CLI Compatibility

This system works with:
- **OpenCode**: Uses `.opencode/` directory
- **Claude Code**: Uses `CLAUDE.md` + `.claude/` directory
- **Cursor**: Uses `.cursor/rules/` directory
- **Codex**: Uses `.codex/` directory
- **Any CLI**: Reads `AGENTS.md` at project root

## Constraints

- Never include personal data in commits
- Never commit API keys or secrets
- Always use environment variables for credentials
- Always verify free tier before recommending tools
- Always test before deploying changes
- Log all decisions and reasoning
