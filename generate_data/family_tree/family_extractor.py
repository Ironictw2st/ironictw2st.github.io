#!/usr/bin/env python3
"""
Family Tree XLSX + Lua to JavaScript Converter - CORRECTLY FIXED VERSION
Reads family relationship data from Excel and Lua files and generates JS file
WITH EXTENDED FAMILY DETECTION (cousins, uncles, aunts, grandparents, etc.)
FIXED: Uses template_id to identify unique character instances
"""

import os
import pandas as pd
import json
import re
from collections import defaultdict

def extract_character_key(full_id):
    """
    Extract character key from full ID.
    For characters from Excel (with full IDs), use template_id as the unique identifier.
    For characters from Lua (just templates), use the template as-is.
    """
    if pd.isna(full_id) or not full_id:
        return None
    
    # Check if this is a full ID (contains ':') or just a template
    if ':' in full_id:
        parts = full_id.split(':')
        if len(parts) >= 6:
            # Full ID format: template:campaign_name:campaign_key:faction:faction_id:template_id
            template = parts[0].strip()
            template_id = parts[5].strip()
            
            # Use template_id as the unique identifier
            # But keep template for reference (useful for name extraction)
            return f"{template}#{template_id}"  # Use # to separate template from ID
        else:
            # Incomplete ID, just use what we have
            return parts[0].strip()
    else:
        # This is just a template (from Lua file), use as-is
        return full_id.strip()

def extract_template_key(character_key):
    """Extract just the template key (without ID) for name extraction"""
    if not character_key:
        return None
    
    if '#' in character_key:
        # Remove template_id part if present
        return character_key.split('#')[0]
    return character_key

def extract_name_key(character_key):
    """Extract character name key from character key (for matching with CHARACTER_DATA)"""
    if not character_key:
        return None
    
    # Get the template part
    template_key = extract_template_key(character_key)
    
    # Pattern to extract name from template keys
    patterns = [
        r"template_(?:historical|generated|fictional)_(?:lady_)?(.+?)_(?:hero_)?(?:fire|earth|water|wood|metal|nanman)",
        r"template_(?:historical|generated|fictional)_(?:lady_)?(.+?)$",
        r"template_ancestral_(.+?)$",
        r"ironic_template_(?:historical|generated|fictional|ancestral)_(?:lady_)?(.+?)_(?:hero_)?(?:fire|earth|water|wood|metal|nanman)",
        r"ironic_template_(?:historical|generated|fictional|ancestral)_(?:lady_)?(.+?)$",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, template_key)
        if match:
            return match.group(1)
    
    # For generic characters, return a descriptive name
    if 'generic' in template_key:
        return template_key.replace('3k_main_template_generic_', '').replace('3k_dlc05_template_generic_', '').replace('_', ' ')
    
    return None

def parse_lua_file(filepath):
    """Parse the Lua file to extract parent-child relationships from register_born calls"""
    relationships = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Lua file '{filepath}' not found, skipping...")
        return relationships
    except Exception as e:
        print(f"Error reading Lua file: {e}")
        return relationships
    
    # Pattern to match register_born calls
    pattern = r'MTUBornService:register_born\s*\(\s*"[^"]*"\s*,\s*"[^"]*"\s*,\s*"[^"]*"\s*,\s*"([^"]*)"\s*,\s*"([^"]*)"\s*,\s*\d+\s*\)'
    
    matches = re.findall(pattern, content)
    
    for child_template, parent_template in matches:
        if child_template and parent_template:
            # For Lua relationships, we only have templates, not full IDs with template_ids
            # These are typically for unique historical characters
            relationships.append({
                'character': child_template.strip(),
                'related_to': parent_template.strip(),
                'relationship': 'child'
            })
            print(f"  Found from Lua: {child_template} is child of {parent_template}")
    
    return relationships

def infer_reverse_relationship(relationship):
    """Infer the reverse relationship type"""
    reverse_map = {
        'child': 'parent',
        'parent': 'child',
        'spouse': 'spouse',
        'sibling': 'sibling',
        'grandchild': 'grandparent',
        'grandparent': 'grandchild',
        'uncle': 'nephew',
        'aunt': 'niece',
        'nephew': 'uncle',
        'niece': 'aunt',
        'cousin': 'cousin'
    }
    return reverse_map.get(relationship, relationship)

def detect_extended_family(character_families, parent_to_children, child_to_parents):
    """Detect extended family relationships like grandparents, uncles, aunts, cousins"""
    extended_relationships = []
    
    # Detect grandparents and grandchildren
    print("Detecting grandparent relationships...")
    grandparent_count = 0
    for child, parents in child_to_parents.items():
        for parent in parents:
            # Get grandparents (parents of parents)
            grandparents = child_to_parents.get(parent, set())
            for grandparent in grandparents:
                child_name = extract_name_key(child)
                grandparent_name = extract_name_key(grandparent)
                
                # Add grandparent-grandchild relationship
                extended_relationships.append({
                    'character': child,
                    'character_name': child_name,
                    'related_to': grandparent,
                    'related_name': grandparent_name,
                    'relationship': 'grandparent'
                })
                
                extended_relationships.append({
                    'character': grandparent,
                    'character_name': grandparent_name,
                    'related_to': child,
                    'related_name': child_name,
                    'relationship': 'grandchild'
                })
                
                grandparent_count += 1
                if grandparent_count <= 5:  # Only print first few to avoid spam
                    print(f"  {child_name or child} has grandparent {grandparent_name or grandparent}")
    
    if grandparent_count > 5:
        print(f"  ... and {grandparent_count - 5} more grandparent relationships")
    
    # Detect uncles/aunts and nephews/nieces
    print("Detecting uncle/aunt relationships...")
    uncle_count = 0
    for person, parents in child_to_parents.items():
        for parent in parents:
            # Get siblings of parents (uncles/aunts)
            parent_siblings = []
            # Find parent's parents
            grandparents = child_to_parents.get(parent, set())
            for grandparent in grandparents:
                # Get all children of grandparent (parent's siblings)
                for sibling in parent_to_children.get(grandparent, set()):
                    if sibling != parent:
                        parent_siblings.append(sibling)
            
            for uncle_aunt in parent_siblings:
                person_name = extract_name_key(person)
                uncle_aunt_name = extract_name_key(uncle_aunt)
                
                # Determine if uncle or aunt (would need gender info for accuracy)
                # For now, we'll use "uncle" as generic
                extended_relationships.append({
                    'character': person,
                    'character_name': person_name,
                    'related_to': uncle_aunt,
                    'related_name': uncle_aunt_name,
                    'relationship': 'uncle'
                })
                
                extended_relationships.append({
                    'character': uncle_aunt,
                    'character_name': uncle_aunt_name,
                    'related_to': person,
                    'related_name': person_name,
                    'relationship': 'nephew'
                })
                
                uncle_count += 1
                if uncle_count <= 5:
                    print(f"  {person_name or person} has uncle/aunt {uncle_aunt_name or uncle_aunt}")
    
    if uncle_count > 5:
        print(f"  ... and {uncle_count - 5} more uncle/aunt relationships")
    
    # Detect cousins
    print("Detecting cousin relationships...")
    cousins_added = set()
    
    for person, parents in child_to_parents.items():
        for parent in parents:
            # Get parent's siblings
            parent_siblings = []
            grandparents = child_to_parents.get(parent, set())
            for grandparent in grandparents:
                for sibling in parent_to_children.get(grandparent, set()):
                    if sibling != parent:
                        parent_siblings.append(sibling)
            
            # Get children of parent's siblings (cousins)
            for uncle_aunt in parent_siblings:
                for cousin in parent_to_children.get(uncle_aunt, set()):
                    cousin_pair = tuple(sorted([person, cousin]))
                    
                    if cousin_pair not in cousins_added:
                        cousins_added.add(cousin_pair)
                        
                        person_name = extract_name_key(person)
                        cousin_name = extract_name_key(cousin)
                        
                        extended_relationships.append({
                            'character': person,
                            'character_name': person_name,
                            'related_to': cousin,
                            'related_name': cousin_name,
                            'relationship': 'cousin'
                        })
                        
                        extended_relationships.append({
                            'character': cousin,
                            'character_name': cousin_name,
                            'related_to': person,
                            'related_name': person_name,
                            'relationship': 'cousin'
                        })
                        
                        if len(cousins_added) <= 5:
                            print(f"  {person_name or person} and {cousin_name or cousin} are cousins")
    
    if len(cousins_added) > 5:
        print(f"  ... and {len(cousins_added) - 5} more cousin relationships")
    
    return extended_relationships

def main():
    # File paths - UPDATE THESE TO MATCH YOUR DIRECTORY STRUCTURE
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construct paths relative to the script directory
    EXCEL_FILE = os.path.join(script_dir, "starter.xlsx")
    LUA_FILE = os.path.join(script_dir, "3k_all_campaign_birthyears.lua")
    OUTPUT_FILE = os.path.join(script_dir, "family_tree_data.js")
    
    print("Family Tree Data Extractor - CORRECTLY FIXED VERSION")
    print("=" * 60)
    print("Now uses template_id to identify unique character instances")
    print()
    print(f"Script directory: {script_dir}")
    print(f"Looking for Excel file: {EXCEL_FILE}")
    print(f"Looking for Lua file: {LUA_FILE}")
    print(f"Output will be saved to: {OUTPUT_FILE}")
    print()
    
    all_relationships = []
    
    # Read Excel file
    print(f"Reading Excel file...")
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name=0)
        print(f"Found {len(df)} relationships in Excel")
        
        # Debug: Check a few rows to see the structure
        print("\nSample data structure (first 3 rows):")
        for idx in range(min(3, len(df))):
            row = df.iloc[idx]
            char_parts = str(row['character']).split(':') if ':' in str(row['character']) else []
            if len(char_parts) >= 6:
                print(f"  Row {idx}: Template={char_parts[0]}, Template_ID={char_parts[5]}")
        
        # Process Excel relationships
        for idx, row in df.iterrows():
            char_id = row['character']
            related_id = row['related_to']
            relationship = row['relationship']
            
            # Extract character keys (using template_id for uniqueness)
            char_key = extract_character_key(char_id)
            related_key = extract_character_key(related_id)
            
            if char_key and related_key:
                all_relationships.append({
                    'character': char_key,
                    'related_to': related_key,
                    'relationship': relationship
                })
                
    except FileNotFoundError:
        print(f"Excel file not found at {EXCEL_FILE}")
        print("Please ensure starter.xlsx is in the same directory as this script")
    except Exception as e:
        print(f"Error reading Excel file: {e}")
    
    print()
    
    # Read Lua file
    print(f"Reading Lua file...")
    lua_relationships = parse_lua_file(LUA_FILE)
    print(f"Found {len(lua_relationships)} parent-child relationships in Lua")
    
    # Combine all relationships
    all_relationships.extend(lua_relationships)
    
    print()
    print(f"Total relationships found: {len(all_relationships)}")
    
    # Check for duplicate template_ids (debugging)
    print("\nChecking for generic characters with same template but different IDs...")
    generic_templates = defaultdict(set)
    for rel in all_relationships[:100]:  # Check first 100 relationships
        char_key = rel['character']
        if '#' in char_key and 'generic' in char_key:
            template, template_id = char_key.split('#')
            generic_templates[template].add(template_id)
    
    for template, ids in generic_templates.items():
        if len(ids) > 1:
            print(f"  Template {template} has {len(ids)} different instances")
    
    print()
    
    # Process relationships
    relationships = []
    bidirectional_relationships = []
    character_families = defaultdict(list)
    
    # First pass: collect all parent-child relationships for sibling detection
    parent_to_children = defaultdict(set)
    child_to_parents = defaultdict(set)
    
    for rel_data in all_relationships:
        char_key = rel_data['character']
        related_key = rel_data['related_to']
        relationship = rel_data['relationship']
        
        # Track parent-child relationships
        if relationship == 'child':
            child_to_parents[char_key].add(related_key)
            parent_to_children[related_key].add(char_key)
        
        # Extract name keys
        char_name = extract_name_key(char_key)
        related_name = extract_name_key(related_key)
        
        reverse_rel = infer_reverse_relationship(relationship)
        
        rel_entry = {
            'character': char_key,
            'character_name': char_name,
            'related_to': related_key,
            'related_name': related_name,
            'relationship': reverse_rel
        }
        relationships.append(rel_entry)
        
        # Create bidirectional entries
        bidirectional_relationships.append({
            'character': char_key,
            'character_name': char_name,
            'related_to': related_key,
            'related_name': related_name,
            'relationship': reverse_rel
        })
        
        bidirectional_relationships.append({
            'character': related_key,
            'character_name': related_name,
            'related_to': char_key,
            'character_name': char_name,
            'relationship': relationship
        })
        
        # Track for family groups
        character_families[char_key].append({
            'related_to': related_key,
            'related_name': related_name,
            'relationship': reverse_rel
        })
        character_families[related_key].append({
            'related_to': char_key,
            'related_name': char_name,
            'relationship': relationship
        })
    
    # Detect siblings
    print("\nDetecting sibling relationships...")
    siblings_added = set()
    
    for parent_key, children in parent_to_children.items():
        if len(children) > 1:
            children_list = list(children)
            for i, child1 in enumerate(children_list):
                for child2 in children_list[i+1:]:
                    sibling_pair = tuple(sorted([child1, child2]))
                    
                    if sibling_pair not in siblings_added:
                        siblings_added.add(sibling_pair)
                        
                        child1_name = extract_name_key(child1)
                        child2_name = extract_name_key(child2)
                        
                        # Add sibling relationship
                        relationships.append({
                            'character': child1,
                            'character_name': child1_name,
                            'related_to': child2,
                            'related_name': child2_name,
                            'relationship': 'sibling'
                        })
                        
                        bidirectional_relationships.extend([
                            {
                                'character': child1,
                                'character_name': child1_name,
                                'related_to': child2,
                                'related_name': child2_name,
                                'relationship': 'sibling'
                            },
                            {
                                'character': child2,
                                'character_name': child2_name,
                                'related_to': child1,
                                'related_name': child1_name,
                                'relationship': 'sibling'
                            }
                        ])
                        
                        character_families[child1].append({
                            'related_to': child2,
                            'related_name': child2_name,
                            'relationship': 'sibling'
                        })
                        character_families[child2].append({
                            'related_to': child1,
                            'related_name': child1_name,
                            'relationship': 'sibling'
                        })
    
    print(f"Detected {len(siblings_added)} sibling relationships")
    print()
    
    # Detect extended family
    extended = detect_extended_family(character_families, parent_to_children, child_to_parents)
    
    # Add extended relationships
    for ext_rel in extended:
        relationships.append(ext_rel)
        bidirectional_relationships.append(ext_rel)
        
        character_families[ext_rel['character']].append({
            'related_to': ext_rel['related_to'],
            'related_name': ext_rel['related_name'],
            'relationship': ext_rel['relationship']
        })
    
    print(f"\nDetected {len(extended)} extended family relationships")
    
    # Generate JavaScript file
    print(f"\nGenerating {OUTPUT_FILE}...")
    
    # ------------------------------------------------------------
    # JS export (UI-friendly): keep TEMPLATE keys for navigation,
    # but keep UIDs internally so we don't merge unrelated instances.
    #
    # UID rules:
    # - Excel characters (full IDs) => uid = template_id (the 6th colon field)
    # - Lua-only characters (template only) => uid = "t:<template>"
    # ------------------------------------------------------------
    def to_template_and_uid(internal_key: str):
        if not internal_key:
            return (None, None)
        if '#' in internal_key:
            template, template_id = internal_key.split('#', 1)
            template = template.strip()
            template_id = template_id.strip()
            uid = template_id if template_id else f"t:{template}"
            return (template, uid)
        template = internal_key.strip()
        return (template, f"t:{template}")

    export_relationships = []
    export_relationships_bi = []
    family_by_uid = defaultdict(list)
    family_by_template = defaultdict(list)
    template_to_uids = defaultdict(list)

    def export_rel(rel):
        c_t, c_uid = to_template_and_uid(rel.get('character'))
        r_t, r_uid = to_template_and_uid(rel.get('related_to'))
        if not c_t or not c_uid or not r_t or not r_uid:
            return None
        out = {
            'character_template': c_t,
            'character_uid': c_uid,
            'related_template': r_t,
            'related_uid': r_uid,
            'relationship': rel.get('relationship')
        }
        # Preserve optional name keys if present
        if rel.get('character_name') is not None:
            out['character_name'] = rel.get('character_name')
        if rel.get('related_name') is not None:
            out['related_name'] = rel.get('related_name')
        return out

    for rel in relationships:
        out = export_rel(rel)
        if not out:
            continue
        export_relationships.append(out)
        family_by_uid[out['character_uid']].append({
            'related_uid': out['related_uid'],
            'related_template': out['related_template'],
            'related_name': out.get('related_name'),
            'relationship': out['relationship']
        })
        family_by_template[out['character_template']].append({
            'related_uid': out['related_uid'],
            'related_template': out['related_template'],
            'related_name': out.get('related_name'),
            'relationship': out['relationship']
        })
        if out['character_uid'] not in template_to_uids[out['character_template']]:
            template_to_uids[out['character_template']].append(out['character_uid'])

    for rel in bidirectional_relationships:
        out = export_rel(rel)
        if not out:
            continue
        export_relationships_bi.append(out)

    js_content = (
        "// Auto-generated family tree data for 190 Expanded Wiki\n"
        "// UI-FRIENDLY VERSION - Template keys for navigation, UIDs for correctness\n"
        "// Generated from: starter.xlsx and 3k_all_campaign_birthyears.lua\n"
        f"// Total relationships: {len(relationships)}\n"
        "// Includes extended family: grandparents, uncles, aunts, cousins, etc.\n"
        "//\n"
        "// IMPORTANT:\n"
        "// - character_template / related_template are used for site navigation\n"
        "// - character_uid / related_uid are used to ensure we don't merge unrelated instances\n"
        "//   (Excel UIDs are template_id; Lua-only UIDs are 't:<template>')\n\n"
        f"const FAMILY_RELATIONSHIPS = {json.dumps(export_relationships, indent=2)};\n\n"
        f"const FAMILY_RELATIONSHIPS_BIDIRECTIONAL = {json.dumps(export_relationships_bi, indent=2)};\n\n"
        f"const FAMILY_BY_UID = {json.dumps(dict(family_by_uid), indent=2)};\n\n"
        f"const FAMILY_BY_TEMPLATE = {json.dumps(dict(family_by_template), indent=2)};\n\n"
        f"const TEMPLATE_TO_UIDS = {json.dumps(dict(template_to_uids), indent=2)};\n\n"
        "// Helper functions\n"
        "function getFamilyMembersByUid(uid) {\n"
        "  return (typeof FAMILY_BY_UID !== 'undefined' && FAMILY_BY_UID[uid]) ? FAMILY_BY_UID[uid] : [];\n"
        "}\n\n"
        "function getFamilyMembersByTemplate(templateKey) {\n"
        "  return (typeof FAMILY_BY_TEMPLATE !== 'undefined' && FAMILY_BY_TEMPLATE[templateKey]) ? FAMILY_BY_TEMPLATE[templateKey] : [];\n"
        "}\n\n"
        "function getUidsForTemplate(templateKey) {\n"
        "  return (typeof TEMPLATE_TO_UIDS !== 'undefined' && TEMPLATE_TO_UIDS[templateKey]) ? TEMPLATE_TO_UIDS[templateKey] : [];\n"
        "}\n"
    )
    
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(js_content)
        
        print(f"Successfully generated {OUTPUT_FILE}")
        print("\nIMPORTANT: Characters are now uniquely identified by template_id")
        print("Format: template_key#template_id")
        print("Example: 3k_main_template_generic_fire_envoy_normal_m_hero#1276921292")
        print("\nThis ensures each character instance is treated as a unique individual,")
        print("preventing unrelated characters from being incorrectly linked.")
    except Exception as e:
        print(f"Error writing output file: {e}")

if __name__ == "__main__":
    main()