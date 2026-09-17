import { Link } from 'react-router-dom';
import { Clock, CheckCircle2, ListTodo, Timer, ArrowRight, Square } from 'lucide-react';
import { useCurrentUser } from '@/features/auth/hooks';
import { useTodayDashboard } from '@/features/dashboard/hooks';
import { useActiveTimer, useStopTimer, useElapsedSeconds } from '@/features/timer/hooks';
import { PageHeader } from '@/components/layout/page-header';
import { StatSkeleton, CardSkeleton } from '@/components/feedback/loading-skeleton';
import { EmptyState } from '@/components/ui/empty-state';
import { Button } from '@/components/ui/button';
import { TaskStatusBadge } from '@/features/tasks/components/task-status-badge';
import { formatDuration, formatElapsed, getTimeOfDay } from '@/utils/format';

function StatCard({
  label,
  value,
  icon: Icon,
  iconColor,
}: {
  label: string;
  value: string | number;
  icon: React.ElementType;
  iconColor: string;
}) {
  return (
    <div className="rounded-lg border border-border bg-card p-6">
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium text-muted-foreground">{label}</p>
        <div className={`rounded-full p-2 ${iconColor} bg-opacity-10`}>
          <Icon className={`h-4 w-4 ${iconColor}`} />
        </div>
      </div>
      <p className="mt-2 text-2xl font-bold text-foreground">{value}</p>
    </div>
  );
}

function ActiveTimerCard() {
  const { data: activeTimer } = useActiveTimer();
  const stopTimer = useStopTimer();
  const elapsed = useElapsedSeconds(activeTimer?.started_at ?? null);

  if (!activeTimer) return null;

  return (
    <div className="rounded-lg border border-primary/30 bg-primary/5 p-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="h-3 w-3 rounded-full bg-primary animate-pulse" />
          <div>
            <p className="text-sm font-medium text-muted-foreground">Timer Running</p>
            <p className="font-mono text-2xl font-bold text-foreground mt-0.5">
              {formatElapsed(elapsed)}
            </p>
          </div>
        </div>
        <Button
          variant="outline"
          onClick={() => stopTimer.mutate(activeTimer.id)}
          isLoading={stopTimer.isPending}
          className="gap-2"
        >
          <Square className="h-4 w-4" />
          Stop Timer
        </Button>
      </div>
    </div>
  );
}

export function DashboardPage() {
  const { data: user } = useCurrentUser();
  const { data: dashboard, isLoading, error, refetch } = useTodayDashboard();
  const timeOfDay = getTimeOfDay();

  const greeting = user
    ? `Good ${timeOfDay}, ${user.name.split(' ')[0]}`
    : `Good ${timeOfDay}`;

  return (
    <div className="space-y-6">
      <PageHeader
        title={greeting}
        description="Here's what's happening with your tasks today."
      />

      {/* Stats */}
      {isLoading ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <StatSkeleton />
          <StatSkeleton />
          <StatSkeleton />
        </div>
      ) : error ? (
        <div className="rounded-lg border border-destructive/20 bg-destructive/5 p-4">
          <p className="text-sm text-destructive">Failed to load dashboard data.</p>
          <Button variant="outline" size="sm" className="mt-2" onClick={() => refetch()}>
            Retry
          </Button>
        </div>
      ) : dashboard ? (
        <>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <StatCard
              label="Tasks Worked On"
              value={dashboard.tasks_worked_on?.length ?? 0}
              icon={ListTodo}
              iconColor="text-info"
            />
            <StatCard
              label="Total Time Tracked"
              value={formatDuration(dashboard.total_tracked_seconds)}
              icon={Clock}
              iconColor="text-primary"
            />
            <StatCard
              label="Completed Today"
              value={dashboard.completed_count}
              icon={CheckCircle2}
              iconColor="text-success"
            />
          </div>

          <ActiveTimerCard />

          {/* Today's tasks */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">Today's Tasks</h2>
              <Link
                to="/app/tasks"
                className="flex items-center gap-1 text-sm text-primary hover:underline"
              >
                View all tasks
                <ArrowRight className="h-3 w-3" />
              </Link>
            </div>

            {dashboard.tasks_worked_on && dashboard.tasks_worked_on.length > 0 ? (
              <div className="space-y-2">
                {dashboard.tasks_worked_on.map((task) => (
                  <div
                    key={task.id}
                    className="flex items-center justify-between rounded-lg border border-border bg-card px-4 py-3"
                  >
                    <div className="flex items-center gap-3 min-w-0">
                      <TaskStatusBadge status={task.status} />
                      <span className="text-sm font-medium truncate">{task.title}</span>
                    </div>
                    <div className="flex items-center gap-2 flex-shrink-0 ml-3">
                      <span className="text-xs text-muted-foreground flex items-center gap-1">
                        <Timer className="h-3 w-3" />
                        {formatDuration(task.total_tracked_seconds)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <EmptyState
                icon={ListTodo}
                heading="No activity yet today"
                description="Start working on tasks to track your progress here."
                actionLabel="Go to Tasks"
                onAction={() => {
                  window.location.href = '/app/tasks';
                }}
              />
            )}
          </div>
        </>
      ) : null}
    </div>
  );
}
