import { z } from 'zod';

export const taskFormSchema = z.object({
  title: z
    .string()
    .min(1, 'Title is required')
    .max(200, 'Title must be less than 200 characters'),
  description: z.string().max(2000, 'Description is too long').optional(),
  status: z.enum(['PENDING', 'IN_PROGRESS', 'COMPLETED']).optional(),
});

export type TaskFormValues = z.infer<typeof taskFormSchema>;
