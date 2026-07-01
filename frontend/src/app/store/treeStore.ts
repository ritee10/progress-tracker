// ============================================================
// Zustand Tree Store
// ============================================================

import { create } from 'zustand';
import { fetchTreeRoot, fetchTreeChildren } from '@/lib/treeApi';
import {
  flattenVisibleTree,
  computeCheckState,
  collectDescendants,
  collectAncestors,
} from '@/lib/treeUtils';
import type { TreeNode, CheckState } from '@/types/skill';

// ── State shape ───────────────────────────────────────────────

interface TreeState {
  // Data
  nodes: Record<string, TreeNode>;
  childrenMap: Record<string, string[]>;
  rootIds: string[];

  // UI state
  expandedIds: Set<string>;
  loadingIds: Set<string>;
  errorIds: Set<string>;

  // Root loading state
  rootLoading: boolean;
  rootError: string | null;

  // ── Derived (computed on demand) ──────────────────────────
  flatVisibleNodes: () => TreeNode[];

  // ── Actions ──────────────────────────────────────────────
  loadRoot: () => Promise<void>;
  loadChildren: (id: string) => Promise<void>;
  toggleExpand: (id: string) => Promise<void>;
  expandNode: (id: string) => void;
  collapseNode: (id: string) => void;
  toggleCheckbox: (id: string) => void;
  selectBranch: (id: string) => void;
  unselectBranch: (id: string) => void;
  retryLoadChildren: (id: string) => Promise<void>;
}

// ── Helper: rebuild checkState for a node from its children ──
function refreshCheckState(
  id: string,
  nodes: Record<string, TreeNode>,
  childrenMap: Record<string, string[]>,
): CheckState {
  const children = childrenMap[id] ?? [];
  if (children.length === 0) return nodes[id]?.checkState ?? 'unchecked';
  const childStates = children.map((cid) => nodes[cid]?.checkState ?? 'unchecked');
  return computeCheckState(childStates);
}

// ── Store ─────────────────────────────────────────────────────

export const useTreeStore = create<TreeState>()((set, get) => ({
  nodes: {},
  childrenMap: {},
  rootIds: [],
  expandedIds: new Set(),
  loadingIds: new Set(),
  errorIds: new Set(),
  rootLoading: false,
  rootError: null,

  // ── flatVisibleNodes (memoized via call) ──────────────────
  flatVisibleNodes: () => {
    const { rootIds, nodes, childrenMap, expandedIds } = get();
    return flattenVisibleTree(rootIds, nodes, childrenMap, expandedIds);
  },

  // ── Load root nodes ───────────────────────────────────────
  loadRoot: async () => {
    set({ rootLoading: true, rootError: null });
    try {
      const rootNodes = await fetchTreeRoot();
      const nodes: Record<string, TreeNode> = {};
      const rootIds: string[] = [];
      for (const node of rootNodes) {
        nodes[node.id] = node;
        rootIds.push(node.id);
      }
      set({ nodes, rootIds, rootLoading: false });
    } catch {
      set({ rootLoading: false, rootError: 'Failed to load skills tree.' });
    }
  },

  // ── Lazy load children ────────────────────────────────────
  loadChildren: async (id: string) => {
    const { nodes, loadingIds, errorIds } = get();
    const node = nodes[id];
    if (!node || node.loaded) return;

    // Mark loading
    const newLoading = new Set(loadingIds);
    newLoading.add(id);
    const newErrors = new Set(errorIds);
    newErrors.delete(id);
    set({ loadingIds: newLoading, errorIds: newErrors });

    try {
      const children = await fetchTreeChildren(id);
      const newNodes = { ...get().nodes };
      const newChildrenMap = { ...get().childrenMap };
      const childIds: string[] = [];

      for (const child of children) {
        newNodes[child.id] = child;
        childIds.push(child.id);
      }

      // Mark parent as loaded
      newNodes[id] = { ...newNodes[id], loaded: true, expanded: true };
      newChildrenMap[id] = childIds;

      const doneLoading = new Set(get().loadingIds);
      doneLoading.delete(id);

      set({ nodes: newNodes, childrenMap: newChildrenMap, loadingIds: doneLoading });
    } catch {
      const doneLoading = new Set(get().loadingIds);
      doneLoading.delete(id);
      const withError = new Set(get().errorIds);
      withError.add(id);
      set({ loadingIds: doneLoading, errorIds: withError });
    }
  },

  // ── Toggle expand (lazy-loads if needed) ─────────────────
  toggleExpand: async (id: string) => {
    const { nodes, expandedIds, loadChildren, expandNode, collapseNode } = get();
    const node = nodes[id];
    if (!node || !node.hasChildren) return;

    if (expandedIds.has(id)) {
      collapseNode(id);
    } else {
      if (!node.loaded) {
        // Expand optimistically, load in background
        expandNode(id);
        await loadChildren(id);
      } else {
        expandNode(id);
      }
    }
  },

  expandNode: (id: string) => {
    const newExpanded = new Set(get().expandedIds);
    newExpanded.add(id);
    set((state) => ({
      expandedIds: newExpanded,
      nodes: { ...state.nodes, [id]: { ...state.nodes[id], expanded: true } },
    }));
  },

  collapseNode: (id: string) => {
    const newExpanded = new Set(get().expandedIds);
    newExpanded.delete(id);
    set((state) => ({
      expandedIds: newExpanded,
      nodes: { ...state.nodes, [id]: { ...state.nodes[id], expanded: false } },
    }));
  },

  // ── Toggle checkbox with tri-state propagation ────────────
  toggleCheckbox: (id: string) => {
    const { nodes, childrenMap } = get();
    const node = nodes[id];
    if (!node) return;

    // Cycle: unchecked → checked, indeterminate → checked, checked → unchecked
    const nextState: CheckState =
      node.checkState === 'checked' ? 'unchecked' : 'checked';

    const newNodes = { ...nodes };

    // Set this node
    newNodes[id] = { ...newNodes[id], checkState: nextState };

    // Propagate DOWN to all loaded descendants
    const descendants = collectDescendants(id, childrenMap);
    for (const dId of descendants) {
      if (newNodes[dId]) {
        newNodes[dId] = { ...newNodes[dId], checkState: nextState };
      }
    }

    // Propagate UP to all ancestors
    const ancestors = collectAncestors(id, newNodes);
    for (const aId of ancestors) {
      if (newNodes[aId]) {
        newNodes[aId] = {
          ...newNodes[aId],
          checkState: refreshCheckState(aId, newNodes, childrenMap),
        };
      }
    }

    set({ nodes: newNodes });
  },

  selectBranch: (id: string) => {
    const { nodes, childrenMap } = get();
    const newNodes = { ...nodes };
    newNodes[id] = { ...newNodes[id], checkState: 'checked' };
    const descendants = collectDescendants(id, childrenMap);
    for (const dId of descendants) {
      if (newNodes[dId]) newNodes[dId] = { ...newNodes[dId], checkState: 'checked' };
    }
    const ancestors = collectAncestors(id, newNodes);
    for (const aId of ancestors) {
      if (newNodes[aId]) {
        newNodes[aId] = { ...newNodes[aId], checkState: refreshCheckState(aId, newNodes, childrenMap) };
      }
    }
    set({ nodes: newNodes });
  },

  unselectBranch: (id: string) => {
    const { nodes, childrenMap } = get();
    const newNodes = { ...nodes };
    newNodes[id] = { ...newNodes[id], checkState: 'unchecked' };
    const descendants = collectDescendants(id, childrenMap);
    for (const dId of descendants) {
      if (newNodes[dId]) newNodes[dId] = { ...newNodes[dId], checkState: 'unchecked' };
    }
    const ancestors = collectAncestors(id, newNodes);
    for (const aId of ancestors) {
      if (newNodes[aId]) {
        newNodes[aId] = { ...newNodes[aId], checkState: refreshCheckState(aId, newNodes, childrenMap) };
      }
    }
    set({ nodes: newNodes });
  },

  retryLoadChildren: async (id: string) => {
    // Clear error flag and re-attempt
    set((state) => {
      const newErrors = new Set(state.errorIds);
      newErrors.delete(id);
      const newNodes = { ...state.nodes };
      if (newNodes[id]) newNodes[id] = { ...newNodes[id], loaded: false };
      return { errorIds: newErrors, nodes: newNodes };
    });
    await get().loadChildren(id);
  },
}));
