import { NavLink } from 'react-router-dom';
import { Home, Target, Search, FileText, BookMarked } from 'lucide-react';
import { cn } from '@/lib/utils';

const NAV_ITEMS = [
  { to: '/dashboard', icon: Home, label: 'Home' },
  { to: '/skills', icon: Target, label: 'Skills' },
  { to: '/search', icon: Search, label: 'Search' },
  { to: '/pdf', icon: FileText, label: 'PDF' },
  { to: '/streak', icon: BookMarked, label: 'Streak' },
];

export function BottomNavigation() {
  return (
    <nav
      className="fixed bottom-0 left-0 right-0 z-50 md:hidden bg-card/95 backdrop-blur-md border-t safe-area-pb"
      aria-label="Mobile navigation"
    >
      <div className="flex items-stretch justify-around h-16">
        {NAV_ITEMS.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              cn(
                'flex flex-1 flex-col items-center justify-center gap-0.5 min-w-0',
                'text-xs font-medium transition-all duration-200',
                'relative select-none active:scale-95',
                isActive
                  ? 'text-primary'
                  : 'text-muted-foreground hover:text-foreground'
              )
            }
          >
            {({ isActive }) => (
              <>
                {/* Active indicator pill */}
                {isActive && (
                  <span className="absolute top-1.5 w-8 h-0.5 rounded-full bg-primary" />
                )}
                <Icon
                  className={cn(
                    'h-5 w-5 mt-1 transition-transform duration-200',
                    isActive && 'scale-110'
                  )}
                  strokeWidth={isActive ? 2.5 : 1.75}
                />
                <span className={cn('truncate', isActive && 'font-semibold')}>
                  {label}
                </span>
              </>
            )}
          </NavLink>
        ))}
      </div>
    </nav>
  );
}
