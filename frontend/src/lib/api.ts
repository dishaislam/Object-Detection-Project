import axios from 'axios';
import type {
  LoginCredentials,
  SignupData,
  AuthResponse,
  DetectionResponse,
  QuestionRequest,
  AnswerResponse,
  User,
} from '@/types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const signup = async (data: SignupData): Promise<User> => {
  const response = await api.post<User>('/api/signup', data);
  return response.data;
};

export const login = async (credentials: LoginCredentials): Promise<AuthResponse> => {
  const response = await api.post<AuthResponse>('/api/login', credentials);
  return response.data;
};

export const getCurrentUser = async (): Promise<User> => {
  const response = await api.get<User>('/api/me');
  return response.data;
};

export const detectObjects = async (file: File): Promise<DetectionResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post<DetectionResponse>('/api/detect', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

export const askQuestion = async (data: QuestionRequest): Promise<AnswerResponse> => {
  const response = await api.post<AnswerResponse>('/api/ask', data);
  return response.data;
};

export const isAuthenticated = (): boolean => {
  return !!localStorage.getItem('token');
};

export const saveToken = (token: string): void => {
  localStorage.setItem('token', token);
};

export const removeToken = (): void => {
  localStorage.removeItem('token');
};