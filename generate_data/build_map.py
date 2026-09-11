#!/usr/bin/env python3
"""
190 Expanded Wiki - campaign map builder
========================================

Builds ../total_war/data/map_regions.js and the base map image from the mod's own campaign
map assets. Run it by hand when the map or the start positions change; it is NOT part of
sync_from_mod.py, because it reads image assets rather than the db tables.

    python build_map.py [--no-image] [--tolerance 2.0]

How the region shapes are recovered
-----------------------------------
The mod ships two images of identical size (3840x3024) that line up pixel for pixel:

  three_kingdoms_china_map.png   the artwork players see
  3k_main_lookup.tga             which region each pixel belongs to

The lookup is an uncompressed COLOUR-MAPPED TGA: a 336-entry 32-bit BGRA palette whose first
index is 18, and one 16-bit palette index per pixel. Palette colour -> region key comes from
regions_tables ("unnamed colour group_1", a 24-bit hex). 318 of the 336 entries resolve to a
region; the rest are sea, passes and impassable terrain.

Region outlines are then traced off the index array: connected components via run-length
union-find, a crack-following walk around each component (vertices land on pixel corners,
which stays exact on thin concave shapes where a pixel-centre walk cuts corners), enclave
detection so a sprawling region does not claim the regions inside it, and Douglas-Peucker
simplification. scipy/cv2/shapely are not installed, so all of that is implemented here.

Ownership
---------
start_pos_regions_tables gives owning_faction as a NUMERIC id, which resolves through
start_pos_factions_tables.ID -> faction key. Colours come from faction_banners_tables
(primary_hex) where present, and are otherwise sampled from the faction's own flag image
already in the repo at total_war/data/images/flags/<faction_key>.png.
"""

import os
import re
import sys
import csv
import json
import glob
import struct
from collections import defaultdict, Counter

import numpy as np
from PIL import Image

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SITE_DATA = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "total_war", "data"))
OUTPUT_PATH = os.path.join(SITE_DATA, "map_regions.js")
IMAGE_DIR = os.path.join(SITE_DATA, "images", "map")
FLAG_DIR = os.path.join(SITE_DATA, "images", "flags")
SUMMARY_PATH = os.path.join(SCRIPT_DIR, "last_run_map.json")

MOD_ROOT = r"Z:\Claude\190Expanded\Beta"
MAP_DIR = os.path.join(MOD_ROOT, "1_Faction", "campaign_maps", "3k_dlc07_main_map")
LOOKUP_TGA = os.path.join(MAP_DIR, "3k_main_lookup.tga")
BASE_PNG = os.path.join(MAP_DIR, "three_kingdoms_china_map.png")
START_POS_DIR = os.path.join(MOD_ROOT, "1_Faction", "db")
VANILLA_DB = r"Z:\Claude\XMLViewer\games\3K\DB"

CAMPAIGN = "3k_main_campaign_map"
MIN_PART_PIXELS = 400        # drop specks; a real region part is far larger
WEBP_QUALITY = 86        # the full 3840px map is only ~1.3 MB at this quality
DEFAULT_TOLERANCE = 2.0      # Douglas-Peucker, in source pixels

NO_IMAGE = "--no-image" in sys.argv
TOLERANCE = DEFAULT_TOLERANCE
if "--tolerance" in sys.argv:
    TOLERANCE = float(sys.argv[sys.argv.index("--tolerance") + 1])


# ---------------------------------------------------------------------------
# table loading (same TSV conventions as tw3k_common, kept standalone)
# ---------------------------------------------------------------------------

def read_tsv(path):
    """Header row plus data rows, skipping the RPFM '#table;ver;path' line."""
    with open(path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE))
    if not rows:
        return [], []
    return rows[0], [r for r in rows[1:] if r and r[0] and not r[0].startswith("#")]


def read_loc(path):
    out = {}
    if not os.path.exists(path):
        return out
    with open(path, encoding="utf-8-sig", newline="") as f:
        for row in csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
            if len(row) < 2 or not row[0] or row[0].startswith("#") or row[0] == "key":
                continue
            text = row[1].strip()
            if text and text.upper() != "PLACEHOLDER":
                out[row[0].strip()] = text
    return out


def col(header, *names):
    for n in names:
        if n in header:
            return header.index(n)
    return -1


# ---------------------------------------------------------------------------
# lookup decoding
# ---------------------------------------------------------------------------

def load_lookup(path):
    """-> (index_array HxW uint16, {palette_index: 'RRGGBB'})"""
    with open(path, "rb") as f:
        hdr = f.read(18)
        idlen, cmaptype, imgtype = hdr[0], hdr[1], hdr[2]
        cmap_first, cmap_len, cmap_bpp = struct.unpack("<HHB", hdr[3:8])
        w, h = struct.unpack("<HH", hdr[12:16])
        bpp, desc = hdr[16], hdr[17]
        if cmaptype != 1 or imgtype != 1 or bpp != 16 or cmap_bpp != 32:
            raise SystemExit(
                f"ERROR: {path} is not the expected colour-mapped 16-bit TGA "
                f"(cmaptype={cmaptype} imgtype={imgtype} bpp={bpp} cmap_bpp={cmap_bpp})")
        f.seek(18 + idlen)
        cmap = f.read(cmap_len * 4)
        data = f.read(w * h * 2)

    palette = {}
    for i in range(cmap_len):
        b, g, r, _a = cmap[i * 4:i * 4 + 4]
        palette[cmap_first + i] = f"{r:02X}{g:02X}{b:02X}"

    idx = np.frombuffer(data, dtype="<u2").reshape(h, w)
    # TGA bit 5 of the descriptor set means the first row is the TOP row.
    if not (desc & 0x20):
        idx = idx[::-1]
    return np.ascontiguousarray(idx), palette


# ---------------------------------------------------------------------------
# connected components (run-length + union-find; no scipy)
# ---------------------------------------------------------------------------

def components(mask):
    """Label 4-connected components of a boolean mask. -> (labels int32, count)"""
    h, w = mask.shape
    labels = np.zeros((h, w), dtype=np.int32)
    parent = [0]

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)

    prev_runs = []
    for y in range(h):
        row = mask[y]
        if not row.any():
            prev_runs = []
            continue
        # run starts/ends on this row
        d = np.diff(np.concatenate(([0], row.view(np.int8), [0])))
        starts = np.flatnonzero(d == 1)
        ends = np.flatnonzero(d == -1)
        runs = []
        for s, e in zip(starts, ends):
            lab = 0
            for ps, pe, pl in prev_runs:      # overlap with the row above
                if ps < e and s < pe:
                    lab = pl if lab == 0 else lab
                    union(lab, pl)
            if lab == 0:
                parent.append(len(parent))
                lab = len(parent) - 1
            labels[y, s:e] = lab
            runs.append((s, e, lab))
        prev_runs = runs

    if len(parent) == 1:
        return labels, 0
    roots = np.array([find(i) for i in range(len(parent))], dtype=np.int32)
    uniq = {r: i + 1 for i, r in enumerate(sorted(set(roots[1:])))}
    remap = np.zeros(len(parent), dtype=np.int32)
    for i in range(1, len(parent)):
        remap[i] = uniq[roots[i]]
    return remap[labels], len(uniq)


# ---------------------------------------------------------------------------
# boundary tracing and simplification
# ---------------------------------------------------------------------------

_STEP = [(1, 0), (0, 1), (-1, 0), (0, -1)]   # E, S, W, N


def trace_boundary(mask, start_px):
    """
    Follow the crack between filled and empty pixels, so vertices land on pixel CORNERS
    and the ring encloses exactly the filled pixels. A pixel-centre walk (Moore) cuts
    corners on thin concave shapes; this does not.
    start_px must be the topmost-then-leftmost pixel of the component.
    """
    h, w = mask.shape

    def filled(x, y):
        return 0 <= x < w and 0 <= y < h and mask[y, x]

    sx, sy = start_px
    x, y, d = sx, sy, 0          # begin at its top-left corner heading east
    pts = [(x, y)]
    for _ in range(8 * int(mask.sum()) + 64):
        if d == 0:
            d = 3 if filled(x, y - 1) else (0 if filled(x, y) else 1)
        elif d == 1:
            d = 0 if filled(x, y) else (1 if filled(x - 1, y) else 2)
        elif d == 2:
            d = 1 if filled(x - 1, y) else (2 if filled(x - 1, y - 1) else 3)
        else:
            d = 2 if filled(x - 1, y - 1) else (3 if filled(x, y - 1) else 0)
        dx, dy = _STEP[d]
        x, y = x + dx, y + dy
        if (x, y) == (sx, sy):
            break
        pts.append((x, y))
    return pts


def find_holes(part, min_pixels):
    """
    Enclaves inside a component: other regions completely surrounded by this one.
    Without them a sprawling region's ring encloses far more area than it owns.
    -> list of rings, in the component's own coordinates.
    """
    padded = np.pad(~part, 1, constant_values=True)
    labels, count = components(padded)
    if count <= 1:
        return []
    outside = labels[0, 0]
    rings = []
    for lab in range(1, count + 1):
        if lab == outside:
            continue
        blob = labels == lab
        if int(blob.sum()) < min_pixels:
            continue
        bys, bxs = np.nonzero(blob)
        ring = trace_boundary(blob, (int(bxs[0]), int(bys[0])))
        if len(ring) >= 4:
            rings.append([(x - 1, y - 1) for x, y in ring])   # undo the pad
    return rings


def simplify(points, tol):
    """Douglas-Peucker on a closed ring."""
    if len(points) < 4:
        return points
    keep = [False] * len(points)
    keep[0] = keep[-1] = True
    stack = [(0, len(points) - 1)]
    while stack:
        i, j = stack.pop()
        if j <= i + 1:
            continue
        x1, y1 = points[i]
        x2, y2 = points[j]
        dx, dy = x2 - x1, y2 - y1
        norm = (dx * dx + dy * dy) ** 0.5
        best, best_d = -1, tol
        for k in range(i + 1, j):
            x0, y0 = points[k]
            if norm == 0:
                d = ((x0 - x1) ** 2 + (y0 - y1) ** 2) ** 0.5
            else:
                d = abs(dy * x0 - dx * y0 + x2 * y1 - y2 * x1) / norm
            if d > best_d:
                best, best_d = k, d
        if best != -1:
            keep[best] = True
            stack.append((i, best))
            stack.append((best, j))
    return [p for p, k in zip(points, keep) if k]


def _inside_point(xs, ys):
    """The region pixel closest to the region's mean position, so it is always inside."""
    mx, my = xs.mean(), ys.mean()
    d = (xs - mx) ** 2 + (ys - my) ** 2
    i = int(d.argmin())
    return [int(xs[i]), int(ys[i])]


def ring_area(points):
    """Shoelace area, used to sanity-check a trace against its pixel count."""
    a = 0.0
    n = len(points)
    for i in range(n):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % n]
        a += x1 * y2 - x2 * y1
    return abs(a) / 2.0


# ---------------------------------------------------------------------------
# colours
# ---------------------------------------------------------------------------

def flag_colour(faction_key):
    """Dominant saturated colour of a faction's flag, for factions with no banner row."""
    path = os.path.join(FLAG_DIR, faction_key + ".png")
    if not os.path.exists(path):
        return None
    try:
        im = Image.open(path).convert("RGBA").resize((48, 48))
    except Exception:
        return None
    a = np.asarray(im).reshape(-1, 4)
    a = a[a[:, 3] > 128][:, :3].astype(np.int16)
    if not len(a):
        return None
    mx, mn = a.max(axis=1), a.min(axis=1)
    sat = mx - mn
    strong = a[(sat > 40) & (mx > 50)]
    pick = strong if len(strong) > 20 else a
    counts = Counter(map(tuple, (pick // 24 * 24)))
    r, g, b = counts.most_common(1)[0][0]
    return f"{r:02X}{g:02X}{b:02X}"


def fallback_colour(key):
    """Deterministic, readable colour for anything with neither a banner nor a flag."""
    h = abs(hash(key)) % 360
    import colorsys
    r, g, b = colorsys.hsv_to_rgb(h / 360.0, 0.45, 0.65)
    return f"{int(r*255):02X}{int(g*255):02X}{int(b*255):02X}"


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("190 Expanded Wiki - campaign map builder")
    print("=" * 60)
    for p in (LOOKUP_TGA, BASE_PNG):
        if not os.path.exists(p):
            raise SystemExit(f"ERROR: missing map asset {p}")

    # ---------------------------------------------------------------- tables
    print("[1/6] Loading tables")
    region_colour = {}       # 'RRGGBB' -> region key
    hv, rv = read_tsv(os.path.join(VANILLA_DB, "regions_tables", "data__.tsv"))
    for r in rv:
        if len(r) > 1:
            region_colour[r[1].strip().upper()] = r[0].strip()
    n_vanilla = len(region_colour)
    for f in glob.glob(os.path.join(MOD_ROOT, "**", "db", "regions_tables", "*.tsv"), recursive=True):
        if os.sep + "Output" + os.sep in f:
            continue
        _h, rows = read_tsv(f)
        for r in rows:
            if len(r) > 1:
                region_colour[r[1].strip().upper()] = r[0].strip()
    print(f"  region colours: {n_vanilla} vanilla + {len(region_colour) - n_vanilla} from the mod")

    hf, rf = read_tsv(os.path.join(START_POS_DIR, "start_pos_factions_tables", f"data_{CAMPAIGN}.tsv"))
    fid, fkey = col(hf, "ID"), col(hf, "faction")
    id_to_faction = {r[fid]: r[fkey] for r in rf if len(r) > max(fid, fkey)}

    hr, rr = read_tsv(os.path.join(START_POS_DIR, "start_pos_regions_tables", f"data_{CAMPAIGN}.tsv"))
    c_region, c_owner, c_cap = col(hr, "region"), col(hr, "owning_faction"), col(hr, "faction_capital")
    owner_of, capital_of = {}, set()
    for r in rr:
        if len(r) <= c_cap:
            continue
        key = r[c_region].strip()
        owner_of[key] = id_to_faction.get(r[c_owner].strip(), "")
        if r[c_cap].strip().lower() == "true":
            capital_of.add(key)
    print(f"  start positions: {len(owner_of)} regions, "
          f"{sum(1 for v in owner_of.values() if v)} owned, {len(capital_of)} capitals")

    hb, rb = read_tsv(os.path.join(VANILLA_DB, "faction_banners_tables", "data__.tsv"))
    c_hex = col(hb, "primary_hex")
    banner = {r[0]: r[c_hex].strip().upper() for r in rb if len(r) > c_hex and r[c_hex].strip()}

    loc = read_loc(os.path.join(MOD_ROOT, "1_Faction", "text", "db", "regions.loc.tsv"))
    region_name = {k[len("regions_onscreen_"):]: v for k, v in loc.items()
                   if k.startswith("regions_onscreen_")}
    print(f"  region names: {len(region_name)}")

    faction_name = {}
    fpath = os.path.join(SITE_DATA, "factions.js")
    if os.path.exists(fpath):
        s = open(fpath, encoding="utf-8").read()
        m = re.search(r"const FACTION_DATA = (\[.*?\]);\n\nconst", s, re.S)
        if m:
            for f in json.loads(m.group(1)):
                faction_name.setdefault(f["faction_key"], f.get("state_name") or f["name"])
    # factions.js only covers factions that get a wiki page, so a handful of map owners
    # (minor rebels, one-region holdouts) are missing from it. Fill those from the loc.
    from_js = len(faction_name)
    for rel in ("text/mod/2_Char/db/factions/ironic_added_factions_text.loc.tsv",
                "text/vanilla/factions__.loc.tsv"):  # setdefault: first wins, so mod before vanilla
        for k, v in read_loc(os.path.join(SCRIPT_DIR, rel)).items():
            if k.startswith("factions_screen_name_"):
                faction_name.setdefault(k[len("factions_screen_name_"):], v)
    print(f"  faction display names: {from_js} from factions.js, "
          f"{len(faction_name) - from_js} from loc")

    # ---------------------------------------------------------------- lookup
    print("[2/6] Decoding the region lookup")
    idx, palette = load_lookup(LOOKUP_TGA)
    h, w = idx.shape
    resolved = {i: region_colour[c] for i, c in palette.items() if c in region_colour}
    print(f"  {w}x{h}, palette {len(palette)}, resolved to a region: {len(resolved)}")

    present = set(np.unique(idx).tolist())
    usable = {i: k for i, k in resolved.items() if i in present}
    print(f"  palette entries actually used on the map: {len(usable)}")

    # ---------------------------------------------------------------- shapes
    print("[3/6] Tracing region outlines")
    # Draw only the regions the campaign actually uses. start_pos_regions holds exactly the
    # playable set, which excludes sea and river zones without needing to match on names.
    playable = {pi: key for pi, key in usable.items() if key in owner_of}
    print(f"  of those, used by the {CAMPAIGN} start positions: {len(playable)}")
    no_shape = sorted(set(owner_of) - set(playable.values()))
    if no_shape:
        print(f"  {len(no_shape)} start-position regions have no pixels in the lookup: "
              + ", ".join(no_shape[:8]) + ("..." if len(no_shape) > 8 else ""))

    regions, skipped_parts, area_warnings = [], 0, []
    for n, (pi, key) in enumerate(sorted(playable.items(), key=lambda kv: kv[1]), 1):
        mask_full = idx == pi
        ys, xs = np.nonzero(mask_full)
        if not len(ys):
            continue
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        sub = np.ascontiguousarray(mask_full[y0:y1, x0:x1])
        labels, count = components(sub)

        parts, total_px = [], 0
        for lab in range(1, count + 1):
            part = labels == lab
            px = int(part.sum())
            if px < MIN_PART_PIXELS:
                skipped_parts += 1
                continue
            pys, pxs = np.nonzero(part)
            # np.nonzero walks row-major, so the first entry is the topmost-then-leftmost
            # pixel, which is guaranteed to sit on the outer boundary
            outer = simplify(trace_boundary(part, (int(pxs[0]), int(pys[0]))), TOLERANCE)
            if len(outer) < 3:
                skipped_parts += 1
                continue
            holes = [simplify(hr, TOLERANCE) for hr in find_holes(part, MIN_PART_PIXELS)]
            holes = [hr for hr in holes if len(hr) >= 3]
            traced = ring_area(outer) - sum(ring_area(hr) for hr in holes)
            if px > 5000 and abs(traced - px) / px > 0.25:
                area_warnings.append((key, px, int(traced)))
            # one part = its outer ring followed by any enclave rings, which is exactly
            # the shape L.polygon() expects
            parts.append([[[int(x + x0), int(y + y0)] for x, y in ring]
                          for ring in [outer] + holes])
            total_px += px
        if not parts:
            continue

        owner = owner_of.get(key, "")
        regions.append({
            "key": key,
            "name": region_name.get(key, key.replace("_", " ").title()),
            "owner": owner,
            "ownerName": faction_name.get(owner, ""),
            "isCapital": key in capital_of,
            # the mean of a crescent-shaped region can fall outside it, so snap to the
            # region pixel nearest that mean; a label must sit on its own region
            "centroid": _inside_point(xs, ys),
            "pixels": total_px,
            "parts": parts,
        })
        if n % 60 == 0:
            print(f"    {n}/{len(playable)}...")
    print(f"  {len(regions)} regions traced, {skipped_parts} small parts dropped")
    if area_warnings:
        print(f"  WARNING: {len(area_warnings)} outlines differ from their pixel count by >25%")
        for k, px, ta in area_warnings[:5]:
            print(f"    {k}: {px} px vs traced area {ta}")

    # -------------------------------------------------------------- colours
    print("[4/6] Resolving faction colours")
    owners = sorted({r["owner"] for r in regions if r["owner"]})
    colours, src = {}, Counter()
    for key in owners:
        c = banner.get(key)
        if c:
            src["banner"] += 1
        else:
            c = flag_colour(key)
            src["flag" if c else "generated"] += 1
            c = c or fallback_colour(key)
        colours[key] = "#" + c
    print(f"  {len(owners)} owners: " + ", ".join(f"{v} from {k}" for k, v in src.items()))

    factions = []
    for key in owners:
        caps = [r["key"] for r in regions if r["owner"] == key and r["isCapital"]]
        factions.append({
            "key": key,
            "name": faction_name.get(key) or re.sub(r"^.*?faction_", "", key).replace("_", " ").title(),
            "colour": colours[key],
            "regions": sum(1 for r in regions if r["owner"] == key),
            "capitals": caps,
        })
    factions.sort(key=lambda f: (-f["regions"], f["name"]))

    # ---------------------------------------------------------------- image
    print("[5/6] Exporting the base map")
    image_name = "campaign_map.webp"
    if NO_IMAGE:
        print("  skipped (--no-image)")
    else:
        os.makedirs(IMAGE_DIR, exist_ok=True)
        im = Image.open(BASE_PNG).convert("RGB")
        out = os.path.join(IMAGE_DIR, image_name)
        im.save(out, "WEBP", quality=WEBP_QUALITY, method=6)
        print(f"  {image_name}: {im.width}x{im.height}, {os.path.getsize(out)/1048576:.2f} MB")

    # --------------------------------------------------------------- output
    print("[6/6] Writing data")
    # flatten each ring to [x0,y0,x1,y1,...]; roughly halves the file
    for r in regions:
        r["parts"] = [[[c for pt in ring for c in pt] for ring in part] for part in r["parts"]]

    os.makedirs(SITE_DATA, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write("// Auto-generated by generate_data/build_map.py - do not edit by hand.\n")
        f.write(f"// {len(regions)} regions traced from the mod's campaign map lookup texture.\n")
        f.write("// region.parts = [ part ][ ring ] with flat [x0,y0,x1,y1,...] in source image pixels.\n\n")
        f.write("const MAP_CONFIG = " + json.dumps({
            "width": int(w), "height": int(h), "image": f"data/images/map/{image_name}",
            "campaign": CAMPAIGN,
        }) + ";\n\n")
        f.write("const MAP_REGIONS = " + json.dumps(regions, ensure_ascii=False, separators=(",", ":")) + ";\n\n")
        f.write("const MAP_FACTIONS = " + json.dumps(factions, ensure_ascii=False, indent=1) + ";\n\n")
        f.write("const MAP_FACTION_BY_KEY = {};\nMAP_FACTIONS.forEach(f => { MAP_FACTION_BY_KEY[f.key] = f; });\n")
    size_mb = os.path.getsize(OUTPUT_PATH) / 1048576
    print(f"  Written: {OUTPUT_PATH} ({size_mb:.2f} MB)")

    stats = {
        "regions": len(regions),
        "owned": sum(1 for r in regions if r["owner"]),
        "capitals": sum(1 for r in regions if r["isCapital"]),
        "factions": len(factions),
        "paletteResolved": len(resolved),
        "paletteUsed": len(usable),
        "points": sum(len(ring) // 2 for r in regions for part in r["parts"] for ring in part),
        "holes": sum(len(part) - 1 for r in regions for part in r["parts"]),
        "dataMB": round(size_mb, 2),
        "areaWarnings": len(area_warnings),
        "noShape": no_shape,
    }
    with open(SUMMARY_PATH, "w", encoding="utf-8", newline="\n") as f:
        json.dump(stats, f, indent=2)
    print()
    print("SUMMARY", json.dumps(stats))


if __name__ == "__main__":
    main()
