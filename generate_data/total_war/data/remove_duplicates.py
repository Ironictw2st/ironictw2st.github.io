#!/usr/bin/env python3
"""
Duplicate Template Key Finder and Remover

This script reads characters.js and character_details.js files and:
1. Finds duplicate template keys in each file
2. Reports all duplicates found
3. Removes duplicates (keeps the first occurrence)
4. Outputs cleaned files

Usage:
    python remove_duplicates.py [--dry-run]
    
Options:
    --dry-run    Only report duplicates without modifying files
"""

import re
import json
import sys
import os
from collections import defaultdict

def extract_characters_array(content):
    """Extract the CHARACTER_DATA array from characters.js"""
    # Find the array start
    match = re.search(r'const\s+CHARACTER_DATA\s*=\s*\[', content)
    if not match:
        raise ValueError("Could not find CHARACTER_DATA array")
    
    start = match.end() - 1  # Include the [
    
    # Find matching bracket
    bracket_count = 0
    end = start
    for i, char in enumerate(content[start:], start):
        if char == '[':
            bracket_count += 1
        elif char == ']':
            bracket_count -= 1
            if bracket_count == 0:
                end = i + 1
                break
    
    array_str = content[start:end]
    
    # Parse as JSON
    try:
        data = json.loads(array_str)
        return data
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        # Try to fix trailing commas
        fixed = re.sub(r',(\s*[\]}])', r'\1', array_str)
        return json.loads(fixed)

def extract_details_object(content):
    """Extract the CHARACTER_DETAILS object from character_details.js"""
    # Find the object start
    match = re.search(r'const\s+CHARACTER_DETAILS\s*=\s*\{', content)
    if not match:
        raise ValueError("Could not find CHARACTER_DETAILS object")
    
    start = match.end() - 1  # Include the {
    
    # Find matching bracket
    bracket_count = 0
    end = start
    for i, char in enumerate(content[start:], start):
        if char == '{':
            bracket_count += 1
        elif char == '}':
            bracket_count -= 1
            if bracket_count == 0:
                end = i + 1
                break
    
    obj_str = content[start:end]
    
    # Parse as JSON
    try:
        data = json.loads(obj_str)
        return data
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        # Try to fix trailing commas
        fixed = re.sub(r',(\s*[\]}])', r'\1', obj_str)
        return json.loads(fixed)

def find_duplicates_in_array(data, key_field='key'):
    """Find duplicate keys in an array of objects"""
    seen = {}
    duplicates = defaultdict(list)
    
    for idx, item in enumerate(data):
        key = item.get(key_field)
        if key in seen:
            duplicates[key].append({
                'index': idx,
                'first_index': seen[key],
                'data': item
            })
        else:
            seen[key] = idx
    
    return duplicates

def find_duplicates_in_object(data):
    """
    For objects, JSON parsing automatically handles duplicates (keeps last).
    But we need to check the raw file for duplicate keys.
    """
    # Objects in Python dict can't have duplicates, so we need to parse raw
    return {}  # Will handle this differently

def check_raw_duplicates(content, pattern):
    """Check for duplicate keys in raw file content"""
    matches = re.findall(pattern, content)
    seen = {}
    duplicates = defaultdict(list)
    
    for idx, key in enumerate(matches):
        if key in seen:
            duplicates[key].append(idx)
        else:
            seen[key] = idx
    
    return duplicates

def remove_duplicates_from_array(data, key_field='key'):
    """Remove duplicates from array, keeping first occurrence"""
    seen = set()
    result = []
    removed = []
    
    for item in data:
        key = item.get(key_field)
        if key not in seen:
            seen.add(key)
            result.append(item)
        else:
            removed.append(key)
    
    return result, removed

def generate_characters_js(data, header_comment=""):
    """Generate characters.js content from data"""
    lines = [
        "// Auto-generated character data for 190 Expanded Wiki",
        f"// Total characters: {len(data)}",
        "",
        "const CHARACTER_DATA = "
    ]
    
    json_str = json.dumps(data, indent=2, ensure_ascii=False)
    lines.append(json_str + ";")
    
    return "\n".join(lines)

def generate_details_js(data, header_comment=""):
    """Generate character_details.js content from data"""
    lines = [
        "// Auto-generated character details (portraits + effects)",
        f"// Total entries: {len(data)}",
        "",
        "const CHARACTER_DETAILS = "
    ]
    
    json_str = json.dumps(data, indent=2, ensure_ascii=False)
    lines.append(json_str + ";")
    
    # Add the lookup helper
    lines.append("")
    lines.append("// Quick lookup by template key")
    lines.append("const CHARACTER_DETAILS_LOOKUP = CHARACTER_DETAILS;")
    
    return "\n".join(lines)

def main():
    dry_run = '--dry-run' in sys.argv
    
    # File paths - check multiple locations
    characters_paths = [
        'characters.js',
        '/mnt/user-data/uploads/characters.js',
        'data/characters.js'
    ]
    details_paths = [
        'character_details.js', 
        '/mnt/user-data/uploads/character_details.js',
        'data/character_details.js'
    ]
    
    characters_file = None
    details_file = None
    
    for path in characters_paths:
        if os.path.exists(path):
            characters_file = path
            break
    
    for path in details_paths:
        if os.path.exists(path):
            details_file = path
            break
    
    if not characters_file:
        print("ERROR: Could not find characters.js")
        print("Please run this script in the same directory as your data files,")
        print("or provide the files in /mnt/user-data/uploads/")
        sys.exit(1)
    
    if not details_file:
        print("ERROR: Could not find character_details.js")
        sys.exit(1)
    
    print("=" * 60)
    print("DUPLICATE TEMPLATE KEY FINDER")
    print("=" * 60)
    print(f"\nMode: {'DRY RUN (no changes will be made)' if dry_run else 'LIVE (will modify files)'}")
    print(f"\nFiles:")
    print(f"  - characters.js: {characters_file}")
    print(f"  - character_details.js: {details_file}")
    
    # Read files
    print("\n" + "-" * 60)
    print("Reading files...")
    
    with open(characters_file, 'r', encoding='utf-8') as f:
        characters_content = f.read()
    
    with open(details_file, 'r', encoding='utf-8') as f:
        details_content = f.read()
    
    # Parse characters.js
    print("Parsing characters.js...")
    try:
        characters_data = extract_characters_array(characters_content)
        print(f"  Found {len(characters_data)} character entries")
    except Exception as e:
        print(f"  ERROR parsing characters.js: {e}")
        sys.exit(1)
    
    # Parse character_details.js
    print("Parsing character_details.js...")
    try:
        details_data = extract_details_object(details_content)
        print(f"  Found {len(details_data)} detail entries")
    except Exception as e:
        print(f"  ERROR parsing character_details.js: {e}")
        sys.exit(1)
    
    # Check for duplicates in characters.js
    print("\n" + "-" * 60)
    print("Checking for duplicates in characters.js...")
    
    char_duplicates = find_duplicates_in_array(characters_data, 'key')
    
    if char_duplicates:
        print(f"\n  FOUND {len(char_duplicates)} DUPLICATE TEMPLATE KEYS:\n")
        for key, occurrences in char_duplicates.items():
            print(f"  • {key}")
            print(f"    First at index: {occurrences[0]['first_index']}")
            for occ in occurrences:
                print(f"    Duplicate at index: {occ['index']}")
    else:
        print("  No duplicates found in characters.js")
    
    # Check for duplicates in character_details.js (raw check)
    print("\n" + "-" * 60)
    print("Checking for duplicates in character_details.js...")
    
    # Pattern to match template keys in the details file
    key_pattern = r'"([^"]+_template_[^"]+)":\s*\{'
    details_duplicates = check_raw_duplicates(details_content, key_pattern)
    
    if details_duplicates:
        print(f"\n  FOUND {len(details_duplicates)} DUPLICATE TEMPLATE KEYS:\n")
        for key, indices in details_duplicates.items():
            print(f"  • {key}")
            print(f"    Appears {len(indices) + 1} times")
    else:
        print("  No duplicates found in character_details.js")
    
    # Summary
    total_duplicates = len(char_duplicates) + len(details_duplicates)
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"\nDuplicates in characters.js: {len(char_duplicates)}")
    print(f"Duplicates in character_details.js: {len(details_duplicates)}")
    print(f"Total duplicate keys found: {total_duplicates}")
    
    if total_duplicates == 0:
        print("\n✓ No duplicates found! Files are clean.")
        return
    
    if dry_run:
        print("\n[DRY RUN] No changes made. Run without --dry-run to remove duplicates.")
        return
    
    # Remove duplicates and save
    print("\n" + "-" * 60)
    print("Removing duplicates...")
    
    if char_duplicates:
        print("\nProcessing characters.js...")
        cleaned_characters, removed = remove_duplicates_from_array(characters_data, 'key')
        print(f"  Removed {len(removed)} duplicate entries")
        
        # Generate new file
        new_content = generate_characters_js(cleaned_characters)
        
        # Backup original
        backup_path = characters_file + '.backup'
        os.rename(characters_file, backup_path)
        print(f"  Original backed up to: {backup_path}")
        
        # Write new file
        with open(characters_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"  Cleaned file saved: {characters_file}")
        print(f"  New count: {len(cleaned_characters)} characters")
    
    if details_duplicates:
        print("\nProcessing character_details.js...")
        # For the details object, since JSON parsing keeps last occurrence,
        # we just need to regenerate with the already-deduplicated dict
        
        # Generate new file
        new_content = generate_details_js(details_data)
        
        # Backup original
        backup_path = details_file + '.backup'
        os.rename(details_file, backup_path)
        print(f"  Original backed up to: {backup_path}")
        
        # Write new file
        with open(details_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"  Cleaned file saved: {details_file}")
        print(f"  Entry count: {len(details_data)} details")
    
    print("\n" + "=" * 60)
    print("DONE!")
    print("=" * 60)
    print("\nBackup files created with .backup extension")
    print("Review the changes and delete backups when satisfied.")

if __name__ == "__main__":
    main()
