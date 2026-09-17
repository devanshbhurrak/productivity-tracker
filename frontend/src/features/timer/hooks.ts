import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useEffect, useState } from 'react';
import { ApiError } from '@/lib/api-client';
import { getActiveTimer, startTimer, stopTimer } from './api';
import { taskKeys } from '../tasks/hooks';

export const timerKeys = {
  all: ['timer'] as const,
  active: () => [...timerKeys.all, 'active'] as const,
};

export function useActiveTimer() {
  return useQuery({
    queryKey: timerKeys.active(),
    queryFn: async () => {
      try {
        return await getActiveTimer();
      } catch (err) {
        if (err instanceof ApiError && err.status === 404) {
          return null;
        }
        throw err;
      }
    },
    staleTime: 5 * 1000,
    retry: false,
  });
}

export function useStartTimer() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (taskId: string) => startTimer(taskId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: timerKeys.active() });
      queryClient.invalidateQueries({ queryKey: taskKeys.lists() });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
}

export function useStopTimer() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (sessionId: string) => stopTimer(sessionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: timerKeys.active() });
      queryClient.invalidateQueries({ queryKey: ['time-logs'] });
      queryClient.invalidateQueries({ queryKey: taskKeys.lists() });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
}

export function useElapsedSeconds(startedAt: string | null): number {
  const [elapsed, setElapsed] = useState<number>(() => {
    if (!startedAt) return 0;
    return Math.floor((Date.now() - new Date(startedAt).getTime()) / 1000);
  });

  useEffect(() => {
    if (!startedAt) {
      setElapsed(0);
      return;
    }

    const startedAtMs = new Date(startedAt).getTime();

    const tick = () => {
      setElapsed(Math.floor((Date.now() - startedAtMs) / 1000));
    };

    tick();
    const interval = setInterval(tick, 1000);
    return () => clearInterval(interval);
  }, [startedAt]);

  return elapsed;
}
