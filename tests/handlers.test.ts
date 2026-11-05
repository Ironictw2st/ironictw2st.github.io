import { test } from 'node:test';
import assert from 'node:assert/strict';
import { adminCreate, adminDelete, adminHistory, adminList, adminReorder, adminRestore, adminUpdate } from '../functions/_lib/handlers.ts';
import { makeDb } from './helpers.ts';

const ORIGIN = 'https://190-expanded.com';
function req(method: string, path: string, body?: unknown, headers: Record<string, string> = {}) {
  return new Request(`${ORIGIN}${path}`, {
    method,
    headers: { ...(body !== undefined ? { 'Content-Type': 'application/json' } : {}), ...headers },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
}
const item = (over: Record<string, unknown> = {}) => ({ title: 'T', description: 'd', status: 'next', category: 'Mod', version: '', release_date: '', draft: false, progress: null, link: '', ...over });

function setup() {
  const db = makeDb();
  const ctx = (r: Request) => ({ request: r, db, who: 'me@example.com' });
  return { db, ctx };
}

test('create / list / update / delete round trip, each save writes a history snapshot', async () => {
  const { db, ctx } = setup();
  const created = await adminCreate(ctx(req('POST', '/api/admin/roadmap', item({ title: 'A' }))));
  assert.equal(created.status, 201);
  const id = ((await created.json()) as any).id;
  assert.ok(id > 0);

  let list = (await (await adminList(ctx(req('GET', '/api/admin/roadmap')))).json()) as any;
  assert.equal(list.items.length, 1);

  const upd = await adminUpdate(ctx(req('PUT', `/api/admin/roadmap/${id}`, item({ title: 'A2', status: 'live', draft: true }))), String(id));
  assert.equal(upd.status, 200);
  list = (await (await adminList(ctx(req('GET', '/api/admin/roadmap')))).json()) as any;
  assert.equal(list.items[0].title, 'A2');
  assert.equal(list.items[0].draft, 1);

  assert.equal((await adminDelete(ctx(req('DELETE', `/api/admin/roadmap/${id}`)), String(id))).status, 200);
  assert.equal((await adminDelete(ctx(req('DELETE', `/api/admin/roadmap/${id}`)), String(id))).status, 404);

  const hist = ((await (await adminHistory(ctx(req('GET', '/api/admin/roadmap/history')))).json()) as any).history;
  assert.deepEqual(hist.map((h: any) => h.action).reverse(), ['create', 'update', 'delete']);
  assert.equal(hist[0].saved_by, 'me@example.com');
  db.raw.close();
});

test('invalid input is rejected with 400 and nothing is written', async () => {
  const { db, ctx } = setup();
  for (const body of [item({ status: 'bogus' }), item({ title: '' }), item({ title: 'x'.repeat(81) }), item({ category: "x'); DROP TABLE roadmap_items;--" })]) {
    assert.equal((await adminCreate(ctx(req('POST', '/api/admin/roadmap', body)))).status, 400);
  }
  assert.equal(db.raw.prepare('SELECT COUNT(*) c FROM roadmap_items').get()!.c, 0);
  assert.equal(db.raw.prepare('SELECT COUNT(*) c FROM roadmap_history').get()!.c, 0);
  db.raw.close();
});

test('SQL-injection text is stored literally (parameterised queries)', async () => {
  const { db, ctx } = setup();
  const nasty = "Robert'); DROP TABLE roadmap_items;--";
  assert.equal((await adminCreate(ctx(req('POST', '/api/admin/roadmap', item({ title: nasty }))))).status, 201);
  assert.equal(db.raw.prepare('SELECT title FROM roadmap_items').get()!.title, nasty);
  // a hostile id never reaches SQL
  assert.equal((await adminUpdate(ctx(req('PUT', '/x', item())), '1 OR 1=1')).status, 400);
  assert.equal((await adminDelete(ctx(req('DELETE', '/x')), '1; DROP TABLE roadmap_items')).status, 400);
  db.raw.close();
});

test('CSRF-shaped requests are refused', async () => {
  const { db, ctx } = setup();
  // form post (no JSON content type)
  const form = new Request(`${ORIGIN}/api/admin/roadmap`, { method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body: 'title=x&status=next&category=Mod' });
  assert.equal((await adminCreate(ctx(form))).status, 400);
  // text/plain "simple request" trick
  const plain = new Request(`${ORIGIN}/api/admin/roadmap`, { method: 'POST', headers: { 'Content-Type': 'text/plain' }, body: JSON.stringify(item()) });
  assert.equal((await adminCreate(ctx(plain))).status, 400);
  // cross-origin JSON
  assert.equal((await adminCreate(ctx(req('POST', '/api/admin/roadmap', item(), { Origin: 'https://evil.example' })))).status, 403);
  assert.equal((await adminCreate(ctx(req('POST', '/api/admin/roadmap', item(), { 'Sec-Fetch-Site': 'cross-site' })))).status, 403);
  assert.equal((await adminDelete(ctx(req('DELETE', '/api/admin/roadmap/1', undefined, { Origin: 'https://evil.example' })), '1')).status, 403);
  // same origin is fine
  assert.equal((await adminCreate(ctx(req('POST', '/api/admin/roadmap', item(), { Origin: ORIGIN, 'Sec-Fetch-Site': 'same-origin' })))).status, 201);
  // oversize body
  assert.equal((await adminCreate(ctx(req('POST', '/api/admin/roadmap', item({ description: 'x'.repeat(70000) }))))).status, 400);
  assert.equal(db.raw.prepare('SELECT COUNT(*) c FROM roadmap_items').get()!.c, 1);
  db.raw.close();
});

test('reorder moves items between statuses and rejects id mismatches', async () => {
  const { db, ctx } = setup();
  const ids: number[] = [];
  for (const t of ['A', 'B', 'C']) ids.push(((await (await adminCreate(ctx(req('POST', '/x', item({ title: t }))))).json()) as any).id);
  const ok = await adminReorder(ctx(req('POST', '/x', { order: [{ id: ids[2], status: 'live' }, { id: ids[0], status: 'next' }, { id: ids[1], status: 'next' }] })));
  assert.equal(ok.status, 200);
  const rows = db.raw.prepare('SELECT title, status, sort_order FROM roadmap_items ORDER BY status, sort_order').all() as any[];
  assert.deepEqual(rows.map((r) => `${r.status}:${r.title}`), ['live:C', 'next:A', 'next:B']);
  // missing an id / unknown id
  assert.equal((await adminReorder(ctx(req('POST', '/x', { order: [{ id: ids[0], status: 'live' }] })))).status, 400);
  assert.equal((await adminReorder(ctx(req('POST', '/x', { order: [{ id: 999, status: 'live' }, { id: ids[0], status: 'live' }, { id: ids[1], status: 'live' }] })))).status, 400);
  db.raw.close();
});

test('restore previous version, and the restore itself is undoable', async () => {
  const { db, ctx } = setup();
  const a = ((await (await adminCreate(ctx(req('POST', '/x', item({ title: 'A' }))))).json()) as any).id;
  await adminCreate(ctx(req('POST', '/x', item({ title: 'B' }))));
  const histAfterB = (db.raw.prepare('SELECT id FROM roadmap_history ORDER BY id DESC LIMIT 1').get() as any).id; // snapshot with A and B
  await adminDelete(ctx(req('DELETE', `/x/${a}`)), String(a));
  await adminUpdate(ctx(req('PUT', '/x', item({ title: 'B edited' }))), String((db.raw.prepare('SELECT id FROM roadmap_items').get() as any).id));
  assert.deepEqual((db.raw.prepare('SELECT title FROM roadmap_items').all() as any[]).map((r) => r.title), ['B edited']);

  assert.equal((await adminRestore(ctx(req('POST', '/x', { history_id: histAfterB })))).status, 200);
  assert.deepEqual((db.raw.prepare('SELECT title FROM roadmap_items ORDER BY id').all() as any[]).map((r) => r.title), ['A', 'B']);
  const last = db.raw.prepare('SELECT action, summary FROM roadmap_history ORDER BY id DESC LIMIT 1').get() as any;
  assert.equal(last.action, 'restore');

  assert.equal((await adminRestore(ctx(req('POST', '/x', { history_id: 99999 })))).status, 404);
  assert.equal((await adminRestore(ctx(req('POST', '/x', { history_id: 'abc' })))).status, 400);
  db.raw.close();
});

test('history is capped', async () => {
  const { db, ctx } = setup();
  for (let i = 0; i < 205; i++) await adminCreate(ctx(req('POST', '/x', item({ title: `T${i}` }))));
  assert.equal((db.raw.prepare('SELECT COUNT(*) c FROM roadmap_history').get() as any).c, 200);
  db.raw.close();
});

test('progress and link round-trip; restore of an older snapshot without them still works', async () => {
  const { db, ctx } = setup();
  const id = ((await (await adminCreate(ctx(req('POST', '/x', item({ title: 'P', progress: 60, link: 'total_war/changes.html' }))))).json()) as any).id;
  const row = db.raw.prepare('SELECT progress, link FROM roadmap_items WHERE id = ?').get(id) as any;
  assert.equal(row.progress, 60);
  assert.equal(row.link, '/total_war/changes.html');
  assert.equal((await adminCreate(ctx(req('POST', '/x', item({ link: 'https://evil.example' }))))).status, 400);
  assert.equal((await adminCreate(ctx(req('POST', '/x', item({ progress: 120 }))))).status, 400);

  // a snapshot written before v2 has no progress/link keys
  const old = JSON.stringify([{ id: 99, title: 'Old', description: '', status: 'idea', category: 'Wiki', sort_order: 10, version: '', release_date: '', draft: 0, updated_at: 'x' }]);
  db.raw.prepare("INSERT INTO roadmap_history (saved_at, saved_by, action, summary, snapshot) VALUES ('t', 'x', 'update', 'old', ?)").run(old);
  const hid = (db.raw.prepare('SELECT MAX(id) m FROM roadmap_history').get() as any).m;
  assert.equal((await adminRestore(ctx(req('POST', '/x', { history_id: hid })))).status, 200);
  const r = db.raw.prepare('SELECT title, progress, link FROM roadmap_items').get() as any;
  assert.deepEqual({ ...r }, { title: 'Old', progress: null, link: '' });
  db.raw.close();
});
