#!/usr/bin/env python3
"""
Family Tree XLSX + Lua to JavaScript Converter
Reads family relationship data from Excel and Lua files and generates JS file
WITH EXTENDED FAMILY DETECTION (cousins, uncles, aunts, grandparents, etc.)
"""

import os
import pandas as pd
import json
import re
from collections import defaultdict

def extract_template_key(full_id):
    """Extract just the template key from full character ID"""
    if pd.isna(full_id) or not full_id:
        return None
    # Split by ':' and take the first part
    return full_id.split(':')[0].strip()

def extract_name_key(template_key):
    """Extract character name key from template key (for matching with CHARACTER_DATA)"""
    if not template_key:
        return None
    
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
                
                print(f"  {child_name or child} has grandparent {grandparent_name or grandparent}")
    
    # Detect uncles/aunts and nephews/nieces
    print("Detecting uncle/aunt relationships...")
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
                
                print(f"  {person_name or person} has uncle/aunt {uncle_aunt_name or uncle_aunt}")
    
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
                        
                        print(f"  {person_name or person} and {cousin_name or cousin} are cousins")
    
    return extended_relationships

def main():
    # Configuration
    EXCEL_FILE = "starter.xlsx"  # Your Excel file
    LUA_FILE = "3k_all_campaign_birthyears.lua"  # Your Lua file
    OUTPUT_FILE = "family_tree.js"
    
    print("=" * 60)
    print("Family Tree XLSX + Lua to JavaScript Converter")
    print("With Extended Family Detection")
    print("=" * 60)
    print()
    
    all_relationships = []
    
    # Read Excel file
    print(f"Reading {EXCEL_FILE}...")
    try:
        df = pd.read_excel(EXCEL_FILE)
        print(f"Found {len(df)} relationship records in Excel")
        
        for _, row in df.iterrows():
            char_full = row.get('character', '')
            related_full = row.get('related_to', '')
            relationship = row.get('relationship', '').lower().strip()
            
            char_key = extract_template_key(char_full)
            related_key = extract_template_key(related_full)
            
            if char_key and related_key and relationship:
                all_relationships.append({
                    'character': char_key,
                    'related_to': related_key,
                    'relationship': relationship
                })
    except FileNotFoundError:
        print(f"Excel file '{EXCEL_FILE}' not found, skipping...")
    except Exception as e:
        print(f"Error reading Excel file: {e}")
    
    print()
    
    # Read Lua file
    print(f"Reading {LUA_FILE}...")
    lua_relationships = parse_lua_file(LUA_FILE)
    print(f"Found {len(lua_relationships)} parent-child relationships in Lua")
    
    # Combine all relationships
    all_relationships.extend(lua_relationships)
    
    print()
    print(f"Total relationships found: {len(all_relationships)}")
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
            'related_name': char_name,
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
                        
                        # Add sibling relationship (same as before)
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
    
    # Build family groups (rest of the code remains the same...)
    # [Continue with the rest of the original code for family groups and output]
    
    # Generate JavaScript file
    print(f"\nGenerating {OUTPUT_FILE}...")
    
    js_content = """// Auto-generated family tree data for 190 Expanded Wiki
// Generated from: """ + EXCEL_FILE + """ and """ + LUA_FILE + """
// Total relationships: """ + str(len(relationships)) + """
// Includes extended family: grandparents, uncles, aunts, cousins, etc.
// 
// IMPORTANT: Relationships are stored from the character's perspective

const FAMILY_RELATIONSHIPS = """ + json.dumps(relationships, indent=2) + """;

const FAMILY_RELATIONSHIPS_BIDIRECTIONAL = """ + json.dumps(bidirectional_relationships, indent=2) + """;

const FAMILY_BY_CHARACTER = """ + json.dumps(dict(character_families), indent=2) + """;

// Helper functions...
function getFamilyMembers(characterKey) {
    return FAMILY_BY_CHARACTER[characterKey] || [];
}

function getRelationshipsByType(characterKey, relationshipType) {
    const family = getFamilyMembers(characterKey);
    return family
        .filter(rel => rel.relationship === relationshipType)
        .map(rel => rel.related_to);
}

function getExtendedFamily(characterKey) {
    const family = getFamilyMembers(characterKey);
    const extendedTypes = ['grandparent', 'grandchild', 'uncle', 'aunt', 'nephew', 'niece', 'cousin'];
    return family.filter(rel => extendedTypes.includes(rel.relationship));
}

// All the other helper functions...
"""
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    print(f"Successfully generated {OUTPUT_FILE}")

if __name__ == "__main__":
    main()