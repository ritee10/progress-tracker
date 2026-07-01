import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { topicsApi } from '../api/topics.api';
import { QUERY_KEYS } from '../api/queryKeys';
import { handleApiError } from '../utils/errorHandler';
import { toast } from 'sonner';

export function useTopics(skillId?: string | number) {
  const queryClient = useQueryClient();

  const topicsQuery = useQuery({
    queryKey: skillId ? [...QUERY_KEYS.topics, { skillId }] : QUERY_KEYS.topics,
    queryFn: () => topicsApi.getTopics(skillId),
  });

  const createTopicMutation = useMutation<any, Error, any>({
    mutationFn: topicsApi.createTopic,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.topics });
      toast.success('Topic created successfully');
    },
    onError: (err) => handleApiError(err),
  });

  const updateTopicMutation = useMutation<any, Error, { id: number | string, [key: string]: any }>({
    mutationFn: topicsApi.updateTopic,
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.topics });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.topic(variables.id) });
      toast.success('Topic updated successfully');
    },
    onError: (err) => handleApiError(err),
  });

  const deleteTopicMutation = useMutation<any, Error, number | string>({
    mutationFn: topicsApi.deleteTopic,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.topics });
      toast.success('Topic deleted successfully');
    },
    onError: (err) => handleApiError(err),
  });

  return {
    topics: topicsQuery.data,
    isLoading: topicsQuery.isLoading,
    error: topicsQuery.error,
    createTopic: createTopicMutation.mutateAsync,
    updateTopic: updateTopicMutation.mutateAsync,
    deleteTopic: deleteTopicMutation.mutateAsync,
    isCreating: createTopicMutation.isPending,
    isUpdating: updateTopicMutation.isPending,
    isDeleting: deleteTopicMutation.isPending,
  };
}

export function useOverdueTopics() {
  return useQuery({
    queryKey: QUERY_KEYS.overdueTopics,
    queryFn: topicsApi.getOverdueTopics,
  });
}
