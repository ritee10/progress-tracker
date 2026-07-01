// ============================================================
// Types — Skill
// ============================================================

export type SkillStatus = 'not_started' | 'in_progress' | 'completed' | 'overdue';
export type SkillDifficulty = 'beginner' | 'intermediate' | 'advanced' | 'expert';
export type SkillPriority = 'low' | 'medium' | 'high' | 'critical';
export type SortOption = 'alphabetical' | 'progress' | 'lastActivity' | 'streak';
export type FilterOption = 'all' | 'in_progress' | 'completed' | 'overdue' | 'not_started';

export interface Skill {
  id: string;
  title: string;
  description?: string;
  icon?: string;
  color?: string;
  category?: string;
  difficulty: SkillDifficulty;
  priority: SkillPriority;
  status: SkillStatus;

  totalTopics: number;
  completedTopics: number;
  progress: number; // 0–100

  currentStreak: number;
  longestStreak: number;
  notesCount: number;

  lastActivityDate?: string;
  deadline?: string;
  isPinned: boolean;

  createdAt: string;
  updatedAt: string;
}

export interface SkillStats {
  skillId: string;
  totalTopics: number;
  completedTopics: number;
  pendingTopics: number;
  notesCount: number;
  studyDays: number;
  currentStreak: number;
  longestStreak: number;
  completionPercentage: number;
}

export interface SkillFilters {
  query: string;
  filter: FilterOption;
  sort: SortOption;
}

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  total: number;
  page: number;
  limit: number;
}

// ============================================================
// Types — Tree UI
// ============================================================

export type TreeNodeType = 'skill' | 'topic' | 'subtopic' | 'item';
export type CheckState   = 'unchecked' | 'checked' | 'indeterminate';

export interface TreeNode {
  id: string;
  title: string;
  type: TreeNodeType;
  depth: number;
  progress: number;       // 0–100
  childrenCount: number;
  hasChildren: boolean;
  loaded: boolean;
  expanded: boolean;
  parentId?: string;
  checkState: CheckState;
}

export interface TreeRootResponse {
  nodes: TreeNode[];
}

export interface TreeChildrenResponse {
  parentId: string;
  nodes: TreeNode[];
}
