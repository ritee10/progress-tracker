import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useAuthStore } from '@/app/store/authStore';
import { useNavigate } from 'react-router-dom';

export default function LoginPage() {
  const setAuth = useAuthStore((state) => state.setAuth);
  const navigate = useNavigate();

  const handleLogin = (e: React.FormEvent) => {
      e.preventDefault();

      // Mock login for foundation Phase 14
      setAuth(
        'mock-jwt-token',
        'mock-refresh-token',
        {
          id: '1',
          email: 'user@example.com',
          username: 'user',
          full_name: 'Demo User',
          avatar_url: null,
          role: 'user',
          is_active: true,
          is_verified: true,
        }
      );

      navigate('/dashboard');
    };

  return (
    <div className="bg-card text-card-foreground shadow-sm rounded-xl border p-6">
      <form onSubmit={handleLogin} className="space-y-4">
        <div className="space-y-2">
          <label className="text-sm font-medium">Email</label>
          <Input type="email" placeholder="you@example.com" required />
        </div>
        <div className="space-y-2">
          <label className="text-sm font-medium">Password</label>
          <Input type="password" required />
        </div>
        <Button type="submit" className="w-full">
          Sign In
        </Button>
      </form>
    </div>
  );
}
