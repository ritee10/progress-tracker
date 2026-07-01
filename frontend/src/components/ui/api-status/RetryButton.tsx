import { RefreshCcw } from 'lucide-react';
import { Button } from '../button';

interface RetryButtonProps {
  onClick: () => void;
  isRetrying?: boolean;
}

export function RetryButton({ onClick, isRetrying }: RetryButtonProps) {
  return (
    <Button 
      variant="outline" 
      size="sm" 
      onClick={onClick} 
      disabled={isRetrying}
      className="gap-2"
    >
      <RefreshCcw className={`h-4 w-4 ${isRetrying ? 'animate-spin' : ''}`} />
      Retry
    </Button>
  );
}
