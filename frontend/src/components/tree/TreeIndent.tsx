import { memo } from 'react';

interface TreeIndentProps {
  depth: number;
}

export const TreeIndent = memo(function TreeIndent({ depth }: TreeIndentProps) {
  if (depth === 0) return null;

  // We draw vertical lines for each level of depth to guide the eye.
  // The spacing matches TREE_NODE_INDENT (24px)
  return (
    <div className="flex h-full shrink-0">
      {Array.from({ length: depth }).map((_, i) => (
        <div
          key={i}
          className="h-full w-6 border-l border-border opacity-50 relative ml-3"
          aria-hidden="true"
        />
      ))}
    </div>
  );
});
