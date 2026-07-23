# Site Builder System

## Overview
The Site Builder division operates in two modes: **Mode A (Client Site)** and **Mode B (Rank & Rent)**. The EA routes requests via the Mode Classifier skill, then COO and CTO coordinate execution.

## Mode A: Client Site
Build CRM-powered websites for specific clients using the site-crm-builder template.

### Workflow
```
1. Client Intake (COO: Client Site Builder)
   └─> Requirements, brand, goals

2. Market Validation (COO: Market Intelligence)
   └─> Niche score, competition analysis

3. Architecture (COO: Client Site Builder)
   └─> Page structure, user flows

4. Scaffold (CTO: Site Builder Tech)
   └─> Next.js + Convex + Clerk + Stripe

5. Wire (CTO: Site Builder Tech)
   └─> Connect schemas, auth, billing

6. Build (CTO: Site Builder Tech)
   └─> Pages, components, features

7. CRM Setup (CTO: Site Automation)
   └─> Lead capture, pipeline, automation

8. Payments (CTO: Site Builder Tech)
   └─> Stripe integration

9. QA (CTO: Quality & Compliance)
   └─> Cross-browser, performance, accessibility

10. Deploy + Handoff (COO: Client Site Builder)
    └─> Vercel deploy, client training
```

### Technology Stack
| Layer | Technology | Free Tier |
|-------|-----------|-----------|
| Framework | Next.js 14+ (App Router, TypeScript) | Yes |
| Database | Convex (real-time) | 1M rows, 1GB |
| Auth | Clerk | 10K MAU |
| Payments | Stripe | 2.9% + $0.30 |
| Styling | Tailwind CSS + shadcn/ui | Yes |
| Deployment | Vercel | Hobby free |

## Mode B: Rank & Rent
Build automated local lead generation sites that generate and sell calls/leads.

### Workflow
```
1. Niche Research (COO: Market Intelligence)
   └─> SERP audit, ring-city mapping, EMD check

2. Go/No-Go Decision (COO)
   └─> Score ≥ 7 = proceed

3. Build Site (CTO: Site Builder Tech)
   └─> Next.js + Convex (simplified, no Clerk)

4. SEO Optimization (CTO: SEO Engineer)
   └─> Schema, entity audit, AEO, speed

5. Content (CTO: Site Builder Tech + SEO Engineer)
   └─> 50-page architecture, EMD content

6. Automate (CTO: Site Automation)
   └─> Vapi voice AI, n8n lead routing

7. Partner Outreach (COO: Partner Acquisition)
   └─> Contractor management, lead delivery

8. Monitor (COO: Portfolio Monitor)
   └─> Rank tracking, revenue, Rule of Thirds
```

### Free-First Tool Substitutions
| Original (Paid) | Free Alternative |
|-----------------|-----------------|
| DataForSEO | Manual Google + DuckDuckGo |
| Vapi | Deferred (revenue-gated) |
| n8n cloud | n8n self-hosted (Docker) |
| Google PageSpeed API | Lighthouse CLI (free, local) |
| Twilio | ntfy.sh (push only) |
| Cloudflare Turnstile | Honeypot field |

## Cross-Functional Ownership
| Aspect | COO | CTO |
|--------|-----|-----|
| Client communication | Owner | Advisor |
| Process management | Owner | Executor |
| Technical build | Reviewer | Owner |
| Quality review | Owner | Executor |
| Deployment | Coordinator | Owner |
| Revenue tracking | Owner | Data provider |

## Key Files
- `agents/market-intelligence.md` — Niche validation specialist
- `agents/client-site-builder.md` — Mode A workflow owner
- `agents/partner-acquisition.md` — Contractor management
- `agents/portfolio-monitor.md` — Rank/revenue tracking
- `agents/site-builder-tech.md` — Technical build specialist
- `agents/site-automation.md` — Vapi/n8n automation
- `agents/seo-engineer.md` — Technical SEO specialist
- `agents/quality-compliance.md` — Cross-division QC
- `vault/04-SKILLS/mode-classifier.md` — Mode A vs B routing
