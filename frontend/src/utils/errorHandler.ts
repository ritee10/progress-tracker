import { toast } from 'sonner';
import { AxiosError } from 'axios';
import type { ErrorResponse } from '../types/responses';
import { useAuthStore } from '../app/store/authStore';

export function handleApiError(error: unknown, defaultMessage: string = 'An unexpected error occurred') {
  if (error instanceof AxiosError) {
    const status = error.response?.status;
    const data = error.response?.data as ErrorResponse;

    let message = defaultMessage;

    if (data?.detail) {
      if (typeof data.detail === 'string') {
        message = data.detail;
      } else if (Array.isArray(data.detail) && data.detail.length > 0) {
        message = data.detail[0].msg;
      }
    } else if (error.message) {
      message = error.message;
    }

    if (status === 401) {
      // Clear session and redirect to login
      useAuthStore.getState().logout();
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
      toast.error('Session expired. Please log in again.');
    } else if (status === 403) {
      toast.error('You do not have permission to perform this action.');
    } else if (status === 404) {
      toast.error('Resource not found.');
    } else if (status === 422) {
      toast.error(`Validation Error: ${message}`);
    } else if (status === 429) {
      toast.error('Too many requests. Please slow down and try again.');
    } else if (status && status >= 500) {
      toast.error('Server error. Please try again later.');
    } else {
      toast.error(message);
    }
  } else if (error instanceof Error) {
    toast.error(error.message);
  } else {
    toast.error(defaultMessage);
  }
}
