import { User } from '@/types';

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  name: string;
  email: string;
  password: string;
  timezone?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}
