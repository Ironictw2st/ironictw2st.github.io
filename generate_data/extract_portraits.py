#!/usr/bin/env python3
"""
190 Expanded Wiki - Portrait Extractor
======================================
Extracts character portraits from TW3K art folders and renames them for the wiki.

Input structure:
  AllArt/ui/characters/{character_folder}/composites/large_panel/happy/*.png

Output structure:
  images/db/{character_folder}.png

Usage:
  python extract_portraits.py
"""

import os
import shutil
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Input: Where the art folders are located
ART_INPUT_PATH = os.path.join(SCRIPT_DIR, "AllArt", "ui", "characters")

# Output: Where to save the renamed portraits
OUTPUT_PATH = os.path.join(SCRIPT_DIR, "images", "db")

# The subfolder path within each character folder to find the portrait
PORTRAIT_SUBPATH = os.path.join("composites", "large_panel", "happy")

# ============================================================================
# MAIN
# ============================================================================

def main():
    print("=" * 60)
    print("190 Expanded Wiki - Portrait Extractor")
    print("=" * 60)
    print()
    
    # Check input path exists
    if not os.path.exists(ART_INPUT_PATH):
        print(f"ERROR: Art input folder not found: {ART_INPUT_PATH}")
        print()
        print("Expected folder structure:")
        print("  AllArt/")
        print("    ui/")
        print("      characters/")
        print("        {character_folder}/")
        print("          composites/")
        print("            large_panel/")
        print("              happy/")
        print("                *.png")
        return
    
    # Create output directory
    os.makedirs(OUTPUT_PATH, exist_ok=True)
    print(f"Input:  {ART_INPUT_PATH}")
    print(f"Output: {OUTPUT_PATH}")
    print()
    
    # Track stats
    found = 0
    copied = 0
    skipped = 0
    missing = 0
    errors = []
    
    # Get all character folders
    character_folders = []
    for item in os.listdir(ART_INPUT_PATH):
        item_path = os.path.join(ART_INPUT_PATH, item)
        if os.path.isdir(item_path):
            character_folders.append(item)
    
    character_folders.sort()
    print(f"Found {len(character_folders)} character folders")
    print()
    print("Processing...")
    
    for folder_name in character_folders:
        found += 1
        
        # Build path to the happy portrait folder
        portrait_folder = os.path.join(ART_INPUT_PATH, folder_name, PORTRAIT_SUBPATH)
        
        if not os.path.exists(portrait_folder):
            missing += 1
            continue
        
        # Find PNG file(s) in the happy folder
        png_files = [f for f in os.listdir(portrait_folder) if f.lower().endswith('.png')]
        
        if not png_files:
            missing += 1
            continue
        
        # Use the first PNG found (there's usually only one)
        source_png = os.path.join(portrait_folder, png_files[0])
        
        # Output filename: {folder_name}.png
        output_filename = f"{folder_name}.png"
        output_path = os.path.join(OUTPUT_PATH, output_filename)
        
        # Check if already exists
        if os.path.exists(output_path):
            skipped += 1
            continue
        
        # Copy and rename
        try:
            shutil.copy2(source_png, output_path)
            copied += 1
        except Exception as e:
            errors.append(f"{folder_name}: {e}")
    
    # Summary
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Total folders scanned: {found}")
    print(f"  Portraits copied:      {copied}")
    print(f"  Already existed:       {skipped}")
    print(f"  Missing portrait:      {missing}")
    print(f"  Errors:                {len(errors)}")
    print()
    print(f"Output folder: {OUTPUT_PATH}")
    
    if errors:
        print()
        print("Errors:")
        for err in errors[:10]:  # Show first 10 errors
            print(f"  - {err}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more")
    
    print()
    print("Done!")


if __name__ == "__main__":
    main()
