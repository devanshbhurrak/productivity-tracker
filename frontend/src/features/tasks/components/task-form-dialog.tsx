import { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Dialog, DialogHeader, DialogBody, DialogFooter } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select } from '@/components/ui/select';
import { useCreateTask, useUpdateTask } from '../hooks';
import { taskFormSchema, TaskFormValues } from '../schemas';
import { Task } from '@/types';
import { useToast } from '@/components/ui/toast';

interface TaskFormDialogProps {
  open: boolean;
  onClose: () => void;
  task?: Task;
}

export function TaskFormDialog({ open, onClose, task }: TaskFormDialogProps) {
  const isEditing = !!task;
  const createTask = useCreateTask();
  const updateTask = useUpdateTask();
  const { success, error } = useToast();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<TaskFormValues>({
    resolver: zodResolver(taskFormSchema),
    defaultValues: {
      title: task?.title ?? '',
      description: task?.description ?? '',
      status: task?.status,
    },
  });

  useEffect(() => {
    if (open) {
      reset({
        title: task?.title ?? '',
        description: task?.description ?? '',
        status: task?.status,
      });
    }
  }, [open, task, reset]);

  const isPending = createTask.isPending || updateTask.isPending;

  const onSubmit = handleSubmit(async (values) => {
    try {
      if (isEditing && task) {
        await updateTask.mutateAsync({ id: task.id, data: values });
        success('Task updated successfully');
      } else {
        await createTask.mutateAsync(values);
        success('Task created successfully');
      }
      onClose();
    } catch (err) {
      const message = err instanceof Error ? err.message : 'An error occurred';
      error(isEditing ? 'Failed to update task' : 'Failed to create task', message);
    }
  });

  return (
    <Dialog open={open} onClose={onClose}>
      <DialogHeader title={isEditing ? 'Edit Task' : 'Create Task'} onClose={onClose} />
      <form onSubmit={onSubmit}>
        <DialogBody className="space-y-4">
          <div className="space-y-1.5">
            <label htmlFor="task-title" className="text-sm font-medium text-foreground">
              Title <span className="text-destructive">*</span>
            </label>
            <Input
              {...register('title')}
              id="task-title"
              placeholder="Enter task title"
              error={!!errors.title}
              disabled={isPending}
            />
            {errors.title && (
              <p className="text-xs text-destructive">{errors.title.message}</p>
            )}
          </div>

          <div className="space-y-1.5">
            <label htmlFor="task-description" className="text-sm font-medium text-foreground">Description</label>
            <Textarea
              {...register('description')}
              id="task-description"
              placeholder="Add a description (optional)"
              rows={3}
              error={!!errors.description}
              disabled={isPending}
            />
            {errors.description && (
              <p className="text-xs text-destructive">{errors.description.message}</p>
            )}
          </div>

          {isEditing && (
            <div className="space-y-1.5">
              <label htmlFor="task-status" className="text-sm font-medium text-foreground">Status</label>
              <Select
                {...register('status')}
                id="task-status"
                error={!!errors.status}
                disabled={isPending}
              >
                <option value="PENDING">Pending</option>
                <option value="IN_PROGRESS">In Progress</option>
                <option value="COMPLETED">Completed</option>
              </Select>
            </div>
          )}
        </DialogBody>
        <DialogFooter>
          <Button type="button" variant="outline" onClick={onClose} disabled={isPending}>
            Cancel
          </Button>
          <Button type="submit" isLoading={isPending}>
            {isEditing ? 'Save Changes' : 'Create Task'}
          </Button>
        </DialogFooter>
      </form>
    </Dialog>
  );
}
