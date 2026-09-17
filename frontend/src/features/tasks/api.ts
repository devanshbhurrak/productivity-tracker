import { apiClient } from '@/lib/api-client';
import { Task, TaskTimeSummary } from '@/types';
import {
  GetTasksParams,
  GetTasksResponse,
  CreateTaskRequest,
  UpdateTaskRequest,
} from './types';

function buildTasksQuery(params: GetTasksParams): string {
  const qs = new URLSearchParams();
  if (params.page) qs.set('page', String(params.page));
  if (params.page_size) qs.set('page_size', String(params.page_size));
  if (params.search) qs.set('search', params.search);
  if (params.status) qs.set('status', params.status);
  if (params.sort_by) qs.set('sort_by', params.sort_by);
  if (params.sort_order) qs.set('sort_order', params.sort_order);
  const str = qs.toString();
  return str ? `?${str}` : '';
}

export async function getTasks(params: GetTasksParams = {}): Promise<GetTasksResponse> {
  return apiClient.get<GetTasksResponse>(`/tasks${buildTasksQuery(params)}`);
}

export async function getTask(id: string): Promise<Task> {
  return apiClient.get<Task>(`/tasks/${id}`);
}

export async function createTask(data: CreateTaskRequest): Promise<Task> {
  return apiClient.post<Task>('/tasks', data);
}

export async function updateTask(id: string, data: UpdateTaskRequest): Promise<Task> {
  return apiClient.patch<Task>(`/tasks/${id}`, data);
}

export async function deleteTask(id: string): Promise<void> {
  return apiClient.delete_<void>(`/tasks/${id}`);
}

export async function getTaskTimeSummary(taskId: string): Promise<TaskTimeSummary> {
  return apiClient.get<TaskTimeSummary>(`/tasks/${taskId}/time-summary`);
}
