import { NavLink } from 'react-router-dom';
import { LayoutDashboard, CheckSquare, Clock } from 'lucide-react';
import { UserMenu } from './user-menu';
import { cn } from '@/lib/utils';

const navItems = [
  { to: '/app/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/app/tasks', icon: CheckSquare, label: 'Tasks' },
  { to: '/app/time-logs', icon: Clock, label: 'Time Logs' },
];

interface SidebarProps {
  onNavClick?: () => void;
}

export function Sidebar({ onNavClick }: SidebarProps) {
  return (
    <div className="flex h-full flex-col">
      <div className="flex h-14 items-center px-4 border-b border-border">
        <span className="text-lg font-bold text-primary">ProductivityHub</span>
      </div>

      <nav className="flex-1 p-3 space-y-1">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            onClick={onNavClick}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:bg-accent hover:text-foreground'
              )
            }
          >
            <Icon className="h-4 w-4 flex-shrink-0" />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="border-t border-border p-3">
        <UserMenu />
      </div>
    </div>
  );
}
