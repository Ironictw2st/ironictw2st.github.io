// Public: GET /api/roadmap. Cached at the edge; falls back to the static roadmap.json built at deploy.
import { listItems } from '../_lib/roadmap_db.ts';
import { json } from '../_lib/http.ts';
import type { Env } from '../_lib/types.ts';

const CACHE_HEADERS = { 'Cache-Control': 'public, max-age=30, s-maxage=120, stale-while-revalidate=600' };

export const onRequestGet = async (ctx: { request: Request; env: Env; waitUntil?: (p: Promise<unknown>) => void }): Promise<Response> => {
  const { request, env } = ctx;
  const cache = (globalThis as any).caches?.default as Cache | undefined;
  const key = new Request(new URL('/api/roadmap', request.url).toString());
  try {
    const hit = cache ? await cache.match(key) : undefined;
    if (hit) return hit;
  } catch { /* cache is best effort */ }

  try {
    const items = await listItems(env.DB);
    const updated = items.reduce((m, i) => (i.updated_at > m ? i.updated_at : m), '');
    const res = json({ source: 'live', updated_at: updated || null, items }, 200, CACHE_HEADERS);
    if (cache && ctx.waitUntil) ctx.waitUntil(cache.put(key, res.clone()).catch(() => {}));
    return res;
  } catch {
    // D1 unavailable: serve the static snapshot that shipped with the last deploy
    try {
      const fb = await env.ASSETS.fetch(new URL('/total_war/data/roadmap.json', request.url).toString());
      if (fb.ok) {
        const data = (await fb.json()) as Record<string, unknown>;
        return json({ ...data, source: 'static' }, 200, { 'Cache-Control': 'public, max-age=30' });
      }
    } catch { /* fall through */ }
    return json({ error: 'Roadmap unavailable' }, 503);
  }
};
