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
    expect(range).toBeLessThan(0.15);
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
