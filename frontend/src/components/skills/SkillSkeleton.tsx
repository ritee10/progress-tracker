// ============================================================
// Component — SkillSkeleton
// ============================================================

export function SkillCardSkeleton() {
  return (
    <div className="flex flex-col bg-card border rounded-2xl overflow-hidden animate-pulse">
      <div className="h-1.5 w-full bg-muted" />
      <div className="flex flex-col gap-4 p-5">
        {/* Header */}
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="h-8 w-8 rounded-full bg-muted shrink-0" />
            <div className="space-y-1.5">
              <div className="h-4 w-32 rounded bg-muted" />
              <div className="h-3 w-20 rounded bg-muted" />
            </div>
          </div>
          <div className="h-14 w-14 rounded-full bg-muted shrink-0" />
        </div>

        {/* Badge */}
        <div className="h-5 w-20 rounded-full bg-muted" />

        {/* Progress bar */}
        <div className="h-2.5 w-full rounded-full bg-muted" />

        {/* Stats row */}
        <div className="grid grid-cols-3 gap-2">
          {[1, 2, 3].map(i => (
            <div key={i} className="h-14 rounded-lg bg-muted" />
          ))}
        </div>

        {/* Percentage */}
        <div className="h-4 w-24 rounded bg-muted mx-auto" />

        {/* Last activity */}
        <div className="h-3 w-36 rounded bg-muted" />

        {/* Button */}
        <div className="h-9 w-full rounded-lg bg-muted mt-2" />
      </div>
    </div>
  );
}

export function SkillGridSkeleton({ count = 8 }: { count?: number }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      {Array.from({ length: count }).map((_, i) => (
        <SkillCardSkeleton key={i} />
      ))}
    </div>
  );
}

export function StatsSkeleton() {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4 animate-pulse">
      {Array.from({ length: 5 }).map((_, i) => (
        <div key={i} className="h-24 rounded-xl bg-muted" />
      ))}
    </div>
  );
}
