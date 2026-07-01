import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { progressApi } from '../api/progress.api';
import { QUERY_KEYS } from '../api/queryKeys';
import { handleApiError } from '../utils/errorHandler';

export function useProgress() {
  const queryClient = useQueryClient();

  const progressQuery = useQuery({
    queryKey: QUERY_KEYS.progress,
    queryFn: progressApi.getProgress,
  });

  const dashboardStatsQuery = useQuery({
    queryKey: QUERY_KEYS.dashboard,
    queryFn: progressApi.getDashboardStats,
  });
  
  const recentActivityQuery = useQuery({
    queryKey: QUERY_KEYS.recentActivity,
    queryFn: progressApi.getRecentActivity,
  });

  const toggleCheckboxMutation = useMutation({
    mutationFn: ({ topicId, completed }: { topicId: number | string, completed: boolean }) => 
      progressApi.toggleCheckbox(topicId, completed),
    // Optimistic Update
    onMutate: async () => {
      // Cancel any outgoing refetches so they don't overwrite our optimistic update
      await queryClient.cancelQueries({ queryKey: QUERY_KEYS.topics });

      // Snapshot the previous value
      const previousTopics = queryClient.getQueryData(QUERY_KEYS.topics);

      // Optimistically update to the new value (this logic depends on how your topics list is structured)
      // For now, we'll just invalidate to keep it simple if we don't know the exact structure,
      // but in a real optimistic update we would deeply modify the cached data array.
      
      return { previousTopics };
    },
    onSuccess: () => {
      // Refresh dashboard stats and streak when progress changes
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.dashboard });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.streak });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.recentActivity });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.topics });
    },
    onError: (err, _vars, context) => {
      // Rollback
      if (context?.previousTopics) {
        queryClient.setQueryData(QUERY_KEYS.topics, context.previousTopics);
      }
      handleApiError(err);
    },
    onSettled: () => {
      // Sync with server once mutation is settled
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.topics });
    },
  });

  return {
    progress: progressQuery.data,
    isProgressLoading: progressQuery.isLoading,
    
    dashboardStats: dashboardStatsQuery.data,
    isDashboardStatsLoading: dashboardStatsQuery.isLoading,
    
    recentActivity: recentActivityQuery.data,
    isRecentActivityLoading: recentActivityQuery.isLoading,

    toggleCheckbox: toggleCheckboxMutation.mutate,
    isToggling: toggleCheckboxMutation.isPending,
  };
}
