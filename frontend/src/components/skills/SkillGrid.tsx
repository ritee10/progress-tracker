// ============================================================
// Component — SkillGrid
// ============================================================

import { useState, useMemo } from 'react';
import { Search, SlidersHorizontal } from 'lucide-react';
import { SkillCard } from './SkillCard';
import { EmptySkillState, FilterEmptyState } from './EmptySkillState';
import { SkillGridSkeleton } from './SkillSkeleton';
import { sortSkills, filterSkills } from '@/lib/skillUtils';
import type { Skill, FilterOption, SortOption } from '@/types/skill';
import { cn } from '@/lib/utils';

interface SkillGridProps {
  skills: Skill[];
  isLoading?: boolean;
  error?: string | null;
  onPin?: (id: string) => void;
  onCreateSkill?: () => void;
  onRetry?: () => void;
}

const FILTER_OPTIONS: { label: string; value: FilterOption }[] = [
  { label: 'All', value: 'all' },
  { label: 'In Progress', value: 'in_progress' },
  { label: 'Completed', value: 'completed' },
  { label: 'Overdue', value: 'overdue' },
  { label: 'Not Started', value: 'not_started' },
];

const SORT_OPTIONS: { label: string; value: SortOption }[] = [
  { label: 'Alphabetical', value: 'alphabetical' },
  { label: 'Progress %', value: 'progress' },
  { label: 'Last Activity', value: 'lastActivity' },
  { label: 'Streak', value: 'streak' },
];

export function SkillGrid({
  skills,
  isLoading = false,
  error = null,
  onPin,
  onCreateSkill,
  onRetry,
}: SkillGridProps) {
  const [query, setQuery] = useState('');
  const [filter, setFilter] = useState<FilterOption>('all');
  const [sort, setSort] = useState<SortOption>('lastActivity');

  const processed = useMemo(() => {
    const filtered = filterSkills(skills, filter, query);
    return sortSkills(filtered, sort);
  }, [skills, query, filter, sort]);

  const clearFilters = () => {
    setQuery('');
    setFilter('all');
    setSort('lastActivity');
  };

  // Loading state
  if (isLoading) return <SkillGridSkeleton />;

  // Error state
  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[300px] gap-4 text-center p-8">
        <div className="text-5xl">⚠️</div>
        <div>
          <h2 className="text-xl font-bold">Unable to Load Skills</h2>
          <p className="text-muted-foreground text-sm mt-1">{error}</p>
        </div>
        {onRetry && (
          <button
            onClick={onRetry}
            className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
          >
            Try Again
          </button>
        )}
      </div>
    );
  }

  // Empty state (no skills at all)
  if (!isLoading && skills.length === 0) {
    return <EmptySkillState onCreateSkill={onCreateSkill} />;
  }

  return (
    <div className="space-y-6">
      {/* Controls */}
      <div className="flex flex-col sm:flex-row gap-3 items-stretch sm:items-center">
        {/* Search */}
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground pointer-events-none" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search skills..."
            className="w-full pl-9 pr-4 py-2 text-sm rounded-lg border bg-background focus:outline-none focus:ring-2 focus:ring-ring"
          />
        </div>

        {/* Sort */}
        <div className="flex items-center gap-2">
          <SlidersHorizontal className="h-4 w-4 text-muted-foreground shrink-0" />
          <select
            value={sort}
            onChange={(e) => setSort(e.target.value as SortOption)}
            className="text-sm rounded-lg border bg-background px-2 py-2 focus:outline-none focus:ring-2 focus:ring-ring"
          >
            {SORT_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>{o.label}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Filter tabs — horizontally scrollable on mobile */}
      <div className="flex gap-2 overflow-x-auto pb-1 -mb-1 scrollbar-hide">
        {FILTER_OPTIONS.map((opt) => (
          <button
            key={opt.value}
            onClick={() => setFilter(opt.value)}
            className={cn(
              'rounded-full px-3.5 py-1.5 text-sm font-medium border transition-colors whitespace-nowrap shrink-0 min-h-[36px]',
              filter === opt.value
                ? 'bg-primary text-primary-foreground border-primary'
                : 'bg-muted/50 hover:bg-muted text-muted-foreground border-transparent'
            )}
          >
            {opt.label}
            {opt.value === 'all' && (
              <span className="ml-1.5 text-xs opacity-70">({skills.length})</span>
            )}
          </button>
        ))}
      </div>

      {/* Results count */}
      {processed.length > 0 && (
        <p className="text-sm text-muted-foreground">
          Showing <strong>{processed.length}</strong> of {skills.length} skills
        </p>
      )}

      {/* Grid or empty-filter state */}
      {processed.length === 0 ? (
        <FilterEmptyState query={query} filter={filter} onClear={clearFilters} />
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {processed.map((skill) => (
            <SkillCard key={skill.id} skill={skill} onPin={onPin} />
          ))}
        </div>
      )}
    </div>
  );
}
