// ============================================================
// Tree Utilities
// ============================================================

import type { TreeNode, CheckState } from '@/types/skill';

// ── Flatten visible nodes for the virtualizer ────────────────
/**
 * Depth-first walk: only expands branches that are in expandedIds.
 * Returns a flat array of nodes in display order.
 */
export function flattenVisibleTree(
  rootIds: string[],
  nodes: Record<string, TreeNode>,
  childrenMap: Record<string, string[]>,
  expandedIds: Set<string>,
): TreeNode[] {
  const result: TreeNode[] = [];

  function visit(id: string) {
    const node = nodes[id];
    if (!node) return;
    result.push(node);

    if (node.hasChildren && expandedIds.has(id)) {
      const children = childrenMap[id] ?? [];
      for (const childId of children) {
        visit(childId);
      }
    }
  }

  for (const id of rootIds) {
    visit(id);
  }

  return result;
}

// ── Compute tri-state from children ──────────────────────────
/**
 * Given an array of child check states, derive the parent check state.
 */
export function computeCheckState(childStates: CheckState[]): CheckState {
  if (childStates.length === 0) return 'unchecked';
  const allChecked = childStates.every((s) => s === 'checked');
  const noneChecked = childStates.every((s) => s === 'unchecked');
  if (allChecked) return 'checked';
  if (noneChecked) return 'unchecked';
  return 'indeterminate';
}

// ── Collect all descendant ids ─────────────────────────────
/**
 * Returns all descendant ids (not including the node itself).
 */
export function collectDescendants(
  id: string,
  childrenMap: Record<string, string[]>,
): string[] {
  const result: string[] = [];
  const stack = [...(childrenMap[id] ?? [])];
  while (stack.length > 0) {
    const current = stack.pop()!;
    result.push(current);
    stack.push(...(childrenMap[current] ?? []));
  }
  return result;
}

// ── Get all ancestor ids ──────────────────────────────────
/**
 * Returns ids of all ancestors (parent chain) for a given node.
 */
export function collectAncestors(
  id: string,
  nodes: Record<string, TreeNode>,
): string[] {
  const ancestors: string[] = [];
  let currentId: string | undefined = nodes[id]?.parentId;
  while (currentId) {
    ancestors.push(currentId);
    currentId = nodes[currentId]?.parentId;
  }
  return ancestors;
}

// ── Icon mapping ─────────────────────────────────────────────
export const TREE_NODE_INDENT = 24; // px per depth level

export function getNodeIndent(depth: number): number {
  return depth * TREE_NODE_INDENT;
}

// ── Progress color ────────────────────────────────────────────
export function getProgressColor(progress: number): string {
  if (progress === 100) return 'text-emerald-500';
  if (progress >= 70)  return 'text-blue-500';
  if (progress >= 40)  return 'text-amber-500';
  return 'text-rose-500';
}

export function getProgressBarColor(progress: number): string {
  if (progress === 100) return 'bg-emerald-500';
  if (progress >= 70)  return 'bg-blue-500';
  if (progress >= 40)  return 'bg-amber-500';
  return 'bg-rose-500';
}
