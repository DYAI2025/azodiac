# Signatur API Reference

## BAFE Proxy — `/api/calculate/[endpoint]`

The Signatur app proxies requests to the FuFirE (Fusion Firmament Engine) BAFE API to avoid CORS issues. All endpoints accept POST with JSON body.

### Base Configuration

| Setting | Value |
|---------|-------|
| Proxy route | `POST /api/calculate/{endpoint}` |
| BAFE upstream | `BAFE_BASE_URL` env var |
| Default upstream | `https://bafe-production.up.railway.app` |
| Timeout | Inherited from Next.js server (no custom timeout) |

### Request Format (all endpoints)

```typescript
interface BirthInput {
  date: string;   // ISO 8601 local datetime: "1990-06-15T14:30:00"
  tz: string;     // IANA timezone: "Europe/Berlin"
  lon: number;    // Longitude: -180 to 180
  lat: number;    // Latitude: -90 to 90
}
```

### Endpoints

#### `POST /api/calculate/bazi`

BaZi (Four Pillars of Destiny) calculation.

**Additional request fields:** `standard: "CIVIL"`, `boundary: "midnight"`, `strict: true`

**Response shape:**
```typescript
{
  pillars: {
    year:  { stamm: string, zweig: string, tier: string, element: string },
    month: { ... },
    day:   { ... },
    hour:  { ... }
  },
  chinese: { day_master: string, year: { animal: string } }
}
```

#### `POST /api/calculate/western`

Western astrology: planetary positions, houses, angles.

**Response shape:**
```typescript
{
  bodies: Record<string, {
    zodiac_sign: number,  // 0-11 index
    longitude: number,
    speed: number
  }>,
  angles: { Ascendant: number, MC: number },
  houses: Record<string, number>  // house cusp degrees
}
```

**Key bodies:** Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto

#### `POST /api/calculate/wuxing`

Wu Xing (Five Elements) strength calculation.

**Response shape:**
```typescript
{
  wu_xing_vector: {
    Holz: number,    // Wood
    Feuer: number,   // Fire
    Erde: number,    // Earth
    Metall: number,  // Metal
    Wasser: number   // Water
  },
  dominant_element: string,
  contribution_ledger: { western: [...] }
}
```

#### `POST /api/calculate/fusion`

Fusion interpretation (text summary).

#### `POST /api/calculate/tst`

Transit State calculation.

### Error Responses

```typescript
// 400 — Unknown endpoint
{ "error": "Unknown endpoint" }

// 4xx/5xx — BAFE upstream error (status forwarded)
{ "error": "detail message from BAFE", "status": 422 }

// 502 — Network/connection error
{ "error": "fetch failed" }
```

### Client Usage (from fufire-mapper.ts)

```typescript
import { fetchAndMapFuFirE, type BirthInput } from './components/fufire-mapper';

const input: BirthInput = {
  date: '1990-06-15T14:30:00',
  tz: 'Europe/Berlin',
  lon: 13.405,
  lat: 52.52,
};

const result = await fetchAndMapFuFirE(input);
// result.astroBase → ready for FusionRingProfile
// result.raw → { bazi, western, wuxing, errors[] }
```

The mapper calls `bazi`, `western`, and `wuxing` in parallel via `Promise.allSettled`, so partial failures return data from successful endpoints with errors listed in `result.raw.errors`.

---

## Internal APIs (TypeScript Interfaces)

### FusionRingProfile

The core data structure that shapes the ring permanently.

```typescript
interface FusionRingProfile {
  astro: AstroBase;
  quizStamps: DeformationStamp[];
}

interface AstroBase {
  zodiacSignals: number[];      // 12 values 0-1
  wuxingStrengths: number[];    // 5 values 0-1 (wood, fire, earth, metal, water)
  dominantElement: number;      // Index 0-4 into WU_XING_ORDER
  ascendantSector: number;      // Index 0-11
  baziRoughness: number;        // 0-1
}

interface DeformationStamp {
  sectorIndex: number;          // 0-11
  type: DeformationType;        // 'dent'|'bulge'|'ridge'|'groove'|'thickening'|'thinning'
  magnitude: number;            // 0-1
  spread: number;               // 0.5 (narrow) to 2.0 (wide), default 1.0 = ~30deg
  colorTint?: [number, number, number];  // RGB 0-1
  sourceQuiz?: string;
  timestamp?: number;
}
```

### TransitStateV1

External transit data schema for temporary effects.

```typescript
interface TransitStateV1 {
  schema: string;                // "TRANSIT_STATE_v1"
  generated_at: string;          // ISO timestamp
  ring: { sectors: number[] };   // 12 deformation offsets
  transit_contribution: {
    sectors: number[];           // 12 energy values
    transit_intensity: number;   // 0-1 overall
  };
  delta: {
    sectors_30d_avg?: number[];
    trend?: 'rising' | 'falling' | 'stable';
  };
  events: TransitEvent[];
}

interface TransitEvent {
  type: 'resonance_jump' | 'dominance_shift' | 'moon_event';
  priority: number;              // 1-99, higher = more urgent
  sector: number;                // 0-11
  trigger_planet: string;
  description_de: string;
  personal_context: string;
}
```

### QuizClusterResult

Quiz completion data that produces permanent ring deformation.

```typescript
interface QuizClusterResult {
  cluster_id: string;
  quiz_world: string;            // "Filme", "Werte", "Bindung", etc.
  facettes: QuizFacetteResult[];
  completed_at: string;
}

interface QuizFacetteResult {
  facet_label: string;           // "Humor", "Ritual", "Direktheit"
  zone: 'flow' | 'spark' | 'talk';
  zone_strength: number;         // 0-1
  sector_index: number;          // 0-11
}
```

Zone → deformation mapping:
| Zone | Deformation | Visual | Color |
|------|-------------|--------|-------|
| flow | bulge (outward) | Strength expansion | Green-cyan (0.2, 0.9, 0.5) |
| spark | ridge (sharp line) | Exciting contrast | Amber-orange (1.0, 0.5, 0.2) |
| talk | dent (inward) | Unresolved tension | Purple (0.5, 0.3, 0.9) |

### EffectTrigger

Controls visual effects on the ring.

```typescript
interface EffectTrigger {
  type: RingEffectType;
  duration: number;     // seconds
  intensity: number;    // 0-1
  sector: number;       // 0-11 primary sector
  delay: number;        // seconds before triggering
  source: string;       // debug description
}

type RingEffectType =
  | 'resonanzsprung' | 'dominanzwechsel' | 'mond_event'
  | 'spannungsachse' | 'korona_eruption' | 'divergenz_spike'
  | 'burst' | 'crunch';
```

Default durations: resonanzsprung/dominanzwechsel/mond_event/spannungsachse/korona_eruption = 4s, divergenz_spike = 5s, burst = 3.5s, crunch = 4.5s.
