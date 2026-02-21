"use client";

/**
 * Authentication context provider.
 *
 * Manages user authentication state, token storage, and automatic
 * token refresh. Provides authentication functions to all components.
 */

import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import {
  login as apiLogin,
  logout as apiLogout,
  register as apiRegister,
  refreshToken as apiRefreshToken,
  setAuthToken,
} from "@/lib/api";
import {
  User,
  LoginRequest,
  RegisterRequest,
  TokenResponse,
} from "@/types/api";


// ============================================================================
// Types
// ============================================================================

/**
 * Authentication context state and methods.
 */
interface AuthContextType {
  user: User | null;
  accessToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => Promise<void>;
  refreshAuth: () => Promise<void>;
}

/**
 * Stored tokens in localStorage.
 */
interface StoredTokens {
  accessToken: string;
  refreshToken: string;
  user: User;
}


// ============================================================================
// Context
// ============================================================================

const AuthContext = createContext<AuthContextType | undefined>(undefined);


// ============================================================================
// Local Storage Keys
// ============================================================================

const ACCESS_TOKEN_KEY = "todo_access_token";
const REFRESH_TOKEN_KEY = "todo_refresh_token";
const USER_KEY = "todo_user";


// ============================================================================
// Provider Component
// ============================================================================

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [accessToken, setAccessTokenState] = useState<string | null>(null);
  const [refreshToken, setRefreshTokenState] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  /**
   * Store tokens and user in state and localStorage.
   */
  const storeAuth = useCallback((tokens: TokenResponse, userData: User) => {
    // Update state
    setAccessTokenState(tokens.access_token);
    setRefreshTokenState(tokens.refresh_token);
    setUser(userData);

    // Store in localStorage
    localStorage.setItem(ACCESS_TOKEN_KEY, tokens.access_token);
    localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token);
    localStorage.setItem(USER_KEY, JSON.stringify(userData));

    // Set axios default header
    setAuthToken(tokens.access_token);
  }, []);

  /**
   * Clear tokens and user from state and localStorage.
   */
  const clearAuth = useCallback(() => {
    // Clear state
    setAccessTokenState(null);
    setRefreshTokenState(null);
    setUser(null);

    // Clear localStorage
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(USER_KEY);

    // Clear axios default header
    setAuthToken(null);
  }, []);

  /**
   * Load authentication state from localStorage on mount.
   */
  useEffect(() => {
    const loadAuth = () => {
      try {
        const storedAccessToken = localStorage.getItem(ACCESS_TOKEN_KEY);
        const storedRefreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
        const storedUser = localStorage.getItem(USER_KEY);

        if (storedAccessToken && storedRefreshToken && storedUser) {
          const userData: User = JSON.parse(storedUser);
          setAccessTokenState(storedAccessToken);
          setRefreshTokenState(storedRefreshToken);
          setUser(userData);
          setAuthToken(storedAccessToken);
        }
      } catch (error) {
        console.error("Failed to load auth from localStorage:", error);
        clearAuth();
      } finally {
        setIsLoading(false);
      }
    };

    loadAuth();
  }, [clearAuth]);

  /**
   * Listen for session expiry (e.g. when token refresh fails after 401).
   */
  useEffect(() => {
    const handler = () => {
      clearAuth();
      router.push("/login?expired=1");
    };
    window.addEventListener("auth:session-expired", handler);
    return () => window.removeEventListener("auth:session-expired", handler);
  }, [clearAuth, router]);

  /**
   * Refresh access token using refresh token.
   */
  const refreshAuth = useCallback(async () => {
    try {
      if (!refreshToken) {
        throw new Error("No refresh token available");
      }

      const tokens = await apiRefreshToken({ refresh_token: refreshToken });

      // Update access token (refresh token stays the same)
      setAccessTokenState(tokens.access_token);
      localStorage.setItem(ACCESS_TOKEN_KEY, tokens.access_token);
      setAuthToken(tokens.access_token);
    } catch (error) {
      console.error("Token refresh failed:", error);
      clearAuth();
      router.push("/login");
    }
  }, [refreshToken, clearAuth, router]);

  /**
   * Login user with email and password.
   */
  const login = useCallback(
    async (credentials: LoginRequest) => {
      try {
        const tokens = await apiLogin(credentials);

        // Create user object from email (backend doesn't return user on login)
        const userData: User = {
          id: 0, // Will be populated from token or separate call if needed
          email: credentials.email,
          created_at: new Date().toISOString(),
        };

        storeAuth(tokens, userData);
        router.push("/dashboard");
      } catch (error) {
        throw error;
      }
    },
    [storeAuth, router]
  );

  /**
   * Register new user account.
   */
  const register = useCallback(
    async (data: RegisterRequest) => {
      let userData: User | null = null;
      try {
        userData = await apiRegister(data);
      } catch (error: any) {
        // Re-throw registration errors to be handled by the UI
        console.error("Registration API error:", error);
        if (error.response?.data?.detail) {
          // Handle validation error detail
          const detail = error.response.data.detail;
          if (Array.isArray(detail)) {
            // Validation errors array
            throw new Error(detail.map((e: any) => e.msg || e).join(", "));
          } else {
            throw new Error(String(detail));
          }
        } else if (error instanceof Error) {
          throw error;
        } else {
          throw new Error(String(error));
        }
      }

      if (!userData) {
        throw new Error("Registration failed: No user data returned");
      }

      // After registration, login automatically
      try {
        const tokens = await apiLogin({
          email: data.email,
          password: data.password,
        });

        storeAuth(tokens, userData);
        router.push("/dashboard");
      } catch (loginError: any) {
        // If auto-login fails, redirect to login page
        console.error("Auto-login failed after registration:", loginError);
        if (loginError.response?.data?.detail) {
          router.push(`/login?registered=true&message=${encodeURIComponent(loginError.response.data.detail)}`);
        } else {
          router.push("/login?registered=true");
        }
      }
    },
    [storeAuth, router]
  );

  /**
   * Logout user and clear authentication state.
   */
  const logout = useCallback(async () => {
    try {
      // Call backend logout endpoint (optional, tokens are stateless)
      await apiLogout();
    } catch (error) {
      console.error("Logout API call failed:", error);
      // Continue with local logout even if API call fails
    } finally {
      clearAuth();
      router.push("/");
    }
  }, [clearAuth, router]);

  const value: AuthContextType = {
    user,
    accessToken,
    isAuthenticated: !!accessToken && !!user,
    isLoading,
    login,
    register,
    logout,
    refreshAuth,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}


// ============================================================================
// Hook
// ============================================================================

/**
 * Hook to access authentication context.
 *
 * @throws Error if used outside AuthProvider
 */
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
