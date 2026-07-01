import { Outlet, NavLink, useLocation } from 'react-router-dom';
import {
  Home,
  Target,
  Layers,
  BookOpen,
  BookMarked,
  Search,
  FileText,
  Settings,
  Menu,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';
import { useState, useCallback } from 'react';
import { cn } from '@/lib/utils';
import { MobileDrawer } from '@/components/ui/MobileDrawer';
import { BottomNavigation } from '@/components/ui/BottomNavigation';
import { useTouchGestures } from '@/hooks/useTouchGestures';

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

export const DashboardLayout = () => {
  const [mobileDrawerOpen, setMobileDrawerOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const location = useLocation();

  const openDrawer = useCallback(() => setMobileDrawerOpen(true), []);
  const closeDrawer = useCallback(() => setMobileDrawerOpen(false), []);

  // Swipe right anywhere on mobile to open drawer
  useTouchGestures({ onSwipeRight: openDrawer, onSwipeLeft: closeDrawer });

  // Current page title from nav
  const currentPage =
    NAVIGATION.find((n) => location.pathname.startsWith(n.href))?.name ??
    'Progress Tracker';

  return (
    <div className="min-h-screen bg-background flex">
      {/* ── DESKTOP / TABLET SIDEBAR ──────────────────────── */}
      <aside
        className={cn(
          'hidden md:flex flex-col shrink-0',
          'bg-card border-r transition-all duration-300 ease-in-out',
          sidebarCollapsed ? 'w-[68px]' : 'w-64'
        )}
      >
        {/* Logo / Title */}
        <div
          className={cn(
            'flex items-center h-16 border-b px-4 shrink-0 overflow-hidden',
            sidebarCollapsed ? 'justify-center' : 'gap-2.5 px-5'
          )}
        >
          <span className="text-2xl shrink-0">🎯</span>
          {!sidebarCollapsed && (
            <span className="font-bold text-base tracking-tight truncate">
              Progress Tracker
            </span>
          )}
        </div>

        {/* Nav links */}
        <nav
          className="flex-1 overflow-y-auto overflow-x-hidden px-2 py-3 space-y-0.5"
          aria-label="Sidebar navigation"
        >
          {NAVIGATION.map(({ name, href, icon: Icon }) => (
            <NavLink
              key={href}
              to={href}
              title={sidebarCollapsed ? name : undefined}
              className={({ isActive }) =>
                cn(
                  'group flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium',
                  'transition-all duration-150 overflow-hidden whitespace-nowrap',
                  'min-h-[44px]',
                  isActive
                    ? 'bg-primary/10 text-primary'
                    : 'text-muted-foreground hover:bg-muted hover:text-foreground',
                  sidebarCollapsed && 'justify-center px-0'
                )
              }
            >
              {({ isActive }) => (
                <>
                  <Icon
                    className={cn(
                      'shrink-0 transition-colors',
                      sidebarCollapsed ? 'h-5 w-5' : 'h-[18px] w-[18px]',
                      isActive
                        ? 'text-primary'
                        : 'text-muted-foreground group-hover:text-foreground'
                    )}
                  />
                  {!sidebarCollapsed && name}
                </>
              )}
            </NavLink>
          ))}
        </nav>

        {/* Collapse toggle */}
        <div className="px-2 py-3 border-t shrink-0">
          <button
            onClick={() => setSidebarCollapsed((v) => !v)}
            aria-label={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
            className={cn(
              'w-full flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium',
              'text-muted-foreground hover:bg-muted hover:text-foreground transition-colors',
              'min-h-[44px]',
              sidebarCollapsed && 'justify-center px-0'
            )}
          >
            {sidebarCollapsed ? (
              <ChevronRight className="h-5 w-5 shrink-0" />
            ) : (
              <>
                <ChevronLeft className="h-5 w-5 shrink-0" />
                <span>Collapse</span>
              </>
            )}
          </button>
        </div>
      </aside>

      {/* ── MAIN CONTENT AREA ──────────────────────────────── */}
      <div className="flex flex-col flex-1 min-w-0">
        {/* ── MOBILE HEADER ────── */}
        <header className="md:hidden sticky top-0 z-30 h-14 bg-card/95 backdrop-blur-md border-b flex items-center justify-between px-4 shrink-0">
          <button
            onClick={openDrawer}
            aria-label="Open navigation menu"
            aria-expanded={mobileDrawerOpen}
            className="rounded-xl p-2 text-muted-foreground hover:bg-muted hover:text-foreground transition-colors min-w-[44px] min-h-[44px] flex items-center justify-center"
          >
            <Menu className="h-5 w-5" />
          </button>

          <h1 className="font-semibold text-sm truncate">{currentPage}</h1>

          {/* Right slot — profile avatar placeholder */}
          <div className="h-8 w-8 rounded-full bg-primary/20 flex items-center justify-center text-primary font-semibold text-sm select-none">
            U
          </div>
        </header>

        {/* ── DESKTOP HEADER ───── */}
        <header className="hidden md:flex sticky top-0 z-30 h-14 bg-card/95 backdrop-blur-md border-b items-center justify-between px-6 shrink-0">
          <h1 className="font-semibold text-base text-muted-foreground">{currentPage}</h1>
          <div className="flex items-center gap-3">
            {/* Profile avatar */}
            <div className="h-8 w-8 rounded-full bg-primary/20 flex items-center justify-center text-primary font-semibold text-sm select-none cursor-pointer hover:bg-primary/30 transition-colors">
              U
            </div>
          </div>
        </header>

        {/* ── PAGE CONTENT ──────── */}
        <main className="flex-1 overflow-y-auto">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-5 md:py-8 pb-24 md:pb-8">
            <Outlet />
          </div>
        </main>
      </div>

      {/* ── MOBILE DRAWER ──────────────────────────────────── */}
      <MobileDrawer open={mobileDrawerOpen} onClose={closeDrawer} />

      {/* ── MOBILE BOTTOM NAV ──────────────────────────────── */}
      <BottomNavigation />
    </div>
  );
};
