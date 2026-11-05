// Every /api/admin/* call (reads and writes) must carry a valid Cloudflare Access token. The identity is
// passed to the handlers through ctx.data.who so history rows record who saved.
import { withAccess } from '../../_lib/guard.ts';
import type { Env } from '../../_lib/types.ts';

export const onRequest = async (ctx: { request: Request; env: Env; data: Record<string, unknown>; next: () => Promise<Response> }): Promise<Response> =>
  withAccess(ctx.request, ctx.env, async (who) => {
    ctx.data.who = who.email;
    return ctx.next();
  });
