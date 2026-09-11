#!/usr/bin/env python3
"""
190 Expanded Wiki - shared TW3K parsing helpers
===============================================
Extracted from parse_tw3k_db.py so parse_tw3k_db.py, parse_skill_trees.py and
parse_factions.py share ONE implementation of:
  - loc TSV reading (key<TAB>text<TAB>tooltip)
  - db TSV / Assembly-Kit XML reading
  - table merging (vanilla data__.tsv first, then every mod TSV)
  - TW markup stripping, {{tr:...}} replacement, effect line formatting
"""

import os
import csv
import xml.etree.ElementTree as ET
import re
from collections import defaultdict

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

# Global holder for ui_text_replacements - will be populated at runtime
_ui_text_replacements_kv = {}


def load_ui_text_replacements(filepath):
    """
    Load ui_text_replacements loc file into key->value dict.
    Keys in file are like: ui_text_replacements_localised_text_<token>
    We store them with just the <token> part as the key for easy lookup.
    """
    result = {}
    if not filepath or not os.path.exists(filepath):
        return result
    
    for key, value in iter_loc_tsv(filepath):
        # Extract the token from the full key
        # ui_text_replacements_localised_text_<token> -> <token>
        prefix = "ui_text_replacements_localised_text_"
        if key.startswith(prefix):
            token = key[len(prefix):]
            if token and value:
                result[token] = value
                # Also store lowercase version for case-insensitive lookup
                result[token.lower()] = value
        # Also store with full key for direct lookup
        if key and value:
            result[key] = value
    
    return result


def replace_tr_tokens(text: str, ui_replacements: dict = None) -> str:
    """
    Replace {{tr:...}} tokens with correct TW3K English,
    preserving capitalization.
    
    First checks the dynamic ui_text_replacements dict, 
    then falls back to static TR_REPLACEMENTS.
    """
    if ui_replacements is None:
        ui_replacements = _ui_text_replacements_kv
    
    def repl(match):
        key = match.group(1).strip()
        
        # First try dynamic ui_text_replacements lookup
        replacement = ui_replacements.get(key)
        if not replacement:
            # Try case-insensitive lookup
            replacement = ui_replacements.get(key.lower())
        if not replacement:
            # Try with the full loc key format
            full_key = f"ui_text_replacements_localised_text_{key}"
            replacement = ui_replacements.get(full_key)
        
        # Fall back to static TR_REPLACEMENTS
        if not replacement:
            replacement = TR_REPLACEMENTS.get(key)
        if not replacement:
            replacement = TR_REPLACEMENTS.get(key.lower())
        
        if not replacement:
            # If still not found, return empty string (remove the token)
            return ""
        
        # Preserve capitalization based on the original token
        token = match.group(0)
        # Check if the first letter after {{tr: is uppercase
        # Format is {{tr:KEY}} so check the character at position 5
        if len(key) > 0 and key[0].isupper():
            return replacement[0].upper() + replacement[1:] if len(replacement) > 1 else replacement.upper()
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
    s = re.sub(r"%\s*[nd]\s*%", "", s, flags=re.IGNORECASE)
    s = re.sub(r"\+\s*[nd]\b", "", s, flags=re.IGNORECASE)
    s = re.sub(r"(?<![%\w])%\s*[nd]\b", "", s, flags=re.IGNORECASE)   # bare %n / %d
    s = re.sub(r"\[\[\s*img:[^\]]*\]\]\s*\[\[\s*/\s*img\s*\]\]", "", s, flags=re.IGNORECASE)
    s = re.sub(r"\[\[\s*/?\s*img[^\]]*\]\]", "", s, flags=re.IGNORECASE)
    s = re.sub(r":\s*(?=\(|$)", "", s)   # dangling "Spies provided:" after a removed token

    s = s.replace("\\\\n", " ").replace("\\n", " ")
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

    # text-only effects (loc has no %+n / %n token) carry no meaningful number
    prefix = format_effect_value_prefix(value, raw_loc) if re.search(r"%\+?\s*[nd]", raw_loc, re.I) else ""
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
# TABLE MERGING (vanilla data__.tsv first, then every other TSV, sorted)
# ============================================================================

def _table_sort_key(filename):
    return ("0" if filename == "data__.tsv" else "1") + filename.lower()


def load_table(db_path, table_name, alt_names=()):
    """
    Merge every *.tsv in db/<table_name>/ (data__.tsv first, then the rest sorted).
    Falls back to XML files only when the folder has no TSV at all.
    alt_names: other folder names to try (handles snapshot/mod naming drift).
    Returns (rows, files_loaded).
    """
    candidates = [table_name] + list(alt_names)
    folder = None
    for c in candidates:
        p = os.path.join(db_path, c)
        if os.path.isdir(p):
            folder = p
            break
    if not folder:
        return [], []

    files = os.listdir(folder)
    tsv_files = sorted([f for f in files if f.lower().endswith(".tsv")], key=_table_sort_key)
    xml_files = sorted([f for f in files if f.lower().endswith(".xml")])

    rows, loaded = [], []
    for f in tsv_files:
        r = parse_tsv(os.path.join(folder, f))
        if r:
            rows.extend(r)
            loaded.append(f)
    if not rows:
        for f in xml_files:
            r = parse_xml_to_list(os.path.join(folder, f))
            if r:
                rows.extend(r)
                loaded.append(f)
    return rows, loaded


def load_table_dict(db_path, table_name, key_field="key", alt_names=()):
    """Same as load_table but returns {key: row}; later rows overwrite earlier ones."""
    rows, loaded = load_table(db_path, table_name, alt_names)
    out = {}
    for r in rows:
        k = _s(r.get(key_field, ""))
        if k:
            out[k] = r
    return out, loaded


def load_all_loc_kv_recursive(folder_path):
    """Like load_all_loc_kv_from_folder but walks sub-folders too."""
    merged = {}
    if not os.path.exists(folder_path):
        return merged
    for root, _dirs, files in os.walk(folder_path):
        for filename in sorted(files):
            fl = filename.lower()
            if not (fl.endswith(".loc.tsv") or fl.endswith("_loc.tsv") or fl.endswith(".tsv")):
                continue
            for k, v in iter_loc_tsv(os.path.join(root, filename)):
                if k and v:
                    merged[k] = v
    return merged


def set_ui_text_replacements(kv):
    """Install the {{tr:...}} replacement table used by replace_tr_tokens/strip_tw_markup."""
    global _ui_text_replacements_kv
    _ui_text_replacements_kv = kv or {}


def find_loc_file(folder, *names):
    """First existing file among names inside folder (or None)."""
    for n in names:
        p = os.path.join(folder, n)
        if os.path.exists(p):
            return p
    return None


def load_site_loc(text_root):
    """
    Build the single merged loc dict used by every parser.
    Load order (later overrides earlier): text/vanilla, text/mod/**, text/extra/**.
    """
    merged = {}
    for sub in ("vanilla", "mod", "extra"):
        merged.update(load_all_loc_kv_recursive(os.path.join(text_root, sub)))
    return merged


def sub_loc(loc, prefix):
    """Subset of a loc dict whose keys start with prefix (cheap views for the resolvers)."""
    return {k: v for k, v in loc.items() if k.startswith(prefix)}


def build_ui_text_replacements(loc):
    """Same shape load_ui_text_replacements() produces, but from the merged loc dict."""
    result = {}
    prefix = "ui_text_replacements_localised_text_"
    for key, value in loc.items():
        if not key.startswith(prefix) or not value:
            continue
        token = key[len(prefix):]
        result[token] = value
        result[token.lower()] = value
        result[key] = value
    return result


PLACEHOLDER_TOKENS = {"placeholder", "placeholder.", "tbd", "todo"}


def clean_text(value):
    """Strip and blank out CA/mod placeholder strings."""
    v = _s(value)
    return "" if v.lower() in PLACEHOLDER_TOKENS else v
