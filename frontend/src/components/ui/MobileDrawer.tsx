import { useEffect } from 'react';
import { NavLink } from 'react-router-dom';
import {
  Home,
  Target,
  Layers,
  BookOpen,
  BookMarked,
  Search,
  FileText,
  Settings,
  X,
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface MobileDrawerProps {
  open: boolean;
  onClose: () => void;
}

const NAVIGATION = [
  { name: 'Dashboard', href: '/dashboard', icon: Home },
  { name: 'Skills', href: '/skills', icon: Target },
  { name: 'Topics', href: '/topics', icon: Layers },
  { name: 'Notes', href: '/notes', icon: BookOpen },
  { name: 'Streak', href: '/streak', icon: BookMarked },
  { name: 'Search', href: '/search', icon: Search },
  { name: 'PDF Import', href: '/pdf', icon: FileText },
  { name: 'Settings', href: '/settings', icon: Settings },
];

export function MobileDrawer({ open, onClose }: MobileDrawerProps) {
  // Lock body scroll when drawer open
  useEffect(() => {
    if (open) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [open]);

  // Close on Escape key
  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [onClose]);

  return (
    <>
      {/* Backdrop overlay */}
      <div
        aria-hidden="true"
        onClick={onClose}
        className={cn(
          'fixed inset-0 z-40 bg-black/50 backdrop-blur-sm transition-opacity duration-300 md:hidden',
          open ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none'
        )}
      />

      {/* Drawer panel */}
      <aside
        role="dialog"
        aria-modal="true"
        aria-label="Navigation menu"
        className={cn(
          'fixed inset-y-0 left-0 z-50 w-72 bg-card border-r shadow-2xl',
          'transform transition-transform duration-300 ease-out md:hidden',
          'flex flex-col',
          open ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        {/* Drawer header */}
        <div className="flex items-center justify-between px-6 h-16 border-b shrink-0">
          <div className="flex items-center gap-2.5">
            <span className="text-2xl">🎯</span>
            <span className="font-bold text-lg tracking-tight">Progress Tracker</span>
          </div>
          <button
            onClick={onClose}
            aria-label="Close navigation menu"
            className="rounded-lg p-2 text-muted-foreground hover:bg-muted hover:text-foreground transition-colors min-w-[44px] min-h-[44px] flex items-center justify-center"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Nav links */}
        <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-0.5">
          {NAVIGATION.map(({ name, href, icon: Icon }) => (
            <NavLink
              key={href}
              to={href}
              onClick={onClose}
              className={({ isActive }) =>
                cn(
                  'group flex items-center gap-3 rounded-xl px-3 py-3 text-sm font-medium transition-all duration-150',
                  'min-h-[44px]',
                  isActive
                    ? 'bg-primary/10 text-primary'
                    : 'text-muted-foreground hover:bg-muted hover:text-foreground'
                )
              }
            >
              {({ isActive }) => (
                <>
                  <Icon
                    className={cn(
                      'h-5 w-5 shrink-0 transition-colors',
                      isActive ? 'text-primary' : 'text-muted-foreground group-hover:text-foreground'
                    )}
                  />
                  {name}
                </>
              )}
            </NavLink>
          ))}
        </nav>

        {/* Footer */}
        <div className="px-4 py-4 border-t text-xs text-muted-foreground">
          Progress Tracker v1.0
        </div>
      </aside>
    </>
  );
}
