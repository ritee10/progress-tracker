import { Plus } from 'lucide-react';
import { SkillGrid } from '@/components/skills/SkillGrid';
import { useSkills } from '@/hooks/useSkills';
import { LoadingOverlay } from '@/components/ui/api-status/LoadingOverlay';
import { ErrorBanner } from '@/components/ui/api-status/ErrorBanner';

export default function SkillsPage() {
  const { skills, isLoading, error, updateSkill } = useSkills();

  const handlePin = async (id: string) => {
    const skill =
      skills?.data?.items?.find((s: any) => s.id === id) ||
      skills?.data?.find((s: any) => s.id === id);
    if (!skill) return;
    await updateSkill({ id, is_pinned: !skill.isPinned });
  };

  if (isLoading) return <LoadingOverlay message="Loading skills..." />;

  if (error) {
    return (
      <div className="space-y-6">
        <SkillsHeading />
        <ErrorBanner
          title="Failed to load skills"
          message={(error as any).message}
        />
      </div>
    );
  }

  const skillsList = skills?.data?.items || skills?.data || [];

  return (
    <div className="space-y-5 sm:space-y-6">
      <SkillsHeading />
      <SkillGrid
        skills={skillsList}
        onPin={handlePin}
        onCreateSkill={() => console.log('Open create modal')}
        onRetry={() => {}}
      />
    </div>
  );
}

function SkillsHeading() {
  return (
    <div className="flex items-start justify-between gap-3">
      <div className="min-w-0">
        <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">
          My Skills
        </h1>
        <p className="text-muted-foreground mt-1 text-sm sm:text-base">
          Track and manage your learning progress
        </p>
      </div>

      {/* Min 44x44 touch target */}
      <button className="inline-flex items-center gap-2 rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground hover:bg-primary/90 active:scale-95 transition-all shadow-sm shrink-0 min-h-[44px]">
        <Plus className="h-4 w-4" />
        <span className="hidden sm:inline">Add Skill</span>
        <span className="sm:hidden">Add</span>
      </button>
    </div>
  );
}
