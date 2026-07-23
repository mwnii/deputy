# Video Production System

## Overview
The Video Production division operates two pipelines: **Fern (3D Cinematic)** and **Kurzgesagt (2D Explainer)**. The EA routes requests via the Pipeline Router skill, then CMO (creative), CTO (technical), and COO (delivery) coordinate execution.

## Pipeline Selection
Use `vault/04-SKILLS/pipeline-router.md` to route:
- **Fern**: Documentary, deep-dive, emotional narrative, dark/atmospheric tone
- **Kurzgesagt**: Explainer, educational, data-driven, bright/accessible tone

## Fern Pipeline (3D Cinematic)
Dark, atmospheric Blender-based documentary style.

### Workflow
```
1. Script (CMO: Video Director)
   └─> 1,000-5,000 words, Hook→Context→Body→Climax→CTA

2. Voice (CTO: Fern Script & Voice)
   └─> Kokoro-82M local TTS, multi-voice, word timestamps

3. Assets (CTO: Fern Asset Acquisition)
   └─> B-roll from Pexels/Pixabay/yt-dlp (CC licensed)

4. 3D Scenes (CTO: Fern Scene Agent)
   └─> Blender headless, Workbench/Eevee, 4GB RAM optimized

5. Assembly (CTO: Fern Assembly)
   └─> FFmpeg frame→video, audio sync, color grading, film grain

6. QC (CTO: Quality & Compliance)
   └─> Visual quality, audio sync, brand consistency, fair use

7. Publish (COO: Distribution Agent)
   └─> YouTube upload, metadata, thumbnails, scheduling
```

### Technical Specs
| Metric | Value |
|--------|-------|
| Resolution | 960x540 |
| Renderer | Eevee (not Cycles) |
| RAM Limit | 4GB |
| Max Frames/Scene | 250 |
| Audio Format | WAV/MP3, -16 LUFS |
| Output | H.264 MP4 |

### Free Tools
| Tool | Purpose |
|------|---------|
| Blender | 3D modeling + rendering (headless) |
| Kokoro-82M | Local TTS (offline, no API) |
| Pexels/Pixabay | B-roll footage (free commercial) |
| yt-dlp | YouTube CC content download |
| Poly Haven | HDRIs + textures (CC0) |
| FFmpeg | Video assembly + grading |

## Kurzgesagt Pipeline (2D Explainer)
Vivid, flat-design Manim-based explainer style.

### Workflow
```
1. Script (CMO: Video Director)
   └─> 500-2,000 words, Hook→Context→Body→Climax→CTA

2. Voice (CTO: Kurz Voice & Audio)
   └─> edge-tts (Azure neural), multi-voice, pydub mixing

3. Assets (CTO: Kurz Asset Designer)
   └─> SVG illustrations, characters, infographics

4. Animation (CTO: Kurz Scene Animator)
   └─> Manim Community Edition, data viz, transitions

5. Assembly (CTO: Fern Assembly)
   └─> FFmpeg concat, audio overlay, export

6. QC (CTO: Quality & Compliance)
   └─> Visual quality, audio sync, brand consistency

7. Publish (COO: Distribution Agent)
   └─> YouTube upload, metadata, thumbnails, scheduling
```

### Technical Specs
| Metric | Value |
|--------|-------|
| Resolution | 1920x1080 |
| Renderer | Manim (CLI) |
| Max Scene Duration | 30 seconds |
| Audio Format | MP3, -16 LUFS |
| Output | H.264 MP4 |

### Free Tools
| Tool | Purpose |
|------|---------|
| Manim | 2D animation (open source) |
| edge-tts | Neural TTS (Azure, no key) |
| pydub | Audio manipulation |
| svgwrite | Programmatic SVG creation |
| Inkscape CLI | SVG manipulation |
| FFmpeg | Video assembly |

## Cross-Functional Ownership
| Aspect | CMO | CTO | COO |
|--------|-----|-----|-----|
| Scriptwriting | Owner | — | Reviewer |
| Creative direction | Owner | — | — |
| Brand consistency | Owner | Reviewer | — |
| Voice generation | — | Owner | — |
| 3D/2D production | — | Owner | — |
| Assembly + grading | — | Owner | — |
| Quality review | Reviewer | Executor | Owner |
| Publishing | — | — | Owner |
| Revenue tracking | — | — | Owner |

## Brand Voice Guidelines
- **Tone**: Authoritative but accessible, cinematic, emotionally resonant
- **Language**: Clear, vivid, avoid jargon unless explained
- **Pacing**: Build tension gradually, deliver payoff at climax
- **Style References**: Kurzgesagt, Vox, Wendover Productions

## Production Estimates
| Metric | Fern (3D) | Kurzgesagt (2D) |
|--------|-----------|-----------------|
| Script | 2-4 hours | 1-2 hours |
| Assets | 3-6 hours | 1-3 hours |
| Render | 4-8 hours | 1-2 hours |
| Assembly | 2-4 hours | 1-2 hours |
| **Total** | **11-22 hours** | **4-9 hours** |

## Key Files
- `agents/video-director.md` — Creative direction (CMO)
- `agents/fern-script-voice.md` — Kokoro TTS (CTO)
- `agents/fern-asset-acquisition.md` — B-roll sourcing (CTO)
- `agents/fern-scene-agent.md` — Blender 3D (CTO)
- `agents/fern-assembly.md` — FFmpeg assembly (CTO)
- `agents/kurz-asset-designer.md` — SVG generation (CTO)
- `agents/kurz-voice-audio.md` — edge-tts narration (CTO)
- `agents/kurz-scene-animator.md` — Manim animation (CTO)
- `agents/quality-compliance.md` — Cross-division QC (CTO)
- `agents/distribution-agent.md` — YouTube publishing (COO)
- `vault/04-SKILLS/pipeline-router.md` — Fern vs Kurz routing
