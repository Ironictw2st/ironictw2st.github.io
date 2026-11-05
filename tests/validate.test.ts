import { test } from 'node:test';
import assert from 'node:assert/strict';
import { parseItem, parseId, parseLink, parseReorder, ValidationError } from '../functions/_lib/validate.ts';

const ok = { title: 'Siege AI', description: 'In progress.', status: 'next', category: 'Mod', version: '1105', release_date: '2026-11-05', draft: true };
const bad = (v: unknown) => assert.throws(() => parseItem(v), ValidationError);

test('accepts a valid item and normalises it', () => {
  const r = parseItem({ ...ok, title: '  Siege AI  ' });
  assert.equal(r.title, 'Siege AI');
  assert.equal(r.draft, 1);
  assert.equal(parseItem({ title: 'x', status: 'idea', category: 'Wiki' }).description, '');
});

test('length limits', () => {
  bad({ ...ok, title: '' });
  bad({ ...ok, title: '   ' });
  bad({ ...ok, title: 'x'.repeat(81) });
  parseItem({ ...ok, title: 'x'.repeat(80) });
  bad({ ...ok, description: 'x'.repeat(281) });
  bad({ ...ok, version: 'x'.repeat(21) });
});

test('enums', () => {
  for (const status of ['done', 'LIVE', '', null, 5, 'live; DROP TABLE roadmap_items']) bad({ ...ok, status });
  for (const category of ['mod', 'Other', '', null, "Mod' OR 1=1 --"]) bad({ ...ok, category });
});

test('dates', () => {
  for (const d of ['2026', '2026-11', '2026-11-05', '']) parseItem({ ...ok, release_date: d });
  for (const d of ['11/05/2026', 'tomorrow', '2026-1-5', '20261105', '2026-11-05T00']) bad({ ...ok, release_date: d });
});

test('types and shapes', () => {
  for (const v of [null, undefined, 'x', 5, [], [ok]]) bad(v);
  bad({ ...ok, title: 5 });
  bad({ ...ok, title: ['a'] });
  bad({ ...ok, draft: 'yes' });
});

test('control characters and newlines in single-line fields', () => {
  bad({ ...ok, title: 'a\u0000b' });
  bad({ ...ok, title: 'a\nb' });
  bad({ ...ok, version: 'a\tb' });
  parseItem({ ...ok, description: 'two\nlines' }); // description may be multi-line
});

test('markup is stored as text, not rejected (escaping happens on render)', () => {
  assert.equal(parseItem({ ...ok, title: '<img src=x onerror=alert(1)>' }).title, '<img src=x onerror=alert(1)>');
});

test('ids', () => {
  assert.equal(parseId('42'), 42);
  assert.equal(parseId(7), 7);
  for (const v of ['0', '-1', '1.5', '1e3', 'abc', '', null, undefined, '99999999999999999999', '1 OR 1=1']) assert.throws(() => parseId(v), ValidationError);
});

test('reorder payload', () => {
  assert.deepEqual(parseReorder({ order: [{ id: 1, status: 'live' }, { id: '2', status: 'idea' }] }), [{ id: 1, status: 'live' }, { id: 2, status: 'idea' }]);
  for (const v of [null, {}, { order: [] }, { order: 'x' }, { order: [{ id: 1, status: 'live' }, { id: 1, status: 'next' }] }, { order: [{ id: 1, status: 'bogus' }] }, { order: [null] }]) {
    assert.throws(() => parseReorder(v), ValidationError);
  }
  assert.throws(() => parseReorder({ order: Array.from({ length: 501 }, (_, i) => ({ id: i + 1, status: 'live' })) }), ValidationError);
});

test('progress is a whole number 0-100 or empty', () => {
  assert.equal(parseItem({ ...ok, progress: 40 }).progress, 40);
  assert.equal(parseItem({ ...ok, progress: '75' }).progress, 75);
  assert.equal(parseItem({ ...ok, progress: 0 }).progress, 0);
  for (const v of [undefined, null, '']) assert.equal(parseItem({ ...ok, progress: v }).progress, null);
  for (const v of [-1, 101, 4.5, 'abc', '1e2', true, [], {}]) bad({ ...ok, progress: v });
});

test('links stay inside the wiki', () => {
  assert.equal(parseLink('total_war/changes.html'), '/total_war/changes.html');
  assert.equal(parseLink('/total_war/map.html#region-12'), '/total_war/map.html#region-12');
  assert.equal(parseLink('/tools/mod-manager.html'), '/tools/mod-manager.html');
  assert.equal(parseLink(''), '');
  for (const v of ['https://evil.example/x', '//evil.example/x', 'javascript:alert(1)', '/total_war/../admin/roadmap', '/admin/roadmap', '/total_war/', 'total_war//x', '/total_war/a b', 5, '/total_war/' + 'x'.repeat(200)]) {
    assert.throws(() => parseLink(v), ValidationError);
  }
});
