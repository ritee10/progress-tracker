import { useParams } from 'react-router-dom';
import { useSkill } from '@/hooks/useSkills';
import { SkillHeader } from '@/components/skills/SkillHeader';
import { SkillStats } from '@/components/skills/SkillStats';
import { SkillAnalytics } from '@/components/skills/SkillAnalytics';
import { TreeView } from '@/components/tree';
import { LoadingOverlay } from '@/components/ui/api-status/LoadingOverlay';
import { ErrorBanner } from '@/components/ui/api-status/ErrorBanner';

export default function SkillDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { data: skillData, isLoading, error } = useSkill(id || '');

  if (isLoading) return <LoadingOverlay message="Loading skill details..." />;

  if (error)
    return <ErrorBanner title="Error" message={(error as any).message} />;

  const skill = skillData?.data;

  if (!skill) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] gap-4 text-center px-4">
        <div className="text-5xl">🔍</div>
        <h2 className="text-2xl font-bold">Skill Not Found</h2>
        <p className="text-muted-foreground">
          This skill doesn't exist or has been removed.
        </p>
        <a
          href="/skills"
          className="text-primary underline-offset-4 hover:underline text-sm"
        >
          Go back to Skills
        </a>
      </div>
    );
  }

  const statsPayload = {
    skillId: skill.id,
    totalTopics: skill.totalTopics || 0,
    completedTopics: skill.completedTopics || 0,
    pendingTopics: (skill.totalTopics || 0) - (skill.completedTopics || 0),
    notesCount: skill.notesCount || 0,
    studyDays: 0,
    currentStreak: skill.currentStreak || 0,
    longestStreak: skill.longestStreak || 0,
    completionPercentage: skill.progress || 0,
  };

  return (
    <div className="space-y-5 sm:space-y-6">
      {/* Header */}
      <SkillHeader skill={skill} stats={{ notesCount: skill.notesCount || 0 }} />

      {/* Stats — full width on all screens */}
      <SkillStats stats={statsPayload} />

      {/* Analytics — stacked on mobile, 2-col on md+ (handled inside SkillAnalytics) */}
      <SkillAnalytics stats={statsPayload} />

      {/* Curriculum Tree — horizontally scrollable wrapper on mobile */}
      <div className="bg-card border rounded-2xl p-4 sm:p-6 shadow-sm overflow-hidden">
        <div className="flex items-center justify-between mb-4 sm:mb-5">
          <h3 className="font-semibold text-base sm:text-lg">Curriculum Tree</h3>
          <span className="text-xs text-muted-foreground bg-muted px-2.5 py-1 rounded-md">
            Interactive
          </span>
        </div>
        {/* Horizontal scroll container for very narrow screens */}
        <div className="overflow-x-auto -mx-4 px-4 sm:mx-0 sm:px-0">
          <div className="min-w-[320px]">
            <TreeView skillId={skill.id} />
          </div>
        </div>
      </div>

      {/* Action buttons — full width on mobile, inline on sm+ */}
      <div className="flex flex-col sm:flex-row sm:flex-wrap gap-3">
        <button className="flex-1 sm:flex-none rounded-xl bg-primary px-4 py-3 sm:py-2.5 text-sm font-semibold text-primary-foreground hover:bg-primary/90 active:scale-95 transition-all min-h-[44px]">
          📝 Open Topics
        </button>
        <button className="flex-1 sm:flex-none rounded-xl border px-4 py-3 sm:py-2.5 text-sm font-semibold hover:bg-muted active:scale-95 transition-all min-h-[44px]">
          📒 View Notes
        </button>
        <button className="flex-1 sm:flex-none rounded-xl border px-4 py-3 sm:py-2.5 text-sm font-semibold hover:bg-muted active:scale-95 transition-all min-h-[44px]">
          📄 Import PDF
        </button>
      </div>
    </div>
  );
}
