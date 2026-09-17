import { Menu, X } from 'lucide-react';
import { UserMenu } from './user-menu';

interface MobileHeaderProps {
  menuOpen: boolean;
  onToggleMenu: () => void;
}

export function MobileHeader({ menuOpen, onToggleMenu }: MobileHeaderProps) {
  return (
    <header className="flex h-14 items-center justify-between border-b border-border bg-card px-4 lg:hidden">
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={onToggleMenu}
          className="rounded-md p-1.5 hover:bg-accent transition-colors"
        >
          {menuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
        <span className="text-base font-bold text-primary">ProductivityHub</span>
      </div>
      <div className="w-8">
        <UserMenu />
      </div>
    </header>
  );
}
