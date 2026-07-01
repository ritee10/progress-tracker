import { QueryClient, QueryClientProvider, QueryCache } from '@tanstack/react-query';
import type { ReactNode } from 'react';
import { useState } from 'react';
import { useAuthStore } from '../app/store/authStore';
import { AxiosError } from 'axios';

interface QueryProviderProps {
  children: ReactNode;
}

export function QueryProvider({ children }: QueryProviderProps) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        queryCache: new QueryCache({
          onError: (error) => {
            // Global 401 handler: any query returning 401 clears auth and redirects
            if (error instanceof AxiosError && error.response?.status === 401) {
              useAuthStore.getState().logout();
              if (window.location.pathname !== '/login') {
                window.location.href = '/login';
              }
            }
          },
        }),
        defaultOptions: {
          queries: {
            retry: (failureCount, error) => {
              // Never retry on 401/403/404 — these are definitive server responses
              if (error instanceof AxiosError) {
                const status = error.response?.status;
                if (status === 401 || status === 403 || status === 404) return false;
              }
              return failureCount < 2;
            },
            staleTime: 5 * 60 * 1000, // 5 minutes
            refetchOnWindowFocus: false,
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
}
