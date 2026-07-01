import { RouterProvider } from 'react-router-dom';
import { ErrorBoundary } from 'react-error-boundary';
import { Toaster } from 'sonner';
import { ThemeProvider } from './app/providers/ThemeProvider';
import { QueryProvider } from './providers/QueryProvider';
import { router } from './app/router';
import { OfflineBanner } from './components/ui/api-status/OfflineBanner';
import { ErrorBanner } from './components/ui/api-status/ErrorBanner';

function App() {
  return (
    <ErrorBoundary 
      FallbackComponent={({ error, resetErrorBoundary }) => (
        <div className="flex min-h-screen items-center justify-center p-4">
          <ErrorBanner 
            title="Application Error" 
            message={(error as Error).message || 'A critical error occurred that crashed the application.'} 
            onRetry={resetErrorBoundary} 
          />
        </div>
      )}
    >
      <QueryProvider>
        <ThemeProvider>
          <OfflineBanner />
          <RouterProvider router={router} />
          <Toaster position="top-right" />
        </ThemeProvider>
      </QueryProvider>
    </ErrorBoundary>
  );
}

export default App;
