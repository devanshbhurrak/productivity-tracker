import { LogOut, User } from 'lucide-react';
import { useCurrentUser, useLogout } from '@/features/auth/hooks';
import { DropdownMenu, DropdownMenuItem } from '@/components/ui/dropdown-menu';

export function UserMenu() {
  const { data: user } = useCurrentUser();
  const logoutMutation = useLogout();

  if (!user) return null;

  return (
    <DropdownMenu
      align="right"
      trigger={
        <button
          type="button"
          className="flex items-center gap-2 rounded-md px-3 py-2 w-full hover:bg-accent transition-colors text-left"
        >
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground text-sm font-semibold flex-shrink-0">
            {user.name.charAt(0).toUpperCase()}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate">{user.name}</p>
            <p className="text-xs text-muted-foreground truncate">{user.email}</p>
          </div>
        </button>
      }
    >
      <div className="px-3 py-2 border-b border-border">
        <p className="text-xs text-muted-foreground">Signed in as</p>
        <p className="text-sm font-medium truncate">{user.email}</p>
      </div>
      <DropdownMenuItem
        destructive
        onClick={() => logoutMutation.mutate()}
        className="mt-1"
      >
        <LogOut className="h-4 w-4" />
        Sign out
      </DropdownMenuItem>
    </DropdownMenu>
  );
}
