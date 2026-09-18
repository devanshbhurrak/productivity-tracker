import { useState, useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  Plus,
  Search,
  Play,
  Square,
  MoreVertical,
  Pencil,
  Trash2,
  Timer,
  ChevronUp,
  ChevronDown,
  ListTodo,
} from 'lucide-react';
import { useTasks } from '@/features/tasks/hooks';
import { useActiveTimer, useStartTimer, useStopTimer } from '@/features/timer/hooks';
import { PageHeader } from '@/components/layout/page-header';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select } from '@/components/ui/select';
import { Pagination } from '@/components/ui/pagination';
import { EmptyState } from '@/components/ui/empty-state';
import { ErrorState } from '@/components/ui/error-state';
import { DropdownMenu, DropdownMenuItem, DropdownMenuSeparator } from '@/components/ui/dropdown-menu';
import { RowSkeleton } from '@/components/feedback/loading-skeleton';
import { TaskFormDialog } from '@/features/tasks/components/task-form-dialog';
import { DeleteTaskDialog } from '@/features/tasks/components/delete-task-dialog';
import { TaskStatusBadge } from '@/features/tasks/components/task-status-badge';
import { Task, TaskStatus } from '@/types';
import { formatDuration } from '@/utils/format';
import { useToast } from '@/components/ui/toast';
import { cn } from '@/lib/utils';

function SortButton({
  column,
  currentSort,
  currentOrder,
  onSort,
  children,
}: {
  column: string;
  currentSort: string;
  currentOrder: string;
  onSort: (col: string, order: 'asc' | 'desc') => void;
  children: React.ReactNode;
}) {
  const isActive = currentSort === column;
  const nextOrder = isActive && currentOrder === 'asc' ? 'desc' : 'asc';

  return (
    <button
      type="button"
      className="flex items-center gap-1 text-xs font-medium text-muted-foreground hover:text-foreground"
      onClick={() => onSort(column, nextOrder)}
    >
      {children}
      {isActive ? (
        currentOrder === 'asc' ? (
          <ChevronUp className="h-3 w-3" />
        ) : (
          <ChevronDown className="h-3 w-3" />
        )
      ) : null}
    </button>
  );
}

export function TasksPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const { success, error } = useToast();

  const search = searchParams.get('search') ?? '';
  const status = (searchParams.get('status') ?? '') as TaskStatus | '';
  const sortBy = searchParams.get('sort_by') ?? 'created_at';
  const sortOrder = (searchParams.get('sort_order') ?? 'desc') as 'asc' | 'desc';
  const page = Number(searchParams.get('page') ?? '1');

  const [searchInput, setSearchInput] = useState(search);
  const [formDialogOpen, setFormDialogOpen] = useState(false);
  const [editTask, setEditTask] = useState<Task | null>(null);
  const [deleteTask, setDeleteTask] = useState<Task | null>(null);

  // Debounce search
  useEffect(() => {
    const timer = setTimeout(() => {
      setSearchParams((prev) => {
        const next = new URLSearchParams(prev);
        if (searchInput) {
          next.set('search', searchInput);
        } else {
          next.delete('search');
        }
        next.set('page', '1');
        return next;
      });
    }, 400);
    return () => clearTimeout(timer);
  }, [searchInput, setSearchParams]);

  const { data, isLoading, error: fetchError, refetch } = useTasks({
    page,
    page_size: 20,
    search,
    status: status || undefined,
    sort_by: sortBy,
    sort_order: sortOrder,
  });

  const { data: activeTimer } = useActiveTimer();
  const startTimer = useStartTimer();
  const stopTimer = useStopTimer();

  const updateParam = useCallback(
    (key: string, value: string) => {
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
    },
    [setSearchParams]
  );

  const handleSort = (col: string, order: 'asc' | 'desc') => {
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev);
      next.set('sort_by', col);
      next.set('sort_order', order);
      return next;
    });
  };

  const handleTimerToggle = async (task: Task) => {
    if (task.active_time_session_id) {
      try {
        await stopTimer.mutateAsync(task.active_time_session_id);
        success('Timer stopped');
      } catch {
        error('Failed to stop timer');
      }
    } else if (activeTimer) {
      error('Stop the active timer first', 'You can only track one task at a time.');
    } else {
      try {
        await startTimer.mutateAsync(task.id);
        success('Timer started');
      } catch {
        error('Failed to start timer');
      }
    }
  };

  const openEditDialog = (task: Task) => {
    setEditTask(task);
    setFormDialogOpen(true);
  };

  const closeFormDialog = () => {
    setFormDialogOpen(false);
    setEditTask(null);
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Tasks"
        description="Manage and track your tasks"
        actions={
          <Button onClick={() => setFormDialogOpen(true)}>
            <Plus className="h-4 w-4" />
            Create Task
          </Button>
        }
      />

      {/* Filters */}
      <div className="flex flex-col gap-3 sm:flex-row">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            placeholder="Search tasks..."
            className="pl-9"
          />
        </div>
        <Select
          value={status}
          onChange={(e) => updateParam('status', e.target.value)}
          className="w-full sm:w-40"
        >
          <option value="">All statuses</option>
          <option value="PENDING">Pending</option>
          <option value="IN_PROGRESS">In Progress</option>
          <option value="COMPLETED">Completed</option>
        </Select>
        <Select
          value={`${sortBy}:${sortOrder}`}
          onChange={(e) => {
            const [col, order] = e.target.value.split(':');
            setSearchParams((prev) => {
              const next = new URLSearchParams(prev);
              next.set('sort_by', col);
              next.set('sort_order', order);
              return next;
            });
          }}
          className="w-full sm:w-48"
        >
          <option value="created_at:desc">Newest first</option>
          <option value="created_at:asc">Oldest first</option>
          <option value="title:asc">Title A-Z</option>
          <option value="title:desc">Title Z-A</option>
          <option value="updated_at:desc">Recently updated</option>
        </Select>
      </div>

      {/* Task list */}
      {isLoading ? (
        <div className="rounded-lg border border-border bg-card divide-y divide-border">
          {Array.from({ length: 5 }).map((_, i) => (
            <RowSkeleton key={i} />
          ))}
        </div>
      ) : fetchError ? (
        <ErrorState
          message="Failed to load tasks"
          onRetry={() => refetch()}
        />
      ) : !data || data.items.length === 0 ? (
        <EmptyState
          icon={ListTodo}
          heading={search || status ? 'No tasks match your filters' : 'No tasks yet'}
          description={
            search || status
              ? 'Try adjusting your search or filters.'
              : 'Create your first task to start tracking your work.'
          }
          actionLabel={!search && !status ? 'Create Task' : undefined}
          onAction={!search && !status ? () => setFormDialogOpen(true) : undefined}
        />
      ) : (
        <div className="rounded-lg border border-border bg-card overflow-hidden">
          {/* Table header */}
          <div className="hidden sm:grid sm:grid-cols-[1fr_auto_auto_auto_auto] sm:gap-4 px-4 py-2 bg-muted/40 border-b border-border text-xs text-muted-foreground font-medium">
            <SortButton
              column="title"
              currentSort={sortBy}
              currentOrder={sortOrder}
              onSort={handleSort}
            >
              Task
            </SortButton>
            <span>Status</span>
            <span>Time</span>
            <span>Timer</span>
            <span></span>
          </div>

          <div className="divide-y divide-border">
            {data.items.map((task) => {
              const isRunning = !!task.active_time_session_id;
              const isThisTimer = activeTimer?.task_id === task.id;

              return (
                <div
                  key={task.id}
                  className={cn(
                    'flex flex-col sm:grid sm:grid-cols-[1fr_auto_auto_auto_auto] sm:items-center gap-3 sm:gap-4 px-4 py-3',
                    isRunning && 'bg-primary/5'
                  )}
                >
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-foreground truncate">
                      {task.title}
                    </p>
                    {task.description && (
                      <p className="text-xs text-muted-foreground truncate mt-0.5 max-w-md">
                        {task.description}
                      </p>
                    )}
                  </div>

                  <div className="flex items-center gap-3 sm:contents">
                    <div>
                      <TaskStatusBadge status={task.status} />
                    </div>
                    <div className="flex items-center gap-1 text-xs text-muted-foreground">
                      <Timer className="h-3 w-3" />
                      {formatDuration(task.total_tracked_seconds)}
                    </div>
                  </div>

                  <div>
                    <Button
                      size="sm"
                      variant={isRunning ? 'destructive' : 'outline'}
                      onClick={() => handleTimerToggle(task)}
                      isLoading={
                        (startTimer.isPending && startTimer.variables === task.id) ||
                        (stopTimer.isPending && stopTimer.variables === task.active_time_session_id)
                      }
                      disabled={
                        !isRunning && !!activeTimer && !isThisTimer
                      }
                      title={!isRunning && !!activeTimer && !isThisTimer ? 'Stop the active timer first' : undefined}
                      className="h-8 gap-1.5"
                    >
                      {isRunning ? (
                        <>
                          {!(stopTimer.isPending && stopTimer.variables === task.active_time_session_id) && (
                            <Square className="h-3 w-3" />
                          )}
                          Stop
                        </>
                      ) : (
                        <>
                          {!(startTimer.isPending && startTimer.variables === task.id) && (
                            <Play className="h-3 w-3" />
                          )}
                          Start
                        </>
                      )}
                    </Button>
                  </div>

                  <div>
                    <DropdownMenu
                      trigger={
                        <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                          <MoreVertical className="h-4 w-4" />
                        </Button>
                      }
                    >
                      <DropdownMenuItem onClick={() => openEditDialog(task)}>
                        <Pencil className="h-4 w-4" />
                        Edit
                      </DropdownMenuItem>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem
                        destructive
                        onClick={() => setDeleteTask(task)}
                      >
                        <Trash2 className="h-4 w-4" />
                        Delete
                      </DropdownMenuItem>
                    </DropdownMenu>
                  </div>
                </div>
              );
            })}
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

      <TaskFormDialog
        open={formDialogOpen}
        onClose={closeFormDialog}
        task={editTask ?? undefined}
      />

      <DeleteTaskDialog
        open={!!deleteTask}
        onClose={() => setDeleteTask(null)}
        task={deleteTask}
      />
    </div>
  );
}
