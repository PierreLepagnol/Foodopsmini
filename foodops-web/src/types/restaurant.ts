import { z } from 'zod';

export enum RestaurantType {
  FAST = 'fast',
  CLASSIC = 'classic',
  GASTRONOMIQUE = 'gastronomique',
  BRASSERIE = 'brasserie',
}

export const RestaurantSchema = z.object({
  id: z.string(),
  name: z.string(),
  type: z.nativeEnum(RestaurantType),
  capacityBase: z.number().int().positive(),
  speedService: z.number().positive(),
  cash: z.number().optional(),
});

export type Restaurant = z.infer<typeof RestaurantSchema>;
