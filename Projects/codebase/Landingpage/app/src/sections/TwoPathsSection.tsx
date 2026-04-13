import React, { useMemo, useRef, useLayoutEffect } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { SunRing, OrnateDivider } from '../components/SunIcon';
import { User, Users } from 'lucide-react';
import { getPathButtonCopy, type ExperimentVariant } from '../utils/experiments';

gsap.registerPlugin(ScrollTrigger);

interface TwoPathsSectionProps {
  onSelectPath: (path: 'character' | 'partnership') => void;
  experimentVariant: ExperimentVariant;
}

export const TwoPathsSection: React.FC<TwoPathsSectionProps> = ({ onSelectPath, experimentVariant }) => {
  const sectionRef = useRef<HTMLElement>(null);
  const buttonCopy = useMemo(() => getPathButtonCopy(experimentVariant), [experimentVariant]);
  const sealRef = useRef<HTMLDivElement>(null);
  const sealLabelRef = useRef<HTMLDivElement>(null);
  const leftCardRef = useRef<HTMLDivElement>(null);
  const rightCardRef = useRef<HTMLDivElement>(null);
  const dividerRef = useRef<HTMLDivElement>(null);

  useLayoutEffect(() => {
    const section = sectionRef.current;
    if (!section) return;

    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReducedMotion) return;

    const ctx = gsap.context(() => {
      const scrollTl = gsap.timeline({
        scrollTrigger: {
          trigger: section,
          start: 'top top',
          end: '+=130%',
          pin: true,
          scrub: 0.6,
        }
      });

      // ENTRANCE (0-30%)
      scrollTl
        // Central seal enters
        .fromTo(sealRef.current,
          { scale: 0.65, opacity: 0, rotation: -25 },
          { scale: 1, opacity: 1, rotation: 0, ease: 'none' },
          0
        )
        // Seal label fades in
        .fromTo(sealLabelRef.current,
          { opacity: 0, y: 10 },
          { opacity: 1, y: 0, ease: 'none' },
          0.12
        )
        // Left card slides in from left
        .fromTo(leftCardRef.current,
          { x: '-40vw', opacity: 0, rotation: -2 },
          { x: 0, opacity: 1, rotation: 0, ease: 'none' },
          0.06
        )
        // Right card slides in from right
        .fromTo(rightCardRef.current,
          { x: '40vw', opacity: 0, rotation: 2 },
          { x: 0, opacity: 1, rotation: 0, ease: 'none' },
          0.10
        )
        // Divider line draws
        .fromTo(dividerRef.current,
          { scaleY: 0 },
          { scaleY: 1, ease: 'none' },
          0.18
        );

      // SETTLE (30-70%): Hold positions - no animation needed

      // EXIT (70-100%)
      scrollTl
        .to(leftCardRef.current,
          { x: '-30vw', opacity: 0, ease: 'power2.in' },
          0.70
        )
        .to(rightCardRef.current,
          { x: '30vw', opacity: 0, ease: 'power2.in' },
          0.70
        )
        .to(sealRef.current,
          { scale: 0.85, opacity: 0, ease: 'power2.in' },
          0.70
        )
        .to(dividerRef.current,
          { scaleY: 0, opacity: 0, ease: 'power2.in' },
          0.78
        )
        .to(sealLabelRef.current,
          { opacity: 0 },
          0.75
        );

    }, section);

    return () => ctx.revert();
  }, []);

  return (
    <section
      ref={sectionRef}
      className="relative w-screen h-screen bg-[#F4EFE6] grain-overlay overflow-hidden z-20"
    >
      {/* Central Seal */}
      <div
        ref={sealRef}
        className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2"
      >
        <div className="relative">
          {/* Outer ring */}
          <SunRing size={320} className="opacity-60" />
          
          {/* Inner circle */}
          <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-[34vmin] h-[34vmin] rounded-full bg-white/85 backdrop-blur-sm flex items-center justify-center">
            <div ref={sealLabelRef} className="text-center">
              <span className="font-mono text-xs uppercase tracking-[0.18em] text-[#6D6A61] block mb-2">
                Choose Your
              </span>
              <span className="font-mono text-xs uppercase tracking-[0.18em] text-[#C8A14A]">
                Reading
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Left Path Card - Character Portrait */}
      <div
        ref={leftCardRef}
        className="absolute left-[8vw] md:left-[14vw] top-1/2 -translate-y-1/2 w-[38vw] md:w-[22vw] max-w-[320px]"
      >
        <div className="bg-white/80 backdrop-blur-sm rounded-sm p-6 md:p-8 shadow-sm hover:shadow-md transition-shadow duration-300 group">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-full bg-[#C8A14A]/10 flex items-center justify-center">
              <User aria-hidden="true" className="w-5 h-5 text-[#C8A14A]" />
            </div>
            <h3 className="text-xl md:text-2xl text-[#14181F]">Character Portrait</h3>
          </div>
          
          <p className="text-sm text-[#6D6A61] mb-6 leading-relaxed">
            Your sun sign, BaZi day master, and elemental balance—unified into one coherent portrait.
          </p>
          
          <button
            type="button"
            onClick={() => onSelectPath('character')}
            className="w-full py-3 px-4 border border-[#053B3F] text-[#053B3F] rounded-sm text-sm font-medium hover:bg-[#053B3F] hover:text-[#F4EFE6] transition-[background-color,color,box-shadow] duration-300"
          >
            {buttonCopy.single}
          </button>
        </div>
      </div>

      {/* Vertical Divider */}
      <div
        ref={dividerRef}
        className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 origin-center hidden md:block"
      >
        <OrnateDivider horizontal={false} className="h-[28vh]" />
      </div>

      {/* Right Path Card - Partnership */}
      <div
        ref={rightCardRef}
        className="absolute right-[8vw] md:right-[14vw] top-1/2 -translate-y-1/2 w-[38vw] md:w-[22vw] max-w-[320px]"
      >
        <div className="bg-white/80 backdrop-blur-sm rounded-sm p-6 md:p-8 shadow-sm hover:shadow-md transition-shadow duration-300 group">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-full bg-[#C8A14A]/10 flex items-center justify-center">
              <Users aria-hidden="true" className="w-5 h-5 text-[#C8A14A]" />
            </div>
            <h3 className="text-xl md:text-2xl text-[#14181F]">Partnership</h3>
          </div>
          
          <p className="text-sm text-[#6D6A61] mb-6 leading-relaxed">
            Compare two charts. See resonance, tension, and shared timing between two souls.
          </p>
          
          <button
            type="button"
            onClick={() => onSelectPath('partnership')}
            className="w-full py-3 px-4 border border-[#053B3F] text-[#053B3F] rounded-sm text-sm font-medium hover:bg-[#053B3F] hover:text-[#F4EFE6] transition-[background-color,color,box-shadow] duration-300"
          >
            {buttonCopy.partner}
          </button>
        </div>
      </div>
    </section>
  );
};
