// Slim release list for the roadmap timeline, built from the generated changelog data.
// total_war/data/changelog.js (197 KB) -> total_war/data/releases.json (a few KB: major releases only).
// Run after generate_data/fetch_changelog.py; the deploy workflow runs it too.
import { readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import vm from 'node:vm';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const src = readFileSync(join(root, 'total_war', 'data', 'changelog.js'), 'utf8').replace(/\bconst CHANGELOG_DATA\b/, 'var CHANGELOG_DATA');
const ctx = {};
vm.createContext(ctx);
vm.runInContext(src, ctx);

const plain = (s) => String(s ?? '').replace(/<[^>]*>/g, ' ').replace(/&amp;/g, '&').replace(/\s+/g, ' ').trim();
const releases = ctx.CHANGELOG_DATA
  .filter((e) => e.kind === 'release')
  .map((e) => ({
    date: e.date,
    display_date: e.display_date,
    title: plain(e.title) || `Update of ${e.display_date}`,
    packs: e.packs,
  }))
  .sort((a, b) => a.date.localeCompare(b.date));

writeFileSync(join(root, 'total_war', 'data', 'releases.json'), JSON.stringify({ releases }, null, 2) + '\n');
console.log(`releases: ${releases.length} major releases -> total_war/data/releases.json`);
