#!/usr/bin/env python3
"""
190 Expanded Wiki - biography coverage report
=============================================

Compares CHARACTER_DATA (total_war/data/characters.js) with the hand-written
CHARACTER_BIOS (character_bios.js) and the review file CHARACTER_BIOS_NEW
(character_bios_new.js, optional).

Writes generate_data/bios_missing.md listing every character with no biography,
together with the in-game frontend blurb (frontend_faction_leader_unique_characters
loc) when the mod has one, so a writer has something to start from.
Also lists bios whose template key no longer exists (orphans).

    python bios_report.py
"""

import os
import re
import json

from tw3k_common import load_site_loc, strip_tw_markup

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SITE_DATA = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "total_war", "data"))
OUT_PATH = os.path.join(SCRIPT_DIR, "bios_missing.md")


def load_js_const(path, name, opener):
    s = open(path, encoding="utf-8").read()
    m = re.search(r"const %s\s*=\s*(%s.*?)\s*;\s*\n" % (re.escape(name), re.escape(opener)), s, re.S)
    if not m:
        raise SystemExit(f"{name} not found in {path}")
    return json.loads(m.group(1))


def main():
    chars = load_js_const(os.path.join(SITE_DATA, "characters.js"), "CHARACTER_DATA", "[")
    bios = load_js_const(os.path.join(SITE_DATA, "character_bios.js"), "CHARACTER_BIOS", "{")
    new_path = os.path.join(SITE_DATA, "character_bios_new.js")
    bios_new = load_js_const(new_path, "CHARACTER_BIOS_NEW", "{") if os.path.exists(new_path) else {}

    LOC = load_site_loc(os.path.join(SCRIPT_DIR, "text"))
    blurb_prefix = "frontend_faction_leader_unique_characters_localised_description_"

    keys = {c["key"] for c in chars}
    missing = [c for c in chars if c["key"] not in bios and c["key"] not in bios_new]
    orphans = sorted(k for k in list(bios) + list(bios_new) if k not in keys)

    lines = ["# Biography coverage", "",
             f"- characters: {len(chars)}",
             f"- with hand-written bio: {sum(1 for c in chars if c['key'] in bios)}",
             f"- with drafted bio (character_bios_new.js): {sum(1 for c in chars if c['key'] in bios_new and c['key'] not in bios)}",
             f"- missing: {len(missing)}",
             f"- orphan bios (key no longer exists): {len(orphans)}", ""]
    if orphans:
        lines += ["## Orphan bios", ""] + [f"- `{k}`" for k in orphans] + [""]
    lines += ["## Missing biographies", ""]
    for c in sorted(missing, key=lambda c: c["display_name"]):
        blurb = strip_tw_markup(LOC.get(blurb_prefix + c["key"], ""))
        blurb = re.sub(r"\s*General type:.*?(?=\s[A-Z]|$)", " ", blurb).strip()
        lines.append(f"### {c['display_name']}  `{c['key']}`")
        meta = [x for x in (c.get("title"), c.get("element"), f"born {c['birth_year']}" if c.get("birth_year") else "",
                            "unique" if c.get("is_unique") else "generic") if x]
        lines.append("- " + " · ".join(meta))
        if c.get("description"):
            lines.append(f"- career text: {c['description']}")
        if blurb:
            lines.append(f"- in-game blurb: {blurb}")
        lines.append("")

    with open(OUT_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))
    print(f"characters {len(chars)}, bios {len(bios)}, drafted {len(bios_new)}, missing {len(missing)}, orphans {len(orphans)}")
    print(f"Written: {OUT_PATH}")


if __name__ == "__main__":
    main()
