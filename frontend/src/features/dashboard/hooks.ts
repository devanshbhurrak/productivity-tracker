import { useQuery } from '@tanstack/react-query';
import { getTodayDashboard } from './api';

export const dashboardKeys = {
  all: ['dashboard'] as const,
  today: () => [...dashboardKeys.all, 'today'] as const,
};

export function useTodayDashboard() {
  return useQuery({
    queryKey: dashboardKeys.today(),
    queryFn: getTodayDashboard,
    staleTime: 30 * 1000,
  });
}
