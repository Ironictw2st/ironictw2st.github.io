#!/usr/bin/env python3
"""
190 Expanded Wiki - tool docs + release metadata
================================================

Builds the two data files behind the /tools/ pages:

    ../total_war/data/tools.js     release metadata for both tools (GitHub Releases API)
    ../total_war/data/se_docs.js   the se.* Lua API reference, converted from Markdown

    python fetch_tool_docs.py [--dry-run] [--offline] [--docs-dir DIR]

Like fetch_changelog.py this is NOT part of sync_from_mod.py: it depends on a sibling repo on
disk and on a live website, not on the mod tree. Run it when the script extender docs change or
a new release is tagged.

Markdown conversion is hand-rolled against the subset SCRIPTING.md actually uses, verified by
profiling the real file: ATX headings, fenced code blocks, pipe tables, `---` rules, flat
bullet / ordered lists, and inline code, links, bold and italic. There are no blockquotes, no
images, no raw HTML and no nested lists in the source. Two deliberate restrictions:

  1. Emphasis is *asterisk only*. The docs contain ~800 snake_case identifiers outside code
     spans (se.modify.build_number, script_extender.cfg); underscore emphasis would shred them.
  2. Output is an allow-listed HTML subset, built here rather than trusted, because se-api.html
     injects it with innerHTML (the same rule fetch_changelog.py follows).

Upstream staleness is REPORTED, never patched: docs/SCRIPTING.md is the source of truth and this
script does not edit it. That includes the doc's own "current DLL version at the time of writing"
sentence - it is wrapped prose in the middle of a paragraph, so editing it out would mangle the
sentence. Instead it is compared against the live release and any mismatch is reported, while the
page header shows the real latest release either way.
"""

import os
import re
import io
import sys
import json
import html
import urllib.request
import urllib.error

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(SCRIPT_DIR, ".."))
DATA = os.path.join(ROOT, "total_war", "data")

# Sibling repo on disk, the way sync_from_mod.py points at the mod tree. Reading locally means
# docs can be published before they are pushed.
SE_REPO = r"Z:\Claude\ScriptExtender"
SE_DOCS_DIR = os.path.join(SE_REPO, "docs")

# Rendered into se-api.html, in order. AI_RECRUITMENT.md and AI_RECRUITMENT_RUN_T1_T50.md are a
# design writeup and a dated experiment log rather than reference material, so they are linked
# out to GitHub instead; adding one here is all it takes to promote it.
DOCS = [
    {"file": "SCRIPTING.md", "id": "scripting", "title": "Campaign Lua API"},
]

REPOS = {
    "mod_manager": {
        "repo": "Ironictw2st/TKModManager",
        "name": "TK Mod Manager",
        "asset_hint": ".zip",
    },
    "script_extender": {
        "repo": "Ironictw2st/TK-ScriptExtender",
        "name": "TK Script Extender",
        "asset_hint": "script_extender.dll",
    },
}

API = "https://api.github.com/repos/%s/releases/latest"
UA = {"User-Agent": "190-expanded-wiki-docs/1.0", "Accept": "application/vnd.github+json"}

# The doc states which DLL it was written against. Read only, to compare against the live
# release - the sentence is wrapped prose, so it is never edited or removed.
DOC_VERSION = re.compile(
    r"current\s+DLL\s+version\s+at\s+the\s+time\s+of\s+writing:\s*\**v?([0-9][0-9.]*)", re.I)


# --------------------------------------------------------------------------- inline markdown

CODE_TOKEN = "\x00%d\x00"


def inline(text):
    """Convert inline markdown to the allowed HTML subset. Everything is escaped first."""
    # 1. lift code spans out so no other rule can touch their contents
    spans = []

    def stash(m):
        spans.append(m.group(1))
        return CODE_TOKEN % (len(spans) - 1)

    text = re.sub(r"`([^`]+)`", stash, text)

    # 2. escape the remaining prose
    text = html.escape(text, quote=False)

    # 3. links: [label](url) - only http(s), anchors and relative .md targets survive
    def link(m):
        label, url = m.group(1), m.group(2).strip()
        if url.startswith(("http://", "https://")):
            return '<a href="%s" target="_blank" rel="noopener">%s</a>' % (
                html.escape(url, quote=True), label)
        if url.startswith("#"):
            return '<a href="%s">%s</a>' % (html.escape(url, quote=True), label)
        return label  # in-repo path such as docs/SCRIPTING.md: keep the words, drop the link

    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, text)

    # 4. emphasis - asterisks only, never underscores (see module docstring)
    text = re.sub(r"\*\*(?=\S)(.+?)(?<=\S)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*(?=\S)([^*]+?)(?<=\S)\*(?!\*)", r"<em>\1</em>", text)

    # 5. put the code spans back, escaped
    def unstash(m):
        return "<code>%s</code>" % html.escape(spans[int(m.group(1))], quote=False)

    return re.sub(r"\x00(\d+)\x00", unstash, text)


def plain(text):
    """Heading text with markup stripped, for the TOC and for slugs."""
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    return re.sub(r"\*+", "", text).strip()


def slug(text, seen):
    s = re.sub(r"[^a-z0-9]+", "-", plain(text).lower()).strip("-") or "section"
    if s in seen:
        seen[s] += 1
        s = "%s-%d" % (s, seen[s])
    else:
        seen[s] = 1
    return s


# --------------------------------------------------------------------------- block markdown

FENCE = re.compile(r"^```\s*([a-zA-Z0-9_+-]*)\s*$")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*$")
HR = re.compile(r"^(?:-{3,}|\*{3,}|_{3,})$")
BULLET = re.compile(r"^\s*[-*+]\s+(.*)$")
ORDERED = re.compile(r"^\s*(\d+)\.\s+(.*)$")
TABLE_SEP = re.compile(r"^\|[\s:|-]+\|$")


def render_blocks(lines):
    """Block-level markdown -> HTML, for the body of one section."""
    out = []
    i, n = 0, len(lines)

    while i < n:
        line = lines[i]

        if not line.strip():
            i += 1
            continue

        m = FENCE.match(line)
        if m:
            lang = m.group(1).lower()
            i += 1
            code = []
            while i < n and not FENCE.match(lines[i]):
                code.append(lines[i])
                i += 1
            i += 1  # closing fence (or EOF)
            cls = ' class="lang-%s"' % lang if lang else ""
            out.append("<pre><code%s>%s</code></pre>"
                       % (cls, html.escape("\n".join(code), quote=False)))
            continue

        if HR.match(line.strip()):
            out.append("<hr>")
            i += 1
            continue

        # table: a | row followed by a |---|---| separator
        if line.lstrip().startswith("|") and i + 1 < n and TABLE_SEP.match(lines[i + 1].strip()):
            header = split_row(line)
            aligns = [cell_align(c) for c in split_row(lines[i + 1])]
            i += 2
            body = []
            while i < n and lines[i].lstrip().startswith("|"):
                body.append(split_row(lines[i]))
                i += 1
            out.append(table_html(header, aligns, body))
            continue

        if BULLET.match(line) or ORDERED.match(line):
            tag = "ul" if BULLET.match(line) else "ol"
            items, i = collect_list(lines, i, tag)
            out.append("<%s>%s</%s>"
                       % (tag, "".join("<li>%s</li>" % inline(t) for t in items), tag))
            continue

        # paragraph: run to the next blank line or block starter
        para = []
        while i < n and lines[i].strip() and not starts_block(lines[i]):
            para.append(lines[i].strip())
            i += 1
        if para:
            out.append("<p>%s</p>" % inline(" ".join(para)))

    return "".join(out)


def starts_block(line):
    s = line.strip()
    return bool(FENCE.match(line) or HEADING.match(line) or HR.match(s)
                or BULLET.match(line) or ORDERED.match(line) or s.startswith("|"))


def collect_list(lines, i, tag):
    """Flat list items; a wrapped continuation line folds into the current item."""
    pat = BULLET if tag == "ul" else ORDERED
    items, n = [], len(lines)
    while i < n:
        m = pat.match(lines[i])
        if m:
            items.append((m.group(1) if tag == "ul" else m.group(2)).strip())
            i += 1
            continue
        s = lines[i].strip()
        if s and items and lines[i].startswith((" ", "\t")) and not starts_block(lines[i]):
            items[-1] += " " + s          # continuation of the previous item
            i += 1
            continue
        break
    return items, i


def split_row(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [c.strip() for c in line.split("|")]


def cell_align(sep):
    sep = sep.strip()
    if sep.startswith(":") and sep.endswith(":"):
        return "center"
    if sep.endswith(":"):
        return "right"
    return ""


def table_html(header, aligns, body):
    def cells(row, tag):
        out = []
        for j, c in enumerate(row):
            a = aligns[j] if j < len(aligns) else ""
            style = ' style="text-align:%s"' % a if a else ""
            out.append("<%s%s>%s</%s>" % (tag, style, inline(c), tag))
        return "".join(out)

    rows = "".join("<tr>%s</tr>" % cells(r, "td") for r in body)
    return ("<div class=\"doc-table\"><table><thead><tr>%s</tr></thead><tbody>%s</tbody>"
            "</table></div>" % (cells(header, "th"), rows))


def convert(md):
    """Split a document into sections at every heading; render each section's body."""
    lines = [l.rstrip("\n") for l in md.splitlines()]

    sections, seen = [], {}
    current = {"level": 1, "id": "top", "title": "", "body": []}

    for line in lines:
        m = HEADING.match(line)
        if m:
            sections.append(current)
            current = {"level": len(m.group(1)), "id": slug(m.group(2), seen),
                       "title": m.group(2), "body": []}
        else:
            current["body"].append(line)
    sections.append(current)

    out = []
    for s in sections:
        body = render_blocks(s["body"])
        if not s["title"] and not body:
            continue                      # empty preamble before the first heading
        out.append({
            "level": s["level"],
            "id": s["id"],
            "title": inline(s["title"]),
            "text": plain(s["title"]),
            "html": body,
        })
    return out


# --------------------------------------------------------------------------- releases

def latest_release(repo):
    req = urllib.request.Request(API % repo, headers=UA)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def release_info(key, cfg, offline, previous):
    if offline:
        return previous.get(key)
    try:
        rel = latest_release(cfg["repo"])
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as e:
        # Never write an empty file: keep whatever the last good run produced.
        print("  ! %s: release lookup failed (%s) - keeping previous values" % (cfg["repo"], e))
        return previous.get(key)

    assets = rel.get("assets") or []
    pick = next((a for a in assets if cfg["asset_hint"] in a.get("name", "")), None)
    return {
        "name": cfg["name"],
        "repo": cfg["repo"],
        "url": "https://github.com/%s" % cfg["repo"],
        # Permanent URL: keeps working even when this file is stale.
        "latest_url": "https://github.com/%s/releases/latest" % cfg["repo"],
        "version": rel.get("tag_name", ""),
        "published": (rel.get("published_at") or "")[:10],
        "prerelease": bool(rel.get("prerelease")),
        "asset": (pick or {}).get("name", ""),
        "asset_size": (pick or {}).get("size", 0),
        "asset_url": (pick or {}).get("browser_download_url", ""),
    }


def read_previous(path, const):
    """Last good values, so a failed API call degrades instead of blanking the page."""
    try:
        s = open(path, encoding="utf-8").read()
        m = re.search(r"const %s\s*=\s*(\{.*?)\s*;\s*\n" % re.escape(const), s, re.S)
        return json.loads(m.group(1)) if m else {}
    except (OSError, ValueError):
        return {}


# --------------------------------------------------------------------------- staleness report

SE_CALL = re.compile(r"\bse\.(?:[a-z_]+\.)*[a-z_]+(?=\s*\()")


def staleness_report(sections, live_version, md):
    """Report what the docs no longer match. Never edits them - upstream owns the text."""
    notes = []

    index = next((s for s in sections if s["text"].lower().startswith("6.")), None)
    if index:
        listed = set(SE_CALL.findall(index["html"]))
        documented = set()
        for s in sections:
            if s is index:
                continue
            documented |= set(SE_CALL.findall(s["title"] + " " + s["html"]))
        missing = sorted(documented - listed)
        if missing:
            notes.append("section 6 (index of public functions) does not list %d documented "
                         "call(s): %s" % (len(missing), ", ".join(missing[:14])
                                          + (" ..." if len(missing) > 14 else "")))
    else:
        notes.append("no 'Index of public functions' section found")

    mp = [s for s in sections if "not verified on two machines" in s["html"]]
    if mp:
        notes.append("multiplayer is documented but flagged unverified in: "
                     + ", ".join(s["text"] or "(preamble)" for s in mp))

    # The doc says which DLL it was written against; flag it when the release has moved on.
    # Read from the Markdown, not the converted HTML, where the ** has become <strong>.
    m = DOC_VERSION.search(md)
    stated = m.group(1) if m else None
    if stated and live_version:
        if stated.lstrip("v") != live_version.lstrip("v"):
            notes.append("the doc says it was written against DLL %s, but the latest release is "
                         "%s - update the line in SCRIPTING.md" % (stated, live_version))
    elif live_version and not stated:
        notes.append("the doc does not state which DLL version it describes (latest is %s)"
                     % live_version)
    return notes


# --------------------------------------------------------------------------- output

def write_js(path, const, payload, banner, dry_run):
    body = json.dumps(payload, ensure_ascii=False, indent=2)
    text = "%s\nconst %s = %s;\n" % (banner, const, body)
    if dry_run:
        print("  (dry run) would write %s  [%.1f KB]"
              % (os.path.relpath(path, ROOT), len(text.encode("utf-8")) / 1024))
        return
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print("  wrote %s  [%.1f KB]" % (os.path.relpath(path, ROOT), len(text.encode("utf-8")) / 1024))


BANNER = """// data/%s
// GENERATED by generate_data/fetch_tool_docs.py - do not edit by hand.
// Source: %s"""


def main():
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    offline = "--offline" in args
    docs_dir = SE_DOCS_DIR
    if "--docs-dir" in args:
        docs_dir = args[args.index("--docs-dir") + 1]

    print("tool docs")
    print("  docs dir: %s" % docs_dir)

    # ---- releases
    prev_tools = read_previous(os.path.join(DATA, "tools.js"), "TOOLS_DATA")
    tools = {}
    for key, cfg in REPOS.items():
        info = release_info(key, cfg, offline, prev_tools)
        if info:
            tools[key] = info
            print("  %-16s %s (%s)  %s" % (key, info.get("version", "?"),
                                           info.get("published", "?"), info.get("asset", "")))
        else:
            print("  %-16s no data (and no previous values to keep)" % key)

    # ---- docs
    docs, problems = [], []
    for d in DOCS:
        path = os.path.join(docs_dir, d["file"])
        if not os.path.exists(path):
            problems.append("missing source doc: %s" % path)
            print("  ! missing %s" % path)
            continue
        md = open(path, encoding="utf-8").read()
        sections = convert(md)
        docs.append({"id": d["id"], "title": d["title"], "file": d["file"],
                     "source": "https://github.com/%s/blob/master/docs/%s"
                               % (REPOS["script_extender"]["repo"], d["file"]),
                     "sections": sections})
        print("  %-22s %d lines -> %d sections" % (d["file"], md.count("\n") + 1, len(sections)))

        notes = staleness_report(sections,
                                 tools.get("script_extender", {}).get("version", ""), md)
        for note in notes:
            print("    - %s" % note)
        problems.extend(notes)

    if not docs:
        print("\nno documents converted; nothing written")
        return 1

    write_js(os.path.join(DATA, "tools.js"), "TOOLS_DATA", tools,
             BANNER % ("tools.js", "GitHub Releases API"), dry_run)
    write_js(os.path.join(DATA, "se_docs.js"), "SE_DOCS", {"docs": docs},
             BANNER % ("se_docs.js", os.path.join(docs_dir, "*.md")), dry_run)

    print("\n%d upstream note(s) - these are reported, not patched" % len(problems))
    return 0


if __name__ == "__main__":
    sys.exit(main())
