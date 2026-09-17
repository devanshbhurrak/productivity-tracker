import { StatusBadge } from '@/components/ui/badge';
import { TaskStatus } from '@/types';

interface TaskStatusBadgeProps {
  status: TaskStatus;
  className?: string;
}

export function TaskStatusBadge({ status, className }: TaskStatusBadgeProps) {
  return <StatusBadge status={status} className={className} />;
}
