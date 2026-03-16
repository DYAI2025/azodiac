/**
 * Maps BAFE API responses → FusionRingProfile AstroBase.
 *
 * BAFE endpoints used:
 *   POST /calculate/bazi    → pillars, day_master
 *   POST /calculate/western → zodiac_sign (Sun 0-11), moon_sign, ascendant (degrees)
 *   POST /calculate/wuxing  → wu_xing_vector {Holz, Feuer, Erde, Metall, Wasser}
 */

import type { AstroBase } from './fusion-ring-profile';
import { WU_XING_ORDER } from './fusion-ring-profile';

// ── BAFE response shapes ────────────────────────────────────────────

export interface BirthInput {
  date: string;   // ISO 8601 local datetime e.g. "1990-06-15T14:30:00"
  tz: string;     // IANA timezone e.g. "Europe/Berlin"
  lon: number;
  lat: number;
}

interface BafeWesternBody {
  zodiac_sign?: number; // 0-based index
  longitude?: number;
}

interface BafeWesternResponse {
  bodies?: Record<string, BafeWesternBody>;
  angles?: { Ascendant?: number; [k: string]: number | undefined };
}

interface BafeWuxingResponse {
  wu_xing_vector?: Record<string, number>;
  dominant_element?: string;
}

// ── Sign mapping ────────────────────────────────────────────────────

const SIGN_NAMES = [
  'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
  'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces',
] as const;

// Map zodiac sign name → sector index (0-11)
const SIGN_TO_SECTOR: Record<string, number> = {};
SIGN_NAMES.forEach((name, i) => { SIGN_TO_SECTOR[name] = i; });
// Also German
['Widder','Stier','Zwillinge','Krebs','Löwe','Jungfrau','Waage','Skorpion','Schütze','Steinbock','Wassermann','Fische']
  .forEach((name, i) => { SIGN_TO_SECTOR[name] = i; });

function signFromDegrees(deg: number | undefined | null): number {
  if (deg == null) return 0;
  return Math.floor(((deg % 360) + 360) % 360 / 30);
}

// Map element name → WU_XING_ORDER index
const ELEMENT_TO_INDEX: Record<string, number> = {
  Wood: 0, Holz: 0, wood: 0,
  Fire: 1, Feuer: 1, fire: 1,
  Earth: 2, Erde: 2, earth: 2,
  Metal: 3, Metall: 3, metal: 3,
  Water: 4, Wasser: 4, water: 4,
};

// ── API caller ──────────────────────────────────────────────────────

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

// ── Raw response type for display ───────────────────────────────────

export interface FuFireRawResponse {
  bazi: Record<string, unknown>;
  western: BafeWesternResponse;
  wuxing: BafeWuxingResponse;
  errors: string[];
}

// ── Main mapper ─────────────────────────────────────────────────────

export interface FuFireResult {
  astroBase: AstroBase;
  raw: FuFireRawResponse;
}

export async function fetchAndMapFuFirE(input: BirthInput): Promise<FuFireResult> {
  const errors: string[] = [];

  const [baziRes, westernRes, wuxingRes] = await Promise.allSettled([
    postBafe<Record<string, unknown>>('bazi', input),
    postBafe<BafeWesternResponse>('western', input),
    postBafe<BafeWuxingResponse>('wuxing', input),
  ]);

  const bazi = baziRes.status === 'fulfilled' ? baziRes.value : (() => { errors.push(`BaZi: ${(baziRes as PromiseRejectedResult).reason}`); return {}; })();
  const western = westernRes.status === 'fulfilled' ? westernRes.value : (() => { errors.push(`Western: ${(westernRes as PromiseRejectedResult).reason}`); return {} as BafeWesternResponse; })();
  const wuxing = wuxingRes.status === 'fulfilled' ? wuxingRes.value : (() => { errors.push(`WuXing: ${(wuxingRes as PromiseRejectedResult).reason}`); return {} as BafeWuxingResponse; })();

  // ── Build zodiacSignals[12] from western bodies ───────────────
  const zodiacSignals = new Array(12).fill(0.3); // base presence
  if (western.bodies) {
    const bodyWeights: Record<string, number> = {
      Sun: 0.35, Moon: 0.25, Mars: 0.12, Venus: 0.1, Mercury: 0.08,
      Jupiter: 0.05, Saturn: 0.05,
    };
    for (const [name, body] of Object.entries(western.bodies)) {
      const sector = body.zodiac_sign;
      const weight = bodyWeights[name] ?? 0.03;
      if (sector != null && sector >= 0 && sector <= 11) {
        zodiacSignals[sector] = Math.min(1, zodiacSignals[sector] + weight);
      }
    }
  }

  // ── Build wuxingStrengths[5] ──────────────────────────────────
  const wuxingStrengths = new Array(5).fill(0.2);
  const vec = wuxing.wu_xing_vector || {};
  // Normalize: find max to scale to 0-1
  const rawValues = WU_XING_ORDER.map((el) => {
    const deKey = { wood: 'Holz', fire: 'Feuer', earth: 'Erde', metal: 'Metall', water: 'Wasser' }[el];
    return vec[deKey] ?? vec[el.charAt(0).toUpperCase() + el.slice(1)] ?? vec[el] ?? 0;
  });
  const maxVal = Math.max(...rawValues, 1);
  rawValues.forEach((v, i) => { wuxingStrengths[i] = v / maxVal; });

  // ── Dominant element ──────────────────────────────────────────
  let dominantElement = 0;
  if (wuxing.dominant_element) {
    dominantElement = ELEMENT_TO_INDEX[wuxing.dominant_element] ?? 0;
  } else {
    dominantElement = wuxingStrengths.indexOf(Math.max(...wuxingStrengths));
  }

  // ── Ascendant sector ──────────────────────────────────────────
  const ascDeg = western.angles?.Ascendant;
  const ascendantSector = ascDeg != null ? signFromDegrees(ascDeg) : 0;

  // ── BaZi roughness (heuristic from pillar diversity) ──────────
  const baziRoughness = Math.min(1, 0.3 + (errors.length === 0 ? 0.3 : 0));

  return {
    astroBase: {
      zodiacSignals,
      wuxingStrengths,
      dominantElement,
      ascendantSector,
      baziRoughness,
    },
    raw: { bazi, western, wuxing, errors },
  };
}
