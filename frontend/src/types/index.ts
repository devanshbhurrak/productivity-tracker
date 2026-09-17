export interface User {
  id: string;
  name: string;
  email: string;
  timezone: string;
  created_at: string;
}

export type TaskStatus = 'PENDING' | 'IN_PROGRESS' | 'COMPLETED';

export interface Task {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  status: TaskStatus;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
  total_tracked_seconds: number;
  active_time_session_id: string | null;
}

export interface TimeSession {
  id: string;
  user_id: string;
  task_id: string;
  started_at: string;
  ended_at: string | null;
  duration: number | null;
  created_at: string;
}

export interface PaginationMeta {
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface PaginatedResponse<T> {
  items: T[];
  pagination: PaginationMeta;
}

export interface TaskTimeSummary {
  task_id: string;
  total_sessions: number;
  total_tracked_seconds: number;
}

export interface DashboardToday {
  date: string;
  timezone: string;
  tasks_worked_on: Task[];
  total_tracked_seconds: number;
  completed_count: number;
  in_progress_count: number;
  pending_count: number;
  active_timer?: TimeSession;
}
