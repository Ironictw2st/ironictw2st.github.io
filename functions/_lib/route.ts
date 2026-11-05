import type { Env } from './types.ts';
import type { Ctx } from './handlers.ts';

/** Build the handler context from a Pages Function context; purge drops the cached public copy. */
export function toCtx(c: { request: Request; env: Env; data?: Record<string, unknown> }): Ctx {
  return {
    request: c.request,
    db: c.env.DB,
    who: String(c.data?.who ?? 'unknown'),
    purge: async () => {
      await (globalThis as any).caches?.default?.delete(new Request(new URL('/api/roadmap', c.request.url).toString()));
    },
  };
}
