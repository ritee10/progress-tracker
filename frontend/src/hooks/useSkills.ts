import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { skillsApi } from '../api/skills.api';
import { QUERY_KEYS } from '../api/queryKeys';
import { handleApiError } from '../utils/errorHandler';
import { toast } from 'sonner';

export function useSkills() {
  const queryClient = useQueryClient();

  const skillsQuery = useQuery({
    queryKey: QUERY_KEYS.skills,
    queryFn: skillsApi.getSkills,
  });

  const createSkillMutation = useMutation<any, Error, any>({
    mutationFn: skillsApi.createSkill,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.skills });
      toast.success('Skill created successfully');
    },
    onError: (err) => handleApiError(err),
  });

  const updateSkillMutation = useMutation<any, Error, { id: number | string, [key: string]: any }>({
    mutationFn: skillsApi.updateSkill,
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.skills });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.skill(variables.id) });
      toast.success('Skill updated successfully');
    },
    onError: (err) => handleApiError(err),
  });

  const deleteSkillMutation = useMutation<any, Error, number | string>({
    mutationFn: skillsApi.deleteSkill,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.skills });
      toast.success('Skill deleted successfully');
    },
    onError: (err) => handleApiError(err),
  });

  return {
    skills: skillsQuery.data,
    isLoading: skillsQuery.isLoading,
    error: skillsQuery.error,
    createSkill: createSkillMutation.mutateAsync,
    updateSkill: updateSkillMutation.mutateAsync,
    deleteSkill: deleteSkillMutation.mutateAsync,
    isCreating: createSkillMutation.isPending,
    isUpdating: updateSkillMutation.isPending,
    isDeleting: deleteSkillMutation.isPending,
  };
}

export function useSkill(id: string | number) {
  return useQuery({
    queryKey: QUERY_KEYS.skill(id),
    queryFn: () => skillsApi.getSkill(id),
    enabled: !!id,
  });
}
