import { useQuery } from '@tanstack/react-query';
import { getTimeLogs } from './api';
import { GetTimeLogsParams } from './types';

export const timeLogKeys = {
  all: ['time-logs'] as const,
  lists: () => [...timeLogKeys.all, 'list'] as const,
  list: (params: GetTimeLogsParams) => [...timeLogKeys.lists(), params] as const,
};

export function useTimeLogs(params: GetTimeLogsParams = {}) {
  return useQuery({
    queryKey: timeLogKeys.list(params),
    queryFn: () => getTimeLogs(params),
    staleTime: 30 * 1000,
  });
}
