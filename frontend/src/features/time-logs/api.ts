import { apiClient } from '@/lib/api-client';
import { GetTimeLogsParams, GetTimeLogsResponse } from './types';

function buildQuery(params: GetTimeLogsParams): string {
  const qs = new URLSearchParams();
  if (params.page) qs.set('page', String(params.page));
  if (params.page_size) qs.set('page_size', String(params.page_size));
  if (params.task_id) qs.set('task_id', params.task_id);
  if (params.date) qs.set('date', params.date);
  if (params.from) qs.set('from', params.from);
  if (params.to) qs.set('to', params.to);
  if (params.sort_by) qs.set('sort_by', params.sort_by);
  if (params.sort_order) qs.set('sort_order', params.sort_order);
  const str = qs.toString();
  return str ? `?${str}` : '';
}

export async function getTimeLogs(params: GetTimeLogsParams = {}): Promise<GetTimeLogsResponse> {
  return apiClient.get<GetTimeLogsResponse>(`/time-sessions${buildQuery(params)}`);
}
