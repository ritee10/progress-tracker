import { apiClient } from './axios';

export const searchApi = {
  globalSearch: async (query: string) => {
    const { data } = await apiClient.get('/api/search', { params: { q: query } });
    return data;
  },

  topicSearch: async (query: string) => {
    const { data } = await apiClient.get('/api/search/topics', { params: { q: query } });
    return data;
  },

  skillSearch: async (query: string) => {
    const { data } = await apiClient.get('/api/search/skills', { params: { q: query } });
    return data;
  }
};
