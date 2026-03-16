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
