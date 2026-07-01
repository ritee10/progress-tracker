import { useBreakpoint } from './useBreakpoint';

export function useMobile(): boolean {
  // If not >= md, it's mobile
  const isMd = useBreakpoint('md');
  return !isMd;
}
