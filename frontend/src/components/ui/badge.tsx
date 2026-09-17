import { HTMLAttributes } from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { CheckCircle2, Clock, Play } from 'lucide-react';
import { cn } from '@/lib/utils';
import { TaskStatus } from '@/types';

const badgeVariants = cva(
  'inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors',
  {
    variants: {
      variant: {
        default: 'bg-secondary text-secondary-foreground',
        success: 'bg-success text-success-foreground',
        warning: 'bg-warning text-warning-foreground',
        info: 'bg-info text-info-foreground',
        destructive: 'bg-destructive text-destructive-foreground',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  }
);

export interface BadgeProps
  extends HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  );
}

const statusVariantMap: Record<TaskStatus, VariantProps<typeof badgeVariants>['variant']> = {
  COMPLETED: 'success',
  IN_PROGRESS: 'info',
  PENDING: 'warning',
};

const statusLabelMap: Record<TaskStatus, string> = {
  COMPLETED: 'Completed',
  IN_PROGRESS: 'In Progress',
  PENDING: 'Pending',
};

const statusIconMap: Record<TaskStatus, React.ElementType> = {
  COMPLETED: CheckCircle2,
  IN_PROGRESS: Play,
  PENDING: Clock,
};

interface StatusBadgeProps {
  status: TaskStatus;
  className?: string;
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const variant = statusVariantMap[status];
  const label = statusLabelMap[status];
  const Icon = statusIconMap[status];

  return (
    <Badge variant={variant} className={className}>
      <Icon className="h-3 w-3" />
      {label}
    </Badge>
  );
}
