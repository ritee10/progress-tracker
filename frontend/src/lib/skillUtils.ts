// ============================================================
// Lib — Skill Utilities
// ============================================================

import type { Skill, SkillStatus } from '@/types/skill';

export function getProgressColor(progress: number): string {
  if (progress <= 25) return 'text-red-500';
  if (progress <= 50) return 'text-orange-500';
  if (progress <= 75) return 'text-blue-500';
  return 'text-green-500';
}

export function getProgressBarColor(progress: number): string {
  if (progress <= 25) return 'bg-red-500';
  if (progress <= 50) return 'bg-orange-500';
  if (progress <= 75) return 'bg-blue-500';
  return 'bg-green-500';
}

export function getProgressStrokeColor(progress: number): string {
  if (progress <= 25) return '#ef4444';
  if (progress <= 50) return '#f97316';
  if (progress <= 75) return '#3b82f6';
  return '#22c55e';
}

export function getStatusLabel(status: SkillStatus): string {
  const labels: Record<SkillStatus, string> = {
    not_started: 'Not Started',
    in_progress: 'In Progress',
    completed: 'Completed',
    overdue: 'Overdue',
  };
  return labels[status];
}

export function getStatusColors(status: SkillStatus): { bg: string; text: string; border: string } {
  const map: Record<SkillStatus, { bg: string; text: string; border: string }> = {
    not_started: { bg: 'bg-gray-100 dark:bg-gray-800', text: 'text-gray-600 dark:text-gray-400', border: 'border-gray-200 dark:border-gray-700' },
    in_progress: { bg: 'bg-blue-50 dark:bg-blue-950', text: 'text-blue-600 dark:text-blue-400', border: 'border-blue-200 dark:border-blue-800' },
    completed: { bg: 'bg-green-50 dark:bg-green-950', text: 'text-green-600 dark:text-green-400', border: 'border-green-200 dark:border-green-800' },
    overdue: { bg: 'bg-red-50 dark:bg-red-950', text: 'text-red-600 dark:text-red-400', border: 'border-red-200 dark:border-red-800' },
  };
  return map[status];
}

export function formatRelativeTime(dateString?: string): string {
  if (!dateString) return 'Never';
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHrs = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHrs / 24);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHrs < 24) return `${diffHrs}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  return date.toLocaleDateString();
}

export function sortSkills(skills: Skill[], sort: string): Skill[] {
  return [...skills].sort((a, b) => {
    switch (sort) {
      case 'alphabetical': return a.title.localeCompare(b.title);
      case 'progress': return b.progress - a.progress;
      case 'streak': return b.currentStreak - a.currentStreak;
      case 'lastActivity': {
        const dateA = a.lastActivityDate ? new Date(a.lastActivityDate).getTime() : 0;
        const dateB = b.lastActivityDate ? new Date(b.lastActivityDate).getTime() : 0;
        return dateB - dateA;
      }
      default: return 0;
    }
  });
}

export function filterSkills(skills: Skill[], filter: string, query: string): Skill[] {
  let result = skills;
  if (filter !== 'all') {
    result = result.filter(s => s.status === filter);
  }
  if (query.trim()) {
    const q = query.toLowerCase();
    result = result.filter(s =>
      s.title.toLowerCase().includes(q) ||
      s.description?.toLowerCase().includes(q) ||
      s.category?.toLowerCase().includes(q)
    );
  }
  return result;
}
