import { Navigate, Outlet } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';

/**
 * Decode JWT payload to check expiry WITHOUT verifying signature
 * (signature verification happens server-side).
 */
function isTokenExpired(token: string): boolean {
  try {
    const parts = token.split('.');
    if (parts.length !== 3) return true;
    const payload = JSON.parse(atob(parts[1]));
    const exp = payload?.exp as number | undefined;
    if (!exp) return true;
    // Add 30s buffer to account for clock skew
    return Date.now() / 1000 > exp - 30;
  } catch {
    return true;
  }
}

export const ProtectedRoute = () => {
  const token = useAuthStore((state) => state.token);

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
};

export const PublicRoute = () => {
  const token = useAuthStore((state) => state.token);

  if (token) {
    return <Navigate to="/dashboard" replace />;
  }

  return <Outlet />;
};
