import { Square } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useActiveTimer, useStopTimer, useElapsedSeconds } from '@/features/timer/hooks';
import { useTasks } from '@/features/tasks/hooks';
import { Button } from '@/components/ui/button';
import { formatElapsed } from '@/utils/format';

export function ActiveTimerBar() {
  const { data: activeTimer } = useActiveTimer();
  const stopTimer = useStopTimer();
  const navigate = useNavigate();

  const elapsed = useElapsedSeconds(activeTimer?.started_at ?? null);

  // Fetch tasks to look up the task title
  const { data: tasksData } = useTasks({ page_size: 100 });
  const task = tasksData?.items.find((t) => t.id === activeTimer?.task_id);

  if (!activeTimer) return null;

  const taskTitle = task?.title ?? `Task ${activeTimer.task_id.slice(0, 8)}`;

  const handleStop = () => {
    stopTimer.mutate(activeTimer.id);
  };

  return (
    <div className="flex items-center justify-between bg-primary px-4 py-2 text-primary-foreground">
      <div className="flex items-center gap-3 min-w-0">
        <div className="h-2 w-2 rounded-full bg-primary-foreground animate-pulse flex-shrink-0" />
        <button
          type="button"
          onClick={() => navigate('/app/tasks')}
          className="text-sm font-medium truncate hover:underline text-left"
        >
          {taskTitle}
        </button>
      </div>
      <div className="flex items-center gap-3 flex-shrink-0 ml-4">
        <span className="font-mono text-sm font-semibold tabular-nums">
          {formatElapsed(elapsed)}
        </span>
        <Button
          size="sm"
          variant="outline"
          className="border-primary-foreground/30 bg-transparent text-primary-foreground hover:bg-primary-foreground/10 h-7"
          onClick={handleStop}
          isLoading={stopTimer.isPending}
        >
          <Square className="h-3 w-3" />
          Stop
        </Button>
      </div>
    </div>
  );
}
