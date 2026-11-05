// Admin handlers as plain functions so tests can call them with a fake D1 (no Workers runtime).
import { createItem, deleteItem, listHistory, listItems, reorderItems, restoreSnapshot, updateItem } from './roadmap_db.ts';
import { assertSameSite, errorResponse, json, readJsonBody } from './http.ts';
import { parseId, parseItem, parseReorder, ValidationError } from './validate.ts';
import type { D1Like } from './types.ts';

export interface Ctx { request: Request; db: D1Like; who: string; purge?: () => Promise<void> }

async function purged(c: Ctx, res: Response): Promise<Response> {
  try { await c.purge?.(); } catch { /* best effort */ }
  return res;
}

export async function adminList(c: Ctx): Promise<Response> {
  try { return json({ items: await listItems(c.db) }); } catch (e) { return errorResponse(e); }
}

export async function adminCreate(c: Ctx): Promise<Response> {
  try {
    const item = parseItem(await readJsonBody(c.request));
    const id = await createItem(c.db, item, c.who);
    return purged(c, json({ ok: true, id }, 201));
  } catch (e) { return errorResponse(e); }
}

export async function adminUpdate(c: Ctx, rawId: string): Promise<Response> {
  try {
    const id = parseId(rawId);
    const item = parseItem(await readJsonBody(c.request));
    if (!(await updateItem(c.db, id, item, c.who))) return json({ error: 'Not found' }, 404);
    return purged(c, json({ ok: true }));
  } catch (e) { return errorResponse(e); }
}

export async function adminDelete(c: Ctx, rawId: string): Promise<Response> {
  try {
    const id = parseId(rawId);
    assertSameSite(c.request); // DELETE carries no body, but the same-site checks still apply
    if (!(await deleteItem(c.db, id, c.who))) return json({ error: 'Not found' }, 404);
    return purged(c, json({ ok: true }));
  } catch (e) { return errorResponse(e); }
}

export async function adminReorder(c: Ctx): Promise<Response> {
  try {
    const order = parseReorder(await readJsonBody(c.request));
    if (!(await reorderItems(c.db, order, c.who))) throw new ValidationError('order', 'order must list every item exactly once');
    return purged(c, json({ ok: true }));
  } catch (e) { return errorResponse(e); }
}

export async function adminHistory(c: Ctx): Promise<Response> {
  try { return json({ history: await listHistory(c.db, 50) }); } catch (e) { return errorResponse(e); }
}

export async function adminRestore(c: Ctx): Promise<Response> {
  try {
    const body = (await readJsonBody(c.request)) as Record<string, unknown>;
    const id = parseId(body?.history_id, 'history_id');
    if (!(await restoreSnapshot(c.db, id, c.who))) return json({ error: 'Version not found' }, 404);
    return purged(c, json({ ok: true }));
  } catch (e) { return errorResponse(e); }
}
