#!/usr/bin/env python3
"""
Cache-busting stamps for the generated data files.

GitHub Pages serves the pages with `Cache-Control: max-age=600` but the data files with
`max-age=14400`, and neither is configurable. So a visitor's HTML refreshes four hours
before the JS it loads does, and any release that changes the *shape* of a data file leaves
them running new HTML against a stale file. That is not theoretical: renaming
RECRUIT_SCOPES to RECRUIT_ZONES blanked the live map for exactly that reason - the inline
script threw on the first missing global and no polygons were ever added.

Stamping the src with a hash of the file's contents makes each release a new URL, so there
is nothing cached to go stale. The generators call this after writing their data.
"""

import os
import re
import hashlib

# Every generated file total_war/map.html loads. Any generator that writes one of these
# stamps the whole list, so a single run leaves the page internally consistent.
MAP_PAGE_ASSETS = ["map_regions.js", "map_recruitment.js", "factions.js"]


def stamp(html_path, data_dir, names):
    """Rewrite <script src="data/<name>"> to carry ?v=<content hash>. -> list of (name, hash)."""
    if not os.path.exists(html_path):
        return []
    html = open(html_path, encoding="utf-8", newline="").read()
    original, stamped = html, []
    for name in names:
        path = os.path.join(data_dir, name)
        if not os.path.exists(path):
            continue
        with open(path, "rb") as f:
            digest = hashlib.sha1(f.read()).hexdigest()[:10]
        pattern = re.compile(r'(src="data/%s)(?:\?v=[0-9a-f]+)?(")' % re.escape(name))
        html, n = pattern.subn(lambda m: f"{m.group(1)}?v={digest}{m.group(2)}", html)
        if n:
            stamped.append((name, digest))
    if html != original:
        with open(html_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(html)
    return stamped


def stamp_map_page(script_dir):
    """Stamp total_war/map.html for every data file it loads."""
    root = os.path.normpath(os.path.join(script_dir, ".."))
    return stamp(os.path.join(root, "total_war", "map.html"),
                 os.path.join(root, "total_war", "data"), MAP_PAGE_ASSETS)
