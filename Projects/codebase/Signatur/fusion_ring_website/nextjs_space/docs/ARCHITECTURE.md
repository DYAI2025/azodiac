# Signatur Architecture

## System Context

```mermaid
graph TB
    User([User / Browser])

    subgraph "Signatur App"
        NextJS[Next.js 14<br/>App Router]
        ProxyAPI["/api/calculate/[endpoint]<br/>BAFE Proxy"]
        FRCanvas[Fusion Ring Canvas<br/>Three.js + GLSL]
        BirthPanel[Birth Input Panel<br/>React UI]
    end

    subgraph "External Services"
        BAFE[FuFirE / BAFE<br/>Railway]
        QuizzMe[QuizzMe Engine<br/>Quiz Clusters]
        Levi[Levi<br/>Conversation AI]
    end

    DB[(PostgreSQL)]

    User --> NextJS
    NextJS --> ProxyAPI
    ProxyAPI -->|POST /calculate/*| BAFE
    NextJS --> FRCanvas
    NextJS --> BirthPanel
    BirthPanel -->|birth data| ProxyAPI
    QuizzMe -->|QuizClusterResult| FRCanvas
    Levi -->|ConversationProfile| FRCanvas
    NextJS --> DB
```

## Component Architecture

```mermaid
graph LR
    subgraph "Entry Points"
        Page["page.tsx<br/>(App Router)"]
    end

    subgraph "UI Layer"
        BIP["birth-input-panel.tsx<br/>Form + Results Display"]
        Scene["fusion-ring-scene.tsx<br/>Dynamic Import Wrapper"]
    end

    subgraph "Data Layer"
        Mapper["fufire-mapper.ts<br/>BAFE → AstroBase"]
        Profile["fusion-ring-profile.ts<br/>Profile Compiler"]
        Input["fusion-ring-input.ts<br/>Input Controller"]
        Transit["fusion-ring-transit.ts<br/>Transit Parser"]
    end

    subgraph "Render Layer"
        Canvas["fusion-ring-canvas.tsx<br/>Three.js + GLSL<br/>28k particles"]
        Audio["fusion-ring-audio.ts<br/>Web Audio API<br/>Procedural"]
    end

    Page --> BIP
    Page --> Scene
    Scene -->|dynamic import, ssr:false| Canvas
    BIP -->|fetchAndMapFuFirE| Mapper
    Mapper -->|AstroBase| BIP
    BIP -->|FusionRingProfile| Scene
    Profile -->|DeformationChannels| Canvas
    Input -->|EffectTrigger| Canvas
    Input -->|profile update| Profile
    Transit -->|ParsedTransitData| Input
    Canvas --> Audio
```

## Data Flow: Birth Input to Ring

```mermaid
sequenceDiagram
    participant U as User
    participant BIP as BirthInputPanel
    participant API as /api/calculate/*
    participant BAFE as BAFE Railway
    participant M as fufire-mapper
    participant P as fusion-ring-profile
    participant C as fusion-ring-canvas

    U->>BIP: Enter birth data
    U->>BIP: Click "Signatur enthüllen"
    BIP->>M: fetchAndMapFuFirE(input)

    par Parallel API calls
        M->>API: POST /api/calculate/bazi
        API->>BAFE: POST /calculate/bazi
        BAFE-->>API: BaZi response
        API-->>M: BaZi data
    and
        M->>API: POST /api/calculate/western
        API->>BAFE: POST /calculate/western
        BAFE-->>API: Western response
        API-->>M: Western data
    and
        M->>API: POST /api/calculate/wuxing
        API->>BAFE: POST /calculate/wuxing
        BAFE-->>API: WuXing response
        API-->>M: WuXing data
    end

    M->>M: Map western bodies → zodiacSignals[12]
    M->>M: Normalize wu_xing_vector → wuxingStrengths[5]
    M->>M: Extract ascendant, dominant element

    M-->>BIP: FuFireResult { astroBase, raw }
    BIP->>BIP: Display profile (Signatur tab)
    BIP->>C: onProfileChange({ astro, quizStamps: [] })
    C->>P: compileProfile(profile)
    P-->>C: 5 DeformationChannels
    C->>C: Ring rebuilds with new particle positions
```

## Data Flow: Quiz Completion

```mermaid
sequenceDiagram
    participant QM as QuizzMe Engine
    participant IC as InputController
    participant P as Profile
    participant C as Canvas

    QM->>IC: ingestQuizCluster(result)
    IC->>IC: Map facettes → DeformationStamps
    Note over IC: flow→bulge, spark→ridge, talk→dent
    IC->>P: Append stamps to profile.quizStamps
    IC->>C: onProfileUpdate(profile)
    IC->>C: Trigger 'burst' effect on affected sector
    C->>C: Ring rebuilds + burst animation
```

## Data Flow: Transit State

```mermaid
sequenceDiagram
    participant API as Transit API
    participant IC as InputController
    participant T as TransitParser
    participant C as Canvas

    API->>IC: ingestTransitState(state)
    IC->>T: parseTransitState(state)
    T->>T: Map events → EffectTriggers (priority-sorted)
    T->>T: Derive computed effects (opposition, eruption, divergence)
    T->>T: Stagger delays to prevent overlap
    T-->>IC: ParsedTransitData

    loop Effect Queue (staggered)
        IC->>C: onEffect(trigger) after delay
        C->>C: Play effect (GLSL animation + audio)
    end
```

## Module Responsibilities

### fusion-ring-profile.ts — The Brain

Defines the ring's permanent shape from two additive layers:

1. **AstroBase** (immutable): zodiac signals, Wu Xing strengths, BaZi roughness
2. **QuizStamps** (accumulating): deformation stamps from completed quizzes + Levi sessions

`compileProfile()` compiles both into 5 continuous functions that the renderer samples per-particle:

| Channel | Input Sources | Output |
|---------|--------------|--------|
| radiusOffset | zodiac signals, ascendant, bulge/dent/ridge/groove stamps | Hills and valleys in the ring |
| tubeScale | dominant element, thickening/thinning stamps | Ring tube thickness |
| roughness | BaZi roughness, zodiac signals, tension stamps | Surface texture scatter |
| colorTint | Wu Xing element colors, stamp color overrides | Sector coloring |
| coronaFactor | zodiac signals, bulge/ridge stamps | Corona strand height |

### fusion-ring-canvas.tsx — The Renderer

2000+ line Three.js renderer with:
- Custom vertex/fragment GLSL shaders for particles
- 28k ring particles + 3k corona particles + 500 dust particles
- ACES Filmic tone mapping, exposure 1.8, fog at 16-40 distance
- 8 effect animations with per-particle displacement
- Debug UI panel with effect buttons and profile controls
- `updateProfile()` triggers ring geometry rebuild via `window.__fusionRingRebuild`

### fusion-ring-input.ts — The Controller

Unified input manager for all 3 data channels:

| Channel | Weight | Source | Persistence |
|---------|--------|--------|-------------|
| A: Transit | T=0.18 | TRANSIT_STATE_v1 JSON | Temporary (session) |
| B: Quiz | via stamps | QuizClusterResult | Permanent (accumulating) |
| C: Conversation | C=0.10 | Levi ConversationProfile | Semi-permanent (bucket) |

Manages effect queue with proper staggering (4s between events, re-stagger on overlap).

### fusion-ring-transit.ts — The Transit Parser

Parses TRANSIT_STATE_v1 into:
- Explicit effects from `events[]` (resonance_jump, dominance_shift, moon_event)
- Derived effects from patterns:
  - **spannungsachse**: sector opposition > 0.4
  - **korona_eruption**: transit intensity > 0.7
  - **divergenz_spike**: rising trend + delta > 0.3
  - **burst**: 4+ sectors > 0.6
  - **crunch**: falling trend + intensity < 0.3

### fusion-ring-audio.ts — The Sound

Procedural Web Audio API (no audio files):
- Sub-bass drone: 3 oscillators at 32Hz, 48Hz, 24Hz
- LFO modulation for breathing rhythm
- Thunder peaks triggered by effects
- Lazy AudioContext init (requires user gesture)

## Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `BAFE_BASE_URL` | FuFirE API upstream | `https://bafe-production.up.railway.app` |
| `DATABASE_URL` | PostgreSQL connection string | Required for Prisma |
| `NEXTAUTH_URL` | Base URL for metadata | `http://localhost:3000` |
