// ============================================================
// Component — SkillStats
// ============================================================

import { CheckCircle2, Clock, BookOpen, Flame, Trophy } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { SkillStats as SkillStatsType } from '@/types/skill';

interface SkillStatsProps {
  stats: SkillStatsType;
  className?: string;
}

interface StatCardProps {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  sub?: string;
  color?: string;
}

function StatCard({ icon, label, value, sub, color = 'text-primary' }: StatCardProps) {
  return (
    <div className="flex flex-col items-center gap-2 rounded-2xl bg-card border p-4 text-center shadow-sm">
      <span className={cn('p-2.5 rounded-full bg-muted', color)}>{icon}</span>
      <span className="text-2xl font-bold tracking-tight">{value}</span>
      <span className="text-sm text-muted-foreground font-medium">{label}</span>
      {sub && <span className="text-xs text-muted-foreground">{sub}</span>}
    </div>
  );
}

export function SkillStats({ stats, className }: SkillStatsProps) {
  return (
    <div className={cn('grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4', className)}>
      <StatCard
        icon={<CheckCircle2 className="h-5 w-5 text-green-500" />}
        label="Completed"
        value={stats.completedTopics}
        color="text-green-500"
      />
      <StatCard
        icon={<Clock className="h-5 w-5 text-orange-500" />}
        label="Pending"
        value={stats.pendingTopics}
        color="text-orange-500"
      />
      <StatCard
        icon={<BookOpen className="h-5 w-5 text-blue-500" />}
        label="Notes"
        value={stats.notesCount}
        color="text-blue-500"
      />
      <StatCard
        icon={<Flame className="h-5 w-5 text-red-500" />}
        label="Current Streak"
        value={`${stats.currentStreak}d`}
        color="text-red-500"
      />
      <StatCard
        icon={<Trophy className="h-5 w-5 text-amber-500" />}
        label="Longest Streak"
        value={`${stats.longestStreak}d`}
        color="text-amber-500"
      />
    </div>
  );
}
