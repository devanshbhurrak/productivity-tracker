import { useEffect, useState } from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import { Sidebar } from './sidebar';
import { MobileHeader } from './mobile-header';
import { ActiveTimerBar } from './active-timer-bar';
import { cn } from '@/lib/utils';

export function AppShell() {
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleUnauthorized = () => {
      navigate('/login', { replace: true });
    };
    window.addEventListener('auth:unauthorized', handleUnauthorized);
    return () => window.removeEventListener('auth:unauthorized', handleUnauthorized);
  }, [navigate]);

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      {/* Desktop sidebar */}
      <aside className="hidden lg:flex lg:flex-shrink-0 lg:w-60 border-r border-border bg-card">
        <Sidebar />
      </aside>

      {/* Mobile overlay */}
      {mobileMenuOpen && (
        <div
          className="fixed inset-0 z-40 lg:hidden"
          onClick={() => setMobileMenuOpen(false)}
        >
          <div className="absolute inset-0 bg-black/50" />
          <div className="absolute left-0 top-0 h-full w-60 bg-card border-r border-border">
            <Sidebar onNavClick={() => setMobileMenuOpen(false)} />
          </div>
        </div>
      )}

      {/* Main content */}
      <div className="flex flex-1 flex-col overflow-hidden">
        <MobileHeader
          menuOpen={mobileMenuOpen}
          onToggleMenu={() => setMobileMenuOpen((v) => !v)}
        />
        <ActiveTimerBar />
        <main className="flex-1 overflow-y-auto">
          <div className="mx-auto max-w-6xl p-4 lg:p-6">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
