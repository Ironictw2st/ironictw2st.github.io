#!/usr/bin/env python3
"""
190 Expanded Wiki - sync generator inputs from the mod + vanilla trees
=====================================================================

Makes generate_data/ reproducible. Run this BEFORE the parsers:

    python sync_from_mod.py [--dry-run] [--no-portraits]

Sources
  MOD_CHAR = Z:\\Claude\\190Expanded\\Beta\\2_Char   (characters, factions, most db + text)
  MOD_FAC  = Z:\\Claude\\190Expanded\\Beta\\1_Faction (ceo_db, start_pos, region text)
  VAN      = Z:\\Claude\\XMLViewer\\games\\3K         (vanilla DB / ceo_db / text / ui dumps)

Targets (all relative to this folder)
  db/<table>/data__.tsv           vanilla row set (refreshed only when the header matches)
  db/<table>/<mod file>.tsv       every mod TSV for that table (mod files literally named
                                  data__.tsv are written as data__mod_<pack>.tsv so they overlay)
  text/vanilla/*.loc.tsv          vanilla loc files the parsers need
  text/mod/<pack>/**              full mirror of the mod's text trees
  text/extra/**                   NOT touched: hand-kept loc from companion mods (MTU)
  ../total_war/data/images/db/    character portraits (only missing ones are added)

Protected files (kept when the mod tree no longer provides them): anything matching
PROTECT_PATTERNS - these come from the MTU companion mod, which is not in Beta.
"""

import os
import re
import sys
import shutil

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SITE_DATA = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "total_war", "data"))

MOD_ROOT = r"Z:\Claude\190Expanded\Beta"
MOD_CHAR = os.path.join(MOD_ROOT, "2_Char")
MOD_FAC = os.path.join(MOD_ROOT, "1_Faction")
VAN = r"Z:\Claude\XMLViewer\games\3K"

SRC = {
    "van_db": os.path.join(VAN, "DB"),
    "van_ceo": os.path.join(VAN, "ceo_db"),
    "char_db": os.path.join(MOD_CHAR, "db"),
    "fac_db": os.path.join(MOD_FAC, "db"),
    "fac_ceo": os.path.join(MOD_FAC, "ceo_db"),
}

PROTECT_PATTERNS = [r"^_mtu_", r"^zase_skillset\.tsv$"]

CHAR = ["van_db", "char_db"]
CEO = ["van_ceo", "fac_ceo"]
FAC = ["van_db", "char_db", "fac_db"]

# table -> ordered sources (vanilla first)
TABLES = {
    # characters
    "character_generation_templates_tables": CHAR,
    "character_generation_template_game_mode_details_tables": CHAR,
    "character_generation_spawn_age_ranges_tables": CHAR,
    "campaign_character_arts_tables": CHAR,
    "campaign_character_art_sets_tables": CHAR,
    "names_tables": CHAR,
    "names_groups_tables": CHAR,
    "effects_tables": CHAR,
    "effects_generalised_descriptions_tables": CHAR,
    "campaign_effect_scopes_tables": CHAR,
    # skills
    "character_skill_node_sets_tables": CHAR,
    "character_skill_nodes_tables": CHAR,
    "character_skill_node_links_tables": CHAR,
    "character_skills_tables": CHAR,
    "character_skill_level_to_effects_junctions_tables": CHAR,
    "character_skill_level_details_tables": CHAR,
    # ceo
    "ceos_tables": CEO,
    "ceo_nodes_tables": CEO,
    "ceo_thresholds_tables": CEO,
    "ceo_threshold_nodes_tables": CEO,
    "ceo_effect_lists_tables": CEO + ["char_db"],
    "ceo_effect_list_to_effects_tables": CEO + ["char_db"],
    "ceo_initial_datas_tables": CEO + ["char_db"],
    "ceo_initial_data_active_ceos_tables": CEO,
    "ceo_initial_data_to_stages_tables": CEO,
    "ceo_initial_data_stages_tables": CEO,
    "ceo_initial_data_equipments_tables": CEO,
    "ceo_categories_tables": CEO,
    # factions
    "frontend_faction_to_frontend_faction_leaders_tables": FAC,
    "frontend_faction_leaders_tables": FAC,
    "frontend_factions_tables": FAC,
    "frontend_characters_tables": FAC,
    "frontend_faction_leader_playstyles_tables": FAC,
    "frontend_faction_leader_unique_features_tables": FAC,
    "frontend_faction_leaders_to_frontend_faction_leader_unique_features_junctions_tables": FAC,
    "frontend_faction_leader_unique_characters_tables": FAC,
    "factions_tables": FAC,
    "cultures_subcultures_tables": FAC,
    "faction_groups_tables": FAC,
    "faction_to_faction_groups_junctions_tables": FAC,
    "political_parties_tables": FAC,
    "faction_political_parties_junctions_tables": FAC,
    "political_parties_frontend_leaders_junctions_tables": FAC,
    "pooled_resources_tables": FAC,
    "pooled_resource_factors_tables": FAC,
    "pooled_resource_factor_junctions_tables": FAC,
    "ui_primary_faction_pooled_resources_tables": FAC,
    "campaign_groups_tables": FAC,
    "campaign_group_members_tables": FAC,
    "campaign_group_member_criteria_factions_tables": FAC,
    "campaign_group_member_criteria_pooled_resources_tables": FAC,
    "campaign_group_member_criteria_numeric_ranges_tables": FAC,
    "campaign_group_member_criteria_player_game_difficulty_types_tables": FAC,
    "campaign_group_pooled_resources_tables": FAC,
    "campaign_group_pooled_resource_effects_tables": FAC,
    "campaign_group_faction_effect_bundles_tables": FAC,
    "effect_bundles_tables": FAC,
    "effect_bundles_to_effects_junctions_tables": FAC,
    # regional recruitment: region slot -> building -> unit requirement -> unit
    "start_pos_region_slot_templates_tables": FAC,
    "start_pos_factions_tables": FAC,
    "start_pos_regions_tables": FAC,
    "slot_templates_tables": FAC,
    "slot_template_to_building_superchain_junctions_tables": FAC,
    "building_superchains_tables": FAC,
    "building_chains_tables": FAC,
    "building_levels_tables": FAC,
    "campaign_unit_requirements_tables": FAC,
    "campaign_unit_permission_requirements_tables": FAC,
    "campaign_unit_permissions_tables": FAC,
    "campaign_unit_permission_groups_tables": FAC,
    "campaign_unit_permission_group_to_permission_junctions_tables": FAC,
    "main_units_tables": FAC,
    "land_units_tables": FAC,
    "building_chain_availability_sets_tables": FAC,
    "building_chain_availabilities_tables": FAC,
    "factions_tables": FAC,
}

# old snapshot folders superseded by the *_tables names above
OBSOLETE_DB_FOLDERS = [
    "ceos", "ceo_thresholds", "ceo_threshold_nodes", "ceo_effect_lists",
    "ceo_effect_list_to_effects", "campaign_effect_scopes",
]

VANILLA_LOC = [
    "names__", "effects__", "effects_generalised_descriptions__", "campaign_effect_scopes__",
    "ui_text_replacements__", "ceo_nodes__", "ceos__", "ceo_categories__",
    "character_skills__", "character_skill_node_sets__", "character_skill_level_details__",
    "frontend_faction_leaders__", "frontend_faction_leader_unique_features__",
    "frontend_faction_leader_playstyles__", "frontend_faction_leader_unique_characters__",
    "frontend_characters__", "factions__", "faction_groups__", "cultures_subcultures__",
    "pooled_resources__", "pooled_resource_factors__", "effect_bundles__",
    "political_parties__", "campaign_groups__",
    "land_units__", "unit_description_short_texts__",
]

DRY = "--dry-run" in sys.argv
DO_PORTRAITS = "--no-portraits" not in sys.argv


def log(msg):
    print(msg)


def is_protected(name):
    return any(re.search(p, name) for p in PROTECT_PATTERNS)


def header_of(path):
    with open(path, "r", encoding="utf-8-sig", errors="replace") as f:
        return f.readline().rstrip("\r\n")


def rm(path):
    if DRY:
        return
    if os.path.isdir(path):
        shutil.rmtree(path)
    elif os.path.exists(path):
        os.remove(path)


def cp(src, dst):
    if DRY:
        return
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)


def sync_table(table, sources):
    target = os.path.join(SCRIPT_DIR, "db", table)
    if not DRY:
        os.makedirs(target, exist_ok=True)
    stats = {"deleted": 0, "kept_protected": 0, "vanilla": "-", "mod": 0}

    # 1) clear old mod files (and legacy XML dumps)
    if os.path.isdir(target):
        for f in os.listdir(target):
            p = os.path.join(target, f)
            if f == "data__.tsv":
                continue
            if is_protected(f):
                stats["kept_protected"] += 1
                continue
            rm(p)
            stats["deleted"] += 1

    # 2) vanilla data__.tsv
    for s in sources:
        if not s.startswith("van_"):
            continue
        src = os.path.join(SRC[s], table, "data__.tsv")
        if not os.path.exists(src):
            stats["vanilla"] = "NO VANILLA"
            continue
        dst = os.path.join(target, "data__.tsv")
        if os.path.exists(dst) and header_of(dst) != header_of(src):
            stats["vanilla"] = "HEADER MISMATCH - kept old"
        else:
            cp(src, dst)
            stats["vanilla"] = "refreshed"

    # 3) mod files
    seen = set()
    for s in sources:
        if s.startswith("van_"):
            continue
        folder = os.path.join(SRC[s], table)
        if not os.path.isdir(folder):
            continue
        for f in sorted(os.listdir(folder)):
            src = os.path.join(folder, f)
            if not os.path.isfile(src):
                continue
            name = f
            if not name.lower().endswith(".tsv"):
                # RPFM sometimes exports without extension
                if os.path.getsize(src) > 0 and header_of(src).count("\t") > 0:
                    name = name + ".tsv"
                else:
                    continue
            if name.lower() == "data__.tsv":
                name = f"data__mod_{s}.tsv"
            if name in seen:
                name = f"{s}__{name}"
            seen.add(name)
            cp(src, os.path.join(target, name))
            stats["mod"] += 1
    return stats


def sync_vanilla_loc():
    target = os.path.join(SCRIPT_DIR, "text", "vanilla")
    rm(target)
    n = 0
    for base in VANILLA_LOC:
        src = os.path.join(VAN, "text", "db", base + ".loc.tsv")
        if os.path.exists(src):
            cp(src, os.path.join(target, base + ".loc.tsv"))
            n += 1
        else:
            log(f"  [vanilla loc] missing: {base}")
    return n


def sync_mod_loc():
    n = 0
    for tag, root in (("2_Char", os.path.join(MOD_CHAR, "text")), ("1_Faction", os.path.join(MOD_FAC, "text"))):
        target = os.path.join(SCRIPT_DIR, "text", "mod", tag)
        rm(target)
        for dirpath, _dirs, files in os.walk(root):
            rel = os.path.relpath(dirpath, root)
            for f in files:
                src = os.path.join(dirpath, f)
                name = f
                if f.startswith("test-") and f.endswith(".txt"):
                    continue
                if not f.lower().endswith(".loc.tsv"):
                    # extensionless loc export (e.g. !!!ironic_flags_handan_shang)
                    if os.path.getsize(src) > 0 and header_of(src).startswith("key\t"):
                        name = f + ".loc.tsv"
                    else:
                        continue
                cp(src, os.path.join(target, rel, name))
                n += 1
    return n


def sync_portraits():
    """Copy composites/large_panel/happy/*.png -> images/db/<art folder>.png (only missing)."""
    out = os.path.join(SITE_DATA, "images", "db")
    if not DRY:
        os.makedirs(out, exist_ok=True)
    copied = missing = 0
    for root in (os.path.join(MOD_CHAR, "ui", "characters"), os.path.join(VAN, "ui", "characters")):
        if not os.path.isdir(root):
            continue
        for folder in sorted(os.listdir(root)):
            dst = os.path.join(out, folder + ".png")
            if os.path.exists(dst):
                continue
            happy = os.path.join(root, folder, "composites", "large_panel", "happy")
            pngs = [f for f in os.listdir(happy)] if os.path.isdir(happy) else []
            pngs = [f for f in pngs if f.lower().endswith(".png")]
            if not pngs:
                missing += 1
                continue
            cp(os.path.join(happy, sorted(pngs)[0]), dst)
            copied += 1
    return copied, missing


def main():
    log("=" * 60)
    log("190 Expanded Wiki - sync from mod" + (" (DRY RUN)" if DRY else ""))
    log("=" * 60)
    for k, v in SRC.items():
        log(f"  {k:8s} {v}  {'OK' if os.path.isdir(v) else 'MISSING'}")
    log("")

    for folder in OBSOLETE_DB_FOLDERS:
        p = os.path.join(SCRIPT_DIR, "db", folder)
        if os.path.isdir(p):
            log(f"  removing obsolete folder db/{folder}")
            rm(p)

    log("[1/4] db tables")
    warn = []
    for table, sources in TABLES.items():
        st = sync_table(table, sources)
        log(f"  {table:70s} vanilla={st['vanilla']:12s} mod={st['mod']:3d} deleted={st['deleted']:3d}"
            + (f" protected={st['kept_protected']}" if st["kept_protected"] else ""))
        if "MISMATCH" in st["vanilla"]:
            warn.append(table)
    log("")

    log("[2/4] vanilla loc")
    log(f"  {sync_vanilla_loc()} files")
    log("[3/4] mod loc")
    log(f"  {sync_mod_loc()} files")
    log("")

    if DO_PORTRAITS:
        log("[4/4] portraits")
        c, m = sync_portraits()
        log(f"  copied {c} new portraits, {m} art folders without a happy composite")
    log("")
    if warn:
        log("WARNING header mismatch (old data__.tsv kept): " + ", ".join(warn))
    log("Done.")


if __name__ == "__main__":
    main()
