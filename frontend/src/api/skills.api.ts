import { apiClient } from './axios';

export const skillsApi = {
  getSkills: async () => {
    const { data } = await apiClient.get('/api/skills');
    return data;
  },
  
  getSkill: async (id: number | string) => {
    const { data } = await apiClient.get(`/api/skills/${id}`);
    return data;
  },

  createSkill: async (skillData: any) => {
    const { data } = await apiClient.post('/api/skills', skillData);
    return data;
  },

  updateSkill: async ({ id, ...skillData }: { id: number | string, [key: string]: any }) => {
    const { data } = await apiClient.put(`/api/skills/${id}`, skillData);
    return data;
  },

  deleteSkill: async (id: number | string) => {
    const { data } = await apiClient.delete(`/api/skills/${id}`);
    return data;
  }
};
