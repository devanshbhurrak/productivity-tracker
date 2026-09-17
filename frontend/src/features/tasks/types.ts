import { Task, TaskStatus, PaginatedResponse, TaskTimeSummary } from '@/types';

export type { Task, TaskStatus, TaskTimeSummary };

export interface GetTasksParams {
  page?: number;
  page_size?: number;
  search?: string;
  status?: TaskStatus | '';
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export type GetTasksResponse = PaginatedResponse<Task>;

export interface CreateTaskRequest {
  title: string;
  description?: string;
  status?: TaskStatus;
}

export interface UpdateTaskRequest {
  title?: string;
  description?: string;
  status?: TaskStatus;
}
