import { useSearchParams } from 'react-router-dom';
import { Clock } from 'lucide-react';
import { useTimeLogs } from '@/features/time-logs/hooks';
import { useTasks } from '@/features/tasks/hooks';
import { PageHeader } from '@/components/layout/page-header';
import { Pagination } from '@/components/ui/pagination';
import { EmptyState } from '@/components/ui/empty-state';
import { ErrorState } from '@/components/ui/error-state';
import { Badge } from '@/components/ui/badge';
import { Select } from '@/components/ui/select';
import { TableRowSkeleton } from '@/components/feedback/loading-skeleton';
import { formatDuration, formatDateTime } from '@/utils/format';

export function TimeLogsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const page = Number(searchParams.get('page') ?? '1');
  const taskId = searchParams.get('task_id') ?? '';

  const { data, isLoading, error, refetch } = useTimeLogs({
    page,
    page_size: 20,
    task_id: taskId || undefined,
    sort_by: 'started_at',
    sort_order: 'desc',
  });

  const { data: tasksData } = useTasks({ page_size: 100 });

  const getTaskTitle = (taskId: string) => {
    const task = tasksData?.items.find((t) => t.id === taskId);
    return task?.title ?? `Task ${taskId.slice(0, 8)}...`;
  };

  const updateParam = (key: string, value: string) => {
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev);
      if (value) {
        next.set(key, value);
      } else {
        next.delete(key);
      }
      if (key !== 'page') next.set('page', '1');
      return next;
    });
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Time Logs"
        description="View all tracked time sessions"
      />

      {/* Filters */}
      <div className="flex gap-3">
        <Select
          value={taskId}
          onChange={(e) => updateParam('task_id', e.target.value)}
          className="w-full sm:w-56"
        >
          <option value="">All tasks</option>
          {tasksData?.items.map((task) => (
            <option key={task.id} value={task.id}>
              {task.title}
            </option>
          ))}
        </Select>
      </div>

      {isLoading ? (
        <div className="rounded-lg border border-border bg-card overflow-hidden">
          <table className="w-full">
            <thead className="bg-muted/40 border-b border-border">
              <tr>
                {['Task', 'Start', 'End', 'Duration', 'Status'].map((h) => (
                  <th
                    key={h}
                    className="px-4 py-2 text-left text-xs font-medium text-muted-foreground"
                  >
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {Array.from({ length: 8 }).map((_, i) => (
                <TableRowSkeleton key={i} cols={5} />
              ))}
            </tbody>
          </table>
        </div>
      ) : error ? (
        <ErrorState
          message="Failed to load time logs"
          onRetry={() => refetch()}
        />
      ) : !data || data.items.length === 0 ? (
        <EmptyState
          icon={Clock}
          heading="No time logs yet"
          description={
            taskId
              ? 'No time has been tracked for this task.'
              : 'Start tracking time on your tasks to see logs here.'
          }
        />
      ) : (
        <div className="rounded-lg border border-border bg-card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-muted/40 border-b border-border">
                <tr>
                  {['Task', 'Start', 'End', 'Duration', 'Status'].map((h) => (
                    <th
                      key={h}
                      className="px-4 py-3 text-left text-xs font-medium text-muted-foreground"
                    >
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {data.items.map((session) => {
                  const isActive = !session.ended_at;
                  const duration =
                    session.duration != null
                      ? formatDuration(session.duration)
                      : null;

                  return (
                    <tr key={session.id} className="hover:bg-muted/30 transition-colors">
                      <td className="px-4 py-3 text-sm font-medium text-foreground max-w-[200px]">
                        <span className="truncate block">{getTaskTitle(session.task_id)}</span>
                      </td>
                      <td className="px-4 py-3 text-sm text-muted-foreground whitespace-nowrap">
                        {formatDateTime(session.started_at)}
                      </td>
                      <td className="px-4 py-3 text-sm text-muted-foreground whitespace-nowrap">
                        {session.ended_at ? formatDateTime(session.ended_at) : '—'}
                      </td>
                      <td className="px-4 py-3 text-sm text-muted-foreground whitespace-nowrap font-mono">
                        {duration ?? '—'}
                      </td>
                      <td className="px-4 py-3">
                        {isActive ? (
                          <Badge variant="info" className="text-xs">
                            Active
                          </Badge>
                        ) : (
                          <Badge variant="default" className="text-xs">
                            Completed
                          </Badge>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {data && data.pagination.total_pages > 1 && (
        <Pagination
          page={data.pagination.page}
          totalPages={data.pagination.total_pages}
          hasNext={data.pagination.has_next}
          hasPrev={data.pagination.has_prev}
          onPageChange={(p) => updateParam('page', String(p))}
        />
      )}
    </div>
  );
}
