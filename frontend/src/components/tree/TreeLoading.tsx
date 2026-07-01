import { memo } from 'react';
import { Loader2 } from 'lucide-react';
import { TreeIndent } from './TreeIndent';

interface TreeLoadingProps {
  depth: number;
}

export const TreeLoadingRow = memo(function TreeLoadingRow({ depth }: TreeLoadingProps) {
  return (
    <div className="flex h-[44px] items-center w-full px-2 py-1.5 transition-colors">
      <TreeIndent depth={depth} />
      <div className="flex items-center pl-1">
        <Loader2 className="h-4 w-4 animate-spin text-muted-foreground mr-3" />
        <span className="text-sm text-muted-foreground animate-pulse">Loading items...</span>
      </div>
    </div>
  );
});
