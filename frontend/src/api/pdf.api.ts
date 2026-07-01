import { apiClient } from './axios';

export const pdfApi = {
  uploadPdf: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const { data } = await apiClient.post('/api/pdf/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return data;
  },

  extractHierarchy: async (pdfId: string) => {
    const { data } = await apiClient.post(`/api/pdf/${pdfId}/extract`);
    return data;
  },

  saveHierarchy: async (hierarchyData: any) => {
    const { data } = await apiClient.post('/api/pdf/hierarchy/save', hierarchyData);
    return data;
  }
};
