import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { ApiError, setAuthToken, clearAuthToken } from '@/lib/api-client';
import { login, register, logout, getCurrentUser } from './api';
import { LoginRequest, RegisterRequest } from './types';

export function useCurrentUser() {
  return useQuery({
    queryKey: ['auth', 'currentUser'],
    queryFn: async () => {
      try {
        return await getCurrentUser();
      } catch (err) {
        if (err instanceof ApiError && err.status === 401) {
          return null;
        }
        throw err;
      }
    },
    retry: false,
  });
}

export function useLogin() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: LoginRequest) => login(data),
    onSuccess: (data) => {
      setAuthToken(data.access_token);
      queryClient.invalidateQueries({ queryKey: ['auth', 'currentUser'] });
    },
  });
}

export function useRegister() {
  return useMutation({
    mutationFn: (data: RegisterRequest) => register(data),
  });
}

export function useLogout() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  return useMutation({
    mutationFn: () => logout(),
    onSuccess: () => {
      clearAuthToken();
      queryClient.clear();
      navigate('/login');
    },
    onError: () => {
      clearAuthToken();
      queryClient.clear();
      navigate('/login');
    },
  });
}
