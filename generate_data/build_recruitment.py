#!/usr/bin/env python3
"""
190 Expanded Wiki - regional recruitment
========================================

Builds ../total_war/data/map_recruitment.js: which units each region of the 190 campaign
unlocks for whoever holds it. The Map page uses it for the recruitment filter.

    python build_recruitment.py [--dry-run]

The chain
---------
Recruitment is not stored as "region -> unit" anywhere. It is assembled from five joins,
and the mod's regional rosters live at the far end of it:

    start_pos_region_slot_templates   region        -> slot template   (per campaign)
    slot_template_to_building_superchain_junctions  -> superchain
    building_chains                   superchain    -> chain
    building_levels                   chain         -> building level
    campaign_unit_requirements        building1     -> requirement      (the gate)
    campaign_unit_permission_requirements           -> unit + permission

So a region grants a unit when the region's slot template leads to a building whose level
is named as `building1` on a requirement that some permission attaches to that unit. Rows
flagged `is_restriction` are exclusions, not grants, and are skipped.

Who is allowed to build it
--------------------------
The join above on its own is far too generous, and the failure is not obvious: most regions
carry the generic `3k_districts` slot template, which reaches every district chain in the
game - including faction-unique ones like Ma Teng's `3k_district_military_security_ma_teng`.
Taken at face value that put Qiang units in Korea. Chains are gated separately:

    building_chain_availability_sets   chain  -> availability set
    building_chain_availabilities      set    -> culture / sub_culture / faction

Each grant therefore carries the scope that owns it. A chain open to a whole culture is
ordinary regional recruitment; one pinned to a single faction is that faction's roster and
is labelled as such, so the page never implies anyone can walk into a region and raise it.

What this does NOT model
------------------------
`campaign_unit_requirements` also carries tech, character-rank and agent-subtype gates.
Those ride along as notes rather than being filtered on, because the question the page
answers is "what can come out of this region", not "what can this exact save recruit now".
"""

import os
import re
import sys
import csv
import json
import glob
from collections import defaultdict, Counter

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SITE_DATA = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "total_war", "data"))
OUTPUT_PATH = os.path.join(SITE_DATA, "map_recruitment.js")
SUMMARY_PATH = os.path.join(SCRIPT_DIR, "last_run_recruitment.json")
DB = os.path.join(SCRIPT_DIR, "db")
CAMPAIGN = "3k_main_campaign_map"

DRY = "--dry-run" in sys.argv

# The Five Elements are baked into every 3K unit key and matter to players building an army,
# so they are lifted out of the key rather than left buried in it.
ELEMENTS = ("metal", "wood", "water", "fire", "earth")


def read_tsv(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE))
    if not rows:
        return [], []
    return rows[0], [r for r in rows[1:] if r and r[0] and not r[0].startswith("#")]


def table(name, pattern="*.tsv"):
    """Every synced TSV for a table, vanilla first then the mod's, as one row list."""
    header, out = None, []
    for p in sorted(glob.glob(os.path.join(DB, name, pattern))):
        h, rows = read_tsv(p)
        if h:
            header = h
        out += rows
    return header, out


def col(header, *names):
    for n in names:
        if header and n in header:
            return header.index(n)
    return -1


def read_loc(path):
    out = {}
    if not os.path.exists(path):
        return out
    with open(path, encoding="utf-8-sig", newline="") as f:
        for row in csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
            if len(row) < 2 or not row[0] or row[0].startswith("#") or row[0] == "key":
                continue
            text = row[1].strip()
            if text and text.upper() != "PLACEHOLDER":
                out[row[0].strip()] = text
    return out


def load_unit_names():
    """land_units_onscreen_name_<key>, vanilla first then every mod loc so the mod wins."""
    names = {}
    paths = [os.path.join(SCRIPT_DIR, "text", "vanilla", "land_units__.loc.tsv")]
    paths += sorted(glob.glob(os.path.join(SCRIPT_DIR, "text", "mod", "**", "*.loc.tsv"),
                              recursive=True))
    prefix = "land_units_onscreen_name_"
    for p in paths:
        for k, v in read_loc(p).items():
            if k.startswith(prefix):
                names[k[len(prefix):]] = v
    return names


def load_faction_names():
    """Display names, preferring the ones already resolved into the site's factions.js."""
    names = {}
    fjs = os.path.join(SITE_DATA, "factions.js")
    if os.path.exists(fjs):
        m = re.search(r"const FACTION_DATA = (\[.*?\]);\n", open(fjs, encoding="utf-8").read(), re.S)
        if m:
            for f in json.loads(m.group(1)):
                names.setdefault(f["faction_key"], f.get("name") or f["faction_key"])
    prefix = "factions_screen_name_"
    for rel in ("text/mod/2_Char/db/factions/ironic_added_factions_text.loc.tsv",
                "text/vanilla/factions__.loc.tsv"):
        for k, v in read_loc(os.path.join(SCRIPT_DIR, rel)).items():
            if k.startswith(prefix):
                names.setdefault(k[len(prefix):], v)
    return names


def load_subculture_names():
    prefix = "cultures_subcultures_name_"
    out = {}
    for p in [os.path.join(SCRIPT_DIR, "text", "vanilla", "cultures_subcultures__.loc.tsv")] + \
             sorted(glob.glob(os.path.join(SCRIPT_DIR, "text", "mod", "**", "*.loc.tsv"),
                              recursive=True)):
        for k, v in read_loc(p).items():
            if k.startswith(prefix):
                out.setdefault(k[len(prefix):], v)
    return out


def pretty(unit_key):
    """Readable fallback for a unit with no loc entry: strip pack, 'unit', element."""
    s = re.sub(r"^(?:3k_[a-z0-9]+_|ironic_|rew_iro_|unit_)+", "", unit_key)
    s = re.sub(r"^(?:regional_[a-z]+_)?", "", s)
    parts = [p for p in s.split("_") if p and p != "unit" and p not in ELEMENTS]
    return " ".join(parts).title() or unit_key


def element_of(unit_key):
    for e in ELEMENTS:
        if f"_{e}_" in unit_key or unit_key.startswith(f"{e}_"):
            return e.title()
    return ""


def main():
    print("190 Expanded Wiki - regional recruitment")
    print("=" * 60)
    print("[1/4] Walking region -> building -> unit")

    h, r = table("start_pos_region_slot_templates_tables", f"data_{CAMPAIGN}.tsv")
    i_reg, i_tpl = col(h, "region"), col(h, "slot_template")
    region_templates = defaultdict(set)
    for x in r:
        if len(x) > max(i_reg, i_tpl):
            region_templates[x[i_reg].strip()].add(x[i_tpl].strip())
    print(f"  {len(r)} slot rows over {len(region_templates)} regions")

    h, r = table("slot_template_to_building_superchain_junctions_tables")
    i_sup, i_tpl = col(h, "building_superchain"), col(h, "slot_template")
    tpl_super = defaultdict(set)
    for x in r:
        if len(x) > max(i_sup, i_tpl):
            tpl_super[x[i_tpl].strip()].add(x[i_sup].strip())

    h, r = table("building_chains_tables")
    i_key, i_sup = col(h, "key"), col(h, "building_superchain")
    super_chains = defaultdict(set)
    for x in r:
        if len(x) > max(i_key, i_sup):
            super_chains[x[i_sup].strip()].add(x[i_key].strip())

    h, r = table("building_levels_tables")
    i_lvl, i_chain = col(h, "level_name"), col(h, "chain")
    chain_levels = defaultdict(set)
    level_chain = {}
    for x in r:
        if len(x) > max(i_lvl, i_chain):
            chain_levels[x[i_chain].strip()].add(x[i_lvl].strip())
            level_chain[x[i_lvl].strip()] = x[i_chain].strip()

    # who may build a given chain at all
    h, r = table("building_chain_availability_sets_tables")
    i_ch, i_set = col(h, "building_chain"), col(h, "id")
    chain_sets = defaultdict(set)
    for x in r:
        if len(x) > max(i_ch, i_set):
            chain_sets[x[i_ch].strip()].add(x[i_set].strip())

    h, r = table("building_chain_availabilities_tables")
    i_sid = col(h, "set_id")
    i_cul, i_sub, i_fac = col(h, "culture"), col(h, "sub_culture"), col(h, "faction")
    i_camp = col(h, "campaign")
    set_scope = defaultdict(lambda: {"factions": set(), "cultures": set(), "subcultures": set()})
    for x in r:
        if len(x) <= i_sid:
            continue
        # rows scoped to another campaign do not apply here
        if i_camp >= 0 and len(x) > i_camp and x[i_camp].strip() and x[i_camp].strip() != CAMPAIGN:
            continue
        sc = set_scope[x[i_sid].strip()]
        for i_col, bucket in ((i_fac, "factions"), (i_cul, "cultures"), (i_sub, "subcultures")):
            if i_col >= 0 and len(x) > i_col and x[i_col].strip():
                sc[bucket].add(x[i_col].strip())
    print(f"  {len(chain_sets)} chains carry an availability set, "
          f"{len(set_scope)} sets have a scope")

    def scope_of(chain):
        """Merged scope for a chain: who is allowed to build it. Empty = unrestricted."""
        facs, culs, subs = set(), set(), set()
        for sid in chain_sets.get(chain, ()):
            sc = set_scope.get(sid)
            if sc:
                facs |= sc["factions"]
                culs |= sc["cultures"]
                subs |= sc["subcultures"]
        return facs, culs, subs

    # requirement rows: the building that gates them, plus the other gates we report as notes
    h, r = table("campaign_unit_requirements_tables")
    i_key = col(h, "key")
    i_b1, i_t1, i_rank, i_agent = (col(h, "building1"), col(h, "tech1"),
                                   col(h, "minimum_character_rank"), col(h, "agent_subtype"))
    level_reqs = defaultdict(set)
    req_notes = {}
    for x in r:
        if len(x) <= i_key:
            continue
        key = x[i_key].strip()
        note = {}
        if i_t1 >= 0 and len(x) > i_t1 and x[i_t1].strip():
            note["tech"] = x[i_t1].strip()
        if i_rank >= 0 and len(x) > i_rank and x[i_rank].strip() not in ("", "0"):
            note["rank"] = x[i_rank].strip()
        if i_agent >= 0 and len(x) > i_agent and x[i_agent].strip():
            note["agent"] = x[i_agent].strip()
        req_notes[key] = note
        if i_b1 >= 0 and len(x) > i_b1 and x[i_b1].strip():
            level_reqs[x[i_b1].strip()].add(key)
    print(f"  {len(level_reqs)} building levels gate a unit requirement")

    h, r = table("campaign_unit_permission_requirements_tables")
    i_req, i_unit, i_perm = col(h, "requirement"), col(h, "unit"), col(h, "permission")
    i_restrict = col(h, "is_restriction")
    req_units = defaultdict(set)
    restrictions = 0
    for x in r:
        if len(x) <= max(i_req, i_unit, i_perm):
            continue
        if i_restrict >= 0 and len(x) > i_restrict and x[i_restrict].strip().lower() == "true":
            restrictions += 1          # an exclusion, not a grant
            continue
        req_units[x[i_req].strip()].add(x[i_unit].strip())
    print(f"  {len(req_units)} requirements grant a unit ({restrictions} restriction rows skipped)")

    # ------------------------------------------------------------------ join
    region_units = defaultdict(dict)   # region -> {unit: {gate, facs, culs, subs, open}}
    for region, tpls in region_templates.items():
        for tpl in tpls:
            for sup in tpl_super.get(tpl, ()):
                for chain in super_chains.get(sup, ()):
                    facs, culs, subs = scope_of(chain)
                    for lvl in chain_levels.get(chain, ()):
                        for req in level_reqs.get(lvl, ()):
                            for unit in req_units.get(req, ()):
                                cur = region_units[region].setdefault(
                                    unit, {"facs": set(), "culs": set(), "subs": set(),
                                           "open": False})
                                # a unit granted by several chains is as open as the
                                # broadest of them
                                if not (facs or culs or subs):
                                    cur["open"] = True
                                cur["facs"] |= facs
                                cur["culs"] |= culs
                                cur["subs"] |= subs
                                # likewise the loosest extra gate wins: a unit reachable
                                # with no tech requirement should not be shown as gated
                                note = req_notes.get(req, {})
                                if "gate" not in cur or not note:
                                    cur["gate"] = note

    print("[2/4] Naming units")
    loc_names = load_unit_names()
    h, r = table("main_units_tables")
    i_u, i_cost, i_up = col(h, "unit"), col(h, "recruitment_cost"), col(h, "upkeep_cost")
    i_caste, i_land = col(h, "caste"), col(h, "land_unit")
    main_by_unit, land_of = {}, {}
    for x in r:
        if len(x) > i_u:
            main_by_unit[x[i_u].strip()] = x
            if i_land >= 0 and len(x) > i_land:
                land_of[x[i_u].strip()] = x[i_land].strip()

    h, r = table("land_units_tables")
    i_k, i_cls, i_cat = col(h, "key"), col(h, "class"), col(h, "category")
    land_by_key = {x[i_k].strip(): x for x in r if len(x) > i_k}

    used = sorted({u for v in region_units.values() for u in v})
    units, unit_index = [], {}
    named = 0
    for u in used:
        land_key = land_of.get(u, "")
        land = land_by_key.get(land_key) or land_by_key.get(u)
        m = main_by_unit.get(u)
        name = loc_names.get(land_key) or loc_names.get(u)
        if name:
            named += 1
        entry = {
            "key": u,
            "name": name or pretty(u),
            "element": element_of(u),
            "cls": (land[i_cls].strip().replace("_", " ").title()
                    if land and i_cls >= 0 and len(land) > i_cls else ""),
            "caste": (m[i_caste].strip().replace("_", " ").title()
                      if m and i_caste >= 0 and len(m) > i_caste else ""),
        }
        for src_i, field in ((i_cost, "cost"), (i_up, "upkeep")):
            if m and src_i >= 0 and len(m) > src_i and m[src_i].strip().isdigit():
                entry[field] = int(m[src_i].strip())
        unit_index[u] = len(units)
        units.append(entry)
    print(f"  {len(units)} units, {named} with a loc name, {len(units) - named} from the key")

    print("[3/4] Resolving who may build what")
    # Translate each grant's culture/subculture/faction scope into the concrete list of
    # factions on this map, so the page can filter without knowing the culture tree.
    h, r = table("factions_tables")
    i_fk = col(h, "key")
    i_fcul, i_fsub = col(h, "culture"), col(h, "subculture")
    fac_culture, fac_sub = {}, {}
    for x in r:
        if len(x) > i_fk:
            k = x[i_fk].strip()
            if i_fcul >= 0 and len(x) > i_fcul:
                fac_culture[k] = x[i_fcul].strip()
            if i_fsub >= 0 and len(x) > i_fsub:
                fac_sub[k] = x[i_fsub].strip()

    # Resolve against the factions that actually hold ground at the start of this campaign,
    # not every faction record in the tables. "326 of 348" is noise; "every Han faction" is
    # an answer, and the map only ever shows a region's owner anyway.
    h, r = table("start_pos_factions_tables", f"data_{CAMPAIGN}.tsv")
    i_id, i_f = col(h, "ID"), col(h, "faction")
    id_to_faction = {x[i_id].strip(): x[i_f].strip() for x in r if len(x) > max(i_id, i_f)}
    h, r = table("start_pos_regions_tables", f"data_{CAMPAIGN}.tsv")
    i_own = col(h, "owning_faction")
    owners = sorted({id_to_faction.get(x[i_own].strip(), "") for x in r if len(x) > i_own} - {""})
    # factions_tables carries subculture but no culture column, and the availability rows
    # use faction + sub_culture, so subculture is the axis that actually resolves here
    print(f"  {len(owners)} factions hold a region at turn one, "
          f"{sum(1 for f in owners if fac_sub.get(f))} with a subculture")

    faction_label = load_faction_names()
    sub_label = load_subculture_names()

    def sub_name(key):
        if key in sub_label:
            return sub_label[key]
        return re.sub(r"^(?:3k_|dlc\d+_|ironic_|main_|subculture_)+", "", key).replace("_", " ").title()

    def describe(allowed, meta):
        """
        Name the scope the way a player would.

        Almost every grant carries *some* scope, so a bare count reads as a restriction
        when it is not one. A scope covering most of the map is the ordinary case and is
        labelled as such; the sharp ones - a single faction, one culture - are the news.
        """
        if allowed is None:
            return "Any faction holding this region"
        if not allowed:
            return "No faction on this map"
        if len(allowed) == 1:
            return faction_label.get(allowed[0], allowed[0]) + " only"
        if len(allowed) >= 0.85 * len(owners):
            return "Most factions"
        if len(allowed) <= 3:
            return ", ".join(faction_label.get(f, f) for f in allowed)
        subs = sorted({sub_name(s) for s in meta["subs"]})
        if subs and len(subs) <= 2:
            return " and ".join(subs) + " factions"
        return f"{len(allowed)} factions"

    scopes, scope_index = [], {}

    def scope_id(meta):
        if meta["open"]:
            key, allowed = ("open",), None
        else:
            allowed = sorted(
                f for f in owners
                if f in meta["facs"]
                or fac_culture.get(f) in meta["culs"]
                or fac_sub.get(f) in meta["subs"])
            key = tuple(allowed)
        if key not in scope_index:
            scope_index[key] = len(scopes)
            scopes.append({"factions": allowed, "label": describe(allowed, meta),
                           "share": (1.0 if allowed is None
                                     else round(len(allowed) / max(len(owners), 1), 3))})
        return scope_index[key]

    print("[4/4] Building the region index")
    by_region, gated, restricted = {}, 0, 0
    for region, us in region_units.items():
        entries = []
        for u, meta in sorted(us.items(), key=lambda kv: unit_index[kv[0]]):
            gate = meta.get("gate") or {}
            sid = scope_id(meta)
            if scopes[sid]["factions"] is not None:
                restricted += 1
            entry = [unit_index[u], sid]
            if gate:
                gated += 1
                entry.append(gate)
            entries.append(entry)
        by_region[region] = entries
    print(f"  {len(scopes)} distinct availability scopes, "
          f"{restricted} of {sum(len(v) for v in by_region.values())} grants faction-restricted")

    reach = Counter()
    for region, us in region_units.items():
        for u in us:
            reach[u] += 1
    n = len(by_region)
    for e, u in zip(units, used):
        e["regions"] = reach[u]
    exclusive = [e["name"] for e in units if e["regions"] <= 2]
    print(f"  {sum(len(v) for v in by_region.values())} region-unit pairs over {n} regions")
    print(f"  {len(exclusive)} units appear in 2 regions or fewer, "
          f"{sum(1 for e in units if e['regions'] > 0.5 * n)} in more than half")

    if DRY:
        print("\n--dry-run, nothing written")
        return

    print("Writing data")
    lines = [
        "// Auto-generated by generate_data/build_recruitment.py - do not edit by hand.",
        f"// Regional recruitment for {CAMPAIGN}: which units a region unlocks for its holder.",
        "// RECRUIT_BY_REGION[regionKey] = [[unitIndex, scopeIndex, {tech|rank|agent}?], ...]",
        "// RECRUIT_SCOPES[i].factions = null means anyone holding the region; otherwise the",
        "// building behind the unit is that faction's or culture's own, so only they can raise it.",
        "",
        "const RECRUIT_UNITS = " + json.dumps(units, ensure_ascii=False, indent=1) + ";",
        "",
        "const RECRUIT_SCOPES = " + json.dumps(scopes, ensure_ascii=False,
                                               separators=(",", ":")) + ";",
        "",
        "const RECRUIT_BY_REGION = " + json.dumps(by_region, ensure_ascii=False,
                                                  separators=(",", ":")) + ";",
        "",
    ]
    os.makedirs(SITE_DATA, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))
    size = os.path.getsize(OUTPUT_PATH) / 1024
    print(f"  Written: {OUTPUT_PATH} ({size:.0f} KB)")

    summary = {
        "campaign": CAMPAIGN,
        "regions": n,
        "units": len(units),
        "pairs": sum(len(v) for v in by_region.values()),
        "gatedPairs": gated,
        "unitsNamedFromLoc": named,
        "unitsInTwoRegionsOrFewer": len(exclusive),
        "scopes": len(scopes),
        "restrictedGrants": restricted,
        "kb": round(size),
    }
    json.dump(summary, open(SUMMARY_PATH, "w", encoding="utf-8"), indent=2)
    print("\nSUMMARY " + json.dumps(summary))


if __name__ == "__main__":
    main()
