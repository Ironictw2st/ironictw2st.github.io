// Assemble ./dist for `wrangler pages deploy dist`: the static wiki exactly as it is in the repo, plus the
// Pages config files. Dev-only things (functions/, tests/, node_modules, db/, scripts/, generate_data/) are not published;
// Pages compiles functions/ from the project root separately.
import { cpSync, existsSync, mkdirSync, rmSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const dist = join(root, 'dist');
rmSync(dist, { recursive: true, force: true });
mkdirSync(dist, { recursive: true });

// generator output that pages no longer load (replaced by the split files); keep them out of the deploy
// the 430 MB of full-size portrait PNGs are not referenced by any page any more (WebP variants are served instead)
const SKIP = ['total_war/data/skill_trees.js', 'total_war/data/character_details.js', 'total_war/data/images/db'];
const publish = ['index.html', 'robots.txt', 'sitemap.xml', 'CNAME', 'total_war', 'tools', 'changes', 'admin', '_headers', '_redirects', '_routes.json'];
for (const p of publish) {
  const from = join(root, p);
  if (existsSync(from)) cpSync(from, join(dist, p), { recursive: true, filter: (src) => { const s = src.split('\\').join('/'); return !SKIP.some((x) => s.endsWith('/' + x)); } });
}
console.log('dist ready:', publish.filter((p) => existsSync(join(root, p))).join(', '));
