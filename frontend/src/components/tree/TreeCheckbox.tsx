import { memo } from 'react';
import { Check, Minus } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { CheckState } from '@/types/skill';

interface TreeCheckboxProps {
  state: CheckState;
  onClick: (e: React.MouseEvent) => void;
  disabled?: boolean;
}

export const TreeCheckbox = memo(function TreeCheckbox({
  state,
  onClick,
  disabled = false,
}: TreeCheckboxProps) {
  const isChecked = state === 'checked';
  const isIndeterminate = state === 'indeterminate';

  return (
    <button
      type="button"
      role="checkbox"
      aria-checked={isIndeterminate ? 'mixed' : isChecked}
      onClick={onClick}
      disabled={disabled}
      tabIndex={-1} // Focus is managed by the row, not individual elements
      className={cn(
        "peer h-4 w-4 shrink-0 rounded-sm border border-primary ring-offset-background transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 ml-1 mr-2",
        (isChecked || isIndeterminate) && "bg-primary text-primary-foreground",
        state === 'unchecked' && "bg-transparent text-transparent",
      )}
    >
      {isChecked && <Check className="h-3.5 w-3.5 stroke-[3]" />}
      {isIndeterminate && <Minus className="h-3.5 w-3.5 stroke-[3]" />}
    </button>
  );
});
