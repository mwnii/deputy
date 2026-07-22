# Setup Wizard

This guide walks you through setting up all required services. The agent can help with each step using Playwright browser automation.

## Before You Start

The agent will ask you about each service before proceeding:
- Do you already have an account/project?
- Do you already have API keys?

If you have existing credentials, provide them and skip to the verification step. If not, the agent will use Playwright to walk you through the setup.

---

## 1. Groq (Required — LLM Inference)

**What it does:** Powers all agent AI responses (free tier: 30 req/min, 14K tokens/min)

**Setup time:** 2 minutes

**Steps:**
1. Go to https://console.groq.com
2. Sign up with Google or email
3. Click "Create API Key"
4. Copy the key (starts with `gsk_`)
5. Add to `config/.env`: `GROQ_API_KEY=gsk_...`

**Playwright assist:** The agent can open this page and guide you through each click.

**Verification:**
```bash
python -c "import httpx; r = httpx.get('https://api.groq.com/openapi/v1/models', headers={'Authorization': 'Bearer gsk_your_key'}); print('OK' if r.status_code == 200 else 'FAILED')"
```

---

## 2. Google Workspace OAuth (Required for EA Agent)

**What it does:** Lets the EA agent read/send emails, manage calendar, create tasks

**Setup time:** 5 minutes

**Prerequisites:** A Google account (Gmail)

### Step-by-step:

#### 2a. Create Google Cloud Project
1. Go to https://console.cloud.google.com
2. Click project dropdown (top bar) → "New Project"
3. Name it `deputy`
4. Click "Create"

#### 2b. Enable APIs
1. Go to https://console.cloud.google.com/apis/library
2. Search for "Gmail API" → Click → "Enable"
3. Search for "Google Calendar API" → Click → "Enable"
4. Search for "Google Tasks API" → Click → "Enable"

#### 2c. Create OAuth Credentials
1. Go to https://console.cloud.google.com/apis/credentials
2. Click "Create Credentials" → "OAuth client ID"
3. If prompted, configure OAuth consent screen first:
   - User type: "External"
   - App name: "Deputy"
   - Add your email as developer contact
   - Save and continue through scopes (add email, calendar, tasks, gmail scopes)
   - Add your email as test user
4. Back to "Create Credentials" → "OAuth client ID"
5. Application type: "Desktop app"
6. Name: "Deputy Desktop"
7. Click "Create"
8. Copy the **Client ID** and **Client Secret**

#### 2d. Add to config
```env
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
```

#### 2e. First-time authorization
When you first use a Google Workspace tool, the agent will:
1. Open a browser window with Google's consent screen
2. You log in and approve access
3. The token is cached for future use

**Playwright assist:** The agent can navigate the Google Cloud Console for you, clicking through each step.

---

## 3. ntfy.sh (Required for EA Phone Notifications)

**What it does:** Sends instant push notifications to your phone

**Setup time:** 2 minutes

**Steps:**
1. Install **ntfy** on your phone:
   - iOS: App Store → search "ntfy"
   - Android: Play Store → search "ntfy"
2. Open the app
3. Tap the "+" button to add a subscription
4. Enter a **unique topic name** (e.g., `deputy-alerts-yourname-xyz`)
   - This is like a private channel — only you will subscribe to it
5. You should see an empty notification list — that's correct
6. Copy the topic name to `config/.env`:
   ```env
   NTFY_TOPIC=deputy-alerts-yourname-xyz
   NTFY_SERVER=https://ntfy.sh
   ```

**Test it:**
```bash
curl -d "Test notification from Deputy" https://ntfy.sh/your-topic-name
```
You should see the notification appear on your phone immediately.

**Playwright assist:** The agent can open https://ntfy.sh in a browser to show you the web interface and help verify your topic.

---

## 4. LangSmith (Optional — Tracing)

**What it does:** Tracks LLM calls for debugging (5K traces/month free)

**Setup time:** 2 minutes

**Steps:**
1. Go to https://smith.langchain.com
2. Sign up free
3. Create API key
4. Add to `config/.env`: `LANGSMITH_API_KEY=lsv2_...`
5. Set `LANGSMITH_TRACING=true`

---

## 5. Ollama (Optional — Local LLM)

**What it does:** Run LLMs locally without API keys

**Setup time:** 5 minutes

**Steps:**
1. Install: https://ollama.com/download
2. Pull a model: `ollama pull qwen3:8b`
3. Verify: `ollama run qwen3:8b "Hello"`

---

## 6. SearXNG (Optional — Self-Hosted Search)

**What it does:** Private search engine for research

**Setup time:** 3 minutes (requires Docker)

**Steps:**
```bash
cd config
docker-compose up -d
```

---

## Verification Checklist

After setup, verify all services:

```bash
# Groq
python -c "import httpx; print('Groq:', httpx.get('https://api.groq.com/openapi/v1/models').status_code)"

# ntfy.sh
curl -d "Deputy is online" https://ntfy.sh/your-topic

# Google (check token exists)
ls ~/.workspace-mcp/cli-tokens/

# Playwright
playwright --version

# Python
python --version
```

## Linting & LSP Setup

All code-writing agents must run linters before completing tasks.
These tools ensure code quality across the system.

### Install Linters (required)
```bash
pip install ruff pyright
```

### Install Biome (for JS/TS agents)
```bash
npm install -g @biomejs/biome
```

### Verify Installation
```bash
ruff --version
pyright --version
biome --version
```

### Usage
```bash
# Lint a file
python tools/lint.py path/to/script.py

# Lint entire project
python tools/lint.py --check

# Auto-format entire project
python tools/lint.py --format

# Or run directly
ruff check .
ruff format .
```

### Configuration
Lint rules are in `pyproject.toml`:
- Ruff: E, F, I, N, W, UP rules, 100-char line length
- Pyright: basic type checking, Python 3.10

See `vault/04-SKILLS/code-quality.md` for the full linting protocol.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Groq returns 401 | Check API key, regenerate at console.groq.com |
| Google OAuth fails | Ensure APIs enabled + test user added in consent screen |
| ntfy not receiving | Check topic name matches exactly, check app is open |
| Playwright won't start | Run `playwright install chromium` |
| MCP server won't connect | Check `config/.env` has correct values, no trailing spaces |
