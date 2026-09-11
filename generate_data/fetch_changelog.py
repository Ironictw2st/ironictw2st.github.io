#!/usr/bin/env python3
"""
190 Expanded Wiki - Steam changelog scraper
===========================================

Builds ../total_war/data/changelog.js from the Steam Workshop change notes of the mod's
three packs. Run it by hand after a Steam update; it is NOT part of sync_from_mod.py,
because it depends on a live website rather than the mod tree.

    python fetch_changelog.py [--dry-run] [--cache-dir DIR]

Steam page shape (stable as of 2026-09):
  <div class="changelog headline">Update: Sep 2 @ 11:32am</div>
  <p id="1788373923">...notes...</p>
The headline omits the year for the current year, so it is NOT parsed. The <p> id is the
update's Unix timestamp and is used as the date instead.

Body markup is limited to: br, li, b, i, a, hr, div.bb_h1, div.bb_h2, ul.bb_ul.
It is re-built into a small allowed subset here rather than trusted, because changelog.html
injects the result with innerHTML.

Cleanup applied (each verified against the real data):
  1. The author cross-posts identical notes to several packs -> merge on a hash of the plain
     text into one entry listing every pack it appeared in.
  2. A pack rebuilt with no notes leaves an empty entry -> if another entry on the same day
     does have notes, fold the pack tag into it and drop the empty one.
  3. Same-day cross-posts that differ by a word or two are deliberately left separate.
"""

import os
import re
import sys
import json
import time
import html
import hashlib
import datetime
import urllib.request
import urllib.error
from collections import defaultdict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SITE_DATA = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "total_war", "data"))
OUTPUT_PATH = os.path.join(SITE_DATA, "changelog.js")
SUMMARY_PATH = os.path.join(SCRIPT_DIR, "last_run_changelog.json")

# Workshop id -> display name. Order decides the chip order on the page.
PACKS = [
    ("2875547086", "Factions & Characters"),
    ("3010906135", "Overhaul"),
    ("3240150507", "Extra Regions"),
]

BASE = "https://steamcommunity.com/sharedfiles/filedetails/changelog/{id}"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")

REQUEST_DELAY = 1.0      # be polite to Steam
MAX_PAGES = 40           # guard against a pagination loop
RELEASE_MIN_CHARS = 1000  # notes this long or longer are shown as a release card

DRY = "--dry-run" in sys.argv
CACHE_DIR = None
if "--cache-dir" in sys.argv:
    CACHE_DIR = sys.argv[sys.argv.index("--cache-dir") + 1]


# ---------------------------------------------------------------------------
# fetching
# ---------------------------------------------------------------------------

def fetch(url, cache_key):
    """GET url as text, optionally reading/writing a local cache copy."""
    cache_path = os.path.join(CACHE_DIR, cache_key + ".html") if CACHE_DIR else None
    if cache_path and os.path.exists(cache_path):
        return open(cache_path, encoding="utf-8").read()

    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en"})
    with urllib.request.urlopen(req, timeout=45) as resp:
        if resp.status != 200:
            raise SystemExit(f"ERROR: {url} returned HTTP {resp.status}")
        body = resp.read().decode("utf-8", errors="replace")

    if cache_path:
        os.makedirs(CACHE_DIR, exist_ok=True)
        open(cache_path, "w", encoding="utf-8", newline="\n").write(body)
    time.sleep(REQUEST_DELAY)
    return body


HEADLINE_RE = re.compile(r'class="changelog headline">(.*?)</div>', re.S)
BODY_RE = re.compile(r'<p id="(\d+)"[^>]*>(.*?)</p>', re.S)


def parse_page(page_html, pack_name):
    """Return [{pack, ts, raw}] for one changelog page."""
    heads = HEADLINE_RE.findall(page_html)
    bodies = BODY_RE.findall(page_html)
    if len(heads) != len(bodies):
        print(f"  WARNING: {pack_name}: {len(heads)} headlines vs {len(bodies)} bodies; "
              "using the bodies, which carry the timestamps")
    return [{"pack": pack_name, "ts": int(ts), "raw": raw} for ts, raw in bodies]


def scrape_pack(pack_id, pack_name):
    entries, page = [], 1
    while page <= MAX_PAGES:
        url = BASE.format(id=pack_id) + ("" if page == 1 else f"?p={page}")
        found = parse_page(fetch(url, f"{pack_id}_{page}"), pack_name)
        print(f"  {pack_name:22s} page {page}: {len(found)} entries")
        if not found:
            if page == 1:
                raise SystemExit(
                    f"ERROR: no entries on page 1 of {url}\n"
                    "Steam's changelog layout has probably changed; update HEADLINE_RE / BODY_RE.")
            break
        entries.extend(found)
        page += 1
    return entries


# ---------------------------------------------------------------------------
# body -> safe html
# ---------------------------------------------------------------------------

def to_text(raw):
    """Plain text of a body, used for hashing, classification and titles."""
    t = re.sub(r"<br\s*/?>", "\n", raw)
    t = re.sub(r"</(li|div|ul|p)>", "\n", t)
    t = re.sub(r"<[^>]+>", "", t)
    t = html.unescape(t)
    t = re.sub(r"[ \t]+\n", "\n", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


_TOKEN = "\x00%d\x00"


def to_safe_html(raw):
    """
    Rebuild the body from an allow-list instead of trusting Steam's markup:
    escape everything, then restore only b/i/br/ul/li/hr and http(s) links.
    bb_h1 -> h3, bb_h2 -> h4.
    """
    keep = []

    def stash(replacement):
        keep.append(replacement)
        return _TOKEN % (len(keep) - 1)

    s = raw
    s = re.sub(r'<div class="bb_h1">(.*?)</div>', lambda m: stash("<h3>") + m.group(1) + stash("</h3>"), s, flags=re.S)
    s = re.sub(r'<div class="bb_h2">(.*?)</div>', lambda m: stash("<h4>") + m.group(1) + stash("</h4>"), s, flags=re.S)
    s = re.sub(r'<ul[^>]*>', lambda m: stash("<ul>"), s)
    s = re.sub(r'</ul>', lambda m: stash("</ul>"), s)
    s = re.sub(r'<li[^>]*>', lambda m: stash("<li>"), s)
    s = re.sub(r'</li>', lambda m: stash("</li>"), s)
    s = re.sub(r'<(b|i)>', lambda m: stash(f"<{m.group(1)}>"), s)
    s = re.sub(r'</(b|i)>', lambda m: stash(f"</{m.group(1)}>"), s)
    s = re.sub(r'<br\s*/?>', lambda m: stash("<br>"), s)
    s = re.sub(r'<hr\s*/?>(?:</hr>)?', lambda m: stash("<hr>"), s)

    def link(m):
        href = html.unescape(m.group(1)).strip()
        if not re.match(r"^https?://", href, re.I):
            return ""
        return stash(f'<a href="{html.escape(href, quote=True)}" target="_blank" rel="noopener">')
    s = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>', link, s)
    s = re.sub(r'</a>', lambda m: stash("</a>"), s)

    # anything still tag-shaped is not on the allow-list
    s = re.sub(r"<[^>]*>", "", s)
    s = html.escape(html.unescape(s), quote=False)
    s = re.sub(r"\x00(\d+)\x00", lambda m: keep[int(m.group(1))], s)

    s = re.sub(r"(?:<br>\s*){3,}", "<br><br>", s)
    s = re.sub(r"^(?:<br>\s*)+|(?:<br>\s*)+$", "", s)
    return s.strip()


TITLE_MAX = 60
# A first line only becomes a heading when it reads like one. Without this, bodies that
# simply open with a sentence ("Faction", "Added skills to") would get nonsense headings.
TITLE_PATTERN = re.compile(
    r"^(hot\s*fix|hotfix|patch|fix(es)?|minor update|major update|new content|update|"
    r"190 expanded|release)\b", re.I)


def derive_title(raw, text):
    """The bb_h1 heading if Steam has one, else a first line that looks like a heading."""
    m = re.search(r'<div class="bb_h1">(.*?)</div>', raw, re.S)
    if m:
        return _tidy(re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", m.group(1)))))
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    if (len(lines) > 1 and len(lines[0]) <= TITLE_MAX
            and not lines[0].endswith(".") and TITLE_PATTERN.match(lines[0])):
        return _tidy(lines[0])
    return ""


def _tidy(title):
    """Headings are often written as "Patch:" or "Hotfix 1:" - drop the trailing colon."""
    return re.sub(r"\s*[:\-–]\s*$", "", title.strip()).strip()


def strip_leading_title(raw, safe_html, title):
    """Remove the heading from the body so the page does not print it twice."""
    if not title:
        return safe_html
    # bb_h1 became a whole <h3>...</h3> block; drop the block, not just its text
    if re.search(r'<div class="bb_h1">', raw, re.S):
        return re.sub(r"^\s*(?:<h3>)?.*?</h3>\s*", "", safe_html, count=1, flags=re.S).strip()
    escaped = html.escape(title, quote=False)
    idx = safe_html.find(escaped)
    if idx == -1 or re.sub(r"<[^>]+>", "", safe_html[:idx]).strip():
        return safe_html
    return re.sub(r"^(?:<br>|\s)+", "", safe_html[idx + len(escaped):]).strip()


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("190 Expanded Wiki - Steam changelog" + (" (DRY RUN)" if DRY else ""))
    print("=" * 60)

    print("[1/4] Scraping")
    raw_entries = []
    for pack_id, pack_name in PACKS:
        raw_entries.extend(scrape_pack(pack_id, pack_name))
    print(f"  {len(raw_entries)} raw entries")

    # a pack can repeat an entry across pages if one is posted mid-scrape
    seen, uniq = set(), []
    for e in sorted(raw_entries, key=lambda x: -x["ts"]):
        key = (e["pack"], e["ts"])
        if key not in seen:
            seen.add(key)
            uniq.append(e)
    for e in uniq:
        e["text"] = to_text(e["raw"])

    print("[2/4] Merging cross-posted notes")
    groups = defaultdict(list)
    for e in uniq:
        key = hashlib.md5(e["text"].encode("utf-8")).hexdigest() if e["text"] else f"empty:{e['ts']}:{e['pack']}"
        groups[key].append(e)
    merged = []
    for members in groups.values():
        members.sort(key=lambda x: x["ts"])
        merged.append({
            "ts": members[0]["ts"],
            "packs": [n for _i, n in PACKS if n in {m["pack"] for m in members}],
            "raw": members[0]["raw"],
            "text": members[0]["text"],
        })
    print(f"  {len(uniq)} -> {len(merged)} entries "
          f"({len(uniq) - len(merged)} cross-posted duplicates merged)")

    print("[3/4] Folding silent pushes into the same day's notes")
    by_day = defaultdict(list)
    for e in merged:
        by_day[datetime.datetime.utcfromtimestamp(e["ts"]).date()].append(e)
    final, absorbed = [], 0
    for _day, items in by_day.items():
        with_text = [x for x in items if x["text"]]
        empties = [x for x in items if not x["text"]]
        if with_text and empties:
            target = max(with_text, key=lambda x: len(x["text"]))
            for em in empties:
                for p in em["packs"]:
                    if p not in target["packs"]:
                        target["packs"].append(p)
                absorbed += 1
            for w in with_text:
                w["packs"] = [n for _i, n in PACKS if n in w["packs"]]
            final.extend(with_text)
        else:
            final.extend(items)
    final.sort(key=lambda x: -x["ts"])
    print(f"  {absorbed} silent entries folded in, "
          f"{sum(1 for e in final if not e['text'])} left standing")

    print("[4/4] Building output")
    out = []
    for e in final:
        dt = datetime.datetime.utcfromtimestamp(e["ts"])
        title = derive_title(e["raw"], e["text"])
        body = strip_leading_title(e["raw"], to_safe_html(e["raw"]), title) if e["text"] else ""
        chars = len(e["text"])
        kind = "silent" if not chars else ("release" if chars >= RELEASE_MIN_CHARS else "patch")
        out.append({
            "ts": e["ts"],
            "date": dt.strftime("%Y-%m-%d"),
            "display_date": dt.strftime("%d %b %Y").lstrip("0"),
            "year": dt.year,
            "packs": e["packs"],
            "kind": kind,
            "title": title,
            "html": body,
            "chars": chars,
        })

    by_year = defaultdict(int)
    by_pack = defaultdict(int)
    for e in out:
        by_year[e["year"]] += 1
        for p in e["packs"]:
            by_pack[p] += 1
    stats = {
        "total": len(out),
        "releases": sum(1 for e in out if e["kind"] == "release"),
        "patches": sum(1 for e in out if e["kind"] == "patch"),
        "silent": sum(1 for e in out if e["kind"] == "silent"),
        "first": out[-1]["date"] if out else "",
        "last": out[0]["date"] if out else "",
        "byYear": {str(k): v for k, v in sorted(by_year.items(), reverse=True)},
        "byPack": dict(by_pack),
        "packLinks": {name: BASE.format(id=pid) for pid, name in PACKS},
    }

    if not DRY:
        os.makedirs(SITE_DATA, exist_ok=True)
        with open(OUTPUT_PATH, "w", encoding="utf-8", newline="\n") as f:
            f.write("// Auto-generated by generate_data/fetch_changelog.py - do not edit by hand.\n")
            f.write("// Source: Steam Workshop change notes for the three 190 Expanded packs.\n")
            f.write(f"// {stats['total']} entries, {stats['first']} to {stats['last']}.\n\n")
            f.write("const CHANGELOG_DATA = " + json.dumps(out, indent=2, ensure_ascii=False) + ";\n\n")
            f.write("const CHANGELOG_STATS = " + json.dumps(stats, indent=2, ensure_ascii=False) + ";\n")
        with open(SUMMARY_PATH, "w", encoding="utf-8", newline="\n") as f:
            json.dump(stats, f, indent=2)
        print(f"  Written: {OUTPUT_PATH}")
        print(f"  Written: {SUMMARY_PATH}")

    print()
    print("SUMMARY", json.dumps({k: v for k, v in stats.items() if k not in ("byYear", "byPack", "packLinks")}))
    print("  by year:", dict(stats["byYear"]))
    print("  by pack:", stats["byPack"])


if __name__ == "__main__":
    main()
