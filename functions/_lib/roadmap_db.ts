// All D1 access for the roadmap. Every query is parameterised (bind()); no string-built SQL with user data.
import type { D1Like } from './types.ts';
import type { ItemInput, ReorderEntry } from './validate.ts';

export interface RoadmapItem extends ItemInput { id: number; sort_order: number; updated_at: string }
export const HISTORY_KEEP = 200;
const COLS = 'id, title, description, status, category, sort_order, version, release_date, draft, progress, link, updated_at';

export async function listItems(db: D1Like): Promise<RoadmapItem[]> {
  const r = await db.prepare(`SELECT ${COLS} FROM roadmap_items ORDER BY CASE status WHEN 'live' THEN 0 WHEN 'next' THEN 1 WHEN 'planned' THEN 2 ELSE 3 END, sort_order, id`).all<RoadmapItem>();
  return r.results ?? [];
}

function snapshotStmt(db: D1Like, by: string, action: string, summary: string, now: string) {
  // snapshot = the table contents AFTER the preceding statements in the same batch
  return db.prepare(
    `INSERT INTO roadmap_history (saved_at, saved_by, action, summary, snapshot)
     SELECT ?, ?, ?, ?, COALESCE(json_group_array(json_object(
       'id', id, 'title', title, 'description', description, 'status', status, 'category', category,
       'sort_order', sort_order, 'version', version, 'release_date', release_date, 'draft', draft, 'progress', progress, 'link', link, 'updated_at', updated_at)), '[]')
     FROM (SELECT * FROM roadmap_items ORDER BY id)`,
  ).bind(now, by, action, summary.slice(0, 200));
}

function pruneStmt(db: D1Like) {
  return db.prepare(`DELETE FROM roadmap_history WHERE id NOT IN (SELECT id FROM roadmap_history ORDER BY id DESC LIMIT ${HISTORY_KEEP})`);
}

export async function createItem(db: D1Like, it: ItemInput, by: string, now = new Date().toISOString()): Promise<number | null> {
  const [ins] = await db.batch([
    db.prepare(
      `INSERT INTO roadmap_items (title, description, status, category, sort_order, version, release_date, draft, progress, link, updated_at)
       VALUES (?, ?, ?, ?, COALESCE((SELECT MAX(sort_order) + 10 FROM roadmap_items WHERE status = ?), 10), ?, ?, ?, ?, ?, ?)`,
    ).bind(it.title, it.description, it.status, it.category, it.status, it.version, it.release_date, it.draft, it.progress, it.link, now),
    snapshotStmt(db, by, 'create', `Added "${it.title}"`, now),
    pruneStmt(db),
  ]);
  const id = (ins.meta as { last_row_id?: number } | undefined)?.last_row_id;
  return typeof id === 'number' ? id : null;
}

/** Returns false when the id does not exist. */
export async function updateItem(db: D1Like, id: number, it: ItemInput, by: string, now = new Date().toISOString()): Promise<boolean> {
  const exists = await db.prepare('SELECT id FROM roadmap_items WHERE id = ?').bind(id).first();
  if (!exists) return false;
  await db.batch([
    db.prepare(
      `UPDATE roadmap_items SET title=?, description=?, status=?, category=?, version=?, release_date=?, draft=?, progress=?, link=?, updated_at=? WHERE id=?`,
    ).bind(it.title, it.description, it.status, it.category, it.version, it.release_date, it.draft, it.progress, it.link, now, id),
    snapshotStmt(db, by, 'update', `Edited "${it.title}"`, now),
    pruneStmt(db),
  ]);
  return true;
}

export async function deleteItem(db: D1Like, id: number, by: string, now = new Date().toISOString()): Promise<boolean> {
  const row = await db.prepare('SELECT title FROM roadmap_items WHERE id = ?').bind(id).first<{ title: string }>();
  if (!row) return false;
  await db.batch([
    db.prepare('DELETE FROM roadmap_items WHERE id = ?').bind(id),
    snapshotStmt(db, by, 'delete', `Deleted "${row.title}"`, now),
    pruneStmt(db),
  ]);
  return true;
}

/** order = every item, in final order, with its (possibly new) status. Returns null if ids do not match the table exactly. */
export async function reorderItems(db: D1Like, order: ReorderEntry[], by: string, now = new Date().toISOString()): Promise<boolean> {
  const existing = await db.prepare('SELECT id FROM roadmap_items').all<{ id: number }>();
  const have = new Set((existing.results ?? []).map((r) => r.id));
  if (have.size !== order.length || !order.every((o) => have.has(o.id))) return false;
  const perStatus: Record<string, number> = {};
  const stmts = order.map((o) => {
    perStatus[o.status] = (perStatus[o.status] ?? 0) + 10;
    return db.prepare('UPDATE roadmap_items SET status=?, sort_order=?, updated_at=? WHERE id=?').bind(o.status, perStatus[o.status], now, o.id);
  });
  await db.batch([...stmts, snapshotStmt(db, by, 'reorder', 'Reordered / moved items', now), pruneStmt(db)]);
  return true;
}

export interface HistoryRow { id: number; saved_at: string; saved_by: string; action: string; summary: string }

export async function listHistory(db: D1Like, limit = 50): Promise<HistoryRow[]> {
  const n = Math.max(1, Math.min(HISTORY_KEEP, Math.floor(limit)));
  const r = await db.prepare('SELECT id, saved_at, saved_by, action, summary FROM roadmap_history ORDER BY id DESC LIMIT ?').bind(n).all<HistoryRow>();
  return r.results ?? [];
}

/** Replace the table with a stored snapshot. The restore itself becomes a new history row (so it can be undone). */
export async function restoreSnapshot(db: D1Like, historyId: number, by: string, now = new Date().toISOString()): Promise<boolean> {
  const row = await db.prepare('SELECT snapshot, saved_at FROM roadmap_history WHERE id = ?').bind(historyId).first<{ snapshot: string; saved_at: string }>();
  if (!row) return false;
  let items: RoadmapItem[];
  try { items = JSON.parse(row.snapshot) as RoadmapItem[]; } catch { return false; }
  if (!Array.isArray(items)) return false;
  const stmts = [db.prepare('DELETE FROM roadmap_items')];
  for (const i of items) {
    stmts.push(db.prepare(
      `INSERT INTO roadmap_items (id, title, description, status, category, sort_order, version, release_date, draft, progress, link, updated_at)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
    ).bind(i.id, i.title, i.description, i.status, i.category, i.sort_order, i.version, i.release_date, i.draft ? 1 : 0, i.progress ?? null, i.link ?? '', now));
  }
  stmts.push(snapshotStmt(db, by, 'restore', `Restored version from ${row.saved_at}`, now), pruneStmt(db));
  await db.batch(stmts);
  return true;
}
