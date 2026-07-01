import { Outlet } from 'react-router-dom';

export const AuthLayout = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-muted/50 p-4">
      <div className="w-full max-w-md">
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold tracking-tight">Progress Tracker</h1>
          <p className="text-muted-foreground mt-2">Sign in to your account</p>
        </div>
        <Outlet />
      </div>
    </div>
  );
};
