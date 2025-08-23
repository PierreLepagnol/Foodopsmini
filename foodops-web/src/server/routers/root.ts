import { router, procedure } from '../trpc';
import fs from 'fs';
import path from 'path';
import { spawnSync } from 'child_process';

export const appRouter = router({
  hello: procedure.query(() => {
    return { message: 'Bienvenue sur tRPC' };
  }),
  pythonPing: procedure.query(() => {
    const result = spawnSync('python', ['-c', 'print("pong")']);
    return { message: result.stdout.toString().trim() };
  }),
  scenarios: procedure.query(() => {
    const file = path.join(process.cwd(), 'src', 'data', 'scenarios.json');
    const raw = fs.readFileSync(file, 'utf8');
    return JSON.parse(raw);
  })
});

export type AppRouter = typeof appRouter;
