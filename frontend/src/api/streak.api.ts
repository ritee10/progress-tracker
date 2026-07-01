import { apiClient } from './axios';

export const streakApi = {
  getStreak: async () => {
    const { data } = await apiClient.get('/api/streak');
    return data;
  },

  getHeatmap: async () => {
    const { data } = await apiClient.get('/api/streak/heatmap');
    return data;
  },

  getLongestStreak: async () => {
    const { data } = await apiClient.get('/api/streak/longest');
    return data;
  }
};
