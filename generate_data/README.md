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
- `last_run_*.json`, `last_audit.json` — counts from the last run, used by the audit to show deltas.

## Campaigns

`3k_main_campaign_map` ("Rise of the Warlords") is the 190 campaign and drives the Factions page.
`8p_start_pos` was repurposed by the mod as the optional "Gathering of Heroes" start; only the factions
unique to that mode are emitted, in their own section.

## Biographies

`character_bios.js` is hand-written. `character_bios_new.js` holds drafted bios for characters that had
none (loaded as a fallback by `character.html`). Review a draft, then move it into `character_bios.js`.
