import { create } from 'zustand';
import { persist } from 'zustand/middleware';

// Typed user shape matching backend UserResponse schema
export interface AuthUser {
  id: string;
  email: string;
  username: string;
  full_name: string;
  avatar_url: string | null;
  role: string;
  is_active: boolean;
  is_verified: boolean;
}

interface AuthState {
  token: string | null;
  refreshToken: string | null;
  user: AuthUser | null;
  setAuth: (token: string, refreshToken: string, user: AuthUser) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      refreshToken: null,
      user: null,
      setAuth: (token, refreshToken, user) => set({ token, refreshToken, user }),
      logout: () => set({ token: null, refreshToken: null, user: null }),
    }),
    {
      name: 'auth-storage',
    }
  )
);
