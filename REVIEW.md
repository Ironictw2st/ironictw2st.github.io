# 190 Expanded wiki — site review (5 Nov 2026)

Repo `Z:\Claude\GitHubPage` @ main 050f3c0, live at 190-expanded.com (GitHub Pages, CNAME). Static site, no build step on deploy: the Python generators in `generate_data/` write `total_war/data/*.js` and those are committed.

## Page inventory

| Page | Size | Data JS it loads | Inline CSS / JS lines |
|---|---|---|---|
| `index.html` | 6 KB | stats.js | 0 / 6 |
| `total_war/characters.html` | 52 KB | characters.js (1.7 MB) | 458 / 627 |
| `total_war/character.html` | 76 KB | characters, character_details (4.2 MB), character_bios (+_new), family_tree (1.9 MB), traits, **skill_trees (16 MB)**, factions (3.3 MB) | 1368 / 981 |
| `total_war/factions.html` | 15 KB | characters, factions | 74 / 118 |
| `total_war/faction.html` | 24 KB | characters, character_details, factions | 132 / 219 |
| `total_war/map.html` | 37 KB | map_regions, map_recruitment, factions; Leaflet from unpkg | 162 / 458 |
| `total_war/changelog.html` | 17 KB | changelog.js | 123 / 153 |
| `total_war/changes.html` | 15 KB | changes.js (+battle/campaign split files) | 153 / 151 |
| `total_war/roadmap.html` | 19 KB | factions, roadmap | 177 / 108 |
| `total_war/guides.html` | 3 KB | — (under construction) | 0 / 0 |
| `tools/index, mod-manager, script-extender, se-api.html` | 8–16 KB | tools.js, se_docs.js | `tools/styles/tools.css` shared |

Plus `total_war/index.html` (redirect stub), `sitemap.xml`, `robots.txt`.

## How data reaches the templates

`sync_from_mod.py` (copy DB/loc/portraits from `Beta\2_Char`) → `parse_tw3k_db.py` → `parse_skill_trees.py` → `parse_factions.py` → `bios_report.py` → `audit_site.py`. Separate: `fetch_changelog.py` (Steam scrape), `fetch_tool_docs.py` (script-extender docs + GitHub releases), `build_changes/map/recruitment.py`. Output is plain `const X = [...]` JS files loaded with `<script src>`; each page renders client-side with its own inline script. **Nothing in the generators emits HTML**, so a restyle only touches CSS/templates, never the generators.

## CSS / JS structure

- One shared `tw3k.css` (tokens + header/nav/cards/footer) and `tools/styles/tools.css`; three `family_tree_*.css` for the tree.
- ~2,600 lines of per-page inline `<style>` and ~2,800 lines of inline `<script>`. `character.html` alone is 1,368 CSS + 981 JS lines. No shared JS, no bundler, no framework.
- Tokens exist (`--bg-*`, `--text-*`, `--gold-*`, `--title-cream`) and are used ~450 times, **but ~330 colours are hard-coded** in inline styles (`#252530` ×54, `#303035` ×35, many `rgba(255,255,255,.0x)` overlays). That is why a dark→light retheme cannot be done by changing `:root` alone.
- Header/nav/footer markup is copy-pasted into every page (9 nav links ×14 files); a nav change = 14 edits.
- Google Fonts `@import` for Cinzel (render-blocking third-party request, privacy/GDPR concern). Leaflet from unpkg.

## Performance

- Repo 621 MB; `total_war/data/images` 472 MB (db portraits 430 MB, 739 files, **avg 593 KB, max 1.3 MB, 725×1257 PNG**), `data/UI` 68 MB. GitHub Pages' soft limit is 1 GB and 100 GB/month bandwidth, so the site is already at ~60% of the size ceiling.
- Character page loads **one full-size portrait PNG (0.6–1.3 MB)** plus ~8 JS data files ≈ **27 MB of JS** (skill_trees 16 MB, character_details 4.2, factions 3.3, family_tree 1.9, characters 1.7). The characters *list* only needs characters.js (1.7 MB) but parses all 1,650 records to render cards.
- Faction page shows the leader at ~64 px but loads the full portrait; family-tree nodes do the same for up to 25 relatives (up to ~15 MB of PNG for a 25-member tree).
- No `loading="lazy"`, no WebP/AVIF, no thumbnails, no cache-busting beyond `asset_version.py`.
- Cheapest wins: generate 160 px WebP thumbnails (≈8 KB each) for list/tree/faction use (−95% of image bytes), split `skill_trees.js` per character or per skill-set (only ~1 tree needed per page), gzip/brotli is already applied by GitHub Pages to JS.

## Accessibility

- Dark theme had muted text `#706a60` on `#0a0a0c` fine, but many tag/pill colours (pale blue `#8ab4f8`, lilac `#cc99ff`, pink) were small-text low contrast; the redesign darkens them for the paper ground.
- Only 16 `aria-*`/`role` attributes across all pages; the filter chips, collapsible factions (`div.category-header` with click handler, no `button`/`aria-expanded`), tab bar on the character page (`.tab-btn` without `role=tablist`) and the sortable lists are not keyboard/screen-reader operable as written.
- One `alt=` on the characters page; portraits are CSS backgrounds or JS-built `<img>`s without alt.
- No visible focus styles in the old CSS (added `:focus-visible` in the prototype); no `prefers-reduced-motion` handling (added).
- Fixed animation delay on faction cards (opacity 0 → 1) hides content until JS/animation runs.

## Mobile

Viewport meta is present on all pages. Layouts mostly collapse acceptably (grids use `auto-fit/minmax`), the nav wraps to two rows. Weak spots: the character page's three-column hero, the family tree (needs pinch/pan, currently Ctrl+scroll hint), tables on `changes.html`, and the 16 MB skill-tree payload on cellular.

## Links and data health (`audit_site.py`, run 5 Nov)

73 findings, none breaking pages: 15 characters without a portrait (Bo Cai, Han Zhong, Gao You, …), family_tree.js references 4 template keys that no longer exist (`shamoke_sister_placeholder`, `ironic_template_romance_zhang_gong/ma_chun_f/ma_ya_f`), 183 characters without a hand-written bio (182 drafted). No orphan data files. External links (Steam ×3, Nexus, Discord, GitHub) are plain `target=_blank rel=noopener`; not live-checked (no network crawl done).

## Other observations

- `guides.html` is an "under construction" stub linked from the main nav.
- `character.html?key=` / `faction.html?key=` single-template pages mean no per-character URL for search engines/Discord embeds (no OG tags). Worth adding when moving to a host that can do edge rewrites.
- `sitemap.xml` lists only the top-level pages.

## Redesign prototype (branch `redesign`, worktree `Z:\Claude\GitHubPage_redesign`)

Approach: the legacy token names stay but now hold paper/ink values (`--title-cream` = ink, `--gold-light` = dark bronze…), so every inline rule that uses a token flips automatically; ~330 hard-coded dark colours were remapped by script to line/ink/paper tokens; the shared chrome (header, nav, cards, footer) was rewritten. Generators and page JS are untouched.

Look: parchment ground with procedural paper grain (SVG noise, no images), ink text, vermilion seal chops (CSS squares with a brush character) on the home cards, lacquer-black header/nav/footer with a bronze double rule, hung-scroll rods on home cards, a brush-stroke rule under titles. Fonts self-hosted in `total_war/fonts/` (all SIL OFL 1.1, licences alongside): **Cinzel** (headings), **Source Serif 4** (body), **Ma Shan Zheng** (brush face, subset to 46 CJK glyphs = 16 KB). No AI art; the mod's real UI art (faction flags, feature icons, portraits) is shown as-is on paper.

Done and screenshotted (1440 + 390 wide in `shots/`): home, characters list, character page, faction page, changelog. Map checked at 1440 (renders well; the black fringe is the map image's own transparent edge). Restyled by the same CSS but not yet visually checked: factions list, roadmap, changes, tools/*. Known leftovers: skill-tree widget on the character page (Skills tab) not reviewed; family-tree node cards intentionally stay dark (they sit over portraits).
