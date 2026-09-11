#!/usr/bin/env python3
"""
190 Expanded Wiki - site audit
==============================

Run after the parsers. Checks, relative to the repo root:
  - every image path referenced from the generated data files exists
  - every local href / src in the HTML pages resolves to a file
  - characters without a portrait (and whether a name-based fallback file exists)
  - family tree entries whose template keys are not in CHARACTER_DATA
  - duplicate template keys in characters.js / character_details.js
  - orphan files under total_war/data (not referenced anywhere)
  - counts vs the previous run (generate_data/last_audit.json)

    python audit_site.py            -> prints report, writes generate_data/audit_report.md
"""

import os
import re
import json
from collections import Counter, defaultdict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(SCRIPT_DIR, ".."))
TW = os.path.join(ROOT, "total_war")
DATA = os.path.join(TW, "data")
REPORT = os.path.join(SCRIPT_DIR, "audit_report.md")
LAST = os.path.join(SCRIPT_DIR, "last_audit.json")

PAGES = ["index.html", "total_war/index.html", "total_war/factions.html", "total_war/faction.html",
         "total_war/map.html",
         "total_war/characters.html", "total_war/character.html", "total_war/guides.html",
         "total_war/roadmap.html", "total_war/changelog.html"]


def read(path):
    return open(path, encoding="utf-8").read()


def js_const(path, name, opener):
    s = read(path)
    m = re.search(r"const %s\s*=\s*(%s.*?)\s*;\s*\n" % (re.escape(name), re.escape(opener)), s, re.S)
    return json.loads(m.group(1)) if m else None


def exists_rel(base_dir, rel):
    rel = rel.split("#")[0].split("?")[0]
    if not rel or rel.startswith(("http:", "https:", "mailto:", "data:", "//")):
        return True
    p = os.path.normpath(os.path.join(base_dir, rel.replace("%20", " ")))
    return os.path.exists(p)


def main():
    out = []
    problems = 0

    def section(title):
        out.append(f"\n## {title}\n")

    def item(msg, bad=True):
        nonlocal problems
        if bad:
            problems += 1
        out.append(f"- {msg}")

    chars = js_const(os.path.join(DATA, "characters.js"), "CHARACTER_DATA", "[") or []
    details = js_const(os.path.join(DATA, "character_details.js"), "CHARACTER_DETAILS", "{") or {}
    factions = js_const(os.path.join(DATA, "factions.js"), "FACTION_DATA", "[") or []
    traits = js_const(os.path.join(DATA, "traits.js"), "TRAIT_DATA", "[") or []
    bios = js_const(os.path.join(DATA, "character_bios.js"), "CHARACTER_BIOS", "{") or {}
    family = js_const(os.path.join(DATA, "family_tree.js"), "FAMILY_RELATIONSHIPS", "[") or []
    skill_sets = 0
    m = re.search(r"// Total skill sets: (\d+)", read(os.path.join(DATA, "skill_trees.js")))
    if m:
        skill_sets = int(m.group(1))

    # ---------------------------------------------------------------- counts
    section("Counts")
    counts = {
        "characters": len(chars), "details": len(details), "bios": len(bios), "traits": len(traits),
        "skill_sets": skill_sets, "factions_190": sum(1 for f in factions if f.get("campaign") == "190"),
        "factions_gathering": sum(1 for f in factions if f.get("campaign") == "gathering"),
        "family_relationships": len(family),
    }
    prev = json.load(open(LAST, encoding="utf-8")) if os.path.exists(LAST) else {}
    for k, v in counts.items():
        delta = f" (was {prev[k]})" if k in prev and prev[k] != v else ""
        item(f"{k}: {v}{delta}", bad=False)
    json.dump(counts, open(LAST, "w", encoding="utf-8"), indent=2)

    # ------------------------------------------------------- effect index
    section("Effect index (Characters page filter)")
    effect_types = js_const(os.path.join(DATA, "characters.js"), "EFFECT_TYPES", "[") or []
    if not effect_types:
        item("EFFECT_TYPES is missing from characters.js; the effect filter will be empty")
    else:
        ids = {e["id"] for e in effect_types}
        bad_ids = sorted({i for c in chars for i in (c.get("effects") or []) if i not in ids})
        for i in bad_ids[:10]:
            item(f"character effect id {i} has no EFFECT_TYPES entry")
        dup_labels = [lab for lab, n in Counter(e["label"].lower() for e in effect_types).items() if n > 1]
        for lab in dup_labels[:10]:
            item(f"two effect groups share the label {lab!r}; the filter can only reach one")
        # the stated count must match what the page will actually show
        actual = Counter(i for c in chars for i in (c.get("effects") or []))
        wrong = [e for e in effect_types if e.get("count") != actual.get(e["id"], 0)]
        for e in wrong[:10]:
            item(f"effect {e['label']!r} claims {e.get('count')} characters, index has {actual.get(e['id'], 0)}")
        attr_totals = sum(1 for c in chars if c.get("attributes"))
        item(f"{len(effect_types)} effect groups, {sum(len(c.get('effects') or []) for c in chars)} links, "
             f"{attr_totals} characters with attribute totals", bad=False)
        if not (bad_ids or dup_labels or wrong):
            item("index is consistent", bad=False)

    # ------------------------------------------------------------ duplicates
    section("Duplicate template keys")
    dup = [k for k, n in Counter(c["key"] for c in chars).items() if n > 1]
    if dup:
        for k in dup:
            item(f"characters.js duplicate: {k}")
    else:
        item("none", bad=False)

    # -------------------------------------------------------------- portraits
    section("Portraits")
    no_portrait = [c for c in chars if not details.get(c["key"], {}).get("portrait", {}).get("url")]
    db_dir = os.path.join(DATA, "images", "db")
    for c in no_portrait:
        guess = os.path.join(db_dir, c["key"] + ".png")
        item(f"no portrait: {c['display_name']} ({c['key']})" + (" - file with template name exists" if os.path.exists(guess) else ""))
    if not no_portrait:
        item("all characters have a portrait", bad=False)

    # -------------------------------------------------------- image references
    section("Image references in data files")
    refs = defaultdict(set)
    for c_key, d in details.items():
        url = d.get("portrait", {}).get("url")
        if url:
            refs[url].add("character_details.portrait")
        for cat, eq in (d.get("equipment") or {}).items():
            if eq.get("icon_path"):
                refs["ancillary:" + eq["icon_path"]].add("equipment")
    for f in factions:
        for k in ("flag", "flag_small"):
            if f.get(k):
                refs[f[k]].add("factions.flag")
        for u in f.get("unique_features") or []:
            if u.get("icon"):
                refs[u["icon"]].add("factions.feature")
        for r in f.get("resources") or []:
            if r.get("icon"):
                refs[r["icon"]].add("factions.resource")
            for l in r.get("levels") or []:
                for b in l.get("bundles") or []:
                    if b.get("icon"):
                        refs[b["icon"]].add("factions.level")
        for b in (f.get("specialisation"), f.get("leader_bundle"), f.get("party_bundle")):
            if b and b.get("icon"):
                refs[b["icon"]].add("factions.bundle")
    missing_imgs = []
    for url, srcs in refs.items():
        if url.startswith("ancillary:"):
            continue  # resolved at runtime with several candidate folders; checked below
        if not exists_rel(TW, url):
            missing_imgs.append((url, sorted(srcs)))
    for url, srcs in sorted(missing_imgs):
        item(f"missing image {url} ({', '.join(srcs)})")
    item(f"{len(refs)} referenced images checked, {len(missing_imgs)} missing", bad=False)

    # ancillary icons: character.html tries data/UI/ancillaries/<leaf>.png and data/UI/Campaign UI/ancillaries/<leaf>.png
    anc_dirs = [os.path.join(DATA, "UI", "ancillaries"), os.path.join(DATA, "UI", "Campaign UI", "ancillaries")]
    anc_missing = set()
    for c_key, d in details.items():
        for cat, eq in (d.get("equipment") or {}).items():
            ip = eq.get("icon_path") or ""
            leaf = os.path.basename(ip.replace("\\", "/"))
            if not leaf:
                continue
            if not any(os.path.exists(os.path.join(a, leaf)) or os.path.exists(os.path.join(a, os.path.splitext(leaf)[0] + ".png")) for a in anc_dirs):
                anc_missing.add(ip)
    for ip in sorted(anc_missing)[:40]:
        item(f"ancillary icon not found under data/UI/ancillaries: {ip}")
    if len(anc_missing) > 40:
        item(f"... and {len(anc_missing) - 40} more ancillary icons missing")
    trait_dir = os.path.join(DATA, "UI", "Campaign UI", "traits")
    t_missing = [t["icon_path"] for t in traits if t.get("icon_path")
                 and not os.path.exists(os.path.join(trait_dir, os.path.basename(t["icon_path"].replace("\\", "/"))))]
    for ip in t_missing[:20]:
        item(f"trait icon not found under data/UI/Campaign UI/traits: {ip}")

    # --------------------------------------------------------------- html links
    section("HTML references")
    for page in PAGES:
        p = os.path.join(ROOT, page)
        if not os.path.exists(p):
            item(f"page missing: {page}")
            continue
        base = os.path.dirname(p)
        html = read(p)
        for attr, val in re.findall(r'(?:src|href)\s*=\s*"([^"]+)"', html) and [("x", v) for v in re.findall(r'(?:src|href)\s*=\s*"([^"]+)"', html)]:
            if val.startswith("javascript:") or val == "#" or "${" in val:
                continue  # template literals inside inline scripts are resolved at runtime
            if not exists_rel(base, val):
                item(f"{page}: broken reference {val}")
    item("checked " + ", ".join(PAGES), bad=False)

    # ------------------------------------------------------------- family tree
    section("Family tree")
    keys = {c["key"] for c in chars}
    fam_missing = Counter()
    for r in family:
        for k in (r.get("character"), r.get("related_to")):
            if k and k not in keys:
                fam_missing[k] += 1
    ancestral = {k: n for k, n in fam_missing.items() if "_ancestral_" in k}
    real_missing = {k: n for k, n in fam_missing.items() if "_ancestral_" not in k}
    item(f"{len(ancestral)} ancestral-only templates referenced (no character page by design)", bad=False)
    for k, n in sorted(real_missing.items(), key=lambda kv: -kv[1])[:40]:
        item(f"family_tree.js references unknown template {k} ({n}x)")
    if len(real_missing) > 40:
        item(f"... and {len(real_missing) - 40} more unknown templates")
    if not real_missing:
        item("all non-ancestral family tree keys exist", bad=False)

    # ---------------------------------------------------------------- orphans
    section("Orphan data files (not referenced by any page or data file)")
    referenced_text = "\n".join(read(os.path.join(ROOT, p)) for p in PAGES if os.path.exists(os.path.join(ROOT, p)))
    for name in sorted(os.listdir(DATA)):
        p = os.path.join(DATA, name)
        if os.path.isdir(p) or name in ("titles.js",):  # titles.js: generated lookup kept for tooling
            continue
        if ("data/" + name) not in referenced_text and name not in referenced_text:
            item(f"total_war/data/{name} is not referenced")
    item("checked", bad=False)

    # ---------------------------------------------------------------- bios
    section("Biographies")
    missing_bios = [c for c in chars if c["key"] not in bios]
    new_path = os.path.join(DATA, "character_bios_new.js")
    bios_new = js_const(new_path, "CHARACTER_BIOS_NEW", "{") if os.path.exists(new_path) else {}
    still_missing = [c for c in missing_bios if c["key"] not in bios_new]
    item(f"{len(missing_bios)} without hand-written bio, {len(bios_new)} drafted, {len(still_missing)} still missing", bad=bool(still_missing))

    text = "# Site audit\n" + "\n".join(out) + f"\n\n**{problems} findings**\n"
    open(REPORT, "w", encoding="utf-8", newline="\n").write(text)
    print(text)


if __name__ == "__main__":
    main()
