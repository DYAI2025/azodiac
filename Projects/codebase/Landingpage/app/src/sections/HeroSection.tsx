import React, { useRef, useLayoutEffect } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { SunIcon, SunRing } from '../components/SunIcon';
import { ChevronDown } from 'lucide-react';

gsap.registerPlugin(ScrollTrigger);

interface HeroSectionProps {
  onBegin: () => void;
}

export const HeroSection: React.FC<HeroSectionProps> = ({ onBegin }) => {
  const sectionRef = useRef<HTMLElement>(null);
  const ringRef = useRef<HTMLDivElement>(null);
  const sunRef = useRef<HTMLDivElement>(null);
  const labelRef = useRef<HTMLDivElement>(null);
  const headlineRef = useRef<HTMLHeadingElement>(null);
  const subheadRef = useRef<HTMLParagraphElement>(null);
  const ctaRef = useRef<HTMLButtonElement>(null);

  useLayoutEffect(() => {
    const section = sectionRef.current;
    if (!section) return;

    const ctx = gsap.context(() => {
      // Auto-play entrance animation on load
      const loadTl = gsap.timeline({ defaults: { ease: 'power2.out' } });
      
      loadTl
        .fromTo(ringRef.current, 
          { scale: 0.85, opacity: 0, rotation: -12 },
          { scale: 1, opacity: 1, rotation: 0, duration: 1.1 }
        )
        .fromTo(sunRef.current,
          { scale: 0.6, opacity: 0 },
          { scale: 1, opacity: 1, duration: 0.8 },
          0.2
        )
        .fromTo(labelRef.current,
          { y: -12, opacity: 0 },
          { y: 0, opacity: 1, duration: 0.6 },
          0.4
        )
        .fromTo(headlineRef.current?.querySelectorAll('.word') || [],
          { y: 24, opacity: 0 },
          { y: 0, opacity: 1, duration: 0.6, stagger: 0.03 },
          0.5
        )
        .fromTo([subheadRef.current, ctaRef.current],
          { y: 16, opacity: 0 },
          { y: 0, opacity: 1, duration: 0.6, stagger: 0.1 },
          0.7
        );

      // Scroll-driven exit animation
      const scrollTl = gsap.timeline({
        scrollTrigger: {
          trigger: section,
          start: 'top top',
          end: '+=130%',
          pin: true,
          scrub: 0.6,
          onLeaveBack: () => {
            // Reset all elements to visible when scrolling back to top
            gsap.set([ringRef.current, sunRef.current, labelRef.current, headlineRef.current, subheadRef.current, ctaRef.current], {
              opacity: 1,
              y: 0,
              scale: 1,
              rotation: 0,
            });
          }
        }
      });

      // ENTRANCE (0-30%): Hold - elements already visible from load animation
      // SETTLE (30-70%): Static
      // EXIT (70-100%): Elements exit
      scrollTl
        .fromTo(ringRef.current,
          { rotation: 0, scale: 1, opacity: 1 },
          { rotation: 90, scale: 1.25, opacity: 0, ease: 'power2.in' },
          0.70
        )
        .fromTo([headlineRef.current, subheadRef.current, ctaRef.current],
          { y: 0, opacity: 1 },
          { y: '-18vh', opacity: 0, ease: 'power2.in' },
          0.70
        )
        .fromTo(labelRef.current,
          { opacity: 1 },
          { opacity: 0 },
          0.70
        )
        .fromTo(sunRef.current,
          { opacity: 1 },
          { opacity: 0 },
          0.85
        );

    }, section);

    return () => ctx.revert();
  }, []);

  return (
    <section
      ref={sectionRef}
      className="relative w-screen h-screen bg-[#F4EFE6] grain-overlay overflow-hidden z-10"
    >
      {/* Sun Ring */}
      <div
        ref={ringRef}
        className="absolute left-1/2 top-[40%] md:top-[52%] -translate-x-1/2 -translate-y-1/2 sun-ring"
        style={{ width: '62vmin', height: '62vmin' }}
      >
        <SunRing size={undefined} className="w-full h-full" />
      </div>

      {/* Center Sun Icon */}
      <div
        ref={sunRef}
        className="absolute left-1/2 top-[40%] md:top-[52%] -translate-x-1/2 -translate-y-1/2"
      >
        <SunIcon size={undefined} className="w-[8vmin] h-[8vmin]" opacity={0.18} />
      </div>

      {/* Micro Label */}
      <div
        ref={labelRef}
        className="absolute left-1/2 top-[18%] md:top-[30%] -translate-x-1/2"
      >
        <span className="font-mono text-xs uppercase tracking-[0.18em] text-[#6D6A61]">
          Western · BaZi · WuXing
        </span>
      </div>

      {/* Headline */}
      <h1
        ref={headlineRef}
        className="absolute left-1/2 top-[42%] md:top-[52%] -translate-x-1/2 -translate-y-1/2 text-center px-4"
      >
        <span className="block text-[clamp(36px,6vw,76px)] leading-[0.95] tracking-[-0.01em] text-[#14181F]">
          <span className="word inline-block">Three</span>{' '}
          <span className="word inline-block">ancient</span>{' '}
          <span className="word inline-block">systems.</span>
        </span>
        <span className="block text-[clamp(36px,6vw,76px)] leading-[0.95] tracking-[-0.01em] text-[#14181F] mt-2">
          <span className="word inline-block">One</span>{' '}
          <span className="word inline-block">portrait</span>{' '}
          <span className="word inline-block">of</span>{' '}
          <span className="word inline-block">you.</span>
        </span>
      </h1>

      {/* Subheadline */}
      <p
        ref={subheadRef}
        className="absolute left-1/2 top-[66%] md:top-[73%] -translate-x-1/2 text-center max-w-[52ch] text-base md:text-lg text-[#6D6A61] px-6"
      >
        A single, modern reading that fuses Western astrology, BaZi, and WuXing into practical clarity.
      </p>

      {/* CTA Button */}
      <button
        ref={ctaRef}
        onClick={onBegin}
        className="absolute left-1/2 top-[78%] md:top-[84%] -translate-x-1/2 group flex items-center gap-2 px-8 py-3 bg-[#053B3F] text-[#F4EFE6] rounded-sm font-medium text-sm tracking-wide hover:bg-[#0A4A4E] transition-all duration-300 hover:-translate-y-0.5 hover:shadow-lg"
      >
        Begin Reading
        <ChevronDown className="w-4 h-4 group-hover:translate-y-0.5 transition-transform" />
      </button>
    </section>
  );
};
