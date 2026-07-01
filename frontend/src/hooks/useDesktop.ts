import { useBreakpoint } from './useBreakpoint';

export function useDesktop(): boolean {
  // >= lg
  return useBreakpoint('lg');
}
