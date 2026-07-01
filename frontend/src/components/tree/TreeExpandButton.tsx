import { memo } from 'react';
import { ChevronRight } from 'lucide-react';
import { cn } from '@/lib/utils';

interface TreeExpandButtonProps {
  expanded: boolean;
  hasChildren: boolean;
  onClick: (e: React.MouseEvent) => void;
  disabled?: boolean;
}

export const TreeExpandButton = memo(function TreeExpandButton({
  expanded,
  hasChildren,
  onClick,
  disabled = false,
}: TreeExpandButtonProps) {
  if (!hasChildren) {
    // Occupy the same space (24x24) but show a dot or empty space for alignment
    return <div className="w-6 h-6 shrink-0 flex items-center justify-center" aria-hidden="true">
      <div className="w-1 h-1 rounded-full bg-muted-foreground/30" />
    </div>;
  }

  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      className={cn(
        "w-6 h-6 shrink-0 flex items-center justify-center rounded-md hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring transition-colors",
        disabled && "opacity-50 cursor-not-allowed"
      )}
      aria-label={expanded ? 'Collapse node' : 'Expand node'}
      tabIndex={-1} // Handled by tree-level keyboard nav
    >
      <ChevronRight
        className={cn(
          "h-4 w-4 text-muted-foreground transition-transform duration-200 ease-out",
          expanded && "rotate-90"
        )}
      />
    </button>
  );
});
