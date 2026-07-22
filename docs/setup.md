# Setup Guide

## Prerequisites

- Python 3.10+
- Git
- (Optional) Docker for SearXNG
- (Optional) Ollama for local LLM

## Quick Start

For a guided setup with Playwright browser assistance, see [SETUP_WIZARD.md](SETUP_WIZARD.md).

The agent will ask you about existing credentials before creating new ones, and can navigate service consoles for you.

## Installation

### Step 1: Clone and Enter

```bash
git clone <repo-url>
cd deputy
```

### Step 2: Python Environment

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

### Step 3: Browser Automation

```bash
playwright install chromium
```

### Step 4: Environment Config

```bash
cp config/.env.example config/.env
```

Edit `config/.env`:

```env
GROQ_API_KEY=gsk_your_key_here
LANGSMITH_API_KEY=lsv2_your_key_here
SEARXNG_URL=http://localhost:8080
```

### Step 5: Get Free API Keys

For detailed walkthrough with Playwright assistance, see [SETUP_WIZARD.md](SETUP_WIZARD.md).

#### Groq (Required)
1. Go to https://console.groq.com
2. Sign up free
3. Create API key
4. Add to `.env`

#### Google Workspace (Required for EA Agent)
1. Go to https://console.cloud.google.com
2. Create project → Enable Gmail API, Calendar API, Tasks API
3. Create OAuth 2.0 credentials (Desktop app)
4. Copy Client ID and Client Secret to `.env`

#### ntfy.sh (Required for EA Notifications)
1. Install ntfy app on your phone
2. Create a unique topic subscription
3. Add topic to `.env`

#### LangSmith (Optional)
1. Go to https://smith.langchain.com
2. Sign up free
3. Create API key
4. Add to `.env`

### Step 6: Optional Services

#### SearXNG (self-hosted search)
```bash
cd config && docker-compose up -d
```

#### Ollama (local LLM)
```bash
ollama pull qwen3:8b
```

## CLI Setup

### OpenCode
Already configured. `.opencode/opencode.json` has all agents defined.

### Claude Code
`CLAUDE.md` at root provides instructions.

### Cursor
`.cursor/rules/income-system.mdc` auto-loads.

### Codex
`.codex/instructions.md` provides instructions.

## Verification

```bash
# Check Python
python --version

# Check Playwright
playwright --version

# Check Groq connection
python -c "import httpx; print(httpx.get('https://api.groq.com/openapi/v1/models').status_code)"
```
