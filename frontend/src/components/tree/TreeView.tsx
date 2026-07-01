import { useEffect, useState, useCallback, useRef } from 'react';
import { useTreeStore } from '@/app/store/treeStore';
import { VirtualizedTree } from './VirtualizedTree';
import { Loader2, FolderTree } from 'lucide-react';

interface TreeViewProps {
  skillId?: string; // If provided, load only this skill's tree; else load all.
}

export function TreeView({ skillId }: TreeViewProps) {
  const loadRoot = useTreeStore((state) => state.loadRoot);
  const rootLoading = useTreeStore((state) => state.rootLoading);
  const rootError = useTreeStore((state) => state.rootError);
  const flatNodes = useTreeStore((state) => state.flatVisibleNodes());
  const toggleExpand = useTreeStore((state) => state.toggleExpand);
  const toggleCheckbox = useTreeStore((state) => state.toggleCheckbox);
  const collapseNode = useTreeStore((state) => state.collapseNode);

  const [focusedId, setFocusedId] = useState<string | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Initial load
  useEffect(() => {
    // In future: loadRoot(skillId) to fetch skill-specific tree
    console.log("Loading tree for skill:", skillId);
    loadRoot();
  }, [loadRoot, skillId]);

  // Set initial focus
  useEffect(() => {
    if (flatNodes.length > 0 && !focusedId) {
      setFocusedId(flatNodes[0].id);
    }
  }, [flatNodes, focusedId]);

  // ── Keyboard Navigation ──────────────────────────────────────
  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (!focusedId || flatNodes.length === 0) return;

      const currentIndex = flatNodes.findIndex((n) => n.id === focusedId);
      if (currentIndex === -1) return;

      const node = flatNodes[currentIndex];

      switch (e.key) {
        case 'ArrowDown': {
          e.preventDefault();
          if (currentIndex < flatNodes.length - 1) {
            setFocusedId(flatNodes[currentIndex + 1].id);
          }
          break;
        }
        case 'ArrowUp': {
          e.preventDefault();
          if (currentIndex > 0) {
            setFocusedId(flatNodes[currentIndex - 1].id);
          }
          break;
        }
        case 'ArrowRight': {
          e.preventDefault();
          if (node.hasChildren) {
            if (!node.expanded) {
              toggleExpand(node.id);
            } else if (currentIndex < flatNodes.length - 1) {
              // If already expanded, jump to first child
              setFocusedId(flatNodes[currentIndex + 1].id);
            }
          }
          break;
        }
        case 'ArrowLeft': {
          e.preventDefault();
          if (node.hasChildren && node.expanded) {
            collapseNode(node.id);
          } else if (node.parentId) {
            // Jump to parent
            setFocusedId(node.parentId);
          }
          break;
        }
        case ' ': // Space
          e.preventDefault();
          toggleCheckbox(node.id);
          break;
        case 'Enter':
          e.preventDefault();
          if (node.hasChildren) {
            toggleExpand(node.id);
          }
          break;
        case 'Home':
          e.preventDefault();
          setFocusedId(flatNodes[0].id);
          break;
        case 'End':
          e.preventDefault();
          setFocusedId(flatNodes[flatNodes.length - 1].id);
          break;
      }
    },
    [focusedId, flatNodes, toggleExpand, collapseNode, toggleCheckbox]
  );

  // ── Render States ───────────────────────────────────────────

  if (rootLoading) {
    return (
      <div className="flex h-[400px] flex-col items-center justify-center rounded-md border bg-card text-muted-foreground">
        <Loader2 className="h-8 w-8 animate-spin mb-4" />
        <p>Loading skills tree...</p>
      </div>
    );
  }

  if (rootError) {
    return (
      <div className="flex h-[400px] flex-col items-center justify-center rounded-md border bg-card text-destructive gap-3">
        <p className="font-semibold">Failed to load tree</p>
        <button
          onClick={loadRoot}
          className="rounded bg-destructive px-4 py-2 text-sm font-medium text-destructive-foreground hover:bg-destructive/90"
        >
          Retry
        </button>
      </div>
    );
  }

  if (flatNodes.length === 0) {
    return (
      <div className="flex h-[400px] flex-col items-center justify-center rounded-md border bg-card text-muted-foreground gap-3">
        <FolderTree className="h-12 w-12 opacity-50" />
        <p>No skills available.</p>
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      role="tree"
      aria-label="Skills Navigation Tree"
      tabIndex={0}
      onKeyDown={handleKeyDown}
      className="outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 rounded-md"
    >
      <VirtualizedTree focusedId={focusedId} setFocusedId={setFocusedId} />
    </div>
  );
}
