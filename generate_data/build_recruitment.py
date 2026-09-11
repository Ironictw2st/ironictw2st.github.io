#!/usr/bin/env python3
"""
190 Expanded Wiki - regional recruitment
========================================

Builds ../total_war/data/map_recruitment.js: which units each region of the 190 campaign
can raise, and the recruitment hub each region belongs to. The Map page paints regions by
hub and filters by unit.

    python build_recruitment.py [--dry-run]

Where the answer lives
----------------------
Not in the db tables. The mod's own campaign script is the source of truth:

    2_Char/script/campaign/mod/ui/AOR_recruitment.lua

It holds `aor_region_groups` (named region lists - the recruitment hubs, capitals included)
and `aor_restrictions_with_groups` (unit -> the hubs it is confined to). Its own comment
states the rule: units in the table are ONLY recruitable in the listed regions, and units
absent from it are recruitable anywhere. So the table is the whole of regional recruitment,
and lua_table.py lifts it out directly rather than re-deriving it.

An earlier pass built this from the db instead, walking
start_pos_region_slot_templates -> building superchains -> chains -> levels ->
campaign_unit_requirements -> campaign_unit_permission_requirements. That does describe what
*unlocks* a unit, but it is not where a unit may be *raised*: it missed every province
capital, because the hub building sits on the secondary slots, and it swept in faction-unique
district chains, which put Ma Teng's Qiang units in Korea. Only the requirement gates (rank,
tech) are still read from those tables, keyed by unit.

Two caveats the page states rather than hides
---------------------------------------------
- The restriction table is keyed by subculture and only `3k_main_chinese` is populated, so
  these rules bind Han Chinese factions. Nanman, Korean and steppe factions are not held to
  them.
- `aor_exemptions` lists units certain factions may raise anywhere regardless, and those are
  carried through per faction.
"""

import os
import re
import sys
import csv
import json
import glob
from collections import defaultdict, Counter

import lua_table

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SITE_DATA = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "total_war", "data"))
OUTPUT_PATH = os.path.join(SITE_DATA, "map_recruitment.js")
SUMMARY_PATH = os.path.join(SCRIPT_DIR, "last_run_recruitment.json")
DB = os.path.join(SCRIPT_DIR, "db")
MOD_ROOT = r"Z:\Claude\190Expanded\Beta"
AOR_LUA = os.path.join(MOD_ROOT, "2_Char", "script", "campaign", "mod", "ui",
                       "AOR_recruitment.lua")
CAMPAIGN = "3k_main_campaign_map"
AOR_SUBCULTURE = "3k_main_chinese"

DRY = "--dry-run" in sys.argv

# The Five Elements are baked into every 3K unit key and matter to players building an army,
# so they are lifted out of the key rather than left buried in it.
ELEMENTS = ("metal", "wood", "water", "fire", "earth")

# One hue per province family so a glance at the map reads as regions, not confetti: every
# Korean hub sits in the same blue, every Yi hub in the same green, and variants within a
# family separate by lightness.
FAMILY_HUE = {
    "liang": 4, "jing": 30, "yu": 52, "sili": 68, "qing": 92, "yi": 132,
    "jiao": 172, "yang": 202, "korea": 226, "southern": 244, "yong": 262,
    "bing": 280, "you": 300, "xu": 322, "ji": 344, "yan": 16,
    "qiang": 10, "xiliang": 22, "xiongnu": 270, "xianbei": 290, "wuhuan": 310,
    "yue": 190, "chu": 40, "qi": 100, "wei": 334,
}


# ---------------------------------------------------------------------------
# table / loc loading
# ---------------------------------------------------------------------------

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


def _loc_by_prefix(prefix, vanilla_file=None):
    out = {}
    paths = []
    if vanilla_file:
        paths.append(os.path.join(SCRIPT_DIR, "text", "vanilla", vanilla_file))
    paths += sorted(glob.glob(os.path.join(SCRIPT_DIR, "text", "mod", "**", "*.loc.tsv"),
                              recursive=True))
    for p in paths:
        for k, v in read_loc(p).items():
            if k.startswith(prefix):
                out.setdefault(k[len(prefix):], re.sub(r"\[\[/?[^\]]*\]\]", "", v).strip())
    return out


def load_unit_names():
    """land_units_onscreen_name_<key>, vanilla first then every mod loc so the mod wins."""
    return _loc_by_prefix("land_units_onscreen_name_", "land_units__.loc.tsv")


def load_zone_names():
    """The mod names its hubs on the building chain, e.g. 'Yi-Nanman Recruitment Hub'."""
    return _loc_by_prefix("building_chains_encyclopedia_name_")


def load_region_names():
    loc = read_loc(os.path.join(MOD_ROOT, "1_Faction", "text", "db", "regions.loc.tsv"))
    p = "regions_onscreen_"
    return {k[len(p):]: v for k, v in loc.items() if k.startswith(p)}


def load_faction_names():
    names = {}
    fjs = os.path.join(SITE_DATA, "factions.js")
    if os.path.exists(fjs):
        m = re.search(r"const FACTION_DATA = (\[.*?\]);\n", open(fjs, encoding="utf-8").read(), re.S)
        if m:
            for f in json.loads(m.group(1)):
                names.setdefault(f["faction_key"], f.get("name") or f["faction_key"])
    for k, v in _loc_by_prefix("factions_screen_name_", "factions__.loc.tsv").items():
        names.setdefault(k, v)
    return names


def pretty(unit_key):
    """Readable fallback for a unit with no loc entry: strip pack, 'unit', element."""
    s = re.sub(r"^(?:3k_[a-z0-9]+_|ironic_|rew_iro_|ep_|unit_)+", "", unit_key)
    parts = [p for p in s.split("_") if p and p != "unit" and p not in ELEMENTS]
    return " ".join(parts).title() or unit_key


def element_of(unit_key):
    for e in ELEMENTS:
        if f"_{e}_" in unit_key or unit_key.startswith(f"{e}_"):
            return e.title()
    return ""


def zone_colour(key, variant):
    """Deterministic HSL -> hex: hue by province family, lightness by variant."""
    token = re.sub(r"^ironic_province_", "", key).split("_")[0]
    hue = FAMILY_HUE.get(token)
    if hue is None:                                   # anything unfamiliar still gets a stable hue
        hue = sum(ord(c) * 7 for c in token) % 360
    # variants of one family share a hue and separate by lightness and saturation, so
    # "Yang" and "Yang-Yue" read as related but are still tellable apart in the legend
    sat = 0.62 - 0.16 * (variant % 3)
    light = 0.34 + 0.15 * (variant % 3)
    c = (1 - abs(2 * light - 1)) * sat
    x = c * (1 - abs((hue / 60.0) % 2 - 1))
    m = light - c / 2
    rgb = [(c, x, 0), (x, c, 0), (0, c, x), (0, x, c), (x, 0, c), (c, 0, x)][int(hue // 60) % 6]
    return "#" + "".join(f"{int((v + m) * 255):02X}" for v in rgb)


def zone_label(key, zone_names):
    if key in zone_names:
        return zone_names[key]
    s = re.sub(r"^ironic_province_", "", key)
    s = re.sub(r"_regions$", "", s)
    return s.replace("_", " ").title()


# ---------------------------------------------------------------------------

def main():
    print("190 Expanded Wiki - regional recruitment")
    print("=" * 60)

    print("[1/5] Reading the AOR script")
    if not os.path.exists(AOR_LUA):
        raise SystemExit(f"ERROR: {AOR_LUA} not found - regional recruitment lives there.")
    src = open(AOR_LUA, encoding="utf-8", errors="replace").read()
    groups = lua_table.read_local(src, "aor_region_groups") or {}
    faction_groups = lua_table.read_local(src, "aor_faction_groups") or {}
    restrictions = lua_table.read_local(src, "aor_restrictions_with_groups") or {}
    exemptions = lua_table.read_local(src, "aor_exemptions") or {}
    if AOR_SUBCULTURE not in restrictions:
        raise SystemExit(f"ERROR: {AOR_LUA} has no '{AOR_SUBCULTURE}' restriction block; "
                         f"found {list(restrictions)}. The script's shape has changed.")
    base = {k: v for k, v in restrictions[AOR_SUBCULTURE].items() if k != "faction_specific"}
    print(f"  {len(groups)} region groups, {len(base)} restricted units, "
          f"{len(exemptions)} factions with exemptions")

    print("[2/5] Resolving regions")
    h, r = table("start_pos_regions_tables", f"data_{CAMPAIGN}.tsv")
    i_reg = col(h, "region")
    real_regions = {x[i_reg].strip() for x in r if len(x) > i_reg and x[i_reg].strip()}
    print(f"  {len(real_regions)} regions in this campaign")

    # The lua treats a name it does not recognise as a literal region key, so anything that is
    # neither a known group nor a real region silently contributes nothing in game too. Say so.
    unit_regions, dangling = {}, Counter()
    for unit, refs in base.items():
        regions = set()
        for ref in refs:
            if ref in groups:
                regions |= {x for x in groups[ref]}
            elif ref in real_regions:
                regions.add(ref)
            else:
                dangling[ref] += 1
        unit_regions[unit] = {x for x in regions if x in real_regions}

    ghost_regions = sorted({x for g in groups.values() for x in g} - real_regions)
    if dangling:
        print(f"  WARNING: {len(dangling)} names in the restriction table are neither a region "
              f"group nor a region, so they grant nothing in game either:")
        for name, n in dangling.most_common():
            print(f"    {name} (referenced by {n} units)")
    if ghost_regions:
        print(f"  {len(ghost_regions)} region keys in the groups are not in this campaign: "
              + ", ".join(ghost_regions[:5]) + ("..." if len(ghost_regions) > 5 else ""))

    print("[3/5] Building hubs")
    zone_names = load_zone_names()
    used_groups = sorted({ref for refs in base.values() for ref in refs if ref in groups})
    family_seen = Counter()
    zones, zone_of_group = [], {}
    for g in used_groups:
        fam = re.sub(r"^ironic_province_", "", g).split("_")[0]
        zone_of_group[g] = len(zones)
        zones.append({
            "key": g,
            "name": zone_label(g, zone_names),
            "colour": zone_colour(g, family_seen[fam]),
            "regions": sorted(x for x in groups[g] if x in real_regions),
        })
        family_seen[fam] += 1
    print(f"  {len(zones)} hubs in use of {len(groups)} groups defined")

    region_zones = defaultdict(list)
    for zi, z in enumerate(zones):
        for reg in z["regions"]:
            region_zones[reg].append(zi)
    covered = len(region_zones)
    print(f"  {covered} of {len(real_regions)} regions sit in a hub "
          f"({len(real_regions) - covered} have no regional recruitment)")

    print("[4/5] Naming units")
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
    i_k, i_cls = col(h, "key"), col(h, "class")
    land_by_key = {x[i_k].strip(): x for x in r if len(x) > i_k}

    # the loosest extra gate the unit carries anywhere (rank / tech), from the db side
    h, r = table("campaign_unit_requirements_tables")
    i_key, i_t1, i_rank = col(h, "key"), col(h, "tech1"), col(h, "minimum_character_rank")
    req_gate = {}
    for x in r:
        if len(x) <= i_key:
            continue
        g = {}
        if i_t1 >= 0 and len(x) > i_t1 and x[i_t1].strip():
            g["tech"] = x[i_t1].strip()
        if i_rank >= 0 and len(x) > i_rank and x[i_rank].strip() not in ("", "0"):
            g["rank"] = x[i_rank].strip()
        req_gate[x[i_key].strip()] = g
    h, r = table("campaign_unit_permission_requirements_tables")
    i_req, i_unit, i_res = col(h, "requirement"), col(h, "unit"), col(h, "is_restriction")
    unit_gate = {}
    for x in r:
        if len(x) <= max(i_req, i_unit):
            continue
        if i_res >= 0 and len(x) > i_res and x[i_res].strip().lower() == "true":
            continue
        u, g = x[i_unit].strip(), req_gate.get(x[i_req].strip(), {})
        if u not in unit_gate or not g:      # an ungated route anywhere means it is not gated
            unit_gate[u] = g

    used_units = sorted(u for u, regs in unit_regions.items() if regs)
    units, unit_index, named = [], {}, 0
    for u in used_units:
        land_key = land_of.get(u, "")
        land = land_by_key.get(land_key) or land_by_key.get(u)
        m = main_by_unit.get(u)
        name = loc_names.get(land_key) or loc_names.get(u)
        if name:
            named += 1
        entry = {
            "key": u,
            # the loc carries a non-breaking space in a couple of names; normalise it
            "name": re.sub(r"\s+", " ", name or pretty(u)).strip(),
            "element": element_of(u),
            "cls": (land[i_cls].strip().replace("_", " ").title()
                    if land and i_cls >= 0 and len(land) > i_cls else ""),
            "caste": (m[i_caste].strip().replace("_", " ").title()
                      if m and i_caste >= 0 and len(m) > i_caste else ""),
            "zones": sorted(zone_of_group[g] for g in base[u] if g in zone_of_group),
            "regions": len(unit_regions[u]),
        }
        for src_i, field in ((i_cost, "cost"), (i_up, "upkeep")):
            if m and src_i >= 0 and len(m) > src_i and m[src_i].strip().isdigit():
                entry[field] = int(m[src_i].strip())
        gate = unit_gate.get(u) or {}
        if gate:
            entry["gate"] = gate
        unit_index[u] = len(units)
        units.append(entry)
    dropped = [u for u in unit_regions if not unit_regions[u]]
    print(f"  {len(units)} units, {named} named from loc, {len(units) - named} from the key")
    if dropped:
        print(f"  {len(dropped)} restricted units resolve to no region in this campaign: "
              + ", ".join(sorted(dropped)[:4]))

    by_region = {}
    for u in used_units:
        for reg in unit_regions[u]:
            by_region.setdefault(reg, []).append(unit_index[u])
    for reg in by_region:
        by_region[reg].sort()

    exempt = {}
    for holder, spec in exemptions.items():
        keys = list(spec) if isinstance(spec, dict) else list(spec)
        idxs = sorted({unit_index[k] for k in keys if k in unit_index})
        for f in (faction_groups.get(holder) or [holder]):
            if idxs:
                exempt[f] = idxs
    print(f"  {len(exempt)} factions may raise some of these anywhere regardless")

    if DRY:
        print("\n--dry-run, nothing written")
        return

    print("[5/5] Writing data")
    zones_out = [{"key": z["key"], "name": z["name"], "colour": z["colour"],
                  "regions": len(z["regions"]),
                  "units": sorted(i for i, u in enumerate(units) if zi in u["zones"])}
                 for zi, z in enumerate(zones)]
    lines = [
        "// Auto-generated by generate_data/build_recruitment.py - do not edit by hand.",
        f"// Regional recruitment for {CAMPAIGN}, read from the mod's own AOR_recruitment.lua.",
        "// A unit listed there is recruitable ONLY in the regions of the hubs it names;",
        "// units absent from that table are recruitable anywhere and are not listed here.",
        "// The rules bind " + AOR_SUBCULTURE + " factions; RECRUIT_EXEMPT[faction] may raise",
        "// its units anywhere regardless.",
        "",
        "const RECRUIT_UNITS = " + json.dumps(units, ensure_ascii=False, indent=1) + ";",
        "",
        "const RECRUIT_ZONES = " + json.dumps(zones_out, ensure_ascii=False, indent=1) + ";",
        "",
        "const RECRUIT_ZONE_BY_REGION = " + json.dumps(
            {k: v for k, v in sorted(region_zones.items())}, separators=(",", ":")) + ";",
        "",
        "const RECRUIT_BY_REGION = " + json.dumps(by_region, separators=(",", ":")) + ";",
        "",
        "const RECRUIT_EXEMPT = " + json.dumps(exempt, separators=(",", ":")) + ";",
        "",
    ]
    os.makedirs(SITE_DATA, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))
    size = os.path.getsize(OUTPUT_PATH) / 1024
    print(f"  Written: {OUTPUT_PATH} ({size:.0f} KB)")

    summary = {
        "campaign": CAMPAIGN,
        "source": "AOR_recruitment.lua",
        "units": len(units),
        "hubs": len(zones_out),
        "regionsInAHub": covered,
        "regionsWithout": len(real_regions) - covered,
        "pairs": sum(len(v) for v in by_region.values()),
        "capitalsCovered": sum(1 for r in region_zones if r.endswith("_capital")),
        "factionsWithExemptions": len(exempt),
        "danglingGroupRefs": sorted(dangling),
        "ghostRegionKeys": ghost_regions,
        "kb": round(size),
    }
    json.dump(summary, open(SUMMARY_PATH, "w", encoding="utf-8"), indent=2)
    print("\nSUMMARY " + json.dumps(summary))


if __name__ == "__main__":
    main()
