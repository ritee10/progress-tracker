// ============================================================
// Component — EmptySkillState
// ============================================================

interface EmptySkillStateProps {
  message?: string;
  onCreateSkill?: () => void;
}

export function EmptySkillState({
  message = 'Create your first skill and start tracking progress.',
  onCreateSkill,
}: EmptySkillStateProps) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[400px] gap-5 text-center p-8">
      <div className="text-7xl">📚</div>
      <div>
        <h2 className="text-2xl font-bold">No Skills Yet</h2>
        <p className="text-muted-foreground mt-2 max-w-sm">{message}</p>
      </div>
      {onCreateSkill && (
        <button
          onClick={onCreateSkill}
          className="inline-flex items-center gap-2 rounded-xl bg-primary px-5 py-2.5 text-sm font-semibold text-primary-foreground hover:bg-primary/90 transition-colors"
        >
          + Create Skill
        </button>
      )}
    </div>
  );
}

interface FilterEmptyStateProps {
  query: string;
  filter: string;
  onClear: () => void;
}

export function FilterEmptyState({ query, filter, onClear }: FilterEmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[300px] gap-4 text-center p-8">
      <div className="text-5xl">🔍</div>
      <div>
        <h2 className="text-xl font-bold">No Results Found</h2>
        <p className="text-muted-foreground mt-1 text-sm">
          {query
            ? `No skills match "${query}"`
            : `No skills with status "${filter}"`}
        </p>
      </div>
      <button
        onClick={onClear}
        className="text-sm text-primary underline-offset-4 hover:underline"
      >
        Clear filters
      </button>
    </div>
  );
}
