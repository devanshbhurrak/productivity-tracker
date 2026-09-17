import { apiClient } from '@/lib/api-client';
import { DashboardToday } from '@/types';

export async function getTodayDashboard(): Promise<DashboardToday> {
  return apiClient.get<DashboardToday>('/dashboard/today');
}
