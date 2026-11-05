// Every /admin/* page request must carry a valid Cloudflare Access token for this application.
import { withAccess } from '../_lib/guard.ts';
import type { Env } from '../_lib/types.ts';

const CSP = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; font-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'";

export const onRequest = async (ctx: { request: Request; env: Env; next: () => Promise<Response> }): Promise<Response> =>
  withAccess(ctx.request, ctx.env, async () => {
    const res = await ctx.next();
    const out = new Response(res.body, res);
    out.headers.set('Cache-Control', 'no-store');
    out.headers.set('X-Robots-Tag', 'noindex, nofollow');
    out.headers.set('Content-Security-Policy', CSP);
    return out;
  });
