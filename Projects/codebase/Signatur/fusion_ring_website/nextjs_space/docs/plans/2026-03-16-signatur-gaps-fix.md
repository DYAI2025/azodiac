# Signatur Gaps Fix Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Close 4 documentation/infrastructure gaps: README, BAFE schema-mode parsing, Vitest test setup, and GitHub Actions docs pipeline.

**Architecture:** Add a README.md at project root. Fix the BAFE proxy to handle the non-standard schema-format response by parsing it into real JSON. Bootstrap Vitest for unit testing the mapper and profile compiler. Add a GitHub Actions workflow for build + lint + test + OpenAPI validation.

**Tech Stack:** Next.js 14, Vitest, GitHub Actions, OpenAPI 3.0

---

## Task 1: README.md

**Files:**
- Create: `README.md` (project root: `Signatur/`)

**Step 1: Write README**

```markdown
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
```

**Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add project README with quick start and architecture overview"
```

---

## Task 2: Fix BAFE Schema-Format Response Parsing

The BAFE Railway deployment returns a custom non-JSON format where values are replaced with type annotations (`string`, `float`, `bool`, `int`). The `Content-Type` header says `application/json` but the body isn't valid JSON.

**Root cause:** BAFE is running in a "schema/dry-run" mode. The response uses unquoted keys and type placeholders instead of real values.

**Fix strategy:** Two-layer approach:
1. Add a response format validator in the proxy that detects schema-mode and returns a clear error
2. Add fallback demo data in the mapper so the UI works even when BAFE returns schema-mode

**Files:**
- Modify: `app/api/calculate/[endpoint]/route.ts`
- Modify: `app/components/fufire-mapper.ts`

**Step 1: Write the proxy response validator**

In `app/api/calculate/[endpoint]/route.ts`, after `const data = await res.json().catch(...)`:

```typescript
// BAFE sometimes returns schema-mode responses (type annotations instead of values).
// Detect this by checking if the raw text contains type placeholders.
const rawText = await res.text();

// Try standard JSON parse first
let data: Record<string, unknown>;
try {
  data = JSON.parse(rawText);
} catch {
  // Check if this is schema-mode (contains unquoted keys + type placeholders)
  if (/\b(string|float|bool|int)\b/.test(rawText) && !rawText.includes('"')) {
    return NextResponse.json(
      { error: `BAFE ${endpoint} returned schema-mode response (no real data). The API may need reconfiguration.`, schema_mode: true },
      { status: 503 },
    );
  }
  return NextResponse.json(
    { error: `BAFE ${endpoint} returned invalid JSON` },
    { status: 502 },
  );
}
```

Note: This replaces the existing `const data = await res.json().catch(() => ({}))` + `if (!res.ok)` block. The full updated route:

```typescript
import { NextRequest, NextResponse } from 'next/server';

const BAFE_BASE_URL =
  process.env.BAFE_BASE_URL || 'https://bafe-production.up.railway.app';

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ endpoint: string }> },
) {
  const { endpoint } = await params;
  const allowed = ['bazi', 'western', 'wuxing', 'fusion', 'tst'];
  if (!allowed.includes(endpoint)) {
    return NextResponse.json({ error: 'Unknown endpoint' }, { status: 400 });
  }

  try {
    const body = await request.json();
    const res = await fetch(`${BAFE_BASE_URL}/calculate/${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    const rawText = await res.text();

    // Try standard JSON parse
    let data: Record<string, unknown>;
    try {
      data = JSON.parse(rawText);
    } catch {
      // Detect BAFE schema-mode (type annotations instead of values)
      if (/\b(string|float|bool|int)\b/.test(rawText)) {
        return NextResponse.json(
          { error: `BAFE ${endpoint} returned schema-mode response (no real data). Check BAFE_BASE_URL configuration.`, schema_mode: true },
          { status: 503 },
        );
      }
      return NextResponse.json(
        { error: `BAFE ${endpoint} returned invalid JSON` },
        { status: 502 },
      );
    }

    if (!res.ok) {
      return NextResponse.json(
        { error: (data.detail || data.title || `BAFE ${endpoint} error`) as string, status: res.status },
        { status: res.status },
      );
    }
    return NextResponse.json(data);
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Unknown error';
    return NextResponse.json({ error: message }, { status: 502 });
  }
}
```

**Step 2: Add schema-mode detection in mapper**

In `fufire-mapper.ts`, update `postBafe` to detect 503 schema_mode and throw a descriptive error:

```typescript
async function postBafe<T>(endpoint: string, body: BirthInput): Promise<T> {
  const res = await fetch(`/api/calculate/${endpoint}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      date: body.date,
      tz: body.tz,
      lon: body.lon,
      lat: body.lat,
      ambiguousTime: 'earlier',
      nonexistentTime: 'error',
      ...(endpoint === 'bazi' ? { standard: 'CIVIL', boundary: 'midnight', strict: true } : {}),
    }),
  });
  const data = await res.json().catch(() => ({ error: `${endpoint} failed` }));
  if (!res.ok) {
    if (data.schema_mode) {
      throw new Error(`${endpoint}: BAFE im Schema-Modus — keine echten Daten verfügbar. Demo-Signatur verwenden.`);
    }
    throw new Error(data.error || `${endpoint}: ${res.status}`);
  }
  return data as T;
}
```

**Step 3: Run build to verify**

```bash
npm run build
```

Expected: Build succeeds, no type errors.

**Step 4: Commit**

```bash
git add app/api/calculate/\[endpoint\]/route.ts app/components/fufire-mapper.ts
git commit -m "fix: detect BAFE schema-mode responses and show clear error"
```

---

## Task 3: Bootstrap Vitest + Core Unit Tests

**Files:**
- Modify: `package.json` (add vitest + test script)
- Create: `vitest.config.ts`
- Create: `app/components/__tests__/fusion-ring-profile.test.ts`
- Create: `app/components/__tests__/fufire-mapper.test.ts`

**Step 1: Install Vitest**

```bash
npm install -D vitest @vitejs/plugin-react --legacy-peer-deps
```

**Step 2: Create vitest.config.ts**

```typescript
import { defineConfig } from 'vitest/config';
import path from 'path';

export default defineConfig({
  test: {
    environment: 'node',
    include: ['**/__tests__/**/*.test.ts'],
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, '.'),
    },
  },
});
```

**Step 3: Add test script to package.json**

Add to `"scripts"`:
```json
"test": "vitest run",
"test:watch": "vitest"
```

**Step 4: Write profile compiler tests**

Create `app/components/__tests__/fusion-ring-profile.test.ts`:

```typescript
import { describe, it, expect } from 'vitest';
import {
  compileProfile,
  createDemoProfile,
  WU_XING_ORDER,
  WU_XING_VISUALS,
  ZODIAC_SECTORS,
  ZODIAC_DOMAINS,
  type FusionRingProfile,
} from '../fusion-ring-profile';

describe('compileProfile', () => {
  const demo = createDemoProfile();
  const channels = compileProfile(demo);

  it('returns all 5 channel functions', () => {
    expect(typeof channels.radiusOffset).toBe('function');
    expect(typeof channels.tubeScale).toBe('function');
    expect(typeof channels.roughness).toBe('function');
    expect(typeof channels.colorTint).toBe('function');
    expect(typeof channels.coronaFactor).toBe('function');
  });

  it('radiusOffset returns values in expected range', () => {
    for (let angle = 0; angle < Math.PI * 2; angle += 0.1) {
      const val = channels.radiusOffset(angle);
      expect(val).toBeGreaterThanOrEqual(-0.6);
      expect(val).toBeLessThanOrEqual(0.6);
    }
  });

  it('tubeScale never goes below 0.4', () => {
    for (let angle = 0; angle < Math.PI * 2; angle += 0.1) {
      expect(channels.tubeScale(angle)).toBeGreaterThanOrEqual(0.4);
    }
  });

  it('roughness stays in 0-1 range', () => {
    for (let angle = 0; angle < Math.PI * 2; angle += 0.1) {
      const val = channels.roughness(angle);
      expect(val).toBeGreaterThanOrEqual(0);
      expect(val).toBeLessThanOrEqual(1);
    }
  });

  it('colorTint returns [r, g, b, intensity] tuple', () => {
    const tint = channels.colorTint(0);
    expect(tint).toHaveLength(4);
    tint.forEach(v => {
      expect(v).toBeGreaterThanOrEqual(0);
      expect(v).toBeLessThanOrEqual(1);
    });
  });

  it('coronaFactor is always >= 0.2', () => {
    for (let angle = 0; angle < Math.PI * 2; angle += 0.1) {
      expect(channels.coronaFactor(angle)).toBeGreaterThanOrEqual(0.2);
    }
  });

  it('flat profile produces nearly uniform output', () => {
    const flat: FusionRingProfile = {
      astro: {
        zodiacSignals: Array(12).fill(0.5),
        wuxingStrengths: Array(5).fill(0.5),
        dominantElement: 0,
        ascendantSector: 0,
        baziRoughness: 0.5,
      },
      quizStamps: [],
    };
    const ch = compileProfile(flat);
    const offsets = Array.from({ length: 12 }, (_, i) =>
      ch.radiusOffset((i / 12) * Math.PI * 2)
    );
    const range = Math.max(...offsets) - Math.min(...offsets);
    expect(range).toBeLessThan(0.15); // should be nearly flat
  });
});

describe('WU_XING constants', () => {
  it('has 5 elements in correct order', () => {
    expect(WU_XING_ORDER).toEqual(['wood', 'fire', 'earth', 'metal', 'water']);
  });

  it('each element has color and glow', () => {
    for (const el of WU_XING_ORDER) {
      const vis = WU_XING_VISUALS[el];
      expect(vis.color).toHaveLength(3);
      expect(typeof vis.glow).toBe('number');
    }
  });
});

describe('ZODIAC constants', () => {
  it('has 12 sectors', () => {
    expect(ZODIAC_SECTORS).toHaveLength(12);
  });

  it('each sector has a domain with label and element', () => {
    for (const sector of ZODIAC_SECTORS) {
      const domain = ZODIAC_DOMAINS[sector];
      expect(domain.label).toBeTruthy();
      expect(domain.domain).toBeTruthy();
      expect(WU_XING_ORDER).toContain(domain.element);
    }
  });
});
```

**Step 5: Run tests to verify they pass**

```bash
npx vitest run
```

Expected: All tests pass.

**Step 6: Write transit parser tests**

Create `app/components/__tests__/fusion-ring-transit.test.ts`:

```typescript
import { describe, it, expect } from 'vitest';
import {
  parseTransitState,
  createDemoTransitState,
  createManualTrigger,
  type TransitStateV1,
} from '../fusion-ring-transit';

describe('parseTransitState', () => {
  const demo = createDemoTransitState();
  const parsed = parseTransitState(demo);

  it('returns effectQueue with staggered delays', () => {
    expect(parsed.effectQueue.length).toBeGreaterThan(0);
    for (let i = 1; i < parsed.effectQueue.length; i++) {
      expect(parsed.effectQueue[i].delay).toBeGreaterThanOrEqual(
        parsed.effectQueue[i - 1].delay + parsed.effectQueue[i - 1].duration
      );
    }
  });

  it('maps resonance_jump to resonanzsprung', () => {
    const resonanz = parsed.effectQueue.find(e => e.type === 'resonanzsprung');
    expect(resonanz).toBeDefined();
    expect(resonanz!.sector).toBe(7);
  });

  it('returns 12 sectorEnergy values', () => {
    expect(parsed.sectorEnergy).toHaveLength(12);
  });

  it('returns transitIntensity from contribution', () => {
    expect(parsed.transitIntensity).toBe(0.75);
  });
});

describe('createManualTrigger', () => {
  it('creates trigger with defaults', () => {
    const trigger = createManualTrigger('burst');
    expect(trigger.type).toBe('burst');
    expect(trigger.intensity).toBe(0.8);
    expect(trigger.source).toBe('manual');
  });

  it('clamps intensity to 0-1', () => {
    expect(createManualTrigger('burst', { intensity: 5 }).intensity).toBe(1);
    expect(createManualTrigger('burst', { intensity: -1 }).intensity).toBe(0);
  });
});

describe('deriveComputedEffects (via parseTransitState)', () => {
  it('derives divergenz_spike for rising trend + high delta', () => {
    const state: TransitStateV1 = {
      schema: 'TRANSIT_STATE_v1',
      generated_at: new Date().toISOString(),
      ring: { sectors: Array(12).fill(0) },
      transit_contribution: { sectors: Array(12).fill(0.3), transit_intensity: 0.4 },
      delta: {
        sectors_30d_avg: [0, 0, 0, 0, 0, 0, 0, 0.5, 0, 0, 0, 0],
        trend: 'rising',
      },
      events: [],
    };
    const parsed = parseTransitState(state);
    const divergenz = parsed.effectQueue.find(e => e.type === 'divergenz_spike');
    expect(divergenz).toBeDefined();
    expect(divergenz!.sector).toBe(7);
  });

  it('derives crunch for falling trend + low intensity', () => {
    const state: TransitStateV1 = {
      schema: 'TRANSIT_STATE_v1',
      generated_at: new Date().toISOString(),
      ring: { sectors: Array(12).fill(0) },
      transit_contribution: { sectors: Array(12).fill(0.1), transit_intensity: 0.1 },
      delta: { trend: 'falling' },
      events: [],
    };
    const parsed = parseTransitState(state);
    const crunch = parsed.effectQueue.find(e => e.type === 'crunch');
    expect(crunch).toBeDefined();
  });
});
```

**Step 7: Run all tests**

```bash
npx vitest run
```

Expected: All tests pass.

**Step 8: Commit**

```bash
git add vitest.config.ts package.json app/components/__tests__/
git commit -m "test: bootstrap Vitest with profile compiler and transit parser tests"
```

---

## Task 4: GitHub Actions CI Workflow

**Files:**
- Create: `.github/workflows/ci.yml` (at repo root: `Signatur/`)

**Step 1: Write the workflow**

```yaml
name: CI

on:
  push:
    branches: [main]
    paths:
      - 'fusion_ring_website/nextjs_space/**'
  pull_request:
    branches: [main]
    paths:
      - 'fusion_ring_website/nextjs_space/**'

defaults:
  run:
    working-directory: fusion_ring_website/nextjs_space

jobs:
  build-and-test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
          cache-dependency-path: fusion_ring_website/nextjs_space/package-lock.json

      - name: Install dependencies
        run: npm install --legacy-peer-deps

      - name: Lint
        run: npm run lint

      - name: Type check
        run: npx tsc --noEmit

      - name: Test
        run: npm test

      - name: Build
        run: npm run build

  validate-openapi:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Validate OpenAPI spec
        uses: char0n/swagger-editor-validate@v1
        with:
          definition-file: fusion_ring_website/nextjs_space/docs/openapi.yaml
```

**Step 2: Commit**

```bash
mkdir -p .github/workflows
git add .github/workflows/ci.yml
git commit -m "ci: add GitHub Actions workflow for build, test, lint, and OpenAPI validation"
```

---

## Summary

| Task | What | Impact |
|------|------|--------|
| 1 | README.md | Devs can onboard without reading CLAUDE.md |
| 2 | BAFE schema-mode fix | Clear error instead of silent empty data |
| 3 | Vitest + 15 unit tests | Profile compiler and transit parser are covered |
| 4 | GitHub Actions CI | Lint, type check, test, build, OpenAPI validation on every push |
