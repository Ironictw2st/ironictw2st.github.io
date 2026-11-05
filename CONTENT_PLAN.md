# Next content for the wiki (plan, 5 Nov 2026)

Chosen by the user: Guides, whole-wiki search, region pages, mechanics pages, and (later) reader voting. Done already: Changes + Changelog merged into one "Changes" section; roadmap v2 (timeline, just shipped, progress, links).

Order below is by value for effort. Each step ships on its own.

## 1. Whole-wiki search (about a day)
- One search box in the nav, results grouped by Characters, Factions, Regions, Changes, Guides, Roadmap.
- Build step: `scripts/build_search_index.mjs` writes `total_war/data/search_index.json` (title, kind, url, a short text) from `characters.js`, `factions.js`, `map_regions.js`, `changes.js` section titles, `roadmap.json` and the guide pages. Keep it small (names + one line each, about 300 KB gzipped to 60 KB), loaded only when the box is focused.
- Client: lowercase, accent-insensitive prefix + substring match, Chinese names included (the data has `display_name_alt`), keyboard navigation. No library.
- The Changes page already has its own in-page search; leave it.

## 2. Guides (content, not code)
- Template: one HTML file per guide under `total_war/guides/`, short intro, numbered steps, screenshots from the game.
- Start list (from the changelog and roadmap): Nomadic Hordes, Ma Teng's Stables, Governor Edicts, Trial by Combat, The Black Market, Imperial Favour, Vassal Contracts (once shipped), Korea. Wording follows the mod's `STYLE.md` (one plain point per sentence, British spelling).
- The existing `guides.html` becomes the index (cards per guide). Needs the user's or the mod team's text; I can draft from the changelog notes and the mod's loc files for review.

## 3. Region pages (about two days)
- Data already in `map_regions.js` and `map_recruitment.js` (owner at start, recruitment hub, units). Generate `region.html?key=` the same way `character.html` works, linked from the map's side panel and from faction pages ("Starting regions").
- Add from the mod tables: settlement buildings and slots, resources, province membership, notes from the map round. Needs one new generator in `generate_data/` (`parse_regions.py`).

## 4. Mechanics pages per faction (content + a small template)
- One page per mechanic (Nomadic Hordes, Ma Teng's Stables, Fei Zhan's Undercity, Zhu Fu, Pan Lin, Liu Pan and so on), linked from the faction page's "Unique features" cards and from roadmap items (the roadmap `link` field already supports this).
- Same template as guides; these are the deeper "how it works" pages with numbers.

## 5. Reader voting on the roadmap (needs Discord login)
- Depends on the login and forms work in MIGRATION.md step 10 (Discord OAuth, sessions, D1). Then: a `roadmap_votes(user_id, item_id)` table, a vote button on each card, counts on the public page, one vote per Discord account per item, rate-limited.
- Not started; do it after the site is live on Cloudflare.

## Also pending (from REVIEW.md Phase 1)
- WebP thumbnails and splitting `skill_trees.js`: the biggest real-user speed win.
