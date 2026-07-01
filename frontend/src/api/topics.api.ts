import { apiClient } from './axios';

export const topicsApi = {
  getTopics: async (skillId?: number | string) => {
    const params = skillId ? { skill_id: skillId } : {};
    const { data } = await apiClient.get('/api/topics', { params });
    return data;
  },

  getOverdueTopics: async () => {
    const { data } = await apiClient.get('/api/topics/overdue');
    return data;
  },

  createTopic: async (topicData: any) => {
    const { data } = await apiClient.post('/api/topics', topicData);
    return data;
  },

  updateTopic: async ({ id, ...topicData }: { id: number | string, [key: string]: any }) => {
    const { data } = await apiClient.put(`/api/topics/${id}`, topicData);
    return data;
  },

  deleteTopic: async (id: number | string) => {
    const { data } = await apiClient.delete(`/api/topics/${id}`);
    return data;
  }
};
