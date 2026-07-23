# Mode Classifier Skill

## Skill ID
mode-classifier

## Trigger
When the user requests a website build, site creation, or web project.

## Purpose
Determine whether the request is Mode A (Client Site) or Mode B (Rank & Rent) and route to the appropriate workflow.

## Classification Rules

### Mode A: Client Site
Route when ANY of these are true:
- Client name or business name is specified
- "Build a site for [someone]" or "client site"
- CRM, lead capture, or payment integration requested
- Existing business needs a website
- "Make me a website" (with specific business context)
- Fiverr/Upwork gig fulfillment

### Mode B: Rank & Rent
Route when ANY of these are true:
- "Rank and rent", "lead gen site", "local SEO site"
- Niche + city combination mentioned
- "Build a site for [service] in [city]"
- No specific client — targeting a market
- "Automated site", "passive income site"
- EMD (exact-match domain) strategy

### Default
If unclear, ask: "Is this for a specific client (Mode A) or targeting a market (Mode B)?"

## Routing Output
```
MODE: [A or B]
CONFIDENCE: [High/Medium/Low]
REASONING: [1 sentence]
DELEGATE TO:
  - Process Owner: COO
  - Technical Build: CTO
  - Key Agents: [List relevant agents]
```

## Mode A Workflow (Client Site)
```
Client Site Builder → Market Intelligence → Client Site Builder →
Site Builder Tech → Site Automation → Quality & Compliance →
Client Site Builder (handoff)
```

## Mode B Workflow (Rank & Rent)
```
Market Intelligence → Site Builder Tech → SEO Engineer →
Site Automation → Partner Acquisition → Portfolio Monitor
```

## Constraints
- Always confirm mode with user before proceeding
- Never mix Mode A and Mode B in a single project
- Log classification decision to `logs/routing/`
