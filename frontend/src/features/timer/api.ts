import { apiClient } from '@/lib/api-client';
import { TimeSession } from '@/types';

export async function getActiveTimer(): Promise<TimeSession | null> {
  return apiClient.get<TimeSession | null>('/time-sessions/active');
}

export async function startTimer(taskId: string): Promise<TimeSession> {
  return apiClient.post<TimeSession>('/time-sessions/start', { task_id: taskId });
}

export async function stopTimer(sessionId: string): Promise<TimeSession> {
  return apiClient.post<TimeSession>(`/time-sessions/${sessionId}/stop`);
}
