# Signatur — Fusion Ring Visualization

A personalized 3D particle ring visualization for the Bazodiac platform. The ring represents a user's astrological/personality profile using Three.js with custom GLSL shaders, evolving through onboarding states as the user provides birth data and completes quizzes.

## Quick Start

```bash
cd fusion_ring_website/nextjs_space
npm install --legacy-peer-deps
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). The ring loads with a demo profile. Use the left panel to enter birth data and generate a real profile from the BAFE API.

## Architecture

See [docs/ARCHITECTURE.md](fusion_ring_website/nextjs_space/docs/ARCHITECTURE.md) for Mermaid diagrams and full module breakdown.

The core pipeline:

```
Birth Data → BAFE API (BaZi + Western + WuXing)
                ↓
         fufire-mapper.ts → AstroBase
                ↓
         fusion-ring-profile.ts → compileProfile() → 5 Deformation Channels
                ↓
         fusion-ring-canvas.tsx → 28k particles, GLSL shaders, WebGL
```

## Key Modules

| Module | Purpose |
|--------|---------|
| `fusion-ring-canvas.tsx` | Three.js renderer, GLSL shaders, 8 effect types |
| `fusion-ring-profile.ts` | Profile compiler: AstroBase + QuizStamps → channels |
| `fusion-ring-input.ts` | Unified input controller (transit, quiz, conversation) |
| `fusion-ring-transit.ts` | Transit state parser, effect derivation |
| `fusion-ring-audio.ts` | Procedural Web Audio (sub-bass drone, thunder) |
| `fufire-mapper.ts` | BAFE API → AstroBase mapper |
| `birth-input-panel.tsx` | Birth data form + profile/raw display |

## API

Proxy at `POST /api/calculate/{bazi|western|wuxing|fusion|tst}` forwards to BAFE.

See [docs/API.md](fusion_ring_website/nextjs_space/docs/API.md) and [docs/openapi.yaml](fusion_ring_website/nextjs_space/docs/openapi.yaml).

## Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `BAFE_BASE_URL` | FuFirE API upstream | `https://bafe-production.up.railway.app` |
| `DATABASE_URL` | PostgreSQL (Prisma) | Required |

## Tech Stack

Next.js 14 · React 18 · TypeScript · Three.js (custom GLSL) · Tailwind CSS 3 · shadcn/ui · Prisma · Vitest

## Documentation

- [CLAUDE.md](CLAUDE.md) — Developer guide for Claude Code
- [docs/API.md](fusion_ring_website/nextjs_space/docs/API.md) — API reference
- [docs/ARCHITECTURE.md](fusion_ring_website/nextjs_space/docs/ARCHITECTURE.md) — Architecture diagrams
- [DEV_BRIEF_Fusion_Ring_Integration_v3.md](DEV_BRIEF_Fusion_Ring_Integration_v3.md) — Integration spec
- [SKILL_Frontend_Ring_Onboarding.md](SKILL_Frontend_Ring_Onboarding.md) — UX/UI guide
