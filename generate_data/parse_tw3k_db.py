#!/usr/bin/env python3
"""
190 Expanded Wiki - TW3K DB Parser (Patched + Character Effects + Trimmed UI Strings)
===================================================================================

Exports:
- total_war/data/characters.js
- total_war/data/titles.js
- total_war/data/character_details.js   (portrait + formatted effects)
- total_war/data/traits.js             (static trait CEO -> resolved title/desc/icon/effects)

EFFECT RULE (per your request):
- Effect display text MUST come from:
    effects_description_<effect_key>
  (do NOT use effects_localised_name_*, do NOT humanize the key, do NOT fall back to key text)
- If effects_description_<effect_key> is missing OR empty -> skip the effect entirely.

SCOPE RULE:
- Scope text comes from scope loc keys (e.g. character_to_character_own) in the scopes folder.
- Your loc TSV format is: key<TAB>text<TAB>tooltip(TRUE/FALSE)
  => we MUST read from the SECOND column when the last column is TRUE/FALSE.

TRIMMING:
- Strip TW UI markup: [[b]] [[/b]] [[col:...]] [[/col]] {{tr:...}}
- Remove %+n tokens from the final text (value is formatted separately)
- If loc contains [HIDDEN] -> skip effect entirely
- If scope resolves to something containing "administered" -> force scope to "own character"
- Optional game mode suffix: (Romance)/(Historical)/(Romance/Historical)
- Percent vs flat is decided from loc token:
    [[b]]%+n%[[/b]] => percent
    [[b]]%+n[[/b]]  => flat

TRAITS (FIXED):
- We use the SAME stage 11 key as career selection.
- From ceo_initial_data_active_ceos we collect ALL active CEOs that contain "trait_"
  (not just trait_personality / trait_physical).
- stage_to_trait_ceos[stage11] is a LIST (deduped), not a single value.
- If a stage has no trait CEOs, we pick random traits from the global trait pool,
  and ensure at least 3 traits when possible.
"""

import os
import csv
import xml.etree.ElementTree as ET
import json
import re
import random
from collections import defaultdict

# ============================================================================
# CONFIGURATION (relative to script directory)
# ============================================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(SCRIPT_DIR, "db")

# Your custom CEO loc (optional)
LOC_PATH = os.path.join(SCRIPT_DIR, "text", "__ironic_ceos_loc.tsv")

# Big fallback loc
ALL_TITLES_LOC_PATH = os.path.join(SCRIPT_DIR, "all_titles_full.loc.tsv")

# Names folder
NAMES_LOC_FOLDER = os.path.join(SCRIPT_DIR, "names")

# Effects loc folder (effect descriptions)
EFFECTS_LOC_FOLDER = os.path.join(SCRIPT_DIR, "effects")

# Scopes loc folder
SCOPES_LOC_FOLDER = os.path.join(SCRIPT_DIR, "scopes")

OUTPUT_PATH = os.path.join(SCRIPT_DIR, "total_war", "data", "characters.js")
TITLES_OUTPUT_PATH = os.path.join(SCRIPT_DIR, "total_war", "data", "titles.js")
CHAR_DETAILS_OUTPUT_PATH = os.path.join(SCRIPT_DIR, "total_war", "data", "character_details.js")
TRAITS_OUTPUT_PATH = os.path.join(SCRIPT_DIR, "total_war", "data", "traits.js")

DEBUG_MISSING = True

# Optional: force certain characters to resolve using a different key for fallback searches
NAME_KEY_OVERRIDES = {
    # "zhang_lu": "zhang_luo",
}

# ============================================================================
# HELPERS
# ============================================================================

def _s(x) -> str:
    return ("" if x is None else str(x)).strip()


BOOL_TOKENS = {"true", "false"}


def iter_loc_tsv(filepath):
    """
    Robust CA loc TSV reader.

    Your loc TSVs look like:
      key<TAB>text<TAB>tooltip(TRUE/FALSE)
    So if the last column is TRUE/FALSE, we take column[1] as the localized text.

    Other CA-ish variants exist, so we also support:
      key<TAB>text
      key<TAB>unknown<TAB>text (no TRUE/FALSE at end) -> take last column
    """
    try:
        with open(filepath, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.reader(f, delimiter="\t")
            for row in reader:
                if not row or len(row) < 2:
                    continue

                key = _s(row[0])
                if not key or key.startswith("#"):
                    continue

                # skip header rows like: key  text  tooltip
                if key.lower() in {"key", "loc_key", "id"}:
                    continue

                last = _s(row[-1]).lower()
                if last in BOOL_TOKENS:
                    # key, text, TRUE/FALSE
                    text = _s(row[1])
                else:
                    # key, ..., text
                    text = _s(row[-1])

                if key and text:
                    yield key, text
    except FileNotFoundError:
        return
    except Exception as e:
        print(f"  Error reading loc TSV {filepath}: {e}")
        return


def parse_tsv(filepath):
    rows = []
    try:
        with open(filepath, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                if not row:
                    continue
                first_val = list(row.values())[0] if row else ""
                if first_val and str(first_val).startswith("#"):
                    continue
                cleaned = {k: _s(v) for k, v in row.items()}
                rows.append(cleaned)
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"  Error parsing TSV {filepath}: {e}")
    return rows


def _xml_elem_to_row(elem):
    row = {}
    for k, v in (elem.attrib or {}).items():
        row[k] = _s(v)
    for child in elem:
        row[child.tag] = _s(child.text)
    if row.get("record_key") and not row.get("key"):
        row["key"] = row["record_key"]
    return row


def parse_xml_to_list(filepath):
    rows = []
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
        for elem in root:
            if elem.tag == "edit_uuid":
                continue
            rows.append(_xml_elem_to_row(elem))
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"  Error parsing XML {filepath}: {e}")
    return rows


def parse_xml_to_dict(filepath, key_field="key"):
    result = {}
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
        for elem in root:
            if elem.tag == "edit_uuid":
                continue
            row = _xml_elem_to_row(elem)
            key = row.get(key_field) or row.get("record_key", "")
            key = _s(key)
            if key:
                result[key] = row
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"  Error parsing XML {filepath}: {e}")
    return result


def get_best_file(folder_path):
    """Prefer override TSV over data__.tsv; otherwise XML."""
    if not os.path.exists(folder_path):
        return None, None
    files = os.listdir(folder_path)
    tsv_files = [f for f in files if f.endswith(".tsv")]
    xml_files = [f for f in files if f.endswith(".xml")]

    for f in sorted(tsv_files):
        if f != "data__.tsv":
            return os.path.join(folder_path, f), "tsv"
    if "data__.tsv" in tsv_files:
        return os.path.join(folder_path, "data__.tsv"), "tsv"
    if xml_files:
        return os.path.join(folder_path, xml_files[0]), "xml"
    return None, None


def extract_element_from_key(key):
    parts = key.split("_")
    if parts:
        last_part = parts[-1].lower()
        valid = {"fire", "earth", "water", "wood", "metal", "nanman"}
        if last_part in valid:
            return last_part
    return "unknown"


def load_campaign_character_arts(db_path):
    """
    Load campaign_character_arts_tables to map art_set_id -> portrait.
    Looks for entries where age >= 16 and grabs the portrait column.
    Returns dict: art_set_id -> portrait_key
    """
    folder = os.path.join(db_path, "campaign_character_arts_tables")
    art_lookup = {}

    if not os.path.exists(folder):
        return art_lookup

    files = sorted(os.listdir(folder))
    tsv_files = [f for f in files if f.endswith('.tsv')]

    def sort_key(f):
        if f == 'data__.tsv':
            return '0' + f
        return '1' + f
    tsv_files.sort(key=sort_key)

    for filename in tsv_files:
        filepath = os.path.join(folder, filename)
        rows = parse_tsv(filepath)

        for row in rows:
            art_set_id = _s(row.get('art_set_id', ''))
            if not art_set_id:
                continue

            age_str = _s(row.get('age', ''))
            try:
                age = int(age_str) if age_str else 0
            except ValueError:
                age = 0

            if age < 16:
                continue

            portrait = _s(row.get('portrait', ''))
            if not portrait:
                continue

            art_lookup[art_set_id] = portrait

    return art_lookup


def convert_portrait_to_url(portrait_key):
    """
    Convert portrait key to image URL.
    """
    if not portrait_key:
        return ""
    portrait_key = portrait_key.rstrip('/')
    return f"data/images/db/{portrait_key}.png"


def load_loc_file_ceo_patterns(filepath):
    """
    Load loc in the old "ceo_nodes_title_xxx" / "ceo_nodes_description_xxx" pattern style
    and return (titles_by_node_key, desc_by_node_key).
    """
    titles = {}
    descriptions = {}

    for key, value in iter_loc_tsv(filepath):
        m1 = re.search(r"ceo_nodes_title_(.+)", key)
        if m1:
            titles[_s(m1.group(1))] = value

        m2 = re.search(r"ceo_nodes_description_(.+)", key)
        if m2:
            descriptions[_s(m2.group(1))] = value

    return titles, descriptions


def load_loc_kv(filepath):
    """Load loc TSV as raw key->value dict."""
    loc = {}
    for k, v in iter_loc_tsv(filepath):
        if k and not k.startswith("#"):
            loc[k] = v
    return loc


def load_names_loc_files(folder_path):
    """
    Load all name localization files.
    Supports *.loc.tsv and *_loc.tsv
    All names (forename, family_name, clan_name) use the same lookup tables.
    """
    names = {}
    alt_names = {}  # Chinese/alternative names

    if not os.path.exists(folder_path):
        return names, alt_names

    files = os.listdir(folder_path)
    loc_files = [f for f in files if f.endswith(".loc.tsv") or f.endswith("_loc.tsv")]

    def sort_key(filename):
        if filename.startswith("names__"):
            return "0" + filename
        return "1" + filename
    loc_files.sort(key=sort_key)

    for filename in loc_files:
        filepath = os.path.join(folder_path, filename)
        count = 0
        alt_count = 0

        try:
            for key, value in iter_loc_tsv(filepath):
                m = re.match(r"names_name_(\d+)", key)
                if m:
                    names[m.group(1)] = value
                    count += 1

                m_alt = re.match(r"names_alt_name_(\d+)", key)
                if m_alt:
                    alt_names[m_alt.group(1)] = value
                    alt_count += 1

            if count > 0 or alt_count > 0:
                print(f"    {filename}: {count} names, {alt_count} alt names")
        except Exception as e:
            print(f"  Error loading {filename}: {e}")

    return names, alt_names


def pick_best_ceo_node(threshold, threshold_to_nodes, ceo_nodes, loc_titles, loc_descs):
    """
    ceo_threshold_nodes is 1->many. Choose best:
    1) node has loc title/desc
    2) node has embedded title/desc in ceo_nodes table
    3) first node
    """
    candidates = threshold_to_nodes.get(threshold, [])
    if not candidates:
        return ""

    for node in candidates:
        if node in loc_titles or node in loc_descs:
            return node
        node_data = ceo_nodes.get(node, {})
        if _s(node_data.get("title")) or _s(node_data.get("description")):
            return node

    return candidates[0]


def resolve_name_key(name_key):
    return NAME_KEY_OVERRIDES.get(name_key, name_key)


def fallback_career_title_desc(name_key, loc_kv):
    """
    Fallback: scan all_titles_full.loc.tsv for keys containing:
      - name_key
      - 'career'
      - 'title' / 'description' (or 'desc')
    Picks the most specific (longest key) match.
    """
    nk = _s(name_key).lower()
    if not nk:
        return "", ""

    title_candidates = []
    desc_candidates = []

    for k, v in loc_kv.items():
        kl = k.lower()
        if nk not in kl:
            continue
        if "career" not in kl:
            continue

        if "title" in kl:
            title_candidates.append((len(k), k, v))
        if ("description" in kl) or re.search(r"\bdesc\b", kl):
            desc_candidates.append((len(k), k, v))

    title = max(title_candidates, default=(0, "", ""))[2]
    desc = max(desc_candidates, default=(0, "", ""))[2]
    return title, desc


# ============================================================================
# EFFECTS HELPERS (TRIM + HIDDEN SKIP)
# ============================================================================

def load_all_loc_kv_from_folder(folder_path):
    """
    Loads every .tsv / .loc.tsv / *_loc.tsv file in a folder into a single key->value dict.
    Uses iter_loc_tsv() which reads column[1] when last column is TRUE/FALSE.
    Later files overwrite earlier ones (sorted by name).
    """
    merged = {}
    if not os.path.exists(folder_path):
        return merged

    files = sorted(os.listdir(folder_path))
    for filename in files:
        fl = filename.lower()
        if not (fl.endswith(".loc.tsv") or fl.endswith("_loc.tsv") or fl.endswith(".tsv")):
            continue

        fp = os.path.join(folder_path, filename)
        try:
            for k, v in iter_loc_tsv(fp):
                if k and v:
                    merged[k] = v
        except Exception as e:
            print(f"  Error loading loc file {filename}: {e}")

    return merged


def load_ceo_effect_list_to_effects(db_path):
    """
    Loads ceo_effect_list_to_effects into mapping:
      effect_list_key -> [{effect_key, value, scope, optional_only_in_game_mode}, ...]
    """
    folder = os.path.join(db_path, "ceo_effect_list_to_effects_tables")
    path, ftype = get_best_file(folder)

    # fallback alternative folder naming
    if not path:
        alt = os.path.join(db_path, "ceo_effect_list_to_effects")
        if os.path.exists(alt):
            for f in os.listdir(alt):
                if f.endswith(".xml"):
                    path = os.path.join(alt, f)
                    ftype = "xml"
                    break
            if not path and os.path.exists(os.path.join(alt, "data__.tsv")):
                path = os.path.join(alt, "data__.tsv")
                ftype = "tsv"

    rows = []
    if path and ftype == "tsv":
        rows = parse_tsv(path)
    elif path and ftype == "xml":
        rows = parse_xml_to_list(path)

    mapping = defaultdict(list)
    for r in rows:
        lk = _s(r.get("effect_list", ""))
        ek = _s(r.get("effect", ""))
        if not (lk and ek):
            continue

        mapping[lk].append({
            "effect_key": ek,
            "value": _s(r.get("value", "")),
            "scope": _s(r.get("effect_scope", "")),
            "optional_only_in_game_mode": _s(r.get("optional_only_in_game_mode", "")),
        })

    return dict(mapping), path, ftype, len(rows)


TR_REPLACEMENTS = {
    "only_if_minister": "(only if this character is a court minister)",
    "only_if_faction_leader_factionwide": "(only if this character is prime minister, heir or faction leader)",
    "only_if_faction_leader": "(only if this character is faction leader)",
    "only_if_faction_leader_factionwide": "(only if this character is faction leader)",
    "map_province": "commandery",
    "map_provinces": "commanderies",
    "map_regions": "counties",
    "map_region": "county",
    "public_order": "public order",
    "military_supplies": "military supplies",
}


def replace_tr_tokens(text: str) -> str:
    """
    Replace {{tr:...}} tokens with correct TW3K English,
    preserving capitalization.
    """
    def repl(match):
        key = match.group(1)
        replacement = TR_REPLACEMENTS.get(key)
        if not replacement:
            return ""
        token = match.group(0)
        if len(token) > 5 and token[5].isupper():
            return replacement.capitalize()
        return replacement

    return re.sub(r"\{\{\s*tr:([^}]+)\s*\}\}", repl, text, flags=re.IGNORECASE)


def strip_tw_markup(text: str) -> str:
    """
    Remove TW UI markup, preserve meaning.
    """
    s = _s(text)
    if not s:
        return ""

    s = replace_tr_tokens(s)

    s = re.sub(r"\[\[\s*/?\s*b\s*\]\]", "", s, flags=re.IGNORECASE)
    s = re.sub(r"\[\[\s*/?\s*i\s*\]\]", "", s, flags=re.IGNORECASE)

    s = re.sub(r"\[\[\s*col:[^\]]+\]\]", "", s, flags=re.IGNORECASE)
    s = re.sub(r"\[\[\s*/\s*col\s*\]\]", "", s, flags=re.IGNORECASE)

    s = re.sub(r"%\+\s*[nd]\s*%", "", s, flags=re.IGNORECASE)
    s = re.sub(r"%\+\s*[nd]", "", s, flags=re.IGNORECASE)
    s = re.sub(r"\+\s*[nd]\b", "", s, flags=re.IGNORECASE)

    s = s.replace("\\n", " ")
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"\(\s*\)", "", s).strip()

    return s


def is_hidden_effect(text: str) -> bool:
    return "[hidden]" in _s(text).lower()


def resolve_effect_loc(effect_key, effects_loc_kv):
    """
    YOUR REQUIRED RULE:
      effect text MUST be from:
        effects_description_<effect_key>

    Returns: (raw_loc, cleaned_loc)
    """
    ek = _s(effect_key)
    if not ek:
        return "", ""

    want_key = f"effects_description_{ek}"

    raw = _s(effects_loc_kv.get(want_key, ""))

    if not raw:
        want_l = want_key.lower()
        for k, v in effects_loc_kv.items():
            if _s(k).lower() == want_l and _s(v):
                raw = _s(v)
                break

    cleaned = strip_tw_markup(raw)
    return _s(raw), _s(cleaned)


def resolve_scope_loc(scope_key, scope_loc_kv):
    """
    Convert effect_scope key -> short suffix text.
    Your file stores factionwide as:
      campaign_effect_scopes_localised_text_<scope_key>
    """
    sk = _s(scope_key)
    if not sk:
        return ""

    if not hasattr(resolve_scope_loc, "_lower"):
        resolve_scope_loc._lower = {_s(k).lower(): _s(v) for k, v in scope_loc_kv.items() if _s(k)}

    L = resolve_scope_loc._lower
    skl = sk.lower()

    candidates = [
        skl,
        f"campaign_effect_scopes_localised_text_{skl}",
        f"campaign_effect_scopes_localised_{skl}",
        f"campaign_effect_scopes_localized_text_{skl}",
        f"campaign_effect_scopes_localized_{skl}",
        f"campaign_effect_scopes_{skl}",
        f"effect_scopes_localised_text_{skl}",
        f"effect_scopes_localised_{skl}",
        f"effect_scopes_localized_text_{skl}",
        f"effect_scopes_localized_{skl}",
        f"effect_scopes_{skl}",
        f"effect_scope_{skl}",
        f"effects_scope_{skl}",
    ]

    raw = ""
    for ck in candidates:
        v = L.get(ck, "")
        if v:
            raw = v
            break

    if not raw:
        best_len = 0
        best_val = ""
        for k, v in L.items():
            if skl in k and v and len(k) > best_len:
                best_len = len(k)
                best_val = v
        raw = best_val

    cleaned = strip_tw_markup(raw).strip()
    if not cleaned:
        return ""

    if "administered" in cleaned.lower():
        return "own character"

    return cleaned


def format_optional_mode_suffix(optional_only_in_game_mode: str) -> str:
    """
    If optional_only_in_game_mode is set, append:
      (Romance) / (Historical) / (Romance/Historical)
    """
    raw = _s(optional_only_in_game_mode)
    if not raw:
        return ""

    low = raw.lower()
    parts = re.split(r"[\s,|/]+", low)
    parts = [p for p in parts if p]

    romance_tokens = {"romance", "rom"}
    historical_tokens = {"historical", "records", "record", "his"}

    has_romance = any(p in romance_tokens for p in parts) or ("romance" in low)
    has_historical = any(p in historical_tokens for p in parts) or ("historical" in low) or ("records" in low)

    if has_romance and has_historical:
        return " (Romance/Historical)"
    if has_romance:
        return " (Romance)"
    if has_historical:
        return " (Historical)"

    return f" ({raw.strip().title()})"


def loc_value_is_percent(raw_loc_text: str) -> bool:
    """
    Detect if the loc string expects a percentage value.
    Examples:
      [[b]]%+n%[[/b]]  -> percent
      [[b]]%+n[[/b]]   -> flat
    """
    s = _s(raw_loc_text).lower()
    if not s:
        return False
    return bool(re.search(r"%\+\s*n\s*%", s))


def format_effect_value_prefix(value: str, raw_loc_text: str) -> str:
    """
    Uses loc formatting token to decide percent vs flat.
    """
    v = _s(value)
    if not v:
        return ""

    is_percent = loc_value_is_percent(raw_loc_text)

    try:
        n = float(v)
        sign = "+" if n > 0 else ""
        n_txt = f"{sign}{int(n)}" if n.is_integer() else f"{sign}{n}"
        return f"{n_txt}% " if is_percent else f"{n_txt} "
    except ValueError:
        return f"{v}% " if is_percent else f"{v} "


def format_effect_line(effect_key, value, scope_key, optional_only_in_game_mode, effects_loc_kv, scope_loc_kv):
    raw_loc, base_clean = resolve_effect_loc(effect_key, effects_loc_kv)

    if not base_clean:
        return ""

    if is_hidden_effect(raw_loc) or is_hidden_effect(base_clean):
        return ""

    base_title = strip_tw_markup(base_clean).strip()
    if not base_title:
        return ""

    prefix = format_effect_value_prefix(value, raw_loc)
    scope_txt = resolve_scope_loc(scope_key, scope_loc_kv)
    mode_suffix = format_optional_mode_suffix(optional_only_in_game_mode)

    if scope_txt:
        return f"{prefix}{base_title} {scope_txt}{mode_suffix}"
    return f"{prefix}{base_title}{mode_suffix}"


def extract_effect_list_from_ceo_node(node_data):
    """
    ceo_nodes may store effect list under different columns.
    """
    if not node_data:
        return ""
    for k in ("effect_list", "ceo_effect_list", "effects", "effects_list", "ceo_effects_list"):
        v = _s(node_data.get(k, ""))
        if v:
            return v
    return ""


def _dedupe_preserve(seq):
    seen = set()
    out = []
    for x in seq:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("=" * 60)
    print("190 Expanded Wiki - Database Parser (Patched + Effects Trim)")
    print("=" * 60)
    print()

    if not os.path.exists(DB_PATH):
        print(f"ERROR: Database folder not found: {DB_PATH}")
        return

    # [1/10] loc
    print("[1/10] Loading localization files...")

    loc_titles, loc_descs = load_loc_file_ceo_patterns(LOC_PATH)
    print(f"  From {os.path.basename(LOC_PATH)}: {len(loc_titles)} titles, {len(loc_descs)} descs")

    at_titles, at_descs = load_loc_file_ceo_patterns(ALL_TITLES_LOC_PATH)
    print(f"  From {os.path.basename(ALL_TITLES_LOC_PATH)} (pattern): {len(at_titles)} titles, {len(at_descs)} descs")

    loc_titles.update(at_titles)
    loc_descs.update(at_descs)

    all_titles_kv = load_loc_kv(ALL_TITLES_LOC_PATH)
    print(f"  From {os.path.basename(ALL_TITLES_LOC_PATH)} (raw keys): {len(all_titles_kv)}")
    print()

    # [2/10] names
    print("[2/10] Loading name localizations...")
    print(f"    Names folder: {NAMES_LOC_FOLDER}")
    names_lookup, alt_names_lookup = load_names_loc_files(NAMES_LOC_FOLDER)
    print(f"  Total: {len(names_lookup)} names, {len(alt_names_lookup)} alt names")
    print()

    # [3/10] effects + scopes loc
    print("[3/10] Loading effects & scopes localization files...")
    print(f"    Effects folder: {EFFECTS_LOC_FOLDER}")
    effects_loc_kv = load_all_loc_kv_from_folder(EFFECTS_LOC_FOLDER)
    scope_loc_kv = load_all_loc_kv_from_folder(SCOPES_LOC_FOLDER)
    print(f"  Total effect loc keys loaded: {len(effects_loc_kv)}")
    print(f"  Total scope loc keys loaded: {len(scope_loc_kv)}")
    print()

    # [4/10] templates
    print("[4/10] Loading character templates...")
    templates_folder = os.path.join(DB_PATH, "character_generation_templates_tables")
    templates_by_key = {}

    base_path = os.path.join(templates_folder, "data__.tsv")
    if os.path.exists(base_path):
        base_templates = parse_tsv(base_path)
        for t in base_templates:
            key = _s(t.get("key", ""))
            if key:
                templates_by_key[key] = t
        print(f"  Loaded base data__.tsv: {len(base_templates)} templates")

    if os.path.exists(templates_folder):
        for filename in sorted(os.listdir(templates_folder)):
            if filename.endswith(".tsv") and filename != "data__.tsv":
                filepath = os.path.join(templates_folder, filename)
                custom_templates = parse_tsv(filepath)
                count = 0
                for t in custom_templates:
                    key = _s(t.get("key", ""))
                    if key:
                        templates_by_key[key] = t
                        count += 1
                print(f"  Loaded override {filename}: {count} templates")

    templates = list(templates_by_key.values())
    print(f"  Total merged: {len(templates)} templates")
    print()

    # [5/10] campaign_character_arts
    print("[5/10] Loading campaign character arts...")
    art_to_portrait = load_campaign_character_arts(DB_PATH)
    print(f"  Found {len(art_to_portrait)} art -> portrait mappings")
    if art_to_portrait:
        sample_keys = list(art_to_portrait.keys())[:5]
        print(f"  Sample art_set keys: {sample_keys}")
    print()

    # [6/10] game mode details
    print("[6/10] Loading game mode details...")
    gmd_folder = os.path.join(DB_PATH, "character_generation_template_game_mode_details_tables")
    template_to_initial_ceos = {}
    template_to_skill_set = {}

    base_path = os.path.join(gmd_folder, "data__.tsv")
    if os.path.exists(base_path):
        for gmd in parse_tsv(base_path):
            template_key = _s(gmd.get("character_generation_template", ""))
            initial_ceos = _s(gmd.get("initial_ceos", ""))
            # "skill set override" has spaces, not underscores
            skill_set = _s(gmd.get("skill set override", "")) or _s(gmd.get("skill_set_override", ""))
            if template_key and initial_ceos:
                template_to_initial_ceos[template_key] = initial_ceos
            if template_key and skill_set:
                template_to_skill_set[template_key] = skill_set
        print(f"  Loaded base: {len(template_to_initial_ceos)} ceo mappings, {len(template_to_skill_set)} skill set mappings")

    if os.path.exists(gmd_folder):
        for filename in sorted(os.listdir(gmd_folder)):
            if filename.endswith(".tsv") and filename != "data__.tsv":
                filepath = os.path.join(gmd_folder, filename)
                ceo_count = 0
                skill_count = 0
                for gmd in parse_tsv(filepath):
                    template_key = _s(gmd.get("character_generation_template", ""))
                    initial_ceos = _s(gmd.get("initial_ceos", ""))
                    skill_set = _s(gmd.get("skill set override", "")) or _s(gmd.get("skill_set_override", ""))
                    if template_key and initial_ceos:
                        template_to_initial_ceos[template_key] = initial_ceos
                        ceo_count += 1
                    if template_key and skill_set:
                        template_to_skill_set[template_key] = skill_set
                        skill_count += 1
                print(f"  Loaded override {filename}: {ceo_count} ceo, {skill_count} skill set mappings")

    print(f"  Total: {len(template_to_initial_ceos)} ceo mappings, {len(template_to_skill_set)} skill set mappings")
    print()

    # [7/10] ceo_initial_data_to_stages
    print("[7/10] Loading CEO initial data to stages...")
    stages_folder = os.path.join(DB_PATH, "ceo_initial_data_to_stages_tables")
    stages_path, stype = get_best_file(stages_folder)

    stages_data = []
    if stages_path:
        stages_data = parse_tsv(stages_path) if stype == "tsv" else parse_xml_to_list(stages_path)

    print(f"  Using: {os.path.basename(stages_path) if stages_path else 'NONE'} ({stype})")
    print(f"  Rows: {len(stages_data)}")

    def _get_stage_value(row):
        for k in ("stage", "stage_level", "stage_id", "ceo_stage"):
            v = _s(row.get(k, ""))
            if v:
                return v
        return ""

    def _get_initial_data_key(row):
        for k in ("ceo_initial_data", "initial_data", "ceo_initial_data_key"):
            v = _s(row.get(k, ""))
            if v:
                return v
        return ""

    def _get_initial_data_stage(row):
        for k in ("initial_data_stage", "stage_key", "ceo_initial_data_stage"):
            v = _s(row.get(k, ""))
            if v:
                return v
        return ""

    initial_data_to_stage11 = {}
    initial_data_to_stage3 = {}

    for row in stages_data:
        stage_val = _get_stage_value(row)
        ceo_initial_data = _get_initial_data_key(row)
        initial_data_stage = _get_initial_data_stage(row)

        if not (ceo_initial_data and initial_data_stage and stage_val):
            continue

        if stage_val == "11":
            initial_data_to_stage11[ceo_initial_data] = initial_data_stage
        elif stage_val == "3":
            initial_data_to_stage3[ceo_initial_data] = initial_data_stage

    print(f"  Found {len(initial_data_to_stage11)} stage 11 mappings")
    print(f"  Found {len(initial_data_to_stage3)} stage 3 mappings")
    print()

    # [8/10] active ceos
    print("[8/10] Loading CEO active CEOs...")
    active_folder = os.path.join(DB_PATH, "ceo_initial_data_active_ceos_tables")
    active_path, atype = get_best_file(active_folder)

    active_data = []
    if active_path:
        active_data = parse_tsv(active_path) if atype == "tsv" else parse_xml_to_list(active_path)

    print(f"  Using: {os.path.basename(active_path) if active_path else 'NONE'} ({atype})")
    print(f"  Rows: {len(active_data)}")

    # IMPORTANT: stage -> LIST of trait CEOs (not a single overwrite)
    stage_to_career_ceo = {}
    stage_to_trait_ceos = defaultdict(list)

    trait_ceo_pool = []  # global pool of all trait_* CEOs

    for row in active_data:
        stage = _s(row.get("initial_data_stage", "")) or _s(row.get("stage", "")) or _s(row.get("stage_key", ""))
        active_ceo = _s(row.get("active_ceo", "")) or _s(row.get("ceo", "")) or _s(row.get("ceo_key", ""))
        if not (stage and active_ceo):
            continue

        lower = active_ceo.lower()

        if "career" in lower:
            stage_to_career_ceo[stage] = active_ceo

        # collect ALL traits (personality, physical, etc.)
        if "trait_" in lower:
            stage_to_trait_ceos[stage].append(active_ceo)
            trait_ceo_pool.append(active_ceo)

    # de-dupe
    trait_ceo_pool = _dedupe_preserve(trait_ceo_pool)
    for st, lst in list(stage_to_trait_ceos.items()):
        stage_to_trait_ceos[st] = _dedupe_preserve(lst)

    print(f"  Found {len(stage_to_career_ceo)} career CEOs")
    stages_with_traits = sum(1 for st, lst in stage_to_trait_ceos.items() if lst)
    max_traits_in_stage = max((len(lst) for lst in stage_to_trait_ceos.values()), default=0)
    print(f"  Found traits for {stages_with_traits} stages")
    print(f"  Global trait CEO pool: {len(trait_ceo_pool)}")
    print(f"  Max traits in a stage: {max_traits_in_stage}")
    print()

    # [9/10] thresholds + threshold_nodes + nodes
    print("[9/10] Loading CEO thresholds and nodes...")

    thresholds_candidates = [
        os.path.join(DB_PATH, "ceo_thresholds", "ceo_thresholds.xml"),
        os.path.join(DB_PATH, "ceo_thresholds_tables", "ceo_thresholds.xml"),
    ]
    thresholds_path = next((p for p in thresholds_candidates if os.path.exists(p)), None)
    thresholds_data = parse_xml_to_list(thresholds_path) if thresholds_path else []
    print(f"  thresholds: {os.path.basename(thresholds_path) if thresholds_path else 'NONE'} rows={len(thresholds_data)}")

    ceo_to_threshold = {}
    for row in thresholds_data:
        ceo = _s(row.get("ceo", ""))
        threshold_key = _s(row.get("key", ""))
        if ceo and threshold_key:
            ceo_to_threshold[ceo] = threshold_key

    threshold_nodes_candidates = [
        os.path.join(DB_PATH, "ceo_threshold_nodes", "ceo_threshold_nodes.xml"),
        os.path.join(DB_PATH, "ceo_threshold_nodes_tables", "ceo_threshold_nodes.xml"),
    ]
    threshold_nodes_path = next((p for p in threshold_nodes_candidates if os.path.exists(p)), None)
    threshold_nodes_data = parse_xml_to_list(threshold_nodes_path) if threshold_nodes_path else []
    print(f"  threshold_nodes: {os.path.basename(threshold_nodes_path) if threshold_nodes_path else 'NONE'} rows={len(threshold_nodes_data)}")

    threshold_to_nodes = defaultdict(list)
    for row in threshold_nodes_data:
        threshold = _s(row.get("ceo_threshold", ""))
        node = _s(row.get("ceo_node", ""))
        if threshold and node:
            threshold_to_nodes[threshold].append(node)

    nodes_candidates = [
        os.path.join(DB_PATH, "ceo_nodes_tables", "ceo_nodes.xml"),
        os.path.join(DB_PATH, "ceo_nodes", "ceo_nodes.xml"),
    ]
    nodes_path = next((p for p in nodes_candidates if os.path.exists(p)), None)
    ceo_nodes = parse_xml_to_dict(nodes_path, key_field="key") if nodes_path else {}
    print(f"  ceo_nodes: {os.path.basename(nodes_path) if nodes_path else 'NONE'} rows={len(ceo_nodes)}")
    print()

    # [10/10] ceo_effect_list_to_effects
    print("[10/10] Loading CEO effect lists...")
    effect_list_map, eff_path, eff_type, eff_rows = load_ceo_effect_list_to_effects(DB_PATH)
    print(f"  Using: {os.path.basename(eff_path) if eff_path else 'NONE'} ({eff_type})")
    print(f"  Rows: {eff_rows}")
    print(f"  Lists: {len(effect_list_map)}")
    print()

    # ages
    print("[extra] Loading age ranges...")
    ages_folder = os.path.join(DB_PATH, "character_generation_spawn_age_ranges_tables")
    age_lookup = {}

    base_ages_path = os.path.join(ages_folder, "data__.tsv")
    if os.path.exists(base_ages_path):
        for age in parse_tsv(base_ages_path):
            k = _s(age.get("key", ""))
            if k:
                age_lookup[k] = _s(age.get("birth_year", ""))

    if os.path.exists(ages_folder):
        for filename in sorted(os.listdir(ages_folder)):
            if filename.endswith(".tsv") and filename != "data__.tsv":
                for age in parse_tsv(os.path.join(ages_folder, filename)):
                    k = _s(age.get("key", ""))
                    if k:
                        age_lookup[k] = _s(age.get("birth_year", ""))

    print(f"  Found {len(age_lookup)} age ranges")
    print()

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

        characters.append({
            "key": key,
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
            "death_year": "???",
            "traits": trait_ceos,
            "skill_set": skill_set,
        })

        # =========================
        # Character Details (effects + portrait)
        # =========================
        effects_out = []

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

        # Portrait
        art_set_override = _s(template.get("art_set_override", ""))
        portrait_url = ""

        if art_set_override:
            if art_set_override in art_to_portrait:
                portrait_key = art_to_portrait[art_set_override]
                portrait_url = convert_portrait_to_url(portrait_key)
            elif DEBUG_MISSING:
                print(f"[NO PORTRAIT] {display_name}: art_set_override='{art_set_override}' not in art_to_portrait")

        if effects_out or portrait_url:
            character_details[key] = {
                "portrait": {
                    "url": portrait_url,
                    "alt": f"{display_name} portrait",
                    "caption": ""
                },
                "effects": effects_out,
                "traits": trait_ceos
            }

    characters.sort(key=lambda x: x["display_name"])

    with_titles = sum(1 for c in characters if c["title"])
    with_desc = sum(1 for c in characters if c["description"])
    with_portraits = sum(1 for _, v in character_details.items() if v.get("portrait", {}).get("url"))
    with_skill_sets = sum(1 for c in characters if c.get("skill_set"))

    print(f"  Processed {len(characters)} characters")
    print(f"  With titles: {with_titles}")
    print(f"  With descriptions: {with_desc}")
    print(f"  With portraits: {with_portraits}")
    print(f"  With effects entries: {len(character_details)}")
    print(f"  With skill sets: {with_skill_sets}")
    print()

    # ============================================================================
    # Output JS files
    # ============================================================================

    print("Generating output files...")
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    js_output = f"""// Auto-generated character data for 190 Expanded Wiki
// Total characters: {len(characters)}

const CHARACTER_DATA = {json.dumps(characters, indent=2, ensure_ascii=False)};

const CHARACTER_LOOKUP = {{}};
CHARACTER_DATA.forEach(char => {{ CHARACTER_LOOKUP[char.name_key] = char; }});

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
    details_js = "// Auto-generated character details (portraits + effects)\n"
    details_js += f"// Total entries: {len(character_details)}\n\n"
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

    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Total: {len(characters)}, Titles: {with_titles}, Descriptions: {with_desc}, Details: {len(character_details)}, Skill Sets: {with_skill_sets}")
    print()


if __name__ == "__main__":
    main()