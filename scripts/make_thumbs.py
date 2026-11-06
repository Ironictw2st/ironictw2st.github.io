"""Portrait thumbnails for the wiki (run before building dist; the deploy workflow runs it too).

total_war/data/images/db/<name>.png  (about 600 KB each, 725x1257)
  -> total_war/data/images/db_thumb/<name>.webp   160 px wide, about 8 KB   (lists, family trees, faction leaders)
  -> total_war/data/images/db_med/<name>.webp     640 px wide, about 40 KB  (the character page hero)

The generated folders are git-ignored; the originals stay the source of truth.
Runs on every CPU core (the first version took over 10 minutes on one core).
Usage: python scripts/make_thumbs.py [--force]
"""
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'total_war' / 'data' / 'images' / 'db'
IMAGES = ROOT / 'total_war' / 'data' / 'images'
OUT = {'db_thumb': 160, 'db_med': 640}
QUALITY = 80


def convert(job):
    png, rel, force = job
    made = size = 0
    for folder, width in OUT.items():
        dest = IMAGES / folder / rel
        if not force and dest.exists() and dest.stat().st_mtime >= Path(png).stat().st_mtime:
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(png) as im:
            im = im.convert('RGBA') if im.mode in ('P', 'LA', 'RGBA') else im.convert('RGB')
            if im.width > width:
                im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
            im.save(dest, 'WEBP', quality=QUALITY, method=4)
        made += 1
        size += dest.stat().st_size
    return made, size


def main() -> None:
    force = '--force' in sys.argv
    jobs = [(str(p), str(p.relative_to(SRC).with_suffix('.webp')), force) for p in sorted(SRC.rglob('*.png'))]
    with ProcessPoolExecutor(max_workers=os.cpu_count() or 2) as pool:
        results = list(pool.map(convert, jobs, chunksize=8))
    made = sum(r[0] for r in results)
    print(f'thumbs: {made} written, {len(jobs) * len(OUT) - made} up to date; {sum(r[1] for r in results) / 1e6:.1f} MB of new files')


if __name__ == '__main__':
    main()
