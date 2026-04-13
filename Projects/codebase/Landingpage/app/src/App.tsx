import { useState, useRef, useEffect, useCallback, useMemo } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import './App.css';

import { Navigation } from './components/Navigation';
import { HeroSection } from './sections/HeroSection';
import { TwoPathsSection } from './sections/TwoPathsSection';
import { InputSection } from './sections/InputSection';
import { RevealSection } from './sections/RevealSection';
import { HowItWorksSection } from './sections/HowItWorksSection';
import { SampleReadingsSection } from './sections/SampleReadingsSection';
import { ClosingSection } from './sections/ClosingSection';

import { calculateFullAstrology, type AstrologyResult } from './utils/astrology';
import { getExperimentVariant } from './utils/experiments';
import { trackEvent } from './utils/analytics';

gsap.registerPlugin(ScrollTrigger);

function App() {
  const [selectedPath, setSelectedPath] = useState<'character' | 'partnership' | null>(() => {
    const params = new URLSearchParams(window.location.search);
    const queryPath = params.get('path');
    if (queryPath === 'character' || queryPath === 'partnership') {
      return queryPath;
    }
    return null;
  });
  const [astrologyResult, setAstrologyResult] = useState<AstrologyResult | null>(null);
  const [statusMessage, setStatusMessage] = useState('');
  const experimentVariant = useMemo(() => getExperimentVariant(), []);
  
  const mainRef = useRef<HTMLElement>(null);
  const scrollTriggersRef = useRef<ScrollTrigger[]>([]);

  // Calculate astrology and show reveal
  const handleCalculate = useCallback((
    birthDate: Date, 
    birthTime?: string, 
    partnerDate?: Date, 
    partnerTime?: string
  ) => {
    // Reserved for upcoming multi-chart logic.
    void birthTime;
    void partnerDate;
    void partnerTime;

    const result = calculateFullAstrology(birthDate);
    setAstrologyResult(result);

    trackEvent('calc_submit', {
      variant: experimentVariant,
      path: selectedPath ?? 'unknown',
      hasBirthTime: Boolean(birthTime),
      hasPartnerDate: Boolean(partnerDate),
      hasPartnerTime: Boolean(partnerTime),
    });
    
    // Scroll to reveal section after a brief delay
    setTimeout(() => {
      const revealSection = document.getElementById('reveal-section');
      if (revealSection) {
        revealSection.scrollIntoView({ behavior: 'smooth' });
      }
    }, 100);
  }, [experimentVariant, selectedPath]);

  // Handle path selection
  const handleSelectPath = useCallback((path: 'character' | 'partnership') => {
    setSelectedPath(path);
    trackEvent('path_select', { variant: experimentVariant, path });
    
    // Scroll to input section
    setTimeout(() => {
      const inputSection = document.getElementById('input-section');
      if (inputSection) {
        inputSection.scrollIntoView({ behavior: 'smooth' });
      }
    }, 100);
  }, [experimentVariant]);

  // Handle begin from hero
  const handleBegin = useCallback(() => {
    trackEvent('hero_cta_click', { variant: experimentVariant });

    const pathsSection = document.getElementById('paths-section');
    if (pathsSection) {
      pathsSection.scrollIntoView({ behavior: 'smooth' });
    }
  }, [experimentVariant]);

  // Handle restart
  const handleRestart = useCallback(() => {
    trackEvent('restart_click', { variant: experimentVariant, path: selectedPath ?? 'unknown' });

    setSelectedPath(null);
    setAstrologyResult(null);
    setStatusMessage('');
    
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, [experimentVariant, selectedPath]);

  const announceAction = useCallback((message: string, eventName?: string) => {
    if (eventName) {
      trackEvent(eventName, { variant: experimentVariant, path: selectedPath ?? 'unknown' });
    }

    setStatusMessage(message);
    window.setTimeout(() => setStatusMessage(''), 2400);
  }, [experimentVariant, selectedPath]);

  // Handle navigation
  const handleNavigate = useCallback((section: string) => {
    trackEvent('nav_click', { variant: experimentVariant, section });

    const sectionMap: Record<string, string> = {
      hero: 'hero-section',
      readings: 'paths-section',
      method: 'how-it-works-section',
      about: 'closing-section',
    };
    
    const elementId = sectionMap[section];
    if (elementId) {
      const element = document.getElementById(elementId);
      if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
      }
    }
  }, [experimentVariant]);

  useEffect(() => {
    trackEvent('page_view', {
      variant: experimentVariant,
      path: window.location.pathname,
      query: window.location.search,
    });
  }, [experimentVariant]);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (selectedPath) {
      params.set('path', selectedPath);
    } else {
      params.delete('path');
    }

    const nextQuery = params.toString();
    const nextUrl = `${window.location.pathname}${nextQuery ? `?${nextQuery}` : ''}${window.location.hash}`;
    window.history.replaceState(null, '', nextUrl);
  }, [selectedPath]);

  // Global scroll snap for pinned sections
  useEffect(() => {
    // Wait for all ScrollTriggers to be created
    const timer = setTimeout(() => {
      const pinned = ScrollTrigger.getAll()
        .filter(st => st.vars.pin)
        .sort((a, b) => a.start - b.start);
      
      const maxScroll = ScrollTrigger.maxScroll(window);
      
      if (!maxScroll || pinned.length === 0) return;

      // Build ranges and snap targets from pinned sections
      const pinnedRanges = pinned.map(st => ({
        start: st.start / maxScroll,
        end: (st.end ?? st.start) / maxScroll,
        center: (st.start + ((st.end ?? st.start) - st.start) * 0.5) / maxScroll,
      }));

      // Create global snap
      const snapTrigger = ScrollTrigger.create({
        snap: {
          snapTo: (value: number) => {
            // Check if within any pinned range (with buffer)
            const inPinned = pinnedRanges.some(
              r => value >= r.start - 0.02 && value <= r.end + 0.02
            );
            
            if (!inPinned) return value; // Flowing section: free scroll

            // Find nearest pinned center
            const target = pinnedRanges.reduce((closest, r) =>
              Math.abs(r.center - value) < Math.abs(closest - value) ? r.center : closest,
              pinnedRanges[0]?.center ?? 0
            );
            
            return target;
          },
          duration: { min: 0.15, max: 0.35 },
          delay: 0,
          ease: 'power2.out',
        }
      });

      scrollTriggersRef.current.push(snapTrigger);
    }, 500);

    return () => {
      clearTimeout(timer);
      scrollTriggersRef.current.forEach(st => st.kill());
      scrollTriggersRef.current = [];
    };
  }, []);

  // Cleanup all ScrollTriggers on unmount
  useEffect(() => {
    return () => {
      ScrollTrigger.getAll().forEach(st => st.kill());
    };
  }, []);

  return (
    <div className="relative">
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-[200] focus:rounded-sm focus:bg-[#053B3F] focus:px-4 focus:py-2 focus:text-[#F4EFE6]"
      >
        Skip to content
      </a>

      <div aria-live="polite" className="sr-only">{statusMessage}</div>

      <Navigation onNavigate={handleNavigate} />
      
      <main id="main-content" ref={mainRef} className="relative">
        {/* Section 1: Hero - pin: true */}
        <div id="hero-section" className="scroll-mt-24">
          <HeroSection onBegin={handleBegin} experimentVariant={experimentVariant} />
        </div>

        {/* Section 2: Two Paths - pin: true */}
        <div id="paths-section" className="scroll-mt-24">
          <TwoPathsSection onSelectPath={handleSelectPath} experimentVariant={experimentVariant} />
        </div>

        {/* Section 3: Input Ceremony - pin: true */}
        <div id="input-section" className="scroll-mt-24">
          <InputSection 
            pathType={selectedPath} 
            onCalculate={handleCalculate} 
          />
        </div>

        {/* Section 4: The Reveal - pin: true */}
        <div id="reveal-section" className="scroll-mt-24">
          <RevealSection 
            result={astrologyResult}
            onSave={() => announceAction('Saved locally. PDF export is coming soon…', 'reveal_save_click')}
            onShare={() => announceAction('Share link copied soon. Sharing options are coming soon…', 'reveal_share_click')}
            onReadFull={() => announceAction('Full analysis is coming soon…', 'reveal_read_full_click')}
          />
        </div>

        {/* Section 5: How It Works - pin: false (flowing) */}
        <div id="how-it-works-section" className="scroll-mt-24">
          <HowItWorksSection />
        </div>

        {/* Section 6: Sample Readings - pin: false (flowing) */}
        <div id="sample-readings-section" className="scroll-mt-24">
          <SampleReadingsSection />
        </div>

        {/* Section 7: Closing - pin: false (flowing) */}
        <div id="closing-section" className="scroll-mt-24">
          <ClosingSection onRestart={handleRestart} />
        </div>
      </main>
    </div>
  );
}

export default App;
