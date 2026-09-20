# generate_data — how the wiki data is built

Everything under `total_war/data/*.js` is generated from the mod source and the vanilla game tables.
Never edit those JS files by hand (except `character_bios.js`, which is hand-written).

## Sources

| What | Path |
|---|---|
| Mod: characters, factions, most db + text | `Z:\Claude\190Expanded\Beta\2_Char` |
| Mod: CEO tables (`ceo_db`), start_pos, region text | `Z:\Claude\190Expanded\Beta\1_Faction` |
| Mod: extra flags | `Z:\Claude\190Expanded\Beta\Flags` |
| Vanilla DB / ceo_db / text / ui dumps | `Z:\Claude\XMLViewer\games\3K` |

Paths are constants at the top of `sync_from_mod.py` and `parse_factions.py`.

## Pipeline (run from this folder, in this order)

```
python sync_from_mod.py        # copies db tables, loc and new portraits into generate_data/ + images
python parse_tw3k_db.py        # -> characters.js, character_details.js, traits.js, titles.js
python parse_skill_trees.py    # -> skill_trees.js
python parse_factions.py       # -> factions.js, stats.js, flags/feature/resource icons
python bios_report.py          # -> bios_missing.md (characters with no biography)
python audit_site.py           # -> audit_report.md (broken refs, counts, orphans)
```

`fetch_changelog.py` is separate: it scrapes the Steam Workshop change notes rather than the mod
tree, so run it only when Steam has been updated.

```
python fetch_changelog.py             # -> total_war/data/changelog.js (74 entries, 3 packs)
python fetch_changelog.py --dry-run   # scrape and report without writing
python fetch_changelog.py --cache-dir DIR   # reuse/save page copies while iterating
```

It reads all three Workshop packs, uses the `<p id>` timestamp for the date (the visible headline
omits the year), merges notes the author cross-posted to several packs, folds same-day silent
pushes into the entry that has notes, and rebuilds each body from an HTML allow-list because
`changelog.html` injects it with `innerHTML`. If Steam changes its layout the script fails loudly
rather than writing an empty file.

`fetch_tool_docs.py` is separate as well: it reads the sibling **script extender** repo on disk
and the GitHub Releases API, not the mod tree. Run it when the script extender docs change or a
new release of either tool is tagged.

```
python fetch_tool_docs.py                  # -> total_war/data/se_docs.js + data/tools.js
python fetch_tool_docs.py --dry-run        # convert and report without writing
python fetch_tool_docs.py --offline        # skip the release API, keep the stored versions
python fetch_tool_docs.py --docs-dir DIR   # convert from somewhere other than Z:\Claude\ScriptExtender\docs
```

`se_docs.js` is `docs/SCRIPTING.md` converted to an HTML allow-list and split into one entry per
heading, which `tools/se-api.html` renders with a sidebar TOC and a search box. The Markdown
converter is hand-rolled against the subset that file actually uses (headings, fenced code, pipe
tables, rules, flat lists, inline code/links/bold) because the pipeline is otherwise stdlib-only.
Emphasis is asterisk-only on purpose: the docs contain hundreds of snake_case identifiers outside
code spans, and underscore emphasis would shred them.

`tools.js` is the latest release of each tool. The download buttons on the tools pages always
point at the repo's permanent `/releases/latest` URL, so a stale `tools.js` only makes the version
label old, never the link wrong. A failed API call keeps the previous values rather than blanking
the file.

The script **reports** upstream staleness (a function documented in prose but missing from the
index, an unverified feature) instead of patching it: `docs/SCRIPTING.md` stays the source of
truth. The one thing it drops is the "current DLL version at the time of writing" line, which goes
stale within days; the page shows the real latest release instead.

`build_map.py` is separate too: it reads the mod's campaign map art rather than the db tables, so
run it only when a region's shape or its turn-one owner changes.

```
python build_map.py                 # -> total_war/data/map_regions.js + data/images/map/campaign_map.webp
python build_map.py --tolerance N   # Douglas-Peucker tolerance in pixels (default 2.0)
python build_map.py --no-image      # re-trace the polygons without re-exporting the base map
```

It decodes `3k_main_lookup.tga` (an uncompressed colour-mapped TGA, one 16-bit palette index per
pixel) into a region-id array, matches each palette colour to a row in `regions_tables`, then traces
the outlines itself: run-length union-find for connected parts, crack following around each part,
enclave detection so a region that wraps another does not swallow it, and Douglas-Peucker to
simplify. `scipy`/`shapely`/`cv2` are not installed, so all of that is hand-rolled here.

Which regions appear is decided by data, not by name: a region is drawn only if it has a row in
`start_pos_regions_tables` for the 190 campaign, which excludes sea and river zones for free.
Owners resolve through `start_pos_factions_tables` (`owning_faction` is a numeric id). Faction
colours come from `faction_banners_tables.primary_hex` where there is a row, otherwise from the
dominant colour of the faction's own flag image, otherwise a generated fallback.

Two header fields in the TGA are wrong and are deliberately ignored, because getting either one
wrong produces a map that still looks plausible:

- **Row order.** The descriptor byte clears bit 5, which per spec means bottom-up. The rows are
  actually top-down; honouring the byte puts Korea in the South China Sea.
- **First entry index.** The header says 18, but a pixel's value indexes the stored colour map
  directly. Adding the offset hands every region the *wrong name* while the shapes stay pixel-perfect
  on the artwork, so nothing looks amiss until you read the labels.

Both are pinned by self-checks that fail the run rather than writing bad data. `check_orientation`
asserts two anchor regions at opposite corners of the map (Liaodong north, Yongchang south) came out
in the right halves. `check_province_adjacency` is the stronger one: a province is a contiguous block
of regions, so every region in a multi-region province must border one of its own province-mates.
The correct mapping scores 99%; the offset-by-18 mapping scores 22%. The run also compares each
traced polygon's area against its mask pixel count, confirms every centroid falls inside its own
region, and lists in `last_run_map.json` any start-position region that produced no shape at all
(none currently do).

`build_recruitment.py` answers "what can I raise here" for the Map page, which paints regions
by their area of recruitment.

```
python build_recruitment.py             # -> total_war/data/map_recruitment.js
python build_recruitment.py --dry-run   # report the joins without writing
```

**The answer is not in the db tables.** It is in the mod's own campaign script,
`2_Char/script/campaign/mod/ui/AOR_recruitment.lua`, which holds `aor_region_groups` (named
region lists - the recruitment hubs, capitals included) and `aor_restrictions_with_groups`
(unit -> the hubs it is confined to). The script's own comment states the rule: a unit in that
table is recruitable ONLY in the regions listed, and a unit absent from it is recruitable
anywhere. `lua_table.py` is a small Lua table-literal reader that lifts those tables out; it
handles only the shapes those scripts use and raises on anything else, so a script that changes
shape fails loudly instead of yielding half a table.

An earlier pass derived this from the db instead, walking `start_pos_region_slot_templates` ->
building superchains -> chains -> levels -> `campaign_unit_requirements` ->
`campaign_unit_permission_requirements`. That describes what *unlocks* a unit, but not where it
may be *raised*: it missed every province capital, because the hub building sits on the
secondary slots, and it swept in faction-unique district chains, which put Ma Teng's Qiang units
in Korea. Only the requirement gates (rank, tech) still come from those tables, keyed by unit.

Two limits the page states rather than hides: the restriction table is keyed by subculture and
only `3k_main_chinese` is populated, so these rules bind Han Chinese factions; and
`aor_exemptions` lists units certain factions may raise anywhere regardless, carried through per
faction.

The run reports two classes of problem in the mod's own data rather than silently absorbing
them, because the lua treats an unrecognised name as a literal region key and so does the game:

- **Dangling hub references** - a unit pointing at a hub that does not exist, which therefore
  grants nothing. Currently `ironic_province_yong_qiang` (8 units) and
  `ironic_province_you_standard` (2 units).
- **Ghost region keys** - a region key in a group that is not in the campaign, usually a wrong
  pack prefix. Currently five, all of which have a correctly-prefixed sibling already listed,
  so nothing is lost.

`family_tree/family_extractor.py` is separate and hand-fed (`starter.xlsx` + lua); it is not part of the sync.

## Cache busting (do not remove the `?v=` stamps)

GitHub Pages serves pages with `Cache-Control: max-age=600` and data files with
`max-age=14400`, and neither is configurable. A visitor's HTML therefore refreshes four hours
before the JS it loads does, so any release that changes the **shape** of a data file leaves
them running new HTML against a stale file. That is not hypothetical: renaming
`RECRUIT_SCOPES` to `RECRUIT_ZONES` blanked the live map, because the inline script threw on
the first missing global and no polygons were ever added.

`asset_version.py` fixes it by rewriting `total_war/map.html`'s script tags to
`src="data/<name>?v=<sha1 of the file>"`. A new release is a new URL, so there is nothing
cached to go stale. `build_map.py` and `build_recruitment.py` both call it after writing, and
both stamp the whole list, so either one leaves the page consistent.

Two consequences worth knowing:

- **Generators must be byte-stable.** An unstable output changes the hash on every run and
  invalidates the file for nothing. `fallback_colour()` used `hash()`, which Python salts per
  process, and so gave one faction a new colour every run; it uses `crc32` now.
- **`map.html` is edited by the generators.** Only the `?v=` values, only for the files in
  `MAP_PAGE_ASSETS`. Expect that line to change in a diff after a data run.

The page also refuses to trust half a dataset: it checks the recruitment globals for presence
**and** shape, and falls back to the ownership paint with a visible notice if either fails, so
a mismatch can never blank the map again.

## Layout

- `db/<table>/data__.tsv` — vanilla rows (refreshed by sync when the header matches), then every mod TSV
  for that table. Mod files literally named `data__.tsv` are stored as `data__mod_<pack>.tsv`.
  Files matching `_mtu_*` / `zase_skillset.tsv` come from the MTU companion mod, which is not in `Beta`;
  the sync keeps them untouched (see `PROTECT_PATTERNS`).
- `text/vanilla/` — vanilla loc files the parsers need. `text/mod/<pack>/` — full mirror of the mod's
  text trees. `text/extra/` — hand-kept loc (MTU skill names, salvaged legacy titles). Load order is
  vanilla → mod → extra, later wins.
- `tw3k_common.py` — shared loaders (`load_table`, `load_site_loc`) and text helpers
  (`strip_tw_markup`, `format_effect_line`). All three parsers import from it.
- `faction_categories.json` — which section each faction sits in on the Factions page. Generated on first
  run (seeded from the old hand-written page via `_old_factions_cards.json`), then read-only: edit it to
  move a faction. New factions are appended automatically.
- `factions_report.txt` — data-quality notes from the last faction run (placeholder descriptions, missing
  flags/icons, factions without unique features).
- `characters.js` also carries the Characters page's effect index: `char.attributes` holds the six
  attribute totals summed from the career title plus starting equipment, and `char.effects` holds ids
  into `EFFECT_TYPES`. That index is grouped by effect **label**, not by effect key, because the same
  wording is often delivered by several keys (satisfaction by 8, public order by 4) and a filter
  should find every character with the effect. Attribute effects are deliberately absent from
  `EFFECT_TYPES`, since they are already numbers. Traits are excluded from the totals because
  `pick_traits_for_stage()` fills a character to three traits at random when their stage defines
  fewer, so trait numbers would be fiction for generic characters.
- `../total_war/data/roadmap.js` — the Roadmap page's content. **Hand-maintained, not generated**;
  edit it directly. One item is flagged `computed` so the page appends the live list of Han factions
  that still have no mechanic, read from `factions.js`.
- `../total_war/data/map_regions.js` — the Map page's polygons, written by `build_map.py`. Region
  outlines are flat `[x0,y0,x1,y1,...]` rings in source-image pixels, grouped `parts -> rings` so the
  first ring of a part is its outline and the rest are its enclaves, which is the shape `L.polygon`
  wants. The Map page is the only consumer.
- `../total_war/data/map_recruitment.js` — the Map page's recruitment paint and filter, written
  by `build_recruitment.py`. `RECRUIT_ZONES` are the hubs (name, colour, region count, units),
  `RECRUIT_ZONE_BY_REGION[key]` the hubs a region sits in, `RECRUIT_BY_REGION[key]` the unit
  indices it can raise, and `RECRUIT_EXEMPT[faction]` the units that faction may raise anywhere.
- `lua_table.py` — minimal Lua table-literal reader, used to read data tables straight out of the
  mod's campaign scripts when the db tables do not express them.
- `last_run_*.json`, `last_audit.json` — counts from the last run, used by the audit to show deltas.

## Campaigns

`3k_main_campaign_map` ("Rise of the Warlords") is the 190 campaign and drives the Factions page.
`8p_start_pos` was repurposed by the mod as the optional "Gathering of Heroes" start; only the factions
unique to that mode are emitted, in their own section.

## Biographies

`character_bios.js` is hand-written. `character_bios_new.js` holds drafted bios for characters that had
none (loaded as a fallback by `character.html`). Review a draft, then move it into `character_bios.js`.
