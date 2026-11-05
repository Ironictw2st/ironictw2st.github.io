import { authorise, AccessDenied } from './access.ts';
import type { Identity, KeyFetcher } from './access.ts';
import { errorResponse } from './http.ts';
import type { Env } from './types.ts';

/** Run `fn` only for an authorised caller. Used by the /admin and /api/admin middleware. */
export async function withAccess(
  request: Request, env: Env, fn: (who: Identity) => Promise<Response>,
  opts: { fetchKeys?: KeyFetcher; now?: number } = {},
): Promise<Response> {
  let who: Identity;
  try { who = await authorise(request, env, opts); } catch (e) {
    if (e instanceof AccessDenied) return errorResponse(e);
    return errorResponse(new AccessDenied('Access check failed', 403));
  }
  return fn(who);
}
