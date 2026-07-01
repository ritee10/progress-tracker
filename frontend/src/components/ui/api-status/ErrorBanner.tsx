import { AlertCircle } from 'lucide-react';

interface ErrorBannerProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
}

export function ErrorBanner({ 
  title = 'Something went wrong', 
  message = 'An error occurred while fetching data.', 
  onRetry 
}: ErrorBannerProps) {
  return (
    <div className="mb-4 rounded-lg border border-destructive/50 text-destructive px-4 py-3 flex items-start gap-3 bg-destructive/10">
      <AlertCircle className="h-4 w-4 mt-0.5" />
      <div className="flex flex-col gap-1">
        <h5 className="font-medium leading-none tracking-tight">{title}</h5>
        <div className="text-sm opacity-90">
          {message}
          {onRetry && (
            <button 
              onClick={onRetry}
              className="mt-2 block text-sm font-medium underline underline-offset-4 hover:text-destructive/80"
            >
              Try again
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
