# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Signatur** is the Fusion Ring visualization system for the Bazodiac platform. It renders a personalized 3D particle ring (Three.js) that represents a user's astrological/personality profile. The ring evolves through onboarding states (Latent → Natal → Post-Quiz) and responds to effects, transit overlays, and quiz results.

## Commands

All commands run from `fusion_ring_website/nextjs_space/`:

```bash
npm install --legacy-peer-deps  # Required: eslint v9 conflicts with @typescript-eslint v7
npm run dev                     # Next.js dev server (http://localhost:3000)
npm run build                   # Production build
npm run lint                    # ESLint
npm run start                   # Production server
npx prisma db seed              # Seed database (uses tsx + dotenv)
```

No test runner is configured.

## Architecture

### Data Flow Overview

```
┌─────────────────┐     ┌──────────────┐     ┌──────────────────────┐
│  Birth Input     │────▶│ BAFE API     │────▶│ fufire-mapper.ts     │
│  (birth-input-   │     │ (Railway)    │     │ Maps API → AstroBase │
│   panel.tsx)     │     │ /calculate/* │     └──────────┬───────────┘
└─────────────────┘     └──────────────┘                │
                              ▲                          ▼
                    ┌─────────┴──────────┐   ┌──────────────────────┐
                    │ API Proxy Route    │   │ FusionRingProfile    │
                    │ /api/calculate/    │   │ { astro, quizStamps }│
                    │ [endpoint]/route.ts│   └──────────┬───────────┘
                    └────────────────────┘              │
                                                        ▼
┌─────────────────┐                          ┌──────────────────────┐
│ QuizzMe Engine  │─── DeformationStamps ──▶│ compileProfile()     │
│ (external)      │                          │ → 5 Channel Functions│
└─────────────────┘                          └──────────┬───────────┘
                                                        │
┌─────────────────┐                          ┌──────────▼───────────┐
│ Transit State   │─── EffectTriggers ──────▶│ fusion-ring-canvas   │
│ (fusion-ring-   │                          │ Per-particle sampling│
│  transit.ts)    │                          │ GLSL shaders, WebGL  │
└─────────────────┘                          └──────────────────────┘
```

### Core Module System (`app/components/`)

| File | Size | Purpose |
|------|------|---------|
| `fusion-ring-canvas.tsx` | 120k | Main Three.js renderer, custom GLSL shaders, effect system, debug UI |
| `fusion-ring-profile.ts` | 17k | Profile compiler: AstroBase + QuizStamps → 5 deformation channels |
| `fusion-ring-input.ts` | 13k | Input controller, quiz cluster result processing, signal formula |
| `fusion-ring-transit.ts` | 12k | Transit state parser, effect triggers, "cosmic weather" overlay |
| `fusion-ring-audio.ts` | 11k | Procedural Web Audio: sub-bass drone, thunder peaks, effect sounds |
| `fusion-ring-scene.tsx` | 800 | Next.js dynamic import wrapper (SSR disabled) |
| `fufire-mapper.ts` | 5k | BAFE API caller + response → AstroBase mapper |
| `birth-input-panel.tsx` | 8k | Birth data input form + profile/raw response display |

### Signal Formula

The ring's sector signal combines 5 weighted sources:

```
S = 0.27·W + 0.27·B + 0.18·X + 0.18·T + 0.10·C
```
W = Western Astro, B = BaZi, X = WuXing, T = Transit, C = Conversation

### 5 Deformation Channels

`compileProfile()` outputs 5 continuous functions (angle → value):

| Channel | Range | Source |
|---------|-------|--------|
| `radiusOffset(θ)` | -0.4 to +0.4 | Zodiac signals + stamp types (bulge/dent/ridge/groove) |
| `tubeScale(θ)` | 0.4 to ~1.5 | Dominant element + thickening/thinning stamps |
| `roughness(θ)` | 0 to 1 | BaZi roughness + zodiac signal strength |
| `colorTint(θ)` | [r,g,b,intensity] | Wu Xing element colors + stamp color overrides |
| `coronaFactor(θ)` | 0.2+ | Zodiac signals + bulge/ridge stamps |

### Effect System

Effects are triggered via `EffectState` ref. Each has custom GLSL behavior and procedural audio:

| Effect | Trigger | Visual |
|--------|---------|--------|
| `resonanzsprung` | Delta ≥ 0.18 sector spike | Crystalline burst, red |
| `dominanzwechsel` | Sector override ≥ 0.08 | Golden transition |
| `mond_event` | Lunar phase peak | Pale blue illumination |
| `spannungsachse` | S1↔S7 opposition tension | Violet tension field |
| `korona_eruption` | Energy strands overflow | Green corona explosion |
| `divergenz_spike` | Westworld-style eruption | White/red crystalline |
| `burst` | Quiz completion, cluster unlock | Gold, particles outward |
| `crunch` | Compression event | Blue, particles inward |

### Three Ring States (Onboarding)

```
[LATENT] ──birth data──→ [NATAL] ──quiz──→ [POST_QUIZ] ──clusters──→ [EVOLVING]
  blur:12px               blur:4px          blur:0px                  blur:0px
  opacity:0.6             opacity:0.85      opacity:1.0               opacity:1.0
  colors:muted            colors:on         colors:vivid              colors:vivid+
```

### API Integration

**Proxy Route:** `POST /api/calculate/[endpoint]` — proxies to BAFE (FuFirE engine).

Supported endpoints: `bazi`, `western`, `wuxing`, `fusion`, `tst`

**Request body** (all endpoints):
```json
{ "date": "1990-06-15T14:30:00", "tz": "Europe/Berlin", "lon": 13.405, "lat": 52.52 }
```

**BAFE base URL:** Configured via `BAFE_BASE_URL` env var. Default: `https://bafe-production.up.railway.app`

**Mapper flow** (`fufire-mapper.ts`):
1. Calls `bazi`, `western`, `wuxing` in parallel via `Promise.allSettled`
2. Maps western bodies → `zodiacSignals[12]` (Sun: 0.35 weight, Moon: 0.25, Mars: 0.12, etc.)
3. Normalizes wu_xing_vector → `wuxingStrengths[5]` (0-1 range)
4. Extracts ascendant from degrees → sector index
5. Returns `AstroBase` ready for `FusionRingProfile`

### Dual-Ring System

Onboarding uses two overlapping layers:
- **SVG foreground**: 12 wedge sectors with zodiac labels, domain names, variable outer radius — the "readable" product object
- **Three.js background**: Particle ring (z-index: -1) — the "atmospheric" emotional layer

## Tech Stack

- **Next.js 14** (App Router, `force-dynamic`), React 18, TypeScript (strict)
- **Three.js** via `@react-three/fiber` + `@react-three/drei` — custom GLSL shaders, not declarative R3F
- **Tailwind CSS 3** + **shadcn/ui** (51 Radix-based components in `components/ui/`)
- **Prisma 6.7** with PostgreSQL (`DATABASE_URL` env var)
- **State**: Zustand, Jotai, React Query/SWR
- **Path alias**: `@/*` maps to project root (`fusion_ring_website/nextjs_space/`)
- **Renderer**: ACES Filmic tone mapping, exposure 1.8, clear color `#030308`

## Performance Targets

| Device | Particles | Target FPS |
|--------|-----------|------------|
| Desktop | 28,000 | 60 |
| Mobile High | 16,000 | 30+ |
| Mobile Low | 8,000 | 30+ (fallback blur) |

WebGL unavailable → graceful degradation to SVG-only ring. Pixel ratio capped at 1.5.

## Wu Xing Color System

The 5 elements map to sector tinting. These are canonical — do not change without design sign-off:

| Element | RGB (0-1) | Hex Glow | Sectors |
|---------|-----------|----------|---------|
| Wood | 0.23, 1.0, 0.42 | #3aff6a | Zwillinge |
| Fire | 1.0, 0.29, 0.23 | #ff4a3a | Widder, Loewe, Schuetze |
| Earth | 1.0, 0.78, 0.23 | #ffc83a | Stier, Jungfrau, Steinbock |
| Metal | 0.82, 0.85, 0.94 | #d0d8f0 | Waage, Wassermann |
| Water | 0.23, 0.60, 1.0 | #3a9aff | Krebs, Skorpion, Fische |

## Language & UX Convention

German UI labels throughout (zodiac names, domain labels, effect names). The ring narrative uses "reveal" language — the Signatur already exists and is being *discovered*, never *created*.

**Correct:** "Enthülle", "Entdecke", "Deine Signatur nimmt Form an"
**Forbidden:** "Erstelle deinen Ring", "Baue deine Signatur"

## Documentation

Generated docs live in `fusion_ring_website/nextjs_space/docs/`:

- `docs/API.md` — Full API reference: BAFE proxy endpoints, request/response schemas, internal TypeScript interfaces (FusionRingProfile, TransitStateV1, QuizClusterResult, EffectTrigger)
- `docs/ARCHITECTURE.md` — System context, component architecture, data flow sequence diagrams (Mermaid), module responsibilities, environment variables
- `docs/openapi.yaml` — OpenAPI 3.0.3 spec for the BAFE proxy API (can be loaded in Swagger UI)

Project-level docs:

- `DEV_BRIEF_Fusion_Ring_Integration_v3.md` — Full integration spec with API contracts (FuFirE → Ring, QuizzMe → Ring)
- `SKILL_Frontend_Ring_Onboarding.md` — UX/UI guide: 5 onboarding screens, dual-ring system, visual state machine, copy guidelines
- `Uploads/` — Design references, AI mapping lexicon, earlier dev brief versions
