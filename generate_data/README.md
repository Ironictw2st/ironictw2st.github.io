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

`build_recruitment.py` answers "what can I recruit here" for the Map page. It runs off the
synced tables, so run it after `sync_from_mod.py`.

```
python build_recruitment.py             # -> total_war/data/map_recruitment.js
python build_recruitment.py --dry-run   # report the joins without writing
```

Nothing in the game data says "region -> unit". It is assembled from six joins:

```
start_pos_region_slot_templates   region     -> slot template   (per campaign)
slot_template_to_building_superchain_junctions -> superchain
building_chains                   superchain -> chain
building_levels                   chain      -> building level
campaign_unit_requirements        building1  -> requirement
campaign_unit_permission_requirements        -> unit
```

**The join alone is far too generous, and the failure is silent.** Most regions carry the
generic `3k_districts` slot template, which reaches every district chain in the game -
including faction-unique ones like Ma Teng's `3k_district_military_security_ma_teng`. Taken at
face value that puts Qiang units in Korea. So every grant also carries who is allowed to build
the thing behind it, from `building_chain_availability_sets` -> `building_chain_availabilities`
(faction / sub_culture). A grant open to a whole subculture is ordinary regional recruitment; one
pinned to a single faction is that faction's roster and is labelled `<Faction> only`. Scopes are
resolved against the 108 factions that actually hold ground at turn one, not all 348 faction
records, so "most factions" means something.

`is_restriction` rows in `campaign_unit_permission_requirements` are exclusions, not grants, and
are skipped. Tech, character-rank and agent gates ride along as notes on each grant rather than
being filtered on.

`family_tree/family_extractor.py` is separate and hand-fed (`starter.xlsx` + lua); it is not part of the sync.

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
- `../total_war/data/map_recruitment.js` — the Map page's recruitment filter, written by
  `build_recruitment.py`. `RECRUIT_BY_REGION[key] = [[unitIndex, scopeIndex, gate?], ...]`;
  `RECRUIT_SCOPES[i].factions === null` means anyone holding the region can raise it.
- `last_run_*.json`, `last_audit.json` — counts from the last run, used by the audit to show deltas.

## Campaigns

`3k_main_campaign_map` ("Rise of the Warlords") is the 190 campaign and drives the Factions page.
`8p_start_pos` was repurposed by the mod as the optional "Gathering of Heroes" start; only the factions
unique to that mode are emitted, in their own section.

## Biographies

`character_bios.js` is hand-written. `character_bios_new.js` holds drafted bios for characters that had
none (loaded as a fallback by `character.html`). Review a draft, then move it into `character_bios.js`.
