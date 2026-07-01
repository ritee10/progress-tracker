import { apiClient } from './axios';

export const progressApi = {
  getProgress: async () => {
    const { data } = await apiClient.get('/api/progress');
    return data;
  },

  getDashboardStats: async () => {
    const { data } = await apiClient.get('/api/dashboard/stats');
    return data;
  },

  toggleCheckbox: async (topicId: number | string, completed: boolean) => {
    const { data } = await apiClient.post(`/api/topics/${topicId}/progress`, { completed });
    return data;
  },
  
  getRecentActivity: async () => {
    const { data } = await apiClient.get('/api/activity/recent');
    return data;
  }
};
