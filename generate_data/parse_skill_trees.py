#!/usr/bin/env python3
"""
190 Expanded Wiki - TW3K Skill Tree Parser
==========================================

Exports:
- total_war/data/skill_trees.js

Data flow:
1. character_generation_template_game_mode_details_tables
   -> skill set override -> character_skill_nodes_tables

2. character_skill_nodes_tables
   -> key, character skill key, tier, indent, points on creation, visible in ui, game mode

3. character_skill_node_links_tables
   -> parent key, child key (requirement), parent link position, child link position

4. character_skills_tables
   -> key, image, localised_name (loc), localised_description (loc)

5. character_skill_level_to_effects_junctions_tables
   -> character skill key, effect key, value, effect scope -> loc values

Output JS structure per skill set:
{
  skill_set_key: {
    nodes: [{
      key: "...",
      skill_key: "...",
      tier: 0,
      indent: 0,
      points_on_creation: 0,
      visible_in_ui: true,
      game_mode: "...",
      image: "...",
      title: "...",
      description: "...",
      links: {
        parents: [{key: "...", position: "..."}],
        children: [{key: "...", position: "..."}]
      },
      effects: [{
        effect_key: "...",
        value: "...",
        scope: "...",
        formatted: "..."
      }]
    }]
  }
}
"""

import os
import csv
import xml.etree.ElementTree as ET
import json
import re
from collections import defaultdict

# ============================================================================
# CONFIGURATION (relative to script directory)
# ============================================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(SCRIPT_DIR, "db")

# Big fallback loc
ALL_TITLES_LOC_PATH = os.path.join(SCRIPT_DIR, "all_titles_full.loc.tsv")

# Effects loc folder (effect descriptions)
EFFECTS_LOC_FOLDER = os.path.join(SCRIPT_DIR, "effects")

# Scopes loc folder
SCOPES_LOC_FOLDER = os.path.join(SCRIPT_DIR, "scopes")

# Skills loc folder (for skill names/descriptions)
SKILLS_LOC_FOLDER = os.path.join(SCRIPT_DIR, "skills")

OUTPUT_PATH = os.path.join(SCRIPT_DIR, "total_war", "data", "skill_trees.js")

DEBUG_MISSING = True

# ============================================================================
# HELPERS (copied from base parser)
# ============================================================================

def _s(x) -> str:
    return ("" if x is None else str(x)).strip()


BOOL_TOKENS = {"true", "false"}


def iter_loc_tsv(filepath):
    """
    Robust CA loc TSV reader.
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

                if key.lower() in {"key", "loc_key", "id"}:
                    continue

                last = _s(row[-1]).lower()
                if last in BOOL_TOKENS:
                    text = _s(row[1])
                else:
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


def load_all_loc_kv_from_folder(folder_path):
    """
    Loads every .tsv / .loc.tsv / *_loc.tsv file in a folder into a single key->value dict.
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


def load_loc_kv(filepath):
    """Load loc TSV as raw key->value dict."""
    loc = {}
    for k, v in iter_loc_tsv(filepath):
        if k and not k.startswith("#"):
            loc[k] = v
    return loc


# ============================================================================
# EFFECT FORMATTING HELPERS (from base parser)
# ============================================================================

TR_REPLACEMENTS = {
    "only_if_minister": "(only if this character is a court minister)",
    "only_if_faction_leader_factionwide": "(only if this character is prime minister, heir or faction leader)",
    "only_if_faction_leader": "(only if this character is faction leader)",
    "map_province": "commandery",
    "map_provinces": "commanderies",
    "map_regions": "counties",
    "map_region": "county",
    "public_order": "public order",
    "military_supplies": "military supplies",
}


def replace_tr_tokens(text: str) -> str:
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


def loc_value_is_percent(raw_loc_text: str) -> bool:
    s = _s(raw_loc_text).lower()
    if not s:
        return False
    return bool(re.search(r"%\+\s*n\s*%", s))


def format_effect_value_prefix(value: str, raw_loc_text: str) -> str:
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


def format_effect_line(effect_key, value, scope_key, effects_loc_kv, scope_loc_kv):
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

    if scope_txt:
        return f"{prefix}{base_title} {scope_txt}"
    return f"{prefix}{base_title}"


# ============================================================================
# SKILL TREE SPECIFIC LOADERS
# ============================================================================

def load_all_table_rows(db_path, table_name):
    """
    Load ALL TSV/XML files from a table folder and merge them.
    Later files (alphabetically sorted, with data__.tsv first) override earlier ones.
    Returns: (all_rows, list_of_files_loaded)
    """
    folder = os.path.join(db_path, table_name)
    
    if not os.path.exists(folder):
        return [], []
    
    files = os.listdir(folder)
    tsv_files = [f for f in files if f.endswith(".tsv")]
    xml_files = [f for f in files if f.endswith(".xml")]
    
    # Sort TSV files: data__.tsv first, then others alphabetically
    def sort_key(f):
        if f == 'data__.tsv':
            return '0' + f  # Comes first
        return '1' + f
    tsv_files.sort(key=sort_key)
    
    all_rows = []
    files_loaded = []
    
    # Load all TSV files
    for filename in tsv_files:
        filepath = os.path.join(folder, filename)
        rows = parse_tsv(filepath)
        if rows:
            all_rows.extend(rows)
            files_loaded.append(filename)
    
    # If no TSV files, try XML
    if not all_rows and xml_files:
        for filename in sorted(xml_files):
            filepath = os.path.join(folder, filename)
            rows = parse_xml_to_list(filepath)
            if rows:
                all_rows.extend(rows)
                files_loaded.append(filename)
    
    return all_rows, files_loaded


def load_character_generation_templates(db_path):
    """
    Load character_generation_template_game_mode_details_tables
    Returns: dict of template_key -> skill_set_override
    
    Columns (may have spaces or underscores):
    - character_generation_template / template
    - skill_set_override / skill set override
    """
    rows, files_loaded = load_all_table_rows(db_path, "character_generation_template_game_mode_details_tables")
    
    result = {}
    for row in rows:
        # Try underscore versions first, then space versions
        template_key = (
            _s(row.get("character_generation_template", "")) or 
            _s(row.get("template", ""))
        )
        skill_set = (
            _s(row.get("skill_set_override", "")) or 
            _s(row.get("skill set override", ""))
        )
        
        if template_key and skill_set:
            result[template_key] = skill_set
    
    print(f"  Loaded {len(result)} template -> skill set mappings from {len(files_loaded)} files: {', '.join(files_loaded[:5])}{'...' if len(files_loaded) > 5 else ''}")
    return result


def load_character_skill_nodes(db_path):
    """
    Load character_skill_nodes_tables
    Returns: dict of skill_set_key -> list of node dicts
    
    Columns (may have spaces or underscores):
    - key
    - character_skill_node_set_key / character skill node set key
    - character_skill_key / character skill key
    - tier
    - indent
    - points_on_creation / points on creation
    - visible_in_ui / visible in ui
    - game_mode / game mode
    """
    rows, files_loaded = load_all_table_rows(db_path, "character_skill_nodes_tables")
    
    result = defaultdict(list)
    for row in rows:
        # Get the skill set key (one-to-many relationship) - try underscore first, then space
        skill_set_key = (
            _s(row.get("character_skill_node_set_key", "")) or 
            _s(row.get("character skill node set key", ""))
        )
        
        # Get skill key - try underscore first, then space
        skill_key = (
            _s(row.get("character_skill_key", "")) or 
            _s(row.get("character skill key", ""))
        )
        
        # Get tier and indent - handle empty strings
        tier_val = _s(row.get("tier", "")) or "0"
        indent_val = _s(row.get("indent", "")) or "0"
        
        # Get points_on_creation - try underscore first, then space
        points_val = (
            _s(row.get("points_on_creation", "")) or 
            _s(row.get("points on creation", "")) or 
            "0"
        )
        
        # Get visible_in_ui - try underscore first, then space
        visible_val = (
            _s(row.get("visible_in_ui", "")) or 
            _s(row.get("visible in ui", "")) or 
            "true"
        )
        
        # Get game_mode - try underscore first, then space
        game_mode_val = (
            _s(row.get("game_mode", "")) or 
            _s(row.get("game mode", ""))
        )
        
        node = {
            "key": _s(row.get("key", "")),
            "skill_key": skill_key,
            "tier": tier_val,
            "indent": indent_val,
            "points_on_creation": points_val,
            "visible_in_ui": visible_val,
            "game_mode": game_mode_val,
        }
        
        if skill_set_key and node["key"]:
            result[skill_set_key].append(node)
    
    total_nodes = sum(len(v) for v in result.values())
    print(f"  Loaded {total_nodes} skill nodes across {len(result)} skill sets from {len(files_loaded)} files")
    return dict(result)


def load_character_skill_node_links(db_path):
    """
    Load character_skill_node_links_tables
    Returns: 
    - parent_to_children: dict of parent_key -> list of {child_key, parent_position, child_position}
    - child_to_parents: dict of child_key -> list of {parent_key, parent_position, child_position}
    
    Columns (may have spaces or underscores):
    - parent_key / parent key
    - child_key / child key (requirement)
    - parent_link_position / parent link position
    - child_link_position / child link position
    """
    rows, files_loaded = load_all_table_rows(db_path, "character_skill_node_links_tables")
    
    parent_to_children = defaultdict(list)
    child_to_parents = defaultdict(list)
    
    for row in rows:
        # Try underscore versions first, then space versions
        parent_key = (
            _s(row.get("parent_key", "")) or 
            _s(row.get("parent key", ""))
        )
        child_key = (
            _s(row.get("child_key", "")) or 
            _s(row.get("child key", ""))
        )
        parent_pos = (
            _s(row.get("parent_link_position", "")) or 
            _s(row.get("parent link position", ""))
        )
        child_pos = (
            _s(row.get("child_link_position", "")) or 
            _s(row.get("child link position", ""))
        )
        
        if parent_key and child_key:
            parent_to_children[parent_key].append({
                "key": child_key,
                "parent_position": parent_pos,
                "child_position": child_pos,
            })
            child_to_parents[child_key].append({
                "key": parent_key,
                "parent_position": parent_pos,
                "child_position": child_pos,
            })
    
    print(f"  Loaded {len(parent_to_children)} parent -> child link groups from {len(files_loaded)} files")
    return dict(parent_to_children), dict(child_to_parents)


def load_character_skills(db_path):
    """
    Load character_skills_tables
    Returns: dict of skill_key -> {key, image, localised_name, localised_description}
    
    Columns (may have spaces or underscores):
    - key
    - image_path / image / icon
    - localised_name / localised name
    - localised_description / localised description
    """
    rows, files_loaded = load_all_table_rows(db_path, "character_skills_tables")
    
    result = {}
    for row in rows:
        key = _s(row.get("key", ""))
        if key:
            # Try various column names for image
            image = (
                _s(row.get("image_path", "")) or 
                _s(row.get("image path", "")) or
                _s(row.get("image", "")) or 
                _s(row.get("icon", "")) or
                _s(row.get("icon_path", ""))
            )
            loc_name = (
                _s(row.get("localised_name", "")) or 
                _s(row.get("localised name", ""))
            )
            loc_desc = (
                _s(row.get("localised_description", "")) or 
                _s(row.get("localised description", ""))
            )
            
            result[key] = {
                "key": key,
                "image": image,
                "localised_name": loc_name,
                "localised_description": loc_desc,
            }
    
    print(f"  Loaded {len(result)} character skills from {len(files_loaded)} files")
    return result


def load_skill_level_to_effects(db_path):
    """
    Load character_skill_level_to_effects_junctions_tables
    Returns: dict of skill_key -> list of {effect_key, value, effect_scope}
    
    Columns (may have spaces or underscores):
    - character_skill_key / character skill key / skill
    - effect_key / effect key / effect
    - value
    - effect_scope / effect scope / scope
    """
    rows, files_loaded = load_all_table_rows(db_path, "character_skill_level_to_effects_junctions_tables")
    
    result = defaultdict(list)
    for row in rows:
        # Try underscore versions first, then space versions
        skill_key = (
            _s(row.get("character_skill_key", "")) or 
            _s(row.get("character skill key", "")) or 
            _s(row.get("skill", ""))
        )
        effect_key = (
            _s(row.get("effect_key", "")) or 
            _s(row.get("effect key", "")) or 
            _s(row.get("effect", ""))
        )
        value = _s(row.get("value", ""))
        scope = (
            _s(row.get("effect_scope", "")) or 
            _s(row.get("effect scope", "")) or 
            _s(row.get("scope", ""))
        )
        
        if skill_key and effect_key:
            result[skill_key].append({
                "effect_key": effect_key,
                "value": value,
                "effect_scope": scope,
            })
    
    total_effects = sum(len(v) for v in result.values())
    print(f"  Loaded {total_effects} skill effects across {len(result)} skills from {len(files_loaded)} files")
    return dict(result)


def convert_skill_image_to_url(image_key):
    """Convert skill image key to URL path."""
    if not image_key:
        return ""
    
    # Clean up the path
    image_key = image_key.strip().rstrip('/')
    
    # Normalize backslashes to forward slashes
    image_key = image_key.replace('\\', '/')
    
    # Build the path - match the actual GitHub folder structure:
    # data/UI/Campaign UI/skills/  (with space, URL encoded as %20)
    if image_key.startswith('data/'):
        path = image_key
    elif image_key.lower().startswith('ui/'):
        # Handle ui/ paths from game data
        # e.g., "ui/campaign ui/skills/skill_name" -> "data/UI/Campaign UI/skills/skill_name.png"
        rest = image_key[3:]  # Remove "ui/"
        # Normalize campaign ui folder name variations
        rest_lower = rest.lower()
        if rest_lower.startswith('campaign ui/'):
            rest = 'Campaign UI/' + rest[12:]
        elif rest_lower.startswith('campaign_ui/'):
            rest = 'Campaign UI/' + rest[12:]
        path = f"data/UI/{rest}"
    else:
        # Default: assume it's just a skill name, put in skills folder
        # Match folder structure: data/UI/Campaign UI/skills/
        path = f"data/UI/Campaign UI/skills/{image_key}"
    
    # Add extension if missing
    if not (path.endswith('.png') or path.endswith('.webp')):
        path = f"{path}.png"
    
    # URL-encode spaces as %20 for GitHub Pages
    path = path.replace(' ', '%20')
    
    return path


def resolve_skill_loc(skill_key, loc_key_pattern, all_loc_kv, skills_loc_kv):
    """
    Resolve skill localization.
    Patterns to try:
    - character_skills_localised_name_<skill_key>
    - character_skills_localised_description_<skill_key>
    """
    if not skill_key:
        return ""
    
    # Try skills loc folder first
    for loc_kv in [skills_loc_kv, all_loc_kv]:
        # Direct key
        if skill_key in loc_kv:
            return strip_tw_markup(loc_kv[skill_key])
        
        # Pattern-based keys
        patterns = [
            f"character_skills_{loc_key_pattern}_{skill_key}",
            f"character_skill_{loc_key_pattern}_{skill_key}",
            f"skills_{loc_key_pattern}_{skill_key}",
            f"skill_{loc_key_pattern}_{skill_key}",
        ]
        
        for pattern in patterns:
            if pattern in loc_kv:
                return strip_tw_markup(loc_kv[pattern])
            # Case-insensitive fallback
            pattern_lower = pattern.lower()
            for k, v in loc_kv.items():
                if k.lower() == pattern_lower:
                    return strip_tw_markup(v)
    
    return ""


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("=" * 60)
    print("190 Expanded Wiki - Skill Tree Parser")
    print("=" * 60)
    print()

    if not os.path.exists(DB_PATH):
        print(f"ERROR: Database folder not found: {DB_PATH}")
        return

    # [1/7] Load localization files
    print("[1/7] Loading localization files...")
    
    all_loc_kv = {}
    if os.path.exists(ALL_TITLES_LOC_PATH):
        all_loc_kv = load_loc_kv(ALL_TITLES_LOC_PATH)
        print(f"  Loaded {len(all_loc_kv)} keys from {os.path.basename(ALL_TITLES_LOC_PATH)}")
    
    effects_loc_kv = load_all_loc_kv_from_folder(EFFECTS_LOC_FOLDER)
    print(f"  Loaded {len(effects_loc_kv)} effect loc keys")
    
    scope_loc_kv = load_all_loc_kv_from_folder(SCOPES_LOC_FOLDER)
    print(f"  Loaded {len(scope_loc_kv)} scope loc keys")
    
    skills_loc_kv = load_all_loc_kv_from_folder(SKILLS_LOC_FOLDER)
    print(f"  Loaded {len(skills_loc_kv)} skill loc keys")
    print()

    # [2/7] Load character generation templates
    print("[2/7] Loading character generation templates...")
    template_to_skillset = load_character_generation_templates(DB_PATH)
    print()

    # [3/7] Load skill nodes
    print("[3/7] Loading character skill nodes...")
    skill_nodes_by_set = load_character_skill_nodes(DB_PATH)
    print()

    # [4/7] Load skill node links
    print("[4/7] Loading skill node links...")
    parent_to_children, child_to_parents = load_character_skill_node_links(DB_PATH)
    print()

    # [5/7] Load character skills (for image and loc keys)
    print("[5/7] Loading character skills...")
    character_skills = load_character_skills(DB_PATH)
    print()

    # [6/7] Load skill effects
    print("[6/7] Loading skill level effects...")
    skill_effects = load_skill_level_to_effects(DB_PATH)
    print()

    # [7/7] Build skill tree data
    print("[7/7] Building skill tree data...")
    
    skill_trees = {}
    total_nodes_processed = 0
    total_effects_resolved = 0
    missing_skills = set()
    missing_locs = set()
    
    for skill_set_key, nodes in skill_nodes_by_set.items():
        processed_nodes = []
        
        for node in nodes:
            node_key = node["key"]
            skill_key = node["skill_key"]
            
            # Get skill info
            skill_info = character_skills.get(skill_key, {})
            
            if not skill_info and skill_key:
                missing_skills.add(skill_key)
            
            # Get image
            image = skill_info.get("image", "")
            image_url = convert_skill_image_to_url(image)
            
            # Get title and description from loc
            title = resolve_skill_loc(skill_key, "localised_name", all_loc_kv, skills_loc_kv)
            if not title:
                title = resolve_skill_loc(skill_key, "name", all_loc_kv, skills_loc_kv)
            
            description = resolve_skill_loc(skill_key, "localised_description", all_loc_kv, skills_loc_kv)
            if not description:
                description = resolve_skill_loc(skill_key, "description", all_loc_kv, skills_loc_kv)
            
            if not title and skill_key:
                missing_locs.add(f"title:{skill_key}")
            
            # Get links
            children = parent_to_children.get(node_key, [])
            parents = child_to_parents.get(node_key, [])
            
            # Get effects
            effects_raw = skill_effects.get(skill_key, [])
            effects_formatted = []
            
            for eff in effects_raw:
                formatted = format_effect_line(
                    eff["effect_key"],
                    eff["value"],
                    eff["effect_scope"],
                    effects_loc_kv,
                    scope_loc_kv
                )
                
                effects_formatted.append({
                    "effect_key": eff["effect_key"],
                    "value": eff["value"],
                    "scope": eff["effect_scope"],
                    "formatted": formatted if formatted else "",
                })
                
                if formatted:
                    total_effects_resolved += 1
            
            # Safe conversion for tier and indent (may be floats like "2.0000")
            try:
                tier_int = int(float(node["tier"])) if node["tier"] else 0
            except (ValueError, TypeError):
                tier_int = 0
            
            try:
                indent_float = float(node["indent"]) if node["indent"] else 0
            except (ValueError, TypeError):
                indent_float = 0
            
            try:
                points_int = int(node["points_on_creation"]) if node["points_on_creation"] else 0
            except (ValueError, TypeError):
                points_int = 0
            
            processed_node = {
                "key": node_key,
                "skill_key": skill_key,
                "tier": tier_int,
                "indent": indent_float,
                "points_on_creation": points_int,
                "visible_in_ui": node["visible_in_ui"].lower() == "true",
                "game_mode": node["game_mode"],
                "image": image_url,
                "image_key": image,
                "title": title,
                "description": description,
                "links": {
                    "parents": parents,
                    "children": children,
                },
                "effects": effects_formatted,
            }
            
            processed_nodes.append(processed_node)
            total_nodes_processed += 1
        
        # Sort nodes by tier, then indent
        processed_nodes.sort(key=lambda x: (x["tier"], x["indent"]))
        
        skill_trees[skill_set_key] = {
            "key": skill_set_key,
            "nodes": processed_nodes,
        }
    
    print(f"  Processed {total_nodes_processed} nodes across {len(skill_trees)} skill sets")
    print(f"  Resolved {total_effects_resolved} effect lines")
    
    if DEBUG_MISSING and missing_skills:
        print(f"  [WARNING] {len(missing_skills)} missing skill definitions")
        for sk in list(missing_skills)[:5]:
            print(f"    - {sk}")
        if len(missing_skills) > 5:
            print(f"    ... and {len(missing_skills) - 5} more")
    
    if DEBUG_MISSING and missing_locs:
        print(f"  [WARNING] {len(missing_locs)} missing localizations")
        for lk in list(missing_locs)[:5]:
            print(f"    - {lk}")
        if len(missing_locs) > 5:
            print(f"    ... and {len(missing_locs) - 5} more")
    
    print()

    # ============================================================================
    # Generate output
    # ============================================================================
    
    print("Generating output files...")
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    # Build template to skill set lookup
    template_lookup = {k: v for k, v in template_to_skillset.items() if v in skill_trees}

    js_output = f"""// Auto-generated skill tree data for 190 Expanded Wiki
// Total skill sets: {len(skill_trees)}
// Total nodes: {total_nodes_processed}

const SKILL_TREE_DATA = {json.dumps(skill_trees, indent=2, ensure_ascii=False)};

// Template key -> skill set key lookup
const TEMPLATE_TO_SKILLSET = {json.dumps(template_lookup, indent=2, ensure_ascii=False)};

// Helper functions
const SKILL_TREE_LOOKUP = SKILL_TREE_DATA;

function getSkillTreeBySet(skillSetKey) {{
  return SKILL_TREE_DATA[skillSetKey] || null;
}}

function getSkillTreeByTemplate(templateKey) {{
  const skillSetKey = TEMPLATE_TO_SKILLSET[templateKey];
  if (!skillSetKey) return null;
  return SKILL_TREE_DATA[skillSetKey] || null;
}}

function getSkillNode(skillSetKey, nodeKey) {{
  const tree = SKILL_TREE_DATA[skillSetKey];
  if (!tree) return null;
  return tree.nodes.find(n => n.key === nodeKey) || null;
}}

function getNodesByTier(skillSetKey, tier) {{
  const tree = SKILL_TREE_DATA[skillSetKey];
  if (!tree) return [];
  return tree.nodes.filter(n => n.tier === tier);
}}

// Stats
const SKILL_TREE_STATS = {{
  totalSets: {len(skill_trees)},
  totalNodes: {total_nodes_processed},
  totalEffects: {total_effects_resolved},
  skillSets: Object.keys(SKILL_TREE_DATA),
}};
"""

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(js_output)
    print(f"  Written: {OUTPUT_PATH}")

    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Skill Sets: {len(skill_trees)}")
    print(f"  Total Nodes: {total_nodes_processed}")
    print(f"  Resolved Effects: {total_effects_resolved}")
    print()


if __name__ == "__main__":
    main()