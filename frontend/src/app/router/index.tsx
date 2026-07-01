import { createBrowserRouter, Navigate } from 'react-router-dom';
import { AuthLayout } from '../layouts/AuthLayout';
import { DashboardLayout } from '../layouts/DashboardLayout';
import { PublicRoute, ProtectedRoute } from './guards';
import { useAuthStore } from '../store/authStore';

const CatchAllRoute = () => {
  const token = useAuthStore((state) => state.token);
  return <Navigate to={token ? "/dashboard" : "/login"} replace />;
};

import LoginPage from '@/pages/auth/LoginPage';
import DashboardPage from '@/pages/dashboard/DashboardPage';
import SkillsPage from '@/pages/skills/SkillsPage';
import SkillDetailPage from '@/pages/skills/SkillDetailPage';
import SearchPage from '@/pages/search/SearchPage';
import PdfPage from '@/pages/pdf/PdfPage';

// Placeholder components for future phases
const Placeholder = ({ title }: { title: string }) => (
  <div className="flex items-center justify-center h-64 border-2 border-dashed rounded-xl">
    <h2 className="text-2xl font-semibold text-muted-foreground">{title} Coming Soon</h2>
  </div>
);

export const router = createBrowserRouter([
  {
    element: <PublicRoute />,
    children: [
      {
        element: <AuthLayout />,
        children: [
          { path: '/login', element: <LoginPage /> },
          { path: '/register', element: <Placeholder title="Register" /> },
        ],
      },
    ],
  },
  {
    element: <ProtectedRoute />,
    children: [
      {
        element: <DashboardLayout />,
        children: [
          { path: '/', element: <Navigate to="/dashboard" replace /> },
          { path: '/dashboard', element: <DashboardPage /> },
          { path: '/skills', element: <SkillsPage /> },
          { path: '/skills/:id', element: <SkillDetailPage /> },
          { path: '/topics', element: <Placeholder title="Topics System" /> },
          { path: '/notes', element: <Placeholder title="Notes System" /> },
          { path: '/streak', element: <Placeholder title="Streak Engine" /> },
          { path: '/search', element: <SearchPage /> },
          { path: '/pdf', element: <PdfPage /> },
          { path: '/settings', element: <Placeholder title="Settings" /> },
        ],
      },
    ],
  },
  {
    path: '*',
    element: <CatchAllRoute />,
  },
]);

