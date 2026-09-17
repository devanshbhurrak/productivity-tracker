import { useElapsedSeconds } from '../hooks';
import { formatElapsed } from '@/utils/format';
import { cn } from '@/lib/utils';

interface ElapsedTimerProps {
  startedAt: string;
  className?: string;
}

export function ElapsedTimer({ startedAt, className }: ElapsedTimerProps) {
  const elapsed = useElapsedSeconds(startedAt);

  return (
    <span className={cn('font-mono tabular-nums', className)}>
      {formatElapsed(elapsed)}
    </span>
  );
}
