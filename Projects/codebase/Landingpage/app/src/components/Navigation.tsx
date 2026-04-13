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

  const handleClick = (section: string) => {
    if (onNavigate) {
      onNavigate(section);
    }
  };

  return (
    <nav
      aria-label="Main navigation"
      className={`fixed top-0 left-0 right-0 z-[100] transition-all duration-500 ${
        isScrolled
          ? 'bg-[#F4EFE6]/92 backdrop-blur-md py-4 border-b border-[#C8A14A]/20'
          : 'bg-transparent py-6'
      }`}
    >
      <div className="max-w-7xl mx-auto px-6 md:px-8 flex items-center justify-between">
        {/* Logo */}
        <button
          onClick={() => handleClick('hero')}
          aria-label="Go to top"
          className="flex items-center gap-2 group"
        >
          <Sparkles className="w-5 h-5 text-[#C8A14A] group-hover:scale-110 transition-transform" />
          <span className="text-xl font-medium text-[#14181F] tracking-tight">
            Bazodiac
          </span>
        </button>

        {/* Nav Links */}
        <div className="hidden md:flex items-center gap-8">
          <button
            onClick={() => handleClick('readings')}
            className="text-sm text-[#6D6A61] hover:text-[#14181F] transition-colors"
            aria-label="Go to readings"
          >
            Readings
          </button>
          <button
            onClick={() => handleClick('method')}
            className="text-sm text-[#6D6A61] hover:text-[#14181F] transition-colors"
            aria-label="Go to method"
          >
            Method
          </button>
          <button
            onClick={() => handleClick('about')}
            className="text-sm text-[#6D6A61] hover:text-[#14181F] transition-colors"
            aria-label="Go to about"
          >
            About
          </button>
        </div>
      </div>
    </nav>
  );
};
