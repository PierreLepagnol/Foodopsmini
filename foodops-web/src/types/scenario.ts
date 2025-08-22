import { z } from 'zod';

export const ScenarioSchema = z.object({
  id: z.string(),
  name: z.string(),
  description: z.string().optional(),
});

export type Scenario = z.infer<typeof ScenarioSchema>;
