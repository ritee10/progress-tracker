import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useProgress } from '@/hooks/useProgress';
import { ErrorBanner } from '@/components/ui/api-status/ErrorBanner';
import {
  Target,
  CheckCircle2,
  Flame,
  TrendingUp,
} from 'lucide-react';
import { cn } from '@/lib/utils';

function StatCard({
  title,
  value,
  icon,
  loading,
  accent,
}: {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  loading?: boolean;
  accent?: string;
}) {
  return (
    <Card className="overflow-hidden">
      <div className={cn('h-1 w-full', accent ?? 'bg-primary')} />
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-1 pt-4">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {title}
        </CardTitle>
        <span className="text-muted-foreground">{icon}</span>
      </CardHeader>
      <CardContent className="pb-4">
        {loading ? (
          <div className="h-8 w-20 animate-pulse bg-muted rounded-md" />
        ) : (
          <div className="text-2xl sm:text-3xl font-bold">{value}</div>
        )}
      </CardContent>
    </Card>
  );
}

export default function DashboardPage() {
  const { dashboardStats, isDashboardStatsLoading, error, refetch } =
    useProgress() as any;

  if (error) {
    return (
      <div className="space-y-6">
        <PageHeading />
        <ErrorBanner
          title="Failed to load dashboard"
          message={error.message}
          onRetry={refetch}
        />
      </div>
    );
  }

  return (
    <div className="space-y-6 sm:space-y-8">
      <PageHeading />

      {/* ── Stat Cards — 1-col mobile, 2-col tablet, 4-col desktop ── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <StatCard
          title="Total Skills"
          value={dashboardStats?.totalSkills ?? 0}
          icon={<Target className="h-4 w-4" />}
          loading={isDashboardStatsLoading}
          accent="bg-violet-500"
        />
        <StatCard
          title="Topics Completed"
          value={dashboardStats?.completedTopics ?? 0}
          icon={<CheckCircle2 className="h-4 w-4" />}
          loading={isDashboardStatsLoading}
          accent="bg-emerald-500"
        />
        <StatCard
          title="Current Streak"
          value={`${dashboardStats?.streakDays ?? 0} Days`}
          icon={<Flame className="h-4 w-4 text-orange-500" />}
          loading={isDashboardStatsLoading}
          accent="bg-orange-500"
        />
        <StatCard
          title="Completion Rate"
          value={`${dashboardStats?.progressPercentage ?? 0}%`}
          icon={<TrendingUp className="h-4 w-4" />}
          loading={isDashboardStatsLoading}
          accent="bg-blue-500"
        />
      </div>

      {/* ── Quick tips / placeholder sections ── */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-semibold">Recent Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Your latest study sessions and progress updates will appear here.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-semibold">Pinned Skills</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Pin your most important skills to keep them here for quick access.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function PageHeading() {
  return (
    <div>
      <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">Dashboard</h1>
      <p className="text-muted-foreground mt-1 text-sm sm:text-base">
        Welcome back! Here's an overview of your progress.
      </p>
    </div>
  );
}
