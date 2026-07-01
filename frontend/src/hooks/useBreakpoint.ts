import { useState, useEffect } from 'react';

const breakpoints = {
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
  '2xl': 1536,
};

type BreakpointKey = keyof typeof breakpoints;

export function useBreakpoint(breakpoint: BreakpointKey): boolean {
  const [isAbove, setIsAbove] = useState(false);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const mediaQuery = window.matchMedia(`(min-width: ${breakpoints[breakpoint]}px)`);
    
    const handleChange = (e: MediaQueryListEvent | MediaQueryList) => {
      setIsAbove(e.matches);
    };

    // Initial check
    handleChange(mediaQuery);

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, [breakpoint]);

  return isAbove;
}
