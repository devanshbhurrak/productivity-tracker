import { ConfirmDialog } from '@/components/ui/confirm-dialog';
import { useDeleteTask } from '../hooks';
import { Task } from '@/types';
import { useToast } from '@/components/ui/toast';

interface DeleteTaskDialogProps {
  open: boolean;
  onClose: () => void;
  task: Task | null;
}

export function DeleteTaskDialog({ open, onClose, task }: DeleteTaskDialogProps) {
  const deleteTask = useDeleteTask();
  const { success, error } = useToast();

  const handleConfirm = async () => {
    if (!task) return;
    try {
      await deleteTask.mutateAsync(task.id);
      success('Task deleted', 'The task and all its time history have been removed.');
      onClose();
    } catch (err) {
      const message = err instanceof Error ? err.message : 'An error occurred';
      error('Failed to delete task', message);
    }
  };

  return (
    <ConfirmDialog
      open={open}
      onClose={onClose}
      onConfirm={handleConfirm}
      title="Delete Task"
      description={
        task
          ? `Are you sure you want to delete "${task.title}"? This will permanently delete the task and all associated time tracking history. This action cannot be undone.`
          : 'Are you sure you want to delete this task?'
      }
      confirmLabel="Delete Task"
      isLoading={deleteTask.isPending}
    />
  );
}
