'use client';

import { useState, useCallback } from 'react';
import type { BirthInput, FuFireResult } from './fufire-mapper';
import { fetchAndMapFuFirE } from './fufire-mapper';
import type { FusionRingProfile } from './fusion-ring-profile';
import { createDemoProfile, ZODIAC_SECTORS, ZODIAC_DOMAINS, WU_XING_ORDER, WU_XING_VISUALS } from './fusion-ring-profile';

interface Props {
  onProfileChange: (profile: FusionRingProfile) => void;
}

type ViewTab = 'form' | 'profile' | 'raw';

export default function BirthInputPanel({ onProfileChange }: Props) {
  const [date, setDate] = useState('1990-06-15');
  const [time, setTime] = useState('14:30');
  const [tz, setTz] = useState('Europe/Berlin');
  const [lat, setLat] = useState('52.52');
  const [lon, setLon] = useState('13.405');

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<FuFireResult | null>(null);
  const [activeTab, setActiveTab] = useState<ViewTab>('form');

  const handleSubmit = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const input: BirthInput = {
        date: `${date}T${time}:00`,
        tz,
        lat: parseFloat(lat),
        lon: parseFloat(lon),
      };
      if (!Number.isFinite(input.lat) || !Number.isFinite(input.lon)) {
        throw new Error('Ungültige Koordinaten');
      }
      const res = await fetchAndMapFuFirE(input);
      setResult(res);
      setActiveTab('profile');
      onProfileChange({ astro: res.astroBase, quizStamps: [] });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unbekannter Fehler');
    } finally {
      setLoading(false);
    }
  }, [date, time, tz, lat, lon, onProfileChange]);

  return (
    <div className="absolute top-4 left-4 z-50 w-80 max-h-[calc(100vh-2rem)] flex flex-col bg-black/80 backdrop-blur-md border border-white/10 rounded-xl overflow-hidden text-white text-sm">
      {/* Tab bar */}
      <div className="flex border-b border-white/10 shrink-0">
        {(['form', 'profile', 'raw'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`flex-1 py-2 text-xs font-medium uppercase tracking-wider transition-colors
              ${activeTab === tab ? 'text-cyan-400 border-b-2 border-cyan-400' : 'text-white/40 hover:text-white/60'}`}
          >
            {tab === 'form' ? 'Eingabe' : tab === 'profile' ? 'Signatur' : 'API Raw'}
          </button>
        ))}
      </div>

      {/* Scrollable content */}
      <div className="overflow-y-auto flex-1 scrollbar-hide">
        {/* ── FORM TAB ── */}
        {activeTab === 'form' && (
          <div className="p-4 space-y-3">
            <label className="block">
              <span className="text-white/50 text-xs">Geburtsdatum</span>
              <input
                type="date"
                value={date}
                onChange={(e) => setDate(e.target.value)}
                className="mt-1 w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white focus:border-cyan-500/50 focus:outline-none"
              />
            </label>
            <label className="block">
              <span className="text-white/50 text-xs">Geburtszeit</span>
              <input
                type="time"
                value={time}
                onChange={(e) => setTime(e.target.value)}
                className="mt-1 w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white focus:border-cyan-500/50 focus:outline-none"
              />
            </label>
            <label className="block">
              <span className="text-white/50 text-xs">Zeitzone</span>
              <select
                value={tz}
                onChange={(e) => setTz(e.target.value)}
                className="mt-1 w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white focus:border-cyan-500/50 focus:outline-none"
              >
                <option value="Europe/Berlin">Europe/Berlin</option>
                <option value="Europe/London">Europe/London</option>
                <option value="America/New_York">America/New_York</option>
                <option value="America/Los_Angeles">America/Los_Angeles</option>
                <option value="Asia/Tokyo">Asia/Tokyo</option>
                <option value="Asia/Shanghai">Asia/Shanghai</option>
                <option value="Australia/Sydney">Australia/Sydney</option>
              </select>
            </label>
            <div className="grid grid-cols-2 gap-2">
              <label className="block">
                <span className="text-white/50 text-xs">Breitengrad</span>
                <input
                  type="text"
                  value={lat}
                  onChange={(e) => setLat(e.target.value)}
                  placeholder="52.52"
                  className="mt-1 w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white focus:border-cyan-500/50 focus:outline-none"
                />
              </label>
              <label className="block">
                <span className="text-white/50 text-xs">Längengrad</span>
                <input
                  type="text"
                  value={lon}
                  onChange={(e) => setLon(e.target.value)}
                  placeholder="13.405"
                  className="mt-1 w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white focus:border-cyan-500/50 focus:outline-none"
                />
              </label>
            </div>

            <button
              onClick={handleSubmit}
              disabled={loading}
              className="w-full py-2.5 rounded-lg font-medium text-sm transition-all
                bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500
                disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Signatur wird gelesen...
                </span>
              ) : (
                'Signatur enthüllen'
              )}
            </button>

            <button
              onClick={() => {
                const demo = createDemoProfile();
                const demoResult: FuFireResult = {
                  astroBase: demo.astro,
                  raw: { bazi: {}, western: {}, wuxing: {}, errors: [] },
                };
                setResult(demoResult);
                setActiveTab('profile');
                onProfileChange(demo);
              }}
              className="w-full py-2 rounded-lg text-xs text-white/40 border border-white/10 hover:border-white/20 hover:text-white/60 transition-all"
            >
              Demo-Signatur laden
            </button>

            {error && (
              <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-300 text-xs">
                {error}
              </div>
            )}

            {result && result.raw.errors.length > 0 && (
              <div className="p-3 rounded-lg bg-yellow-500/10 border border-yellow-500/30 text-yellow-300 text-xs space-y-1">
                <p className="font-medium">Teilweise Daten:</p>
                {result.raw.errors.map((e, i) => (
                  <p key={i}>• {e}</p>
                ))}
              </div>
            )}
          </div>
        )}

        {/* ── PROFILE TAB ── */}
        {activeTab === 'profile' && result && (
          <div className="p-4 space-y-4">
            {/* Wu Xing Strengths */}
            <div>
              <h3 className="text-xs font-medium text-white/50 uppercase tracking-wider mb-2">Wu Xing Elemente</h3>
              <div className="space-y-1.5">
                {WU_XING_ORDER.map((el, i) => {
                  const strength = result.astroBase.wuxingStrengths[i];
                  const [r, g, b] = WU_XING_VISUALS[el].color;
                  const color = `rgb(${Math.round(r * 255)}, ${Math.round(g * 255)}, ${Math.round(b * 255)})`;
                  const isDominant = i === result.astroBase.dominantElement;
                  return (
                    <div key={el} className="flex items-center gap-2">
                      <span className={`w-14 text-xs capitalize ${isDominant ? 'text-white font-bold' : 'text-white/60'}`}>
                        {el}
                      </span>
                      <div className="flex-1 h-2 bg-white/5 rounded-full overflow-hidden">
                        <div
                          className="h-full rounded-full transition-all duration-700"
                          style={{ width: `${strength * 100}%`, backgroundColor: color }}
                        />
                      </div>
                      <span className="text-xs text-white/40 w-8 text-right">{(strength * 100).toFixed(0)}%</span>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Zodiac Sector Signals */}
            <div>
              <h3 className="text-xs font-medium text-white/50 uppercase tracking-wider mb-2">Sektor-Signale</h3>
              <div className="space-y-1">
                {ZODIAC_SECTORS.map((sector, i) => {
                  const signal = result.astroBase.zodiacSignals[i];
                  const domain = ZODIAC_DOMAINS[sector];
                  const isAsc = i === result.astroBase.ascendantSector;
                  const [r, g, b] = WU_XING_VISUALS[domain.element].color;
                  const color = `rgb(${Math.round(r * 255)}, ${Math.round(g * 255)}, ${Math.round(b * 255)})`;
                  return (
                    <div key={sector} className="flex items-center gap-2">
                      <span className={`w-20 text-xs truncate ${isAsc ? 'text-cyan-400 font-bold' : 'text-white/60'}`}>
                        {domain.label} {isAsc ? 'AC' : ''}
                      </span>
                      <div className="flex-1 h-1.5 bg-white/5 rounded-full overflow-hidden">
                        <div
                          className="h-full rounded-full transition-all duration-700"
                          style={{ width: `${signal * 100}%`, backgroundColor: color, opacity: 0.7 + signal * 0.3 }}
                        />
                      </div>
                      <span className="text-xs text-white/30 w-6 text-right">{(signal * 100).toFixed(0)}</span>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Meta info */}
            <div className="pt-2 border-t border-white/10 text-xs text-white/30 space-y-1">
              <p>Dominant: <span className="text-white/60 capitalize">{WU_XING_ORDER[result.astroBase.dominantElement]}</span></p>
              <p>Aszendent: <span className="text-white/60">{ZODIAC_DOMAINS[ZODIAC_SECTORS[result.astroBase.ascendantSector]].label}</span></p>
              <p>Roughness: <span className="text-white/60">{result.astroBase.baziRoughness.toFixed(2)}</span></p>
            </div>
          </div>
        )}

        {activeTab === 'profile' && !result && (
          <div className="p-8 text-center text-white/30 text-xs">
            Noch keine Daten — gib Geburtsdaten ein.
          </div>
        )}

        {/* ── RAW TAB ── */}
        {activeTab === 'raw' && result && (
          <div className="p-4 space-y-3">
            <div>
              <h3 className="text-xs font-medium text-white/50 uppercase tracking-wider mb-1">BAFE BaZi Response</h3>
              <pre className="text-[10px] text-green-300/70 bg-white/5 rounded-lg p-2 overflow-x-auto max-h-40">
                {JSON.stringify(result.raw.bazi, null, 2)}
              </pre>
            </div>
            <div>
              <h3 className="text-xs font-medium text-white/50 uppercase tracking-wider mb-1">BAFE Western Response</h3>
              <pre className="text-[10px] text-blue-300/70 bg-white/5 rounded-lg p-2 overflow-x-auto max-h-40">
                {JSON.stringify(result.raw.western, null, 2)}
              </pre>
            </div>
            <div>
              <h3 className="text-xs font-medium text-white/50 uppercase tracking-wider mb-1">BAFE WuXing Response</h3>
              <pre className="text-[10px] text-amber-300/70 bg-white/5 rounded-lg p-2 overflow-x-auto max-h-40">
                {JSON.stringify(result.raw.wuxing, null, 2)}
              </pre>
            </div>
            <div>
              <h3 className="text-xs font-medium text-white/50 uppercase tracking-wider mb-1">Mapped AstroBase</h3>
              <pre className="text-[10px] text-cyan-300/70 bg-white/5 rounded-lg p-2 overflow-x-auto max-h-40">
                {JSON.stringify(result.astroBase, null, 2)}
              </pre>
            </div>
          </div>
        )}

        {activeTab === 'raw' && !result && (
          <div className="p-8 text-center text-white/30 text-xs">
            Noch keine API-Daten — enthülle deine Signatur.
          </div>
        )}
      </div>
    </div>
  );
}
