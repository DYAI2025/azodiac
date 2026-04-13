import React, { useState, useEffect } from 'react';
import { Sparkles } from 'lucide-react';

interface NavigationProps {
  onNavigate?: (section: string) => void;
}

export const Navigation: React.FC<NavigationProps> = ({ onNavigate }) => {
  const [isScrolled, setIsScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 100);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleClick = (e: React.MouseEvent, section: string) => {
    e.preventDefault();
    if (onNavigate) {
      onNavigate(section);
    }
  };

  const links = [
    { key: 'readings', label: 'Readings', href: '#paths-section', ariaLabel: 'Go to readings' },
    { key: 'method', label: 'Method', href: '#how-it-works-section', ariaLabel: 'Go to method' },
    { key: 'about', label: 'About', href: '#closing-section', ariaLabel: 'Go to about' },
  ] as const;

  return (
    <nav
      aria-label="Main navigation"
      className={`fixed top-0 left-0 right-0 z-[100] transition-[background-color,padding,backdrop-filter,border-color] duration-500 ${
        isScrolled
          ? 'bg-[#F4EFE6]/92 backdrop-blur-md py-4 border-b border-[#C8A14A]/20'
          : 'bg-transparent py-6'
      }`}
    >
      <div className="max-w-7xl mx-auto px-6 md:px-8 flex items-center justify-between">
        {/* Logo */}
        <a
          href="#hero-section"
          onClick={(e) => handleClick(e, 'hero')}
          aria-label="Go to top"
          className="flex items-center gap-2 group"
        >
          <Sparkles aria-hidden="true" className="w-5 h-5 text-[#C8A14A] group-hover:scale-110 transition-transform" />
          <span className="text-xl font-medium text-[#14181F] tracking-tight" translate="no">
            Bazodiac
          </span>
        </a>

        {/* Nav Links */}
        <div className="flex items-center gap-4 md:gap-8">
          {links.map((link) => (
            <a
              key={link.key}
              href={link.href}
              onClick={(e) => handleClick(e, link.key)}
              className="text-xs md:text-sm text-[#6D6A61] hover:text-[#14181F] transition-colors"
              aria-label={link.ariaLabel}
            >
              {link.label}
            </a>
          ))}
        </div>
      </div>
    </nav>
  );
};
