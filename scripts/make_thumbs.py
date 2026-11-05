"""Portrait thumbnails for the wiki (run before building dist; the deploy workflow runs it too).

total_war/data/images/db/<name>.png  (about 600 KB each, 725x1257)
  -> total_war/data/images/db_thumb/<name>.webp   160 px wide, about 8 KB   (lists, family trees, faction leaders)
  -> total_war/data/images/db_med/<name>.webp     640 px wide, about 60 KB  (the character page hero)

The generated folders are git-ignored; the originals stay the source of truth.
Usage: python scripts/make_thumbs.py [--force]
"""
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'total_war' / 'data' / 'images' / 'db'
OUT = {'db_thumb': 160, 'db_med': 640}
QUALITY = 80


def main() -> None:
    force = '--force' in sys.argv
    made = skipped = 0
    before = after = 0
    for png in sorted(SRC.rglob('*.png')):
        rel = png.relative_to(SRC).with_suffix('.webp')
        for folder, width in OUT.items():
            dest = ROOT / 'total_war' / 'data' / 'images' / folder / rel
            if not force and dest.exists() and dest.stat().st_mtime >= png.stat().st_mtime:
                skipped += 1
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            with Image.open(png) as im:
                im = im.convert('RGBA') if im.mode in ('P', 'LA', 'RGBA') else im.convert('RGB')
                if im.width > width:
                    im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
                im.save(dest, 'WEBP', quality=QUALITY, method=6)
            made += 1
            after += dest.stat().st_size
        before += png.stat().st_size
    print(f'thumbs: {made} written, {skipped} up to date; originals {before / 1e6:.0f} MB, new files {after / 1e6:.1f} MB')


if __name__ == '__main__':
    main()
