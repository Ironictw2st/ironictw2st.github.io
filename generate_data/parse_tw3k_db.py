#!/usr/bin/env python3
"""
190 Expanded Wiki - TW3K DB Parser (characters)
===============================================

Inputs (produced by sync_from_mod.py, all relative to this folder):
  db/<table>/data__.tsv + every mod TSV     (merged: vanilla first, mod files overlay)
  text/vanilla/*.loc.tsv, text/mod/**, text/extra/**   (one merged loc dict, later wins)

Exports (written straight into ../total_war/data/):
  characters.js          CHARACTER_DATA / CHARACTER_LOOKUP (by name_key) / CHARACTER_BY_KEY (by template key)
  titles.js
  character_details.js   portrait + formatted career effects + traits + equipment
  traits.js              trait CEO -> resolved title/desc/icon/effects

EFFECT RULE:
- Effect display text MUST come from effects_description_<effect_key>; missing/empty/[HIDDEN] -> skip.
- Scope text from campaign_effect_scopes_localised_text_<scope>; "administered" -> "own character".
- {{tr:...}} tokens resolved from ui_text_replacements loc; [[b]]%+n%[[/b]] => percent, [[b]]%+n[[/b]] => flat.

TRAITS:
- Career selection and trait selection both use the stage-11 key of the template's initial_ceos.
- Stages with fewer than 3 trait CEOs are topped up from the global pool with a FIXED random seed
  so regenerating does not churn the diff.
"""

import os
import json
import re
import random
from collections import defaultdict

from tw3k_common import *  # noqa: F401,F403  (shared loaders + text helpers)
import tw3k_common
from tw3k_common import _s, _dedupe_preserve

# ============================================================================
# CONFIGURATION (relative to script directory)
# ============================================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, "db")

# Hand-maintained corrections for characters the merged tables get wrong; see
# character_overrides.json. Loaded here so a typo in the file fails at import.
_OVERRIDES_PATH = os.path.join(SCRIPT_DIR, "character_overrides.json")
_OVERRIDES = json.load(open(_OVERRIDES_PATH, encoding="utf-8")) if os.path.exists(_OVERRIDES_PATH) else {}
OVERRIDE_RENAME = _OVERRIDES.get("rename", {})
OVERRIDE_HIDE = set(_OVERRIDES.get("hide", {}))

# The year the 190 campaign opens. Characters born after it are not on the map at the start,
# which is the honest thing to say about a birth year in the 200s rather than leaving a
# reader to assume the wiki has it wrong - the most common report in #website-feedback.
CAMPAIGN_START_YEAR = 190


def _age_at_start(birth_year):
    """Years old at the opening of the 190 campaign, or None if born after it."""
    if not str(birth_year).isdigit():
        return None
    age = CAMPAIGN_START_YEAR - int(birth_year)
    return age if age >= 0 else None
TEXT_ROOT = os.path.join(SCRIPT_DIR, "text")
SITE_DATA = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "total_war", "data"))

OUTPUT_PATH = os.path.join(SITE_DATA, "characters.js")
TITLES_OUTPUT_PATH = os.path.join(SITE_DATA, "titles.js")
CHAR_DETAILS_OUTPUT_PATH = os.path.join(SITE_DATA, "character_details.js")
TRAITS_OUTPUT_PATH = os.path.join(SITE_DATA, "traits.js")
SUMMARY_PATH = os.path.join(SCRIPT_DIR, "last_run_characters.json")

CAMPAIGN_190 = "3k_main_campaign_map"  # "Rise of the Warlords" (8p_start_pos = Gathering of Heroes mode)

DEBUG_MISSING = True
RANDOM_SEED = 190

# Optional: force certain characters to resolve using a different key for fallback searches
NAME_KEY_OVERRIDES = {
    # "zhang_lu": "zhang_luo",
}


def resolve_name_key(name_key):
    return NAME_KEY_OVERRIDES.get(name_key, name_key)


# The six character attributes are their own effect keys, so the sortable numbers on the
# Characters page are summed from these rather than parsed out of the display text.
ATTRIBUTE_KEYS = {
    "3k_main_effect_character_attribute_authority_mod": "authority",
    "3k_main_effect_character_attribute_cunning_mod": "cunning",
    "3k_main_effect_character_attribute_expertise_mod": "expertise",
    "3k_main_effect_character_attribute_instinct_mod": "instinct",
    "3k_main_effect_character_attribute_resolve_mod": "resolve",
    "3k_main_effect_character_num_lives": "resilience",
}
ATTRIBUTE_ORDER = ["authority", "cunning", "expertise", "instinct", "resolve", "resilience"]


def _effect_value(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _first(row, *cols):
    for c in cols:
        v = _s(row.get(c, ""))
        if v:
            return v
    return ""


# ============================================================================
# MAIN
# ============================================================================

def main():
    random.seed(RANDOM_SEED)
    print("=" * 60)
    print("190 Expanded Wiki - Character Parser")
    print("=" * 60)
    print()

    if not os.path.exists(DB_PATH):
        print(f"ERROR: Database folder not found: {DB_PATH}")
        return

    # ------------------------------------------------------------------ loc
    print("[1/9] Loading localisation (text/vanilla -> text/mod -> text/extra)...")
    LOC = load_site_loc(TEXT_ROOT)
    print(f"  {len(LOC)} loc keys")

    loc_titles, loc_descs = {}, {}
    for k, v in LOC.items():
        if k.startswith("ceo_nodes_title_"):
            loc_titles[k[len("ceo_nodes_title_"):]] = v
        elif k.startswith("ceo_nodes_description_"):
            loc_descs[k[len("ceo_nodes_description_"):]] = v
    print(f"  ceo node titles: {len(loc_titles)}, descriptions: {len(loc_descs)}")
    all_titles_kv = LOC  # fallback scan space for fallback_career_title_desc()

    names_lookup, alt_names_lookup = {}, {}
    for k, v in LOC.items():
        m = re.match(r"names_name_(\d+)$", k)
        if m:
            names_lookup[m.group(1)] = v
            continue
        m = re.match(r"names_alt_name_(\d+)$", k)
        if m:
            alt_names_lookup[m.group(1)] = v
    print(f"  names: {len(names_lookup)}, alt names: {len(alt_names_lookup)}")

    effects_loc_kv = sub_loc(LOC, "effects_")
    scope_loc_kv = sub_loc(LOC, "campaign_effect_scopes_")
    tw3k_common.set_ui_text_replacements(build_ui_text_replacements(LOC))
    print(f"  effect loc keys: {len(effects_loc_kv)}, scope loc keys: {len(scope_loc_kv)}, "
          f"ui text replacements: {len(tw3k_common._ui_text_replacements_kv)}")
    print()

    # ------------------------------------------------------------ templates
    print("[2/9] Loading character templates...")
    templates_by_key = {}
    rows, files = load_table(DB_PATH, "character_generation_templates_tables")
    for t in rows:
        key = _s(t.get("key", ""))
        if key:
            templates_by_key[key] = t
    templates = list(templates_by_key.values())
    print(f"  {len(files)} files -> {len(templates)} templates")
    print()

    # ----------------------------------------------------------------- arts
    print("[3/9] Loading campaign character arts...")
    art_to_portrait = load_campaign_character_arts(DB_PATH)
    print(f"  {len(art_to_portrait)} art set -> portrait mappings")
    print()

    # ------------------------------------------------------ game mode details
    print("[4/9] Loading game mode details...")
    template_to_initial_ceos = {}
    template_to_skill_set = {}
    rows, files = load_table(DB_PATH, "character_generation_template_game_mode_details_tables")
    for gmd in rows:
        template_key = _s(gmd.get("character_generation_template", ""))
        initial_ceos = _s(gmd.get("initial_ceos", ""))
        skill_set = _first(gmd, "skill set override", "skill_set_override")
        if template_key and initial_ceos:
            template_to_initial_ceos[template_key] = initial_ceos
        if template_key and skill_set:
            template_to_skill_set[template_key] = skill_set
    print(f"  {len(files)} files -> {len(template_to_initial_ceos)} ceo mappings, {len(template_to_skill_set)} skill set mappings")
    print()

    # ------------------------------------------------------------ ceo chain
    print("[5/9] Loading CEO initial data (stages / active ceos / equipment)...")
    stages_data, files = load_table(DB_PATH, "ceo_initial_data_to_stages_tables")
    initial_data_to_stage11, initial_data_to_stage3 = {}, {}
    for row in stages_data:
        stage_val = _first(row, "stage", "stage_level", "stage_id", "ceo_stage")
        ceo_initial_data = _first(row, "ceo_initial_data", "initial_data", "ceo_initial_data_key")
        initial_data_stage = _first(row, "initial_data_stage", "stage_key", "ceo_initial_data_stage")
        if not (ceo_initial_data and initial_data_stage and stage_val):
            continue
        if stage_val == "11":
            initial_data_to_stage11[ceo_initial_data] = initial_data_stage
        elif stage_val == "3":
            initial_data_to_stage3[ceo_initial_data] = initial_data_stage
    print(f"  to_stages: {len(files)} files, {len(stages_data)} rows -> stage11 {len(initial_data_to_stage11)}, stage3 {len(initial_data_to_stage3)}")

    active_data, files = load_table(DB_PATH, "ceo_initial_data_active_ceos_tables")
    stage_to_career_ceo = {}
    stage_to_trait_ceos = defaultdict(list)
    trait_ceo_pool = []
    for row in active_data:
        stage = _first(row, "initial_data_stage", "stage", "stage_key")
        active_ceo = _first(row, "active_ceo", "ceo", "ceo_key")
        if not (stage and active_ceo):
            continue
        lower = active_ceo.lower()
        if "career" in lower:
            stage_to_career_ceo[stage] = active_ceo
        if "trait_" in lower:
            stage_to_trait_ceos[stage].append(active_ceo)
            trait_ceo_pool.append(active_ceo)
    trait_ceo_pool = _dedupe_preserve(trait_ceo_pool)
    for st, lst in list(stage_to_trait_ceos.items()):
        stage_to_trait_ceos[st] = _dedupe_preserve(lst)
    print(f"  active_ceos: {len(files)} files, {len(active_data)} rows -> {len(stage_to_career_ceo)} career CEOs, "
          f"traits for {sum(1 for l in stage_to_trait_ceos.values() if l)} stages, pool {len(trait_ceo_pool)}")

    equipment_data, files = load_table(DB_PATH, "ceo_initial_data_equipments_tables")
    ANCILLARY_CATEGORIES = {
        "3k_main_ceo_category_ancillary_armour": "armour",
        "3k_main_ceo_category_ancillary_mount": "mount",
        "3k_main_ceo_category_ancillary_weapon": "weapon",
        "3k_main_ceo_category_ancillary_accessory": "accessory",
        "3k_main_ceo_category_ancillary_follower": "follower",
    }
    stage3_to_equipment = defaultdict(list)
    for eq_row in equipment_data:
        initial_data_stage = _s(eq_row.get("initial_data_stage", ""))
        category = _s(eq_row.get("category", ""))
        equipped_ceo = _s(eq_row.get("equipped_ceo", ""))
        if initial_data_stage and category in ANCILLARY_CATEGORIES and equipped_ceo:
            if any(e["equipped_ceo"] == equipped_ceo and e["category"] == category
                   for e in stage3_to_equipment[initial_data_stage]):
                continue
            stage3_to_equipment[initial_data_stage].append({
                "category": category,
                "category_name": ANCILLARY_CATEGORIES[category],
                "equipped_ceo": equipped_ceo,
            })
    print(f"  equipments: {len(files)} files, {len(equipment_data)} rows -> {len(stage3_to_equipment)} stage3 keys")
    print()

    print("[6/9] Loading CEO thresholds / nodes / effect lists...")
    thresholds_data, files = load_table(DB_PATH, "ceo_thresholds_tables")
    ceo_to_threshold = {}
    for row in thresholds_data:
        ceo, threshold_key = _s(row.get("ceo", "")), _s(row.get("key", ""))
        if ceo and threshold_key:
            ceo_to_threshold[ceo] = threshold_key
    print(f"  thresholds: {len(files)} files, {len(ceo_to_threshold)} ceo->threshold")

    threshold_nodes_data, files = load_table(DB_PATH, "ceo_threshold_nodes_tables")
    threshold_to_nodes = defaultdict(list)
    for row in threshold_nodes_data:
        threshold, node = _s(row.get("ceo_threshold", "")), _s(row.get("ceo_node", ""))
        if threshold and node and node not in threshold_to_nodes[threshold]:
            threshold_to_nodes[threshold].append(node)
    print(f"  threshold_nodes: {len(files)} files, {len(threshold_to_nodes)} thresholds with nodes")

    ceo_nodes, files = load_table_dict(DB_PATH, "ceo_nodes_tables", key_field="key")
    print(f"  ceo_nodes: {len(files)} files, {len(ceo_nodes)} nodes")

    el_rows, files = load_table(DB_PATH, "ceo_effect_list_to_effects_tables")
    effect_list_map = defaultdict(list)
    _seen_el = set()
    for r in el_rows:
        lk, ek = _s(r.get("effect_list", "")), _s(r.get("effect", ""))
        if lk and ek:
            entry = {
                "effect_key": ek,
                "value": _s(r.get("value", "")),
                "scope": _s(r.get("effect_scope", "")),
                "optional_only_in_game_mode": _s(r.get("optional_only_in_game_mode", "")),
            }
            sig = (lk, ek, entry["value"], entry["scope"], entry["optional_only_in_game_mode"])
            if sig in _seen_el:
                continue  # vanilla rows repeated in the mod's own data__ copy
            _seen_el.add(sig)
            effect_list_map[lk].append(entry)
    effect_list_map = dict(effect_list_map)
    print(f"  effect_list_to_effects: {len(files)} files, {len(el_rows)} rows, {len(effect_list_map)} lists")
    print()

    print("[7/9] Loading age ranges...")
    age_lookup = {}
    rows, files = load_table(DB_PATH, "character_generation_spawn_age_ranges_tables")
    for age in rows:
        k = _s(age.get("key", ""))
        if k:
            age_lookup[k] = _s(age.get("birth_year", ""))
    print(f"  {len(age_lookup)} age ranges")
    print()

    # ------------------------------------------------- faction leader links
    print("[8/9] Loading faction leader links (190 campaign)...")
    fc_rows, _ = load_table(DB_PATH, "frontend_characters_tables")
    fc_to_template = {_s(r.get("key", "")): _s(r.get("character_generation_template", "")) for r in fc_rows}
    fl_rows, _ = load_table(DB_PATH, "frontend_faction_leaders_tables")
    leader_to_fc = {_s(r.get("key", "")): _s(r.get("frontend_character", "")) for r in fl_rows}
    spine, _ = load_table(DB_PATH, "frontend_faction_to_frontend_faction_leaders_tables")
    template_to_leaders = defaultdict(list)
    for r in spine:
        if _s(r.get("campaign_key", "")) != CAMPAIGN_190:
            continue
        leader = _s(r.get("frontend_faction_leader", ""))
        tmpl = fc_to_template.get(leader_to_fc.get(leader, ""), "") or fc_to_template.get(leader, "")
        if tmpl and leader not in template_to_leaders[tmpl]:
            template_to_leaders[tmpl].append(leader)
    print(f"  {len(template_to_leaders)} leader templates")
    print()

    print("[9/9] Processing characters...")
    # ============================================================================
    # Process characters
    # ============================================================================

    print("Processing characters...")
    characters = []
    character_details = {}
    trait_defs = {}

    def build_trait_def(trait_ceo_key: str):
        """Resolve a trait CEO -> best node -> (title, description, icon_path, effects)."""
        tkey = _s(trait_ceo_key)
        if not tkey:
            return None
        if tkey in trait_defs:
            return trait_defs[tkey]

        t_threshold = _s(ceo_to_threshold.get(tkey, ""))
        t_node_key = ""
        t_title = ""
        t_desc = ""
        t_icon_path = ""
        t_effects_out = []

        if t_threshold:
            t_node_key = pick_best_ceo_node(t_threshold, threshold_to_nodes, ceo_nodes, loc_titles, loc_descs)
            if t_node_key:
                node_data = ceo_nodes.get(t_node_key, {})
                t_title = _s(node_data.get("title", ""))
                t_desc = _s(node_data.get("description", ""))
                t_icon_path = _s(node_data.get("icon_path", ""))

                # loc overrides (same idea as career)
                if t_node_key in loc_titles:
                    t_title = loc_titles[t_node_key]
                if t_node_key in loc_descs:
                    t_desc = loc_descs[t_node_key]

                effect_list_key = extract_effect_list_from_ceo_node(node_data)
                if effect_list_key:
                    for er in effect_list_map.get(effect_list_key, []):
                        eff_key = _s(er.get("effect_key", ""))
                        val = _s(er.get("value", ""))
                        scp = _s(er.get("scope", ""))
                        opt = _s(er.get("optional_only_in_game_mode", ""))
                        line = format_effect_line(eff_key, val, scp, opt, effects_loc_kv, scope_loc_kv)
                        if not line:
                            continue
                        t_effects_out.append({"name": line, "desc": ""})

        trait_def = {
            "key": tkey,
            "node": t_node_key,
            "title": t_title,
            "description": t_desc,
            "icon_path": t_icon_path,
            "effects": t_effects_out,
        }
        trait_defs[tkey] = trait_def
        return trait_def

    # Cache for ancillary definitions
    ancillary_defs = {}

    def build_ancillary_def(ancillary_ceo_key: str, category_name: str):
        """
        Resolve an ancillary CEO -> best node -> (title, description, icon_path, effects).
        Similar to build_trait_def but for equipment (armour, weapon, mount, accessory, follower).
        """
        akey = _s(ancillary_ceo_key)
        if not akey:
            return None
        
        cache_key = f"{akey}_{category_name}"
        if cache_key in ancillary_defs:
            return ancillary_defs[cache_key]

        a_threshold = _s(ceo_to_threshold.get(akey, ""))
        a_node_key = ""
        a_title = ""
        a_desc = ""
        a_icon_path = ""
        a_effects_out = []
        a_effects_struct = []

        def _populate_from_node(node_key: str):
            nonlocal a_node_key, a_title, a_desc, a_icon_path, a_effects_out
            a_node_key = _s(node_key)
            node_data = ceo_nodes.get(a_node_key, {})
            a_title = _s(node_data.get("title", ""))
            a_desc = _s(node_data.get("description", ""))
            a_icon_path = _s(node_data.get("icon_path", ""))

            # loc overrides
            if a_node_key in loc_titles:
                a_title = loc_titles[a_node_key]
            if a_node_key in loc_descs:
                a_desc = loc_descs[a_node_key]

            # Get effects from the node's effect list
            effect_list_key = extract_effect_list_from_ceo_node(node_data)
            if effect_list_key:
                for er in effect_list_map.get(effect_list_key, []):
                    eff_key = _s(er.get("effect_key", ""))
                    val = _s(er.get("value", ""))
                    scp = _s(er.get("scope", ""))
                    opt = _s(er.get("optional_only_in_game_mode", ""))
                    line = format_effect_line(eff_key, val, scp, opt, effects_loc_kv, scope_loc_kv)
                    if not line:
                        continue
                    a_effects_out.append({"name": line, "desc": ""})
                    # kept for the Characters page index, stripped back out before
                    # character_details.js is written
                    a_effects_struct.append((eff_key, val))

        # PRIMARY: CEO -> threshold -> node
        if a_threshold:
            best_node = pick_best_ceo_node(a_threshold, threshold_to_nodes, ceo_nodes, loc_titles, loc_descs)
            if best_node:
                _populate_from_node(best_node)
        else:
            # FALLBACK 1: some tables store the node key directly in equipped_ceo
            if akey in ceo_nodes:
                _populate_from_node(akey)
            # FALLBACK 2: sometimes equipped_ceo is already a threshold key
            elif akey in threshold_to_nodes:
                best_node = pick_best_ceo_node(akey, threshold_to_nodes, ceo_nodes, loc_titles, loc_descs)
                if best_node:
                    _populate_from_node(best_node)
        ancillary_def = {
            "key": akey,
            "category": category_name,
            "node": a_node_key,
            "title": a_title,
            "description": a_desc,
            "icon_path": a_icon_path,
            "effects": a_effects_out,
            "effects_struct": a_effects_struct,
        }
        
        print("EQUIP RESOLVE", category_name, "ceo=", akey, "threshold=", a_threshold, "node=", a_node_key, "icon=", a_icon_path)
        ancillary_defs[cache_key] = ancillary_def
        return ancillary_def

    def get_equipment_for_stage3(stage3_key: str):
        """
        Get all equipment (ancillaries) for a given stage3 key.
        Returns a dict with keys: armour, weapon, mount, accessory, follower
        Each value is either None or a resolved ancillary definition.
        """
        equipment = {
            "armour": None,
            "weapon": None,
            "mount": None,
            "accessory": None,
            "follower": None,
        }
        
        stage3 = _s(stage3_key)
        if not stage3:
            return equipment
        
        equip_list = stage3_to_equipment.get(stage3, [])
        for eq in equip_list:
            cat_name = eq.get("category_name", "")
            equipped_ceo = eq.get("equipped_ceo", "")
            
            if cat_name and equipped_ceo and cat_name in equipment:
                ancillary_def = build_ancillary_def(equipped_ceo, cat_name)
                if ancillary_def and (ancillary_def.get("title") or ancillary_def.get("icon_path") or ancillary_def.get("description")):
                    equipment[cat_name] = ancillary_def
        
        return equipment

    def pick_traits_for_stage(stage11_key: str, min_traits: int = 3):
        """
        Return a list of trait CEOs for a stage.
        - If stage has trait CEOs: return those (deduped)
        - If missing: sample from global pool
        - Ensure at least min_traits when possible (mix stage traits + random fill)
        """
        stage = _s(stage11_key)
        chosen = []
        if stage:
            chosen = list(stage_to_trait_ceos.get(stage, []))  # already deduped

        chosen = _dedupe_preserve([c for c in chosen if c])

        # If we have fewer than min_traits, fill from pool
        if len(chosen) < min_traits and trait_ceo_pool:
            pool = [t for t in trait_ceo_pool if t not in set(chosen)]
            random.shuffle(pool)
            need = min_traits - len(chosen)
            chosen.extend(pool[:need])

        return _dedupe_preserve(chosen)

    for template in templates:
        key = _s(template.get("key", ""))
        if not key:
            continue

        # keep historical + generated heroes; skip generic non-historical
        if ("generic" in key.lower()) and ("historical" not in key.lower()):
            continue

        name_match = re.search(r"template_(?:historical|generated)_(?:lady_)?(.+?)_hero_", key)
        if not name_match:
            name_match = re.search(r"template_(?:historical|generated)_(?:lady_)?(.+?)_(fire|earth|water|wood|metal|nanman)$", key)
        if not name_match:
            continue

        char_name_key = _s(name_match.group(1))
        element = extract_element_from_key(key)

        forename_id = _s(template.get("forename", "0"))
        family_name_id = _s(template.get("family_name", "0"))
        clan_name_id = _s(template.get("clan_name", "0"))  # Courtesy name ID

        forename = names_lookup.get(forename_id, "")
        family_name = names_lookup.get(family_name_id, "")
        courtesy_name = names_lookup.get(clan_name_id, "")

        # hand-maintained corrections; see character_overrides.json for why each exists
        if key in OVERRIDE_HIDE:
            continue
        _ov = OVERRIDE_RENAME.get(key)
        if _ov:
            forename = _ov.get("forename", forename)
            family_name = _ov.get("family_name", family_name)

        forename_alt = alt_names_lookup.get(forename_id, "")
        family_name_alt = alt_names_lookup.get(family_name_id, "")
        courtesy_name_alt = alt_names_lookup.get(clan_name_id, "")

        if forename and family_name:
            display_name = f"{family_name} {forename}"
        elif forename:
            display_name = forename
        elif family_name:
            display_name = family_name
        else:
            display_name = char_name_key.replace("_", " ").title()

        if forename_alt and family_name_alt:
            display_name_alt = f"{family_name_alt}{forename_alt}"
        elif forename_alt:
            display_name_alt = forename_alt
        elif family_name_alt:
            display_name_alt = family_name_alt
        else:
            display_name_alt = ""

        spawn_age_key = _s(template.get("spawn_age_range", ""))
        birth_year = age_lookup.get(spawn_age_key, "")

        # CEO chain (career -> node -> title/desc)
        title = ""
        description = ""
        ceo_node_key = ""

        initial_ceos = _s(template_to_initial_ceos.get(key, ""))
        stage11_key = ""
        stage3_key = ""
        career_ceo = ""
        threshold = ""

        if initial_ceos:
            stage11_key = _s(initial_data_to_stage11.get(initial_ceos, ""))
            stage3_key = _s(initial_data_to_stage3.get(initial_ceos, ""))
            if stage11_key:
                career_ceo = _s(stage_to_career_ceo.get(stage11_key, ""))
                if career_ceo:
                    threshold = _s(ceo_to_threshold.get(career_ceo, ""))
                    if threshold:
                        ceo_node_key = pick_best_ceo_node(threshold, threshold_to_nodes, ceo_nodes, loc_titles, loc_descs)
                        if ceo_node_key:
                            node_data = ceo_nodes.get(ceo_node_key, {})
                            title = _s(node_data.get("title", ""))
                            description = _s(node_data.get("description", ""))

        # Traits (static): ALL trait_* for stage11; ensure at least 3
        trait_ceos = pick_traits_for_stage(stage11_key, min_traits=3)
        for t in trait_ceos:
            build_trait_def(t)

        # override from loc patterns if available
        if ceo_node_key:
            if ceo_node_key in loc_titles:
                title = loc_titles[ceo_node_key]
            if ceo_node_key in loc_descs:
                description = loc_descs[ceo_node_key]

        if not title and char_name_key in loc_titles:
            title = loc_titles[char_name_key]
        if not title and (char_name_key + "_ironic") in loc_titles:
            title = loc_titles[char_name_key + "_ironic"]

        if not description and char_name_key in loc_descs:
            description = loc_descs[char_name_key]
        if not description and (char_name_key + "_ironic") in loc_descs:
            description = loc_descs[char_name_key + "_ironic"]

        resolved_key = resolve_name_key(char_name_key)
        if (not title) or (not description):
            fb_title, fb_desc = fallback_career_title_desc(resolved_key, all_titles_kv)
            if not title and fb_title:
                title = fb_title
            if not description and fb_desc:
                description = fb_desc

        if DEBUG_MISSING and (not title or not description):
            print(
                f"[MISSING] {display_name} ({char_name_key}) "
                f"initial_ceos={bool(initial_ceos)} stage11={bool(stage11_key)} stage3={bool(stage3_key)} "
                f"career={bool(career_ceo)} threshold={bool(threshold)} node={ceo_node_key or 'NONE'} "
                f"title={bool(title)} desc={bool(description)}"
            )

        computed_is_unique = ("generic" not in stage3_key.lower())

        # Get skill set for this character template
        skill_set = template_to_skill_set.get(key, "")

        char_record = {
            "key": key,
            "faction_leader_of": template_to_leaders.get(key, []),
            "name_key": char_name_key,
            "display_name": display_name,
            "display_name_alt": display_name_alt,
            "forename": forename,
            "family_name": family_name,
            "forename_alt": forename_alt,
            "family_name_alt": family_name_alt,
            "courtesy_name": courtesy_name,
            "courtesy_name_alt": courtesy_name_alt,
            "title": title,
            "description": description,
            "element": element,
            "subtype": _s(template.get("subtype", "")),
            "is_male": _s(template.get("is_male", "true")).lower() == "true",
            "is_unique": computed_is_unique,
            "birth_year": birth_year,
            # age_at_start is None when the character is not yet born in 190; the pages use
            # that to say so outright. There is no death year anywhere in the tables, so the
            # field that used to carry the literal "???" is gone rather than rendered.
            "age_at_start": _age_at_start(birth_year),
            "traits": trait_ceos,
            "skill_set": skill_set,
        }
        characters.append(char_record)

        # =========================
        # Character Details (effects + portrait + equipment)
        # =========================
        effects_out = []
        effects_struct = []   # (effect_key, value) for the Characters page index

        if ceo_node_key:
            node_data = ceo_nodes.get(ceo_node_key, {})
            effect_list_key = extract_effect_list_from_ceo_node(node_data)
            if effect_list_key:
                for er in effect_list_map.get(effect_list_key, []):
                    eff_key = _s(er.get("effect_key", ""))
                    val = _s(er.get("value", ""))
                    scp = _s(er.get("scope", ""))
                    opt = _s(er.get("optional_only_in_game_mode", ""))
                    line = format_effect_line(eff_key, val, scp, opt, effects_loc_kv, scope_loc_kv)
                    if not line:
                        continue
                    effects_out.append({"name": line, "desc": ""})
                    effects_struct.append((eff_key, val))

        # Portrait
        art_set_override = _s(template.get("art_set_override", ""))
        portrait_url = ""

        if art_set_override:
            if art_set_override in art_to_portrait:
                portrait_key = art_to_portrait[art_set_override]
                portrait_url = convert_portrait_to_url(portrait_key)
            elif DEBUG_MISSING:
                print(f"[NO PORTRAIT] {display_name}: art_set_override='{art_set_override}' not in art_to_portrait")

        # Equipment (ancillaries): armour, weapon, mount, accessory, follower
        equipment_out = get_equipment_for_stage3(stage3_key)
        
        # Convert equipment to output format (only include non-None entries)
        equipment_data = {}
        for cat_name, anc_def in equipment_out.items():
            if anc_def and anc_def.get("title"):
                equipment_data[cat_name] = {
                    "key": anc_def.get("key", ""),
                    "title": anc_def.get("title", ""),
                    "description": anc_def.get("description", ""),
                    "icon_path": anc_def.get("icon_path", ""),
                    "effects": anc_def.get("effects", []),
                }
                # equipment counts toward the sortable numbers; the structured form stays
                # out of character_details.js, which only needs the display lines
                effects_struct.extend(anc_def.get("effects_struct", []))

        has_equipment = bool(equipment_data)

        # Index for the Characters page: attribute totals plus the set of other effect keys.
        attributes = {}
        other_keys = set()
        for eff_key, val in effects_struct:
            attr = ATTRIBUTE_KEYS.get(eff_key)
            if attr:
                attributes[attr] = attributes.get(attr, 0.0) + _effect_value(val)
            else:
                other_keys.add(eff_key)
        char_record["attributes"] = {
            a: int(attributes[a]) if float(attributes[a]).is_integer() else round(attributes[a], 2)
            for a in ATTRIBUTE_ORDER if attributes.get(a)
        }
        char_record["_effect_keys"] = sorted(other_keys)   # swapped for ids once the table is built

        if effects_out or portrait_url or has_equipment:
            character_details[key] = {
                "portrait": {
                    "url": portrait_url,
                    "alt": f"{display_name} portrait",
                    "caption": ""
                },
                "effects": effects_out,
                "traits": trait_ceos,
                "equipment": equipment_data,
            }

    characters.sort(key=lambda x: x["display_name"])

    # ------------------------------------------------------------------
    # Effect index for the Characters page.
    # One entry per non-attribute effect key that reaches at least one character, so the
    # list page can filter by effect without loading character_details.js (4 MB).
    # ------------------------------------------------------------------
    # Group by LABEL, not by effect key. The same wording is often delivered by several keys
    # (satisfaction has 8, public order 4), and somebody filtering for "income from all sources"
    # wants every character who gets it, not just those on one of the two keys behind it.
    keys_by_label = defaultdict(set)
    label_display = {}
    for c in characters:
        for k in c.get("_effect_keys", []):
            _raw, label = resolve_effect_loc(k, effects_loc_kv)
            if not label:
                continue   # nothing to show in the control, so nothing to filter on
            low = label.lower()
            keys_by_label[low].add(k)
            label_display.setdefault(low, label)

    effect_types = [{"label": label_display[low], "keys": sorted(ks)} for low, ks in keys_by_label.items()]
    effect_types.sort(key=lambda e: e["label"].lower())
    group_id_by_key = {}
    for i, e in enumerate(effect_types):
        e["id"] = i
        for k in e["keys"]:
            group_id_by_key[k] = i

    for c in characters:
        c["effects"] = sorted({group_id_by_key[k] for k in c.pop("_effect_keys", []) if k in group_id_by_key})

    group_counts = defaultdict(int)
    for c in characters:
        for i in c["effects"]:
            group_counts[i] += 1
    for e in effect_types:
        e["count"] = group_counts[e["id"]]

    with_attributes = sum(1 for c in characters if c.get("attributes"))
    print(f"  Effect index: {len(effect_types)} effect types, "
          f"{sum(len(c['effects']) for c in characters)} character-effect links")
    print(f"  With attribute totals: {with_attributes}")

    with_titles = sum(1 for c in characters if c["title"])
    with_desc = sum(1 for c in characters if c["description"])
    with_portraits = sum(1 for _, v in character_details.items() if v.get("portrait", {}).get("url"))
    with_skill_sets = sum(1 for c in characters if c.get("skill_set"))
    with_equipment = sum(1 for _, v in character_details.items() if v.get("equipment"))
    
    # Count by equipment type
    equip_counts = {"armour": 0, "weapon": 0, "mount": 0, "accessory": 0, "follower": 0}
    for _, v in character_details.items():
        eq = v.get("equipment", {})
        for cat in equip_counts:
            if eq.get(cat):
                equip_counts[cat] += 1

    print(f"  Processed {len(characters)} characters")
    print(f"  With titles: {with_titles}")
    print(f"  With descriptions: {with_desc}")
    print(f"  With portraits: {with_portraits}")
    print(f"  With effects entries: {len(character_details)}")
    print(f"  With skill sets: {with_skill_sets}")
    print(f"  With equipment: {with_equipment}")
    print(f"    - Armour: {equip_counts['armour']}")
    print(f"    - Weapon: {equip_counts['weapon']}")
    print(f"    - Mount: {equip_counts['mount']}")
    print(f"    - Accessory: {equip_counts['accessory']}")
    print(f"    - Follower: {equip_counts['follower']}")
    print()

    # ============================================================================
    # Output JS files
    # ============================================================================

    print("Generating output files...")
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    effect_types_json = json.dumps(
        [{"id": e["id"], "label": e["label"], "count": e["count"], "keys": e["keys"]} for e in effect_types],
        indent=2, ensure_ascii=False)

    def _compact_index_fields(js):
        """
        indent=2 puts every effect id and attribute on its own line, which adds about
        400 KB to a file the Characters page loads up front. Collapse those two fields
        onto one line each; everything else keeps the readable formatting.
        """
        js = re.sub(r'"(effects|traits|faction_leader_of)": \[\s*\n\s*([^\[\]]*?)\s*\n\s*\]',
                    lambda m: '"%s": [%s]' % (m.group(1), " ".join(m.group(2).split())), js)
        js = re.sub(r'"attributes": \{\s*\n\s*([^{}]*?)\s*\n\s*\}',
                    lambda m: '"attributes": {%s}' % " ".join(m.group(1).split()), js)
        return js

    js_output = f"""// Auto-generated character data for 190 Expanded Wiki
// Total characters: {len(characters)}
// Effect types: {len(effect_types)}

const CHARACTER_DATA = {_compact_index_fields(json.dumps(characters, indent=2, ensure_ascii=False))};

const CHARACTER_LOOKUP = {{}};
CHARACTER_DATA.forEach(char => {{ CHARACTER_LOOKUP[char.name_key] = char; }});

const CHARACTER_BY_KEY = {{}};
CHARACTER_DATA.forEach(char => {{ CHARACTER_BY_KEY[char.key] = char; }});

// Effect index: char.effects holds ids into this table. Attribute effects are not listed
// here, because they are already summed into char.attributes.
const EFFECT_TYPES = {effect_types_json};

const EFFECT_TYPE_BY_ID = {{}};
EFFECT_TYPES.forEach(e => {{ EFFECT_TYPE_BY_ID[e.id] = e; }});

const CHARACTERS_BY_ELEMENT = {{
  fire: CHARACTER_DATA.filter(c => c.element === 'fire'),
  earth: CHARACTER_DATA.filter(c => c.element === 'earth'),
  water: CHARACTER_DATA.filter(c => c.element === 'water'),
  wood: CHARACTER_DATA.filter(c => c.element === 'wood'),
  metal: CHARACTER_DATA.filter(c => c.element === 'metal'),
  nanman: CHARACTER_DATA.filter(c => c.element === 'nanman'),
}};

const CHARACTER_STATS = {{
  total: CHARACTER_DATA.length,
  unique: CHARACTER_DATA.filter(c => c.is_unique).length,
  male: CHARACTER_DATA.filter(c => c.is_male).length,
  female: CHARACTER_DATA.filter(c => !c.is_male).length,
  byElement: {{
    fire: CHARACTERS_BY_ELEMENT.fire.length,
    earth: CHARACTERS_BY_ELEMENT.earth.length,
    water: CHARACTERS_BY_ELEMENT.water.length,
    wood: CHARACTERS_BY_ELEMENT.wood.length,
    metal: CHARACTERS_BY_ELEMENT.metal.length,
    nanman: CHARACTERS_BY_ELEMENT.nanman.length
  }}
}};
"""
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(js_output)
    print(f"  Written: {OUTPUT_PATH}")

    # titles.js
    titles_map = {c["name_key"]: c["title"] for c in characters if c["title"]}
    os.makedirs(os.path.dirname(TITLES_OUTPUT_PATH), exist_ok=True)

    titles_js = "const CHARACTER_TITLES = {\n"
    for k, v in sorted(titles_map.items()):
        safe = v.replace("\\", "\\\\").replace('"', '\\"')
        titles_js += f'  "{k}": "{safe}",\n'
    titles_js += "};\n"

    with open(TITLES_OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(titles_js)
    print(f"  Written: {TITLES_OUTPUT_PATH}")

    # character_details.js
    os.makedirs(os.path.dirname(CHAR_DETAILS_OUTPUT_PATH), exist_ok=True)
    details_js = "// Auto-generated character details (portraits + effects + equipment)\n"
    details_js += f"// Total entries: {len(character_details)}\n"
    details_js += f"// With equipment: {with_equipment}\n\n"
    details_js += "const CHARACTER_DETAILS = "
    details_js += json.dumps(character_details, indent=2, ensure_ascii=False)
    details_js += ";\n\n"
    details_js += "const CHARACTER_DETAILS_LOOKUP = CHARACTER_DETAILS;\n"

    with open(CHAR_DETAILS_OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(details_js)
    print(f"  Written: {CHAR_DETAILS_OUTPUT_PATH}")

    # traits.js
    os.makedirs(os.path.dirname(TRAITS_OUTPUT_PATH), exist_ok=True)
    trait_list = list(trait_defs.values())
    trait_list.sort(key=lambda x: x.get("key", ""))

    traits_js = f"""// Auto-generated trait data (trait_* CEOs)
const TRAIT_DATA = {json.dumps(trait_list, indent=2, ensure_ascii=False)};

const TRAIT_LOOKUP = {{}};
TRAIT_DATA.forEach(t => {{ TRAIT_LOOKUP[t.key] = t; }});
"""

    with open(TRAITS_OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(traits_js)
    print(f"  Written: {TRAITS_OUTPUT_PATH}")

    with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
        json.dump({
            "characters": len(characters), "titles": with_titles, "descriptions": with_desc,
            "portraits": with_portraits, "details": len(character_details), "skill_sets": with_skill_sets,
            "equipment": with_equipment, "traits": len(trait_defs),
            "missing_portrait": [c["display_name"] for c in characters
                                 if not character_details.get(c["key"], {}).get("portrait", {}).get("url")],
        }, f, indent=2, ensure_ascii=False)
    print(f"  Written: {SUMMARY_PATH}")

    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Total: {len(characters)}, Titles: {with_titles}, Descriptions: {with_desc}, Details: {len(character_details)}, Skill Sets: {with_skill_sets}, Equipment: {with_equipment}")
    print()


if __name__ == "__main__":
    main()
