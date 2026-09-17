import {
  createContext,
  useContext,
  useState,
  useCallback,
  useEffect,
  ReactNode,
} from 'react';
import { X, CheckCircle2, AlertCircle, Info } from 'lucide-react';
import { cn } from '@/lib/utils';
import { cva, type VariantProps } from 'class-variance-authority';

const toastVariants = cva(
  'flex items-start gap-3 rounded-lg border p-4 shadow-lg transition-all duration-300 max-w-sm w-full',
  {
    variants: {
      variant: {
        success: 'bg-card border-success/30 text-foreground',
        error: 'bg-card border-destructive/30 text-foreground',
        info: 'bg-card border-info/30 text-foreground',
      },
    },
    defaultVariants: {
      variant: 'info',
    },
  }
);

type ToastVariant = 'success' | 'error' | 'info';

interface Toast {
  id: string;
  title: string;
  description?: string;
  variant: ToastVariant;
}

interface ToastContextValue {
  toast: (opts: Omit<Toast, 'id'>) => void;
  dismiss: (id: string) => void;
}

const ToastContext = createContext<ToastContextValue | null>(null);

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const toast = useCallback((opts: Omit<Toast, 'id'>) => {
    const id = Math.random().toString(36).slice(2);
    setToasts((prev) => [...prev, { ...opts, id }]);
  }, []);

  const dismiss = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  return (
    <ToastContext.Provider value={{ toast, dismiss }}>
      {children}
      <div className="fixed bottom-4 right-4 z-[100] flex flex-col gap-2 pointer-events-none">
        {toasts.map((t) => (
          <ToastItem key={t.id} toast={t} onDismiss={dismiss} />
        ))}
      </div>
    </ToastContext.Provider>
  );
}

interface ToastItemProps {
  toast: Toast;
  onDismiss: (id: string) => void;
}

function ToastItem({ toast, onDismiss }: ToastItemProps) {
  useEffect(() => {
    const timer = setTimeout(() => onDismiss(toast.id), 4000);
    return () => clearTimeout(timer);
  }, [toast.id, onDismiss]);

  const Icon =
    toast.variant === 'success'
      ? CheckCircle2
      : toast.variant === 'error'
      ? AlertCircle
      : Info;

  const iconColor =
    toast.variant === 'success'
      ? 'text-success'
      : toast.variant === 'error'
      ? 'text-destructive'
      : 'text-info';

  return (
    <div className={cn(toastVariants({ variant: toast.variant }), 'pointer-events-auto')}>
      <Icon className={cn('h-5 w-5 mt-0.5 flex-shrink-0', iconColor)} />
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium">{toast.title}</p>
        {toast.description && (
          <p className="text-sm text-muted-foreground mt-0.5">{toast.description}</p>
        )}
      </div>
      <button
        type="button"
        onClick={() => onDismiss(toast.id)}
        className="text-muted-foreground hover:text-foreground transition-colors flex-shrink-0"
      >
        <X className="h-4 w-4" />
      </button>
    </div>
  );
}

let _toastFn: ((opts: Omit<Toast, 'id'>) => void) | null = null;

export function Toaster() {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = useCallback((opts: Omit<Toast, 'id'>) => {
    const id = Math.random().toString(36).slice(2);
    setToasts((prev) => [...prev, { ...opts, id }]);
  }, []);

  const dismiss = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  useEffect(() => {
    _toastFn = addToast;
    return () => {
      _toastFn = null;
    };
  }, [addToast]);

  return (
    <div className="fixed bottom-4 right-4 z-[100] flex flex-col gap-2 pointer-events-none">
      {toasts.map((t) => (
        <ToastItem key={t.id} toast={t} onDismiss={dismiss} />
      ))}
    </div>
  );
}

export function useToast() {
  const toast = useCallback(
    (opts: Omit<Toast, 'id'>) => {
      if (_toastFn) {
        _toastFn(opts);
      }
    },
    []
  );

  return {
    toast,
    success: (title: string, description?: string) =>
      toast({ title, description, variant: 'success' }),
    error: (title: string, description?: string) =>
      toast({ title, description, variant: 'error' }),
    info: (title: string, description?: string) =>
      toast({ title, description, variant: 'info' }),
  };
}
