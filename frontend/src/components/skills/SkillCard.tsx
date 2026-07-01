// ============================================================
// Component — SkillCard
// ============================================================

import { Link } from 'react-router-dom';
import { Flame, BookOpen, CheckCircle2, Clock, Pin } from 'lucide-react';
import { cn } from '@/lib/utils';
import {
  formatRelativeTime,
  getStatusColors,
  getStatusLabel,
  getProgressColor,
} from '@/lib/skillUtils';
import { CircularProgressChart } from './CircularProgressChart';
import { ProgressBar } from './ProgressBar';
import type { Skill } from '@/types/skill';

interface SkillCardProps {
  skill: Skill;
  onPin?: (id: string) => void;
  onArchive?: (id: string) => void;
}

const DEFAULT_ICONS: Record<string, string> = {
  default: '📚',
  code: '💻',
  math: '📐',
  science: '🔬',
  language: '🗣️',
};

export function SkillCard({ skill, onPin }: SkillCardProps) {
  const statusColor = getStatusColors(skill.status);
  const progressColor = getProgressColor(skill.progress);
  const icon = skill.icon || DEFAULT_ICONS.default;

  return (
    <div
      className={cn(
        'group relative flex flex-col bg-card border rounded-2xl overflow-hidden',
        'transition-all duration-300 ease-out',
        'hover:shadow-xl hover:-translate-y-1',
        statusColor.border
      )}
    >
      {/* Pinned indicator */}
      {skill.isPinned && (
        <div className="absolute top-3 right-3 z-10">
          <Pin className="h-4 w-4 fill-amber-400 text-amber-400" />
        </div>
      )}

      {/* Top color band */}
      <div
        className={cn(
          'h-1.5 w-full',
          skill.progress <= 25 ? 'bg-red-500' :
          skill.progress <= 50 ? 'bg-orange-500' :
          skill.progress <= 75 ? 'bg-blue-500' : 'bg-green-500'
        )}
      />

      <div className="flex flex-col flex-1 p-5 gap-4">
        {/* Header row */}
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-3 min-w-0">
            <span className="text-2xl shrink-0">{icon}</span>
            <div className="min-w-0">
              <h3 className="font-bold text-base leading-tight line-clamp-1">{skill.title}</h3>
              {skill.category && (
                <span className="text-xs text-muted-foreground">{skill.category}</span>
              )}
            </div>
          </div>
          {/* Mini circular */}
          <div className="shrink-0">
            <CircularProgressChart percentage={skill.progress} size={56} strokeWidth={6} />
          </div>
        </div>

        {/* Status badge */}
        <div>
          <span
            className={cn(
              'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold',
              statusColor.bg,
              statusColor.text
            )}
          >
            {getStatusLabel(skill.status)}
          </span>
        </div>

        {/* Progress bar */}
        <ProgressBar value={skill.progress} size="md" showLabel={false} />

        {/* Stats row */}
        <div className="grid grid-cols-3 gap-2 text-center">
          <StatPill icon={<CheckCircle2 className="h-3.5 w-3.5" />} value={skill.completedTopics} label="Done" />
          <StatPill icon={<BookOpen className="h-3.5 w-3.5" />} value={skill.totalTopics} label="Total" />
          <StatPill icon={<Flame className="h-3.5 w-3.5 text-orange-500" />} value={`${skill.currentStreak}d`} label="Streak" />
        </div>

        {/* Progress percentage text */}
        <p className={cn('text-sm font-semibold text-center', progressColor)}>
          {skill.progress}% Complete
        </p>

        {/* Last activity */}
        <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
          <Clock className="h-3 w-3 shrink-0" />
          <span>Last active {formatRelativeTime(skill.lastActivityDate)}</span>
        </div>

        {/* Actions */}
        <div className="flex gap-2 mt-auto pt-2 border-t">
          <Link
            to={`/skills/${skill.id}`}
            className="flex-1 text-center text-sm font-medium py-1.5 px-3 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-colors"
          >
            Continue
          </Link>
          {onPin && (
            <button
              onClick={() => onPin(skill.id)}
              className="py-1.5 px-3 rounded-lg text-sm border hover:bg-muted transition-colors"
              title={skill.isPinned ? 'Unpin' : 'Pin'}
            >
              {skill.isPinned ? '📌' : '📍'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

function StatPill({ icon, value, label }: { icon: React.ReactNode; value: string | number; label: string }) {
  return (
    <div className="flex flex-col items-center gap-0.5 rounded-lg bg-muted/40 p-2">
      <span className="text-muted-foreground">{icon}</span>
      <span className="text-sm font-bold leading-tight">{value}</span>
      <span className="text-[10px] text-muted-foreground leading-tight">{label}</span>
    </div>
  );
}
