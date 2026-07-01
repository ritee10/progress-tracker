import { useRef, useMemo, useCallback } from 'react';
import { useVirtualizer } from '@tanstack/react-virtual';
import { useTreeStore } from '@/app/store/treeStore';
import { TreeNodeRow } from './TreeNode';
import { TreeLoadingRow } from './TreeLoading';

interface VirtualizedTreeProps {
  focusedId: string | null;
  setFocusedId: (id: string | null) => void;
}

export function VirtualizedTree({ focusedId, setFocusedId }: VirtualizedTreeProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  const flatNodes = useTreeStore((state) => state.flatVisibleNodes());
  const loadingIds = useTreeStore((state) => state.loadingIds);
  const errorIds = useTreeStore((state) => state.errorIds);
  const toggleExpand = useTreeStore((state) => state.toggleExpand);
  const toggleCheckbox = useTreeStore((state) => state.toggleCheckbox);
  const retryLoadChildren = useTreeStore((state) => state.retryLoadChildren);

  // Determine row count. We need an extra row for every node that is currently loading
  // to show the loading skeleton.
  const loadingNodesMap = useMemo(() => {
    const map = new Map<string, number>();
    for (const loadingId of loadingIds) {
      // Find where this id is in the flat list, we inject a loading row right after it.
      const index = flatNodes.findIndex((n) => n.id === loadingId);
      if (index !== -1) {
        map.set(loadingId, index);
      }
    }
    return map;
  }, [flatNodes, loadingIds]);

  // Create a combined list of regular nodes and synthetic loading items
  const virtualItems = useMemo(() => {
    const items: Array<{ type: 'node' | 'loading'; id: string; node?: any; depth: number }> = [];
    
    for (const node of flatNodes) {
      items.push({ type: 'node', id: node.id, node, depth: node.depth });
      if (loadingNodesMap.has(node.id)) {
        items.push({ type: 'loading', id: `loading-${node.id}`, depth: node.depth + 1 });
      }
    }
    return items;
  }, [flatNodes, loadingNodesMap]);

  const rowVirtualizer = useVirtualizer({
    count: virtualItems.length,
    getScrollElement: () => containerRef.current,
    estimateSize: () => 44, // Fixed row height 44px
    overscan: 5,
  });

  const handleToggleExpand = useCallback((id: string) => (e: React.MouseEvent) => {
    e.stopPropagation();
    toggleExpand(id);
  }, [toggleExpand]);

  const handleToggleCheck = useCallback((id: string) => (e: React.MouseEvent) => {
    e.stopPropagation();
    toggleCheckbox(id);
  }, [toggleCheckbox]);

  return (
    <div
      ref={containerRef}
      className="h-[360px] sm:h-[480px] lg:h-[600px] w-full overflow-auto rounded-md border bg-card"
    >
      <div
        className="w-full relative"
        style={{ height: `${rowVirtualizer.getTotalSize()}px` }}
      >
        {rowVirtualizer.getVirtualItems().map((virtualRow) => {
          const item = virtualItems[virtualRow.index];

          return (
            <div
              key={item.id}
              className="absolute top-0 left-0 w-full"
              style={{
                height: `${virtualRow.size}px`,
                transform: `translateY(${virtualRow.start}px)`,
              }}
            >
              {item.type === 'node' ? (
                <TreeNodeRow
                  node={item.node}
                  isFocused={focusedId === item.id}
                  onFocus={() => setFocusedId(item.id)}
                  onToggleExpand={handleToggleExpand(item.id)}
                  onToggleCheck={handleToggleCheck(item.id)}
                  isError={errorIds.has(item.id)}
                  onRetry={() => retryLoadChildren(item.id)}
                />
              ) : (
                <TreeLoadingRow depth={item.depth} />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
