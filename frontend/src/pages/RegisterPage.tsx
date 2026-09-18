import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Link, useNavigate } from 'react-router-dom';
import { useRegister, useLogin } from '@/features/auth/hooks';
import { registerSchema, RegisterFormValues } from '@/features/auth/schemas';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

export function RegisterPage() {
  const navigate = useNavigate();
  const registerMutation = useRegister();
  const loginMutation = useLogin();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
  });

  const onSubmit = handleSubmit(async (values) => {
    try {
      const timezone =
        Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC';
      await registerMutation.mutateAsync({
        name: values.name,
        email: values.email,
        password: values.password,
        timezone,
      });
      // Auto-login after registration
      await loginMutation.mutateAsync({
        email: values.email,
        password: values.password,
      });
      navigate('/app/dashboard');
    } catch {
      // error shown below
    }
  });

  const isPending = registerMutation.isPending || loginMutation.isPending;

  return (
    <div className="min-h-screen flex items-center justify-center bg-background px-4">
      <div className="w-full max-w-[400px]">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-primary">ProductivityHub</h1>
          <p className="text-muted-foreground mt-1">Create your account</p>
        </div>

        <div className="bg-card rounded-lg border border-border p-8 shadow-sm">
          <form onSubmit={onSubmit} className="space-y-4">
            <div className="space-y-1.5">
              <label htmlFor="name" className="text-sm font-medium text-foreground">Name</label>
              <Input
                {...register('name')}
                id="name"
                type="text"
                placeholder="Your full name"
                autoComplete="name"
                error={!!errors.name}
              />
              {errors.name && (
                <p className="text-xs text-destructive">{errors.name.message}</p>
              )}
            </div>

            <div className="space-y-1.5">
              <label htmlFor="email" className="text-sm font-medium text-foreground">Email</label>
              <Input
                {...register('email')}
                id="email"
                type="email"
                placeholder="you@example.com"
                autoComplete="email"
                error={!!errors.email}
              />
              {errors.email && (
                <p className="text-xs text-destructive">{errors.email.message}</p>
              )}
            </div>

            <div className="space-y-1.5">
              <label htmlFor="password" className="text-sm font-medium text-foreground">Password</label>
              <Input
                {...register('password')}
                id="password"
                type="password"
                placeholder="Min. 8 characters"
                autoComplete="new-password"
                error={!!errors.password}
              />
              {errors.password && (
                <p className="text-xs text-destructive">{errors.password.message}</p>
              )}
            </div>

            <div className="space-y-1.5">
              <label htmlFor="confirmPassword" className="text-sm font-medium text-foreground">Confirm Password</label>
              <Input
                {...register('confirmPassword')}
                id="confirmPassword"
                type="password"
                placeholder="Re-enter your password"
                autoComplete="new-password"
                error={!!errors.confirmPassword}
              />
              {errors.confirmPassword && (
                <p className="text-xs text-destructive">{errors.confirmPassword.message}</p>
              )}
            </div>

            {(registerMutation.error || loginMutation.error) && (
              <div className="rounded-md bg-destructive/10 border border-destructive/20 px-4 py-3">
                <p className="text-sm text-destructive">
                  {registerMutation.error instanceof Error
                    ? registerMutation.error.message
                    : loginMutation.error instanceof Error
                    ? loginMutation.error.message
                    : 'Registration failed. Please try again.'}
                </p>
              </div>
            )}

            <Button
              type="submit"
              className="w-full"
              isLoading={isPending}
            >
              Create Account
            </Button>
          </form>

          <p className="mt-6 text-center text-sm text-muted-foreground">
            Already have an account?{' '}
            <Link to="/login" className="text-primary font-medium hover:underline">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
