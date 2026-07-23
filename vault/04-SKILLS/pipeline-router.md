# Pipeline Router Skill

## Skill ID
pipeline-router

## Trigger
When the Video Director or EA needs to choose between Fern (3D) and Kurzgesagt (2D) video production pipelines.

## Purpose
Determine the optimal video production pipeline based on content type, audience, and production constraints.

## Routing Rules

### Fern (3D Cinematic) Pipeline
Route when ANY of these are true:
- Documentary, deep-dive, or investigation content
- Dark, atmospheric, cinematic tone requested
- Emotional narrative with dramatic arc
- Historical or storytelling content
- "Cinematic", "dark", "atmospheric", "documentary" keywords
- Longer format (5-20 minutes)

### Kurzgesagt (2D Explainer) Pipeline
Route when ANY of these are true:
- Explainer, how-to, or educational content
- Data-driven with charts and infographics
- Bright, accessible, family-friendly tone
- Comparison, listicle, or ranking content
- "Explainer", "educational", "how-to", "science" keywords
- Shorter format (3-10 minutes)

### Default
If unclear, ask: "What tone should this video have — cinematic/documentary or bright/explainer?"

## Routing Output
```
PIPELINE: [Fern or Kurzgesagt]
CONFIDENCE: [High/Medium/Low]
REASONING: [1-2 sentences]
ESTIMATED DURATION: [X minutes]
KEY AGENTS:
  - CMO: Video Director (script + creative)
  - CTO: [Pipeline-specific agents]
  - COO: Distribution Agent (publishing)
```

## Fern Pipeline Flow
```
Video Director (script) → Fern Script & Voice (Kokoro TTS) →
Fern Asset Acquisition (B-roll) → Fern Scene Agent (Blender) →
Fern Assembly (FFmpeg) → Quality & Compliance → Distribution
```

## Kurzgesagt Pipeline Flow
```
Video Director (script) → Kurz Voice & Audio (edge-tts) →
Kurz Asset Designer (SVG) → Kurz Scene Animator (Manim) →
Kurz Assembly (FFmpeg) → Quality & Compliance → Distribution
```

## Production Estimates
| Metric | Fern (3D) | Kurzgesagt (2D) |
|--------|-----------|-----------------|
| Script time | 2-4 hours | 1-2 hours |
| Asset time | 3-6 hours | 1-3 hours |
| Render time | 4-8 hours | 1-2 hours |
| Assembly | 2-4 hours | 1-2 hours |
| Total | 11-22 hours | 4-9 hours |
| Target resolution | 960x540 | 1920x1080 |

## Constraints
- Always confirm pipeline with Video Director before starting
- Never switch pipelines mid-production
- Log routing decision to `logs/routing/`
- If resource constraints exist, prefer Kurzgesagt (faster, lighter)
