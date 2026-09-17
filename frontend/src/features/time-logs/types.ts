import { TimeSession, PaginatedResponse } from '@/types';

export type { TimeSession };

export type GetTimeLogsResponse = PaginatedResponse<TimeSession>;

export interface GetTimeLogsParams {
  page?: number;
  page_size?: number;
  task_id?: string;
  date?: string;
  from?: string;
  to?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}
