import { useQuery } from '@tanstack/react-query';
import { streakApi } from '../api/streak.api';
import { QUERY_KEYS } from '../api/queryKeys';

export function useStreak() {
  const streakQuery = useQuery({
    queryKey: QUERY_KEYS.streak,
    queryFn: streakApi.getStreak,
  });

  const heatmapQuery = useQuery({
    queryKey: QUERY_KEYS.heatmap,
    queryFn: streakApi.getHeatmap,
  });

  const longestStreakQuery = useQuery({
    queryKey: QUERY_KEYS.longestStreak,
    queryFn: streakApi.getLongestStreak,
  });

  return {
    streak: streakQuery.data,
    heatmap: heatmapQuery.data,
    longestStreak: longestStreakQuery.data,
    isLoading: streakQuery.isLoading || heatmapQuery.isLoading || longestStreakQuery.isLoading,
  };
}
