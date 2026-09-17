import { apiClient } from '@/lib/api-client';
import { User } from '@/types';
import { LoginRequest, RegisterRequest, AuthResponse } from './types';

export async function login(data: LoginRequest): Promise<AuthResponse> {
  return apiClient.post<AuthResponse>('/auth/login', data);
}

export async function register(data: RegisterRequest): Promise<User> {
  return apiClient.post<User>('/auth/register', data);
}

export async function logout(): Promise<void> {
  return apiClient.post<void>('/auth/logout');
}

export async function getCurrentUser(): Promise<User> {
  return apiClient.get<User>('/auth/me');
}
