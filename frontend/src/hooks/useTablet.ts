import { useBreakpoint } from './useBreakpoint';

export function useTablet(): boolean {
  // >= md and < lg
  const isMd = useBreakpoint('md');
  const isLg = useBreakpoint('lg');
  return isMd && !isLg;
}
