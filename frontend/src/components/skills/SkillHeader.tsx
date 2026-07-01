// ============================================================
// Component — SkillHeader
// ============================================================

import { ArrowLeft, Pin, PinOff } from 'lucide-react';
import { Link } from 'react-router-dom';
import { CircularProgressChart } from './CircularProgressChart';
import { getStatusColors, getStatusLabel, getProgressColor } from '@/lib/skillUtils';
import { cn } from '@/lib/utils';
import type { Skill } from '@/types/skill';

interface SkillHeaderProps {
  skill: Skill;
  stats?: { notesCount: number };
  onPin?: () => void;
}

export function SkillHeader({ skill, onPin }: SkillHeaderProps) {
  const statusColor = getStatusColors(skill.status);
  const progressColor = getProgressColor(skill.progress);

  return (
    <div className="bg-card border rounded-2xl overflow-hidden shadow-sm">
      {/* Color band */}
      <div
        className={cn(
          'h-2',
          skill.progress <= 25 ? 'bg-red-500' :
          skill.progress <= 50 ? 'bg-orange-500' :
          skill.progress <= 75 ? 'bg-blue-500' : 'bg-green-500'
        )}
      />

      <div className="p-6">
        {/* Back nav */}
        <Link
          to="/skills"
          className="inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors mb-6"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Skills
        </Link>

        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-6">
          {/* Icon & title */}
          <div className="flex items-center gap-4 flex-1 min-w-0">
            <span className="text-5xl shrink-0">{skill.icon || '📚'}</span>
            <div className="min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <h1 className="text-2xl font-bold leading-tight">{skill.title}</h1>
                <span
                  className={cn(
                    'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold',
                    statusColor.bg, statusColor.text
                  )}
                >
                  {getStatusLabel(skill.status)}
                </span>
              </div>
              {skill.description && (
                <p className="text-muted-foreground text-sm mt-1 line-clamp-2">{skill.description}</p>
              )}
              {skill.category && (
                <span className="text-xs text-muted-foreground mt-1 block">{skill.category}</span>
              )}
            </div>
          </div>

          {/* Circular Progress & pin */}
          <div className="flex items-center gap-4 shrink-0">
            <div className="flex flex-col items-center gap-1">
              <CircularProgressChart percentage={skill.progress} size={90} strokeWidth={9} />
              <span className={cn('text-xs font-semibold', progressColor)}>
                {skill.progress}% done
              </span>
            </div>

            {onPin && (
              <button
                onClick={onPin}
                className="p-2 rounded-lg border hover:bg-muted transition-colors"
                title={skill.isPinned ? 'Unpin Skill' : 'Pin Skill'}
              >
                {skill.isPinned ? (
                  <PinOff className="h-5 w-5 text-amber-500" />
                ) : (
                  <Pin className="h-5 w-5 text-muted-foreground" />
                )}
              </button>
            )}
          </div>
        </div>

        {/* Quick stats row */}
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 mt-6 pt-5 border-t">
          {[
            { label: 'Total Topics', value: skill.totalTopics },
            { label: 'Completed', value: skill.completedTopics },
            { label: 'Pending', value: skill.totalTopics - skill.completedTopics },
            { label: 'Current Streak', value: `${skill.currentStreak}d` },
            { label: 'Notes', value: skill.notesCount },
          ].map(({ label, value }) => (
            <div key={label} className="text-center rounded-xl bg-muted/40 py-3 px-2">
              <div className="text-xl font-bold">{value}</div>
              <div className="text-xs text-muted-foreground mt-0.5">{label}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
