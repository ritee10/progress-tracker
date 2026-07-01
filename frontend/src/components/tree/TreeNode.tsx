import { memo } from 'react';
import { BookOpen, Folder, FolderTree, FileText, AlertCircle } from 'lucide-react';
import { cn } from '@/lib/utils';
import { TreeIndent } from './TreeIndent';
import { TreeExpandButton } from './TreeExpandButton';
import { TreeCheckbox } from './TreeCheckbox';
import { getProgressColor } from '@/lib/treeUtils';
import type { TreeNode } from '@/types/skill';

interface TreeNodeRowProps {
  node: TreeNode;
  isFocused: boolean;
  onToggleExpand: (e: React.MouseEvent) => void;
  onToggleCheck: (e: React.MouseEvent) => void;
  onFocus: () => void;
  isError?: boolean;
  onRetry?: () => void;
}

const TYPE_ICONS = {
  skill: BookOpen,
  topic: Folder,
  subtopic: FolderTree,
  item: FileText,
};

export const TreeNodeRow = memo(function TreeNodeRow({
  node,
  isFocused,
  onToggleExpand,
  onToggleCheck,
  onFocus,
  isError,
  onRetry,
}: TreeNodeRowProps) {
  const Icon = TYPE_ICONS[node.type] || FileText;

  // Handle click on the entire row
  const handleRowClick = (e: React.MouseEvent) => {
    onFocus();
    // Only expand if clicking the row background itself, not its buttons
    if (e.target === e.currentTarget) {
      if (node.hasChildren) {
        onToggleExpand(e);
      } else {
        onToggleCheck(e);
      }
    }
  };

  return (
    <div
      role="treeitem"
      aria-expanded={node.hasChildren ? node.expanded : undefined}
      aria-selected={isFocused}
      aria-checked={node.checkState === 'indeterminate' ? 'mixed' : node.checkState === 'checked'}
      aria-level={node.depth + 1}
      onClick={handleRowClick}
      className={cn(
        "flex h-[44px] items-center w-full px-2 py-1.5 transition-colors cursor-default rounded-md group select-none",
        isFocused ? "bg-accent text-accent-foreground" : "hover:bg-muted/50",
      )}
    >
      <TreeIndent depth={node.depth} />

      <div className="flex items-center flex-1 min-w-0">
        <TreeExpandButton
          expanded={node.expanded}
          hasChildren={node.hasChildren}
          onClick={onToggleExpand}
        />

        <TreeCheckbox
          state={node.checkState}
          onClick={onToggleCheck}
        />

        <Icon className={cn(
          "h-4 w-4 shrink-0 mr-2.5",
          node.type === 'skill' && "text-primary",
          node.type === 'topic' && "text-blue-500",
          node.type === 'subtopic' && "text-indigo-500",
          node.type === 'item' && "text-emerald-500"
        )} />

        <span className="text-sm font-medium truncate flex-1 pr-4">
          {node.title}
        </span>
      </div>

      <div className="flex items-center shrink-0 space-x-2 sm:space-x-3 text-xs pr-2">
        {isError && (
          <button
            onClick={onRetry}
            className="flex items-center text-destructive hover:underline font-medium"
          >
            <AlertCircle className="w-3.5 h-3.5 mr-1" />
            Retry
          </button>
        )}

        {!isError && (
          <>
            <div className={cn("font-medium min-w-[36px] text-right", getProgressColor(node.progress))}>
              {node.progress}%
            </div>

            <div className="text-muted-foreground min-w-[56px] text-right hidden sm:block">
              {node.hasChildren ? (
                <span>{node.childrenCount} items</span>
              ) : (
                <span>—</span>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
});
