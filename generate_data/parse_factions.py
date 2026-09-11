#!/usr/bin/env python3
"""
190 Expanded Wiki - Faction Parser
==================================

Builds ../total_war/data/factions.js from the frontend faction-selection tables + the
pooled-resource / effect-bundle tables, so factions.html and faction.html are data driven.

Inputs (from sync_from_mod.py): db/<table>/*.tsv (vanilla data__.tsv + mod files),
text/{vanilla,mod,extra}/** loc, plus flag / icon PNGs pulled straight from the mod
and vanilla ui trees into ../total_war/data/images/{flags,features,resources}/.

Spine (190 campaign = 3k_main_campaign_map "Rise of the Warlords"; 8p_start_pos was
renamed by the mod to "Gathering of Heroes", an optional mode, and is emitted as its own section):
  frontend_faction_to_frontend_faction_leaders (campaign_key, frontend_faction, frontend_faction_leader)
    -> frontend_faction_leaders (frontend_character, faction_leader_effect_bundle, is_recommended)
    -> frontend_characters (character_generation_template, optional_specialisation)
    -> frontend_factions (playstyle, sort_order, active_years)
    -> factions (screen_name, subculture, flags_path)
    -> unique features (junction -> frontend_faction_leader_unique_features + loc block)
    -> pooled resources via campaign groups:
         campaign_group_member_criteria_factions -> campaign_group_members -> campaign_group_pooled_resources
         levels: members with campaign_group_member_criteria_pooled_resources + numeric_ranges
                 -> campaign_group_pooled_resource_effects -> effect bundles

Exports: FACTION_DATA, FACTION_LOOKUP (by id), FACTION_BY_LEADER (leader key -> id),
         FACTION_CATEGORIES (ordered section list), FACTION_STATS.
Also writes generate_data/factions_report.txt (data-quality findings) and, on first run,
generate_data/faction_categories.json (editable section/colour mapping per faction).
"""

import os
import re
import json
import shutil
from collections import defaultdict

from tw3k_common import *  # noqa: F401,F403
import tw3k_common
from tw3k_common import _s, _dedupe_preserve

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, "db")
TEXT_ROOT = os.path.join(SCRIPT_DIR, "text")
SITE_DATA = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "total_war", "data"))
OUTPUT_PATH = os.path.join(SITE_DATA, "factions.js")
REPORT_PATH = os.path.join(SCRIPT_DIR, "factions_report.txt")
CATEGORIES_PATH = os.path.join(SCRIPT_DIR, "faction_categories.json")
OLD_CARDS_PATH = os.path.join(SCRIPT_DIR, "_old_factions_cards.json")
SUMMARY_PATH = os.path.join(SCRIPT_DIR, "last_run_factions.json")

MOD_ROOT = r"Z:\Claude\190Expanded\Beta"
UI_ROOTS = [
    os.path.join(MOD_ROOT, "2_Char", "ui"),
    os.path.join(MOD_ROOT, "Flags", "ui"),
    r"Z:\Claude\XMLViewer\games\3K\ui",
]

CAMPAIGN_MAIN = "3k_main_campaign_map"      # "Rise of the Warlords" - the 190 campaign
CAMPAIGN_GATHERING = "8p_start_pos"        # renamed by the mod to "Gathering of Heroes" (optional mode)
CAMPAIGNS = {
    CAMPAIGN_MAIN: {"campaign": "190", "label": "Rise of the Warlords (190)"},
    CAMPAIGN_GATHERING: {"campaign": "gathering", "label": "Gathering of Heroes"},
}

# section order + labels + card colour (data-type) for the factions page
CATEGORIES = [
    ("warlords", "Major Warlords", "han"),
    ("empire", "Han Empire & Governors", "han"),
    ("dlc-awb", "A World Betrayed", "han"),
    ("dlc-fd", "Fates Divided", "han"),
    ("yellow-turbans", "Yellow Turbans", "yellow-turban"),
    ("bandits", "Bandits & Outlaws", "bandit"),
    ("nanman", "Nanman Tribes", "nanman"),
    ("shanyue", "Shanyue & Southern Peoples", "nanman"),
    ("nomads", "Northern Nomads", "nomad"),
    ("korean", "Korean Kingdoms", "korean"),
    ("minor", "Minor Factions", "han"),
    ("gathering", "Gathering Heroes (optional mode)", "han"),
]
CATEGORY_TYPE = {k: t for k, _l, t in CATEGORIES}
CATEGORY_ORDER = {k: i for i, (k, _l, _t) in enumerate(CATEGORIES)}

MAJOR_WARLORDS = {"cao_cao", "liu_bei", "sun_jian", "dong_zhuo", "yuan_shao", "yuan_shu", "lu_bu",
                  "gongsun_zan", "ma_teng", "liu_biao", "liu_yan", "kong_rong"}
NOMAD_TOKENS = ("xianbei", "wuhuan", "xiongnu", "di_tribes", "bakaja", "shitla", "you_tu", "handan",
                "tuoba", "kuitou", "qiulijiu", "yufuluo", "dou_mao", "qiang")
SHANYUE_TOKENS = ("pan_lin", "jia_long", "ni_xiaode", "wu_ju", "lai_gong", "shanyue")

SUBCULTURE_GROUP = {
    "3k_main_chinese": "han",
    "3k_main_subculture_yellow_turban": "yellow-turban",
    "3k_dlc05_subculture_bandits": "bandit",
    "3k_dlc06_subculture_nanman": "nanman",
    "3k_ironic_korea": "korean",
}

DLC_NAMES = {
    "3k_dlc04": "Mandate of Heaven",
    "3k_dlc05": "A World Betrayed",
    "3k_dlc06": "The Furious Wild",
    "3k_dlc07": "Fates Divided",
    "3k_ytr": "Yellow Turban Rebellion",
    "3k_cp01": "Reign of Blood",
    "ep": "Eight Princes",
}

report = []


def note(section, msg):
    report.append(f"[{section}] {msg}")


# ----------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------

def loc(LOC, key, default=""):
    return clean_text(LOC.get(key, default))


def rows_by(rows, col):
    out = defaultdict(list)
    for r in rows:
        k = _s(r.get(col, ""))
        if k:
            out[k].append(r)
    return out


def norm_ui_path(p):
    p = _s(p).replace("\\", "/").strip("/")
    p = re.sub(r"^(data/)?ui/", "", p, flags=re.I)
    return p


def resolve_ui_file(rel):
    """Find rel (already ui-relative) under the mod/vanilla ui roots."""
    rel = norm_ui_path(rel)
    if not rel:
        return None
    for root in UI_ROOTS:
        p = os.path.join(root, rel)
        if os.path.isfile(p):
            return p
    return None


_copied = {}


def copy_image(src, sub, name):
    """Copy src into ../total_war/data/images/<sub>/<name>; return site-relative url or ''."""
    if not src:
        return ""
    dst_dir = os.path.join(SITE_DATA, "images", sub)
    os.makedirs(dst_dir, exist_ok=True)
    dst = os.path.join(dst_dir, name)
    key = (sub, name)
    if key not in _copied:
        if not os.path.exists(dst) or os.path.getsize(dst) != os.path.getsize(src):
            shutil.copy2(src, dst)
        _copied[key] = True
    return f"data/images/{sub}/{name}"


def icon_url(icon_path, sub="features", default_dir=""):
    rel = norm_ui_path(icon_path)
    if not rel or rel in (".", "/") or not re.search(r"\.(png|dds|jpg)$", rel, re.I):
        return ""
    if "/" not in rel and default_dir:
        rel = default_dir.rstrip("/") + "/" + rel
    src = resolve_ui_file(rel)
    if not src:
        note("icon", f"missing icon {icon_path}")
        return ""
    return copy_image(src, sub, os.path.basename(rel))


def parse_feature_block(raw):
    """
    "[[b]]Title[[/b]]\\n[[col:scope_description]]Type[[/col]]\\n\\n[[col:green]]+[[/col]] text\\n..."
    -> title, subtitle, [{sign, text}]
    """
    raw = _s(raw).replace("\\\\n", "\n").replace("\\n", "\n")
    lines = [l.strip() for l in raw.split("\n")]
    lines = [l for l in lines if l]
    title = subtitle = ""
    body = []
    for i, l in enumerate(lines):
        if i == 0 and re.search(r"\[\[b\]\]", l, re.I):
            title = strip_tw_markup(l)
            continue
        if i == 1 and "scope_description" in l:
            subtitle = strip_tw_markup(l)
            continue
        sign = ""
        m = re.match(r"\[\[col:(green|red)\]\]\s*([+\-])\s*\[\[/col\]\]\s*(.*)", l, re.I)
        if m:
            sign = m.group(2)
            text = strip_tw_markup(m.group(3))
        else:
            m2 = re.match(r"^([+\-])\s+(.*)", l)
            if m2:
                sign, text = m2.group(1), strip_tw_markup(m2.group(2))
            else:
                text = strip_tw_markup(l)
        if text:
            body.append({"sign": sign, "text": text})
    return title, subtitle, body


def parse_difficulty(raw):
    raw = _s(raw)
    m = re.search(r"fe_difficulty_([a-z_]+)", raw, re.I)
    level = m.group(1).lower() if m else ""
    text = strip_tw_markup(raw)
    text = re.sub(r"^starting situation:\s*", "", text, flags=re.I).strip()
    return {"text": text, "level": level}


def origin_of(faction_key):
    k = faction_key.lower()
    if k.startswith("3k_main_"):
        return {"origin": "vanilla", "label": "Vanilla"}
    for prefix, name in DLC_NAMES.items():
        if k.startswith(prefix + "_"):
            return {"origin": "dlc", "label": "DLC", "dlc": name}
    return {"origin": "190e", "label": "190 Expanded"}


def default_category(faction_key, subculture, origin, name):
    k = faction_key.lower()
    if subculture == "3k_ironic_korea" or "korea" in k or any(t in k for t in ("goguryeo", "buyeo", "gaya", "tamno", "baekje", "_ye_")):
        return "korean"
    if subculture == "3k_dlc06_subculture_nanman":
        return "nanman"
    if subculture == "3k_main_subculture_yellow_turban":
        return "yellow-turbans"
    if any(t in k for t in NOMAD_TOKENS):
        return "nomads"
    if any(t in k for t in SHANYUE_TOKENS):
        return "shanyue"
    if subculture == "3k_dlc05_subculture_bandits":
        return "bandits"
    if origin["origin"] == "vanilla":
        short = re.sub(r"^3k_main_faction_", "", k)
        return "warlords" if short in MAJOR_WARLORDS else "empire"
    if origin["origin"] == "dlc":
        if origin.get("dlc") == "A World Betrayed":
            return "dlc-awb"
        if origin.get("dlc") == "Fates Divided":
            return "dlc-fd"
        return "empire"
    return "minor"


def slug(name):
    return re.sub(r"[^a-z0-9]+", "", _s(name).lower().replace("ü", "u"))


# ----------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("190 Expanded Wiki - Faction Parser")
    print("=" * 60)

    LOC = load_site_loc(TEXT_ROOT)
    effects_loc = sub_loc(LOC, "effects_")
    scope_loc = sub_loc(LOC, "campaign_effect_scopes_")
    tw3k_common.set_ui_text_replacements(build_ui_text_replacements(LOC))
    print(f"  {len(LOC)} loc keys")

    T = lambda name, key="key": load_table_dict(DB_PATH, name, key_field=key)[0]
    R = lambda name: load_table(DB_PATH, name)[0]

    spine = R("frontend_faction_to_frontend_faction_leaders_tables")
    leaders = T("frontend_faction_leaders_tables")
    ffactions = T("frontend_factions_tables", "faction")
    fchars = T("frontend_characters_tables")
    factions = T("factions_tables")
    features = T("frontend_faction_leader_unique_features_tables")
    feat_j = rows_by(R("frontend_faction_leaders_to_frontend_faction_leader_unique_features_junctions_tables"), "frontend_faction_leader")
    uniq_chars = rows_by(R("frontend_faction_leader_unique_characters_tables"), "frontend_faction_leader")
    party_j = {_s(r.get("frontend_leader")): _s(r.get("political_party")) for r in R("political_parties_frontend_leaders_junctions_tables")}
    parties = T("political_parties_tables")
    fgroups = rows_by(R("faction_to_faction_groups_junctions_tables"), "faction_key")
    pooled = T("pooled_resources_tables")
    factor_j = rows_by(R("pooled_resource_factor_junctions_tables"), "resource")
    ui_primary = rows_by(R("ui_primary_faction_pooled_resources_tables"), "faction")
    cg_members = {_s(r.get("id")): _s(r.get("group")) for r in R("campaign_group_members_tables")}
    cg_crit_f = rows_by(R("campaign_group_member_criteria_factions_tables"), "member")
    cg_crit_f_by_faction = rows_by(R("campaign_group_member_criteria_factions_tables"), "faction")
    cg_pooled = rows_by(R("campaign_group_pooled_resources_tables"), "campaign_group")
    cg_crit_pr = rows_by(R("campaign_group_member_criteria_pooled_resources_tables"), "member")
    cg_ranges = rows_by(R("campaign_group_member_criteria_numeric_ranges_tables"), "member")
    cg_diff = rows_by(R("campaign_group_member_criteria_player_game_difficulty_types_tables"), "member")
    cg_pr_effects = rows_by(R("campaign_group_pooled_resource_effects_tables"), "campaign_group")
    bundles = T("effect_bundles_tables")
    b2e = rows_by(R("effect_bundles_to_effects_junctions_tables"), "effect_bundle_key")
    effects_tbl = T("effects_tables", "effect")
    templates = T("character_generation_templates_tables")
    names_lookup = {}
    for k, v in LOC.items():
        m = re.match(r"names_name_(\d+)$", k)
        if m:
            names_lookup[m.group(1)] = v

    def leader_display_name(template_key):
        t = templates.get(template_key, {})
        fam = names_lookup.get(_s(t.get("family_name", "0")), "")
        fore = names_lookup.get(_s(t.get("forename", "0")), "")
        full = f"{fam} {fore}".strip()
        if full:
            return full
        m = re.search(r"template_(?:historical|generated|fictional|ancestral)_(?:lady_)?(.+?)(?:_hero)?_(?:fire|earth|water|wood|metal|nanman)$", template_key)
        return m.group(1).replace("_", " ").title() if m else ""
    print(f"  spine rows {len(spine)}, leaders {len(leaders)}, factions {len(factions)}, features {len(features)}, "
          f"pooled resources {len(pooled)}, bundles {len(bundles)}")

    # members that are level thresholds for a pooled resource, grouped by resource
    level_members_by_resource = defaultdict(list)
    for member, rows in cg_crit_pr.items():
        for r in rows:
            level_members_by_resource[_s(r.get("pooled_resource"))].append(member)

    categories_cfg = {}
    if os.path.exists(CATEGORIES_PATH):
        categories_cfg = json.load(open(CATEGORIES_PATH, encoding="utf-8"))
    old_cards = {}
    if os.path.exists(OLD_CARDS_PATH):
        old_cards = {slug(k): v for k, v in json.load(open(OLD_CARDS_PATH, encoding="utf-8")).items()}

    # ------------------------------------------------------------------
    def format_bundle(bundle_key):
        bk = _s(bundle_key)
        if not bk or bk.endswith("dummy_effect_bundle"):
            return None
        b = bundles.get(bk, {})
        title = strip_tw_markup(loc(LOC, f"effect_bundles_localised_title_{bk}") or b.get("localised_title", ""))
        desc = strip_tw_markup(loc(LOC, f"effect_bundles_localised_description_{bk}") or b.get("localised_description", ""))
        lines = []
        bullets = []
        for r in b2e.get(bk, []):
            ek = _s(r.get("effect_key"))
            gd = _s(effects_tbl.get(ek, {}).get("generalised_description", ""))
            gd_text = loc(LOC, f"effects_generalised_descriptions_localised_description_{gd}") if gd else ""
            if gd_text:
                bullets.append(strip_tw_markup(gd_text).lstrip("• ").strip())
                continue
            line = format_effect_line(ek, _s(r.get("value")), _s(r.get("effect_scope")), "", effects_loc, scope_loc)
            if line:
                lines.append(line)
        icon = icon_url(b.get("ui_icon", ""), "resources", "campaign ui/effect_bundles")
        return {"key": bk, "title": title, "description": desc, "icon": icon,
                "bullets": _dedupe_preserve(bullets), "effects": _dedupe_preserve(lines)}

    def build_resource(res_key, faction_key, is_primary):
        p = pooled.get(res_key, {})
        name = loc(LOC, f"pooled_resources_display_name_{res_key}")
        if not name:
            # no loc: prettify the key (ironic_han_liu_yu_peace -> Liu Yu Peace)
            name = re.sub(r"^(ironic_|3k_\w+?_pooled_resource_|3k_\w+?_)", "", res_key)
            name = re.sub(r"^(han_|resource_)", "", name).replace("_", " ").title()
            note("resource", f"{res_key}: no display name loc, using '{name}'")
        out = {
            "key": res_key,
            "name": name,
            "description": strip_tw_markup(loc(LOC, f"pooled_resources_description_{res_key}")),
            "tooltip": strip_tw_markup(loc(LOC, f"pooled_resources_foreign_diplomacy_view_tooltip_{res_key}")),
            "positive_label": loc(LOC, f"pooled_resources_positive_factors_display_name_{res_key}"),
            "negative_label": loc(LOC, f"pooled_resources_negative_factors_display_name_{res_key}"),
            "icon": icon_url(p.get("icon_path", ""), "resources"),
            "minimum": _s(p.get("minimum")), "maximum": _s(p.get("maximum")),
            "is_primary": is_primary,
            "factors": [],
            "levels": [],
        }
        for r in factor_j.get(res_key, []):
            fk = _s(r.get("factor"))
            fname = (loc(LOC, f"pooled_resource_factors_display_name_{fk}")
                     or loc(LOC, f"pooled_resource_factors_display_name_positive_{fk}")
                     or loc(LOC, f"pooled_resource_factors_display_name_negative_{fk}"))
            if not fname:
                continue
            out["factors"].append({
                "key": fk, "name": strip_tw_markup(fname),
                "recurring": _s(r.get("is_recurring_factor")).lower() == "true",
            })
        # levels
        seen = set()
        for member in level_members_by_resource.get(res_key, []):
            if "_ai_" in member.lower() or member.lower().endswith("_ai"):
                continue
            if cg_diff.get(member):
                continue
            crit = cg_crit_f.get(member, [])
            if crit and not any(_s(c.get("faction")) == faction_key for c in crit):
                continue
            rng = cg_ranges.get(member, [])
            mn = _s(rng[0].get("min_range")) if rng else ""
            mx = _s(rng[0].get("max_range")) if rng else ""
            group = cg_members.get(member, "")
            bl = []
            for r in cg_pr_effects.get(group, []):
                fb = format_bundle(r.get("effect_bundle"))
                if fb:
                    bl.append(fb)
            sig = (mn, mx, tuple(b["key"] for b in bl))
            if sig in seen or not bl:
                continue
            seen.add(sig)
            out["levels"].append({"member": member, "min": mn, "max": mx, "bundles": bl})

        def _num(v):
            try:
                return float(v)
            except ValueError:
                return 0.0
        out["levels"].sort(key=lambda l: _num(l["min"]))
        return out

    # ------------------------------------------------------------------
    entries = []
    per_faction_leaders = defaultdict(list)
    for r in spine:
        ck = _s(r.get("campaign_key"))
        if ck not in CAMPAIGNS:
            continue
        fk, lk = _s(r.get("frontend_faction")), _s(r.get("frontend_faction_leader"))
        if ck == CAMPAIGN_GATHERING and fk.startswith("ep_faction_"):
            continue  # vanilla Eight Princes rows left in the table the mod repurposed
        if fk and lk and lk not in per_faction_leaders[(ck, fk)]:
            per_faction_leaders[(ck, fk)].append(lk)

    new_categories = False
    for (ck, fk), lks in per_faction_leaders.items():
        camp = CAMPAIGNS[ck]
        frow = factions.get(fk)
        if not frow:
            note("faction", f"no factions_tables row for {fk}")
            continue
        for lk in lks:
            lrow = leaders.get(lk, {})
            if not lrow:
                note("leader", f"no frontend_faction_leaders row for {lk} ({fk})")
            fc_key = _s(lrow.get("frontend_character")) or lk
            fc = fchars.get(fc_key, {})
            template = _s(fc.get("character_generation_template"))
            ff = ffactions.get(fk, {})
            origin = origin_of(fk)
            subculture = _s(frow.get("subculture"))
            state_name = loc(LOC, f"factions_screen_name_{fk}") or _s(frow.get("screen_name")) or fk
            adjective = loc(LOC, f"factions_screen_adjective_{fk}") or _s(frow.get("screen_adjective"))
            leader_name = leader_display_name(template)
            name = leader_name or state_name
            is_gathering = ck == CAMPAIGN_GATHERING

            cfg_key = fk if len(lks) == 1 else f"{fk}__{lk}"
            if is_gathering:
                cfg_key += "~goh"
            cfg = categories_cfg.get(cfg_key)
            if not cfg:
                default = default_category(fk, subculture, origin, name)
                old = old_cards.get(slug(name))
                if is_gathering:
                    cat = "gathering"
                elif default in ("nanman", "korean", "nomads", "yellow-turbans"):
                    cat = default
                else:
                    cat = old["category"] if old else default
                cfg = {"category": cat, "name": name, "state": state_name}
                categories_cfg[cfg_key] = cfg
                new_categories = True
            category = cfg.get("category", "minor")
            if category not in CATEGORY_TYPE:
                note("category", f"{fk}: unknown category {category}, using minor")
                category = "minor"

            description = strip_tw_markup(loc(LOC, f"frontend_faction_leaders_localised_description_{lk}"))
            if not description:
                note("description", f"{name} ({lk}): missing / placeholder description")
            subtitle = strip_tw_markup(loc(LOC, f"frontend_faction_leaders_localised_subtitle_{lk}"))
            difficulty = parse_difficulty(LOC.get(f"frontend_faction_leaders_localised_difficulty_{lk}", ""))
            ps_key = _s(ff.get("playstyle"))
            ps_title = strip_tw_markup(loc(LOC, f"frontend_faction_leader_playstyles_localised_title_{ps_key}"))
            ps_title = re.sub(r"^playstyle focus:\s*", "", ps_title, flags=re.I)
            ps_tip = strip_tw_markup(loc(LOC, f"frontend_faction_leader_playstyles_localised_tooltip_{ps_key}"))
            if ps_key and not ps_title:
                note("playstyle", f"{name}: playstyle {ps_key} has no loc title")

            # flag
            leaf = os.path.basename(norm_ui_path(frow.get("flags_path", "")))
            flag = flag_small = ""
            if leaf:
                src = resolve_ui_file(f"flags/{leaf}/mon_256.png")
                src64 = resolve_ui_file(f"flags/{leaf}/mon_64.png")
                if src:
                    flag = copy_image(src, "flags", f"{fk}.png")
                if src64:
                    flag_small = copy_image(src64, "flags", f"{fk}_64.png")
            if not flag:
                note("flag", f"{name} ({fk}): flag folder '{leaf}' not found")

            # unique features
            uf_out = []
            for j in feat_j.get(lk, []):
                key = _s(j.get("frontend_faction_leader_unique_feature"))
                f = features.get(key, {})
                raw = LOC.get(f"frontend_faction_leader_unique_features_localised_description_{key}", "")
                title, sub, body = parse_feature_block(raw)
                if not title:
                    title = loc(LOC, f"frontend_faction_leader_unique_features_localised_title_{key}") or key
                uf_out.append({
                    "key": key,
                    "type": _s(f.get("feature_type")),
                    "sort_order": int(_s(f.get("sort_order")) or 0),
                    "icon": icon_url(f.get("icon_path", ""), "features"),
                    "title": title, "subtitle": sub, "lines": body,
                })
            uf_out.sort(key=lambda x: x["sort_order"])
            if not uf_out:
                note("features", f"{name} ({lk}): no unique features")

            specialisation = format_bundle(fc.get("optional_specialisation"))
            leader_bundle = format_bundle(lrow.get("faction_leader_effect_bundle"))
            party_key = party_j.get(lk, "")
            party_bundle = format_bundle(parties.get(party_key, {}).get("effect_bundle")) if party_key else None

            # pooled resources
            primary = {_s(r.get("pooled_resource")) for r in ui_primary.get(fk, [])
                       if _s(r.get("optional_campaign_key")) in ("", ck)}
            res_keys = set(primary)
            for c in cg_crit_f_by_faction.get(fk, []):
                if _s(c.get("context")) not in ("owner", "actor", ""):
                    continue
                group = cg_members.get(_s(c.get("member")), "")
                for pr in cg_pooled.get(group, []):
                    res_keys.add(_s(pr.get("resource")))
            resources = [build_resource(rk, fk, rk in primary) for rk in sorted(res_keys) if rk in pooled]
            resources.sort(key=lambda x: (not x["is_primary"], x["name"]))

            notable = []
            for r in sorted(uniq_chars.get(lk, []), key=lambda x: int(_s(x.get("sort_order")) or 0)):
                fck = _s(r.get("frontend_character"))
                tmpl = _s(fchars.get(fck, {}).get("character_generation_template")) or fck
                if tmpl and tmpl != template and tmpl not in notable:
                    notable.append(tmpl)

            entry_id = cfg_key
            entries.append({
                "id": entry_id,
                "faction_key": fk,
                "leader_key": lk,
                "name": name,
                "state_name": state_name,
                "adjective": adjective,
                "mode": "gathering" if is_gathering else "standard",
                "leader_template": template,
                "subtitle": subtitle,
                "description": description,
                "difficulty": difficulty,
                "playstyle": {"key": ps_key, "title": ps_title, "tooltip": ps_tip},
                "campaign": camp["campaign"],
                "campaign_label": camp["label"],
                "campaign_key": ck,
                "is_default": _s(r.get("is_default")).lower() == "true",
                "is_recommended": _s(lrow.get("is_recommended")).lower() == "true",
                "starting_progression_level": _s(lrow.get("starting_progression_level")),
                "active_years": [_s(ff.get("active_years_start")), _s(ff.get("active_years_end"))],
                "sort_order": int(_s(ff.get("sort_order")) or 9999),
                "origin": origin["origin"], "origin_label": origin["label"], "dlc": origin.get("dlc", ""),
                "subculture": subculture,
                "category": category,
                "type": CATEGORY_TYPE[category],
                "faction_groups": [_s(g.get("faction_group_key")) for g in fgroups.get(fk, [])],
                "flag": flag, "flag_small": flag_small,
                "unique_features": uf_out,
                "specialisation": specialisation,
                "leader_bundle": leader_bundle,
                "party_bundle": party_bundle,
                "resources": resources,
                "notable_characters": notable,
                "technical": {"frontend_character": fc_key, "political_party": party_key,
                              "military_group": _s(frow.get("military_group")), "flags_path": _s(frow.get("flags_path"))},
            })

    # Gathering of Heroes re-lists every normal faction; keep only the factions unique to that mode
    main_factions = {e["faction_key"] for e in entries if e["campaign"] == "190"}
    entries = [e for e in entries if e["campaign"] == "190" or e["faction_key"] not in main_factions]
    entries.sort(key=lambda e: (CATEGORY_ORDER.get(e["category"], 99), e["sort_order"], e["name"]))
    if new_categories or not os.path.exists(CATEGORIES_PATH):
        with open(CATEGORIES_PATH, "w", encoding="utf-8", newline="\n") as f:
            json.dump(dict(sorted(categories_cfg.items())), f, indent=2, ensure_ascii=False)
        print(f"  Written: {CATEGORIES_PATH} (edit to move factions between sections)")

    # ------------------------------------------------------------------ output
    by_leader = {}
    for e in sorted(entries, key=lambda e: e["campaign"] != "190"):
        by_leader.setdefault(e["leader_key"], e["id"])
    by_cat = defaultdict(int)
    for e in entries:
        by_cat[e["category"]] += 1
    stats = {
        "total": sum(1 for e in entries if e["campaign"] == "190"),
        "totalGathering": sum(1 for e in entries if e["campaign"] == "gathering"),
        "byCategory": dict(by_cat),
        "withDescription": sum(1 for e in entries if e["description"]),
        "withFeatures": sum(1 for e in entries if e["unique_features"]),
        "withResources": sum(1 for e in entries if e["resources"]),
        "withFlag": sum(1 for e in entries if e["flag"]),
    }
    cats = [{"key": k, "label": l, "type": t, "count": by_cat.get(k, 0)} for k, l, t in CATEGORIES]

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write("// Auto-generated faction data for 190 Expanded Wiki (parse_factions.py)\n")
        f.write(f"// Factions: {stats['total']} (190 campaign) + {stats['totalGathering']} (Gathering of Heroes)\n\n")
        f.write("const FACTION_DATA = " + json.dumps(entries, indent=2, ensure_ascii=False) + ";\n\n")
        f.write("const FACTION_CATEGORIES = " + json.dumps(cats, indent=2, ensure_ascii=False) + ";\n\n")
        f.write("const FACTION_LOOKUP = {};\nFACTION_DATA.forEach(f => { FACTION_LOOKUP[f.id] = f; });\n\n")
        f.write("const FACTION_BY_LEADER = " + json.dumps(by_leader, indent=2, ensure_ascii=False) + ";\n\n")
        f.write("const FACTION_STATS = " + json.dumps(stats, indent=2) + ";\n")
    print(f"  Written: {OUTPUT_PATH}")

    with open(REPORT_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(sorted(report)) + "\n")
    with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    # tiny stats file for the landing page (avoids loading the 1.4 MB characters.js there)
    char_summary_path = os.path.join(SCRIPT_DIR, "last_run_characters.json")
    char_total = 0
    if os.path.exists(char_summary_path):
        char_total = json.load(open(char_summary_path, encoding="utf-8")).get("characters", 0)
    with open(os.path.join(SITE_DATA, "stats.js"), "w", encoding="utf-8", newline="\n") as f:
        f.write("// Auto-generated by parse_factions.py\n")
        f.write("const SITE_STATS = " + json.dumps({
            "factions": stats["total"], "gathering_factions": stats["totalGathering"],
            "characters": char_total,
        }) + ";\n")
    print(f"  Written: {REPORT_PATH} ({len(report)} notes)")
    print()
    print("SUMMARY", json.dumps(stats))


if __name__ == "__main__":
    main()
