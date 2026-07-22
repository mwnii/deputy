# Income System

Hierarchical multi-agent income automation system built with CrewAI + LangGraph + OpenCode.

## Architecture

```
CEO (Orchestrator)
├── EA (Task Router)
├── CMO
│   ├── Outreach Agent (income generation)
│   ├── Content Agent (income generation)
│   ├── Lead Generation Specialist (Hormozi)
│   ├── Advertising Agent (Hormozi)
│   ├── Affiliate Agent (Hormozi)
│   └── Launch Playbook Agent (Hormozi)
├── CFO
│   └── Money Model Designer (Hormozi)
├── CTO
│   ├── Automation Agent (income generation)
│   └── Research Agent (income generation)
└── COO
    ├── Freelance Agent (income generation)
    ├── Microtask Agent (income generation)
    ├── Offer Architect (Hormozi)
    ├── Sales & Closing Agent (Hormozi)
    ├── Retention & Proof Agent (Hormozi)
    ├── Scaling & Operations Agent (Hormozi)
    ├── Launch Playbook Agent (Hormozi)
    └── Fast Cash Agent (Hormozi)
```

## Modules

### Income Generation (Original)
Freelancing, microtasks, content, outreach — immediate revenue.

### Hormozi Business Methodology
9 specialist agents powered by 33 PDFs from Alex Hormozi's library:
- Offer creation, lead generation, advertising, sales
- Money models, retention, scaling, affiliate, launches, fast cash

Each specialist has a dedicated reviewer agent. Handoffs are asynchronous.

See `docs/hormozi-agents.md` for full agent catalog.
See `docs/hormozi-workflows.md` for workflow diagrams.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Configure Environment

```bash
cp config/.env.example config/.env
# Edit config/.env with your settings
```

### 3. Optional: Start SearXNG

```bash
cd config && docker-compose up -d
```

### 4. Run with OpenCode

The system is pre-configured in `.opencode/opencode.json`. Run any agent:

```bash
opencode run offer-architect
opencode run money-model
opencode run review-offer-architect
```

### 5. Run with Claude Code

```bash
claude  # Reads CLAUDE.md automatically
```

### 6. Run with Cursor

Open the project in Cursor — `.cursor/rules/income-system.mdc` loads automatically.

## Zero-Cost Stack

| Component | Tool | Cost |
|-----------|------|------|
| LLM (Manager) | Groq Llama 3.3 70B | $0 |
| LLM (Worker) | Groq Llama 3.1 8B | $0 |
| LLM (Backup) | Ollama local | $0 |
| Search | DuckDuckGo + SearXNG | $0 |
| Browser | Playwright | $0 |
| Memory | LanceDB | $0 |
| DB | SQLite | $0 |
| Tracking | LangSmith (5K traces) | $0 |
| Version Control | GitHub | $0 |

## Self-Improvement

The system implements 5 training-free learning patterns:

1. **Reflexion** — Verbal reflection on tasks
2. **Voyager** — Skill library (persistent)
3. **SkillForge** — Failure-driven skill evolution
4. **ExpeL** — Lesson extraction from outcomes
5. **OPRO** — Prompt optimization via feedback

## Revenue Targets

| Period | Target |
|--------|--------|
| Daily | $35.71 |
| Weekly | $250 |
| Monthly | $1,000 |

## Income Methods

1. AI Training Platforms (Outlier, DataAnnotation)
2. AI-Powered Freelancing (Fiverr, Upwork)
3. Content Services (LinkedIn, Blog)
4. Cold Outreach (US businesses)

## Knowledge Base

```
knowledge/hormozi/
├── offer_architect/     (4 PDFs)
├── lead_generation/     (4 PDFs)
├── advertising/         (2 PDFs)
├── sales_closing/       (2 PDFs)
├── money_model/         (3 PDFs)
├── retention_proof/     (4 PDFs)
├── scaling_ops/         (12 PDFs)
├── affiliate/           (1 PDF)
├── launch_playbook/     (1 PDF)
├── fast_cash/           (1 PDF)
└── INDEX.md
```

## Privacy

- No personal data in Git (see `.gitignore`)
- All sensitive data in `vault/` (excluded from commits)
- `.env` excluded from commits
- Reflections and skills excluded from commits

## License

MIT
