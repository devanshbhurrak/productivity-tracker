import { RouterProvider } from 'react-router-dom';
import { Providers } from './providers';
import { router } from './router';
import { Toaster } from '@/components/ui/toast';

export default function App() {
  return (
    <Providers>
      <RouterProvider router={router} />
      <Toaster />
    </Providers>
  );
}
