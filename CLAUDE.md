# Claude Code Configuration

This project is a hierarchical multi-agent income automation system. Read `AGENTS.md` for full system instructions.

## Quick Reference

- Agent definitions: `agents/*.md`
- Python code: `orchestration/`, `crews/`, `tools/`, `research/`
- Configuration: `config/`
- Documentation: `docs/`

## Key Behaviors

1. **Always read AGENTS.md first** for system context
2. **Use the task tool** to delegate to sub-agents when complex work is needed
3. **Research before recommending** - search GitHub, papers, web
4. **Use free tools only** - Ollama, Groq, DuckDuckGo, SearXNG
5. **Extract lessons** after completing tasks
6. **Never commit secrets** - check .gitignore before committing

## Agent Hierarchy

- EA: Strategic decisions, delegation, task routing, status tracking (primary interface)
- CMO: Outreach, content, marketing
- CFO: Financial tracking, invoicing, platform accounts
- CTO: Automation, tools, self-improvement
- COO: Client work, operations, quality control

## Research Protocol

When researching:
1. Use the 1 -> 10 -> 1 -> 5 pattern
2. Search GitHub for repos (stars, license, maintenance)
3. Search academic papers (Semantic Scholar, arXiv)
4. Search web for tools and benchmarks
5. Compile top 10, recommend top 5, pick #1
6. Save report to `research/reports/`
