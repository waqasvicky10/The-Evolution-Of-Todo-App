/**
 * API client for backend communication.
 *
 * Provides type-safe functions for all API endpoints with automatic
 * token management and error handling.
 */

import axios, { AxiosInstance, AxiosError } from "axios";
import {
  RegisterRequest,
  LoginRequest,
  TokenResponse,
  RefreshTokenRequest,
  User,
  Task,
  TaskCreate,
  TaskUpdate,
  TaskListResponse,
  APIError,
} from "@/types/api";


// ============================================================================
// Constants
// ============================================================================

// Empty = use relative URLs → Next.js rewrites proxy to backend (no CORS, faster)
const API_BASE_URL = (process.env.NEXT_PUBLIC_API_BASE_URL || "").replace(/\/$/, "");

// ============================================================================
// Axios Instance
// ============================================================================

const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: { "Content-Type": "application/json" },
  timeout: 10000, // 10s — fail fast if backend unreachable
});


// ============================================================================
// Token Management
// ============================================================================

/**
 * Set the access token for authenticated requests.
 * Adds Authorization header to all subsequent requests.
 */
export function setAuthToken(token: string | null): void {
  if (token) {
    apiClient.defaults.headers.common["Authorization"] = `Bearer ${token}`;
  } else {
    delete apiClient.defaults.headers.common["Authorization"];
  }
}

/**
 * Get the current auth token from axios instance.
 */
export function getAuthToken(): string | null {
  const authHeader = apiClient.defaults.headers.common["Authorization"];
  if (typeof authHeader === "string" && authHeader.startsWith("Bearer ")) {
    return authHeader.substring(7);
  }
  return null;
}


// ============================================================================
// Automatic Token Refresh Interceptor
// ============================================================================

let isRefreshing = false;
let failedQueue: Array<{
  resolve: (value?: unknown) => void;
  reject: (reason?: unknown) => void;
}> = [];

const processQueue = (error: unknown, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (
      error.response?.status === 401 &&
      !originalRequest._retry &&
      !originalRequest.url?.includes("/api/auth/login") &&
      !originalRequest.url?.includes("/api/auth/register") &&
      !originalRequest.url?.includes("/api/auth/refresh")
    ) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            originalRequest.headers["Authorization"] = `Bearer ${token}`;
            return apiClient(originalRequest);
          })
          .catch((err) => Promise.reject(err));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      const storedRefreshToken =
        typeof window !== "undefined"
          ? localStorage.getItem("todo_refresh_token")
          : null;

      if (!storedRefreshToken) {
        isRefreshing = false;
        processQueue(error, null);
        if (typeof window !== "undefined") {
          localStorage.removeItem("todo_access_token");
          localStorage.removeItem("todo_refresh_token");
          localStorage.removeItem("todo_user");
          setAuthToken(null);
          window.dispatchEvent(new CustomEvent("auth:session-expired"));
        }
        return Promise.reject(error);
      }

      try {
        const { data } = await axios.post<TokenResponse>(
          `${API_BASE_URL}/api/auth/refresh`,
          { refresh_token: storedRefreshToken }
        );

        const newToken = data.access_token;
        setAuthToken(newToken);

        if (typeof window !== "undefined") {
          localStorage.setItem("todo_access_token", newToken);
        }

        processQueue(null, newToken);

        originalRequest.headers["Authorization"] = `Bearer ${newToken}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);

        if (typeof window !== "undefined") {
          localStorage.removeItem("todo_access_token");
          localStorage.removeItem("todo_refresh_token");
          localStorage.removeItem("todo_user");
          setAuthToken(null);
          // Notify AuthContext to clear state and redirect
          window.dispatchEvent(new CustomEvent("auth:session-expired"));
        }

        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);


// ============================================================================
// Error Handling
// ============================================================================

/**
 * Extract error message from API error response.
 * Always returns a string for safe rendering in React.
 */
export function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<{ detail: string | Array<{ msg: string; loc: string[] }> }>;

    // Handle timeout errors specifically
    if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
      return "Request timed out. The server may be slow. Please try again.";
    }

    // Handle network errors
    if (error.code === 'ERR_NETWORK' || error.message?.includes('Network Error')) {
      return "Cannot connect to server. Please check if the backend is running.";
    }

    const detail = axiosError.response?.data?.detail;

    if (detail) {
      // Handle validation errors (array format)
      if (Array.isArray(detail)) {
        return detail.map((e) => e.msg).join(", ");
      }
      // Handle simple string errors
      return String(detail);
    }
    if (axiosError.message) {
      return axiosError.message;
    }
  }
  if (error instanceof Error) {
    return error.message;
  }
  return "An unexpected error occurred";
}


// ============================================================================
// Authentication API
// ============================================================================

/**
 * Register a new user account.
 *
 * @param data - Registration request data
 * @returns Created user data
 * @throws APIError on validation or conflict errors or timeout
 */
export async function register(data: RegisterRequest): Promise<User> {
  try {
    const response = await apiClient.post<User>("/api/auth/register", data, {
      timeout: 15000,
    });
    return response.data;
  } catch (error: any) {
    if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
      throw new Error("Request timed out. The server may be slow. Please try again.");
    }
    throw error;
  }
}

/**
 * Login user and retrieve tokens.
 *
 * @param data - Login credentials
 * @returns Access and refresh tokens
 * @throws APIError on invalid credentials or timeout
 */
export async function login(data: LoginRequest): Promise<TokenResponse> {
  try {
    const response = await apiClient.post<TokenResponse>("/api/auth/login", data, {
      timeout: 15000,
    });
    return response.data;
  } catch (error: any) {
    if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
      throw new Error("Request timed out. The server may be slow. Please try again.");
    }
    throw error;
  }
}

/**
 * Logout user (client-side token removal).
 *
 * @returns Success message
 * @throws APIError if not authenticated
 */
export async function logout(): Promise<{ message: string }> {
  const response = await apiClient.post<{ message: string }>("/api/auth/logout");
  return response.data;
}

/**
 * Refresh access token using refresh token.
 *
 * @param data - Refresh token request
 * @returns New access token and same refresh token
 * @throws APIError if refresh token is invalid or expired
 */
export async function refreshToken(
  data: RefreshTokenRequest
): Promise<TokenResponse> {
  const response = await apiClient.post<TokenResponse>("/api/auth/refresh", data);
  return response.data;
}


// ============================================================================
// Task API
// ============================================================================

/**
 * Get all tasks for the authenticated user.
 *
 * @returns List of tasks with total count
 * @throws APIError if not authenticated
 */
export async function getTasks(): Promise<TaskListResponse> {
  const response = await apiClient.get<TaskListResponse>("/api/tasks");
  return response.data;
}

/**
 * Get a specific task by ID.
 *
 * @param taskId - Task ID
 * @returns Task object
 * @throws APIError if task not found or unauthorized
 */
export async function getTask(taskId: number): Promise<Task> {
  const response = await apiClient.get<Task>(`/api/tasks/${taskId}`);
  return response.data;
}

/**
 * Create a new task.
 *
 * @param data - Task creation data
 * @returns Created task object
 * @throws APIError on validation errors
 */
export async function createTask(data: TaskCreate): Promise<Task> {
  const response = await apiClient.post<Task>("/api/tasks", data);
  return response.data;
}

/**
 * Update a task's description.
 *
 * @param taskId - Task ID
 * @param data - Task update data
 * @returns Updated task object
 * @throws APIError if task not found, unauthorized, or validation errors
 */
export async function updateTask(taskId: number, data: TaskUpdate): Promise<Task> {
  const response = await apiClient.put<Task>(`/api/tasks/${taskId}`, data);
  return response.data;
}

/**
 * Delete a task.
 *
 * @param taskId - Task ID
 * @throws APIError if task not found or unauthorized
 */
export async function deleteTask(taskId: number): Promise<void> {
  await apiClient.delete(`/api/tasks/${taskId}`);
}

/**
 * Toggle a task's completion status.
 *
 * @param taskId - Task ID
 * @returns Updated task object with toggled status
 * @throws APIError if task not found or unauthorized
 */
export async function toggleTask(taskId: number): Promise<Task> {
  const response = await apiClient.patch<Task>(`/api/tasks/${taskId}/toggle`);
  return response.data;
}


// ============================================================================
// Export API Client
// ============================================================================

export default apiClient;
