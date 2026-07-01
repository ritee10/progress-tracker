import { useMutation, useQueryClient } from '@tanstack/react-query';
import { pdfApi } from '../api/pdf.api';
import { handleApiError } from '../utils/errorHandler';
import { toast } from 'sonner';
import { QUERY_KEYS } from '../api/queryKeys';

export function usePdf() {
  const queryClient = useQueryClient();

  const uploadPdfMutation = useMutation<any, Error, File>({
    mutationFn: pdfApi.uploadPdf,
    onSuccess: () => {
      toast.success('PDF uploaded successfully');
    },
    onError: (err) => handleApiError(err),
  });

  const extractHierarchyMutation = useMutation<any, Error, string>({
    mutationFn: pdfApi.extractHierarchy,
    onSuccess: () => {
      toast.success('Hierarchy extracted successfully');
    },
    onError: (err) => handleApiError(err),
  });

  const saveHierarchyMutation = useMutation<any, Error, any>({
    mutationFn: pdfApi.saveHierarchy,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.skills });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.topics });
      toast.success('Hierarchy saved successfully');
    },
    onError: (err) => handleApiError(err),
  });

  return {
    uploadPdf: uploadPdfMutation.mutateAsync,
    extractHierarchy: extractHierarchyMutation.mutateAsync,
    saveHierarchy: saveHierarchyMutation.mutateAsync,
    isUploading: uploadPdfMutation.isPending,
    isExtracting: extractHierarchyMutation.isPending,
    isSaving: saveHierarchyMutation.isPending,
  };
}
