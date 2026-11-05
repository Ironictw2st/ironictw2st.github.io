"""Brush font subsets (Ma Shan Zheng, SIL OFL 1.1) as two WOFF2 files with unicode-range, so a page only
downloads the glyphs it actually shows:
  MaShanZheng-core.woff2  the ~50 glyphs used by the home cards, seals and section pages (about 15 KB)
  MaShanZheng-names.woff2 every other CJK glyph in the character / faction names (about 350 KB, character pages only)
Source font: https://github.com/google/fonts/tree/main/ofl/mashanzheng (download MaShanZheng-Regular.ttf and pass its path).
Usage: python scripts/build_brush_font.py path/to/MaShanZheng-Regular.ttf
Prints the @font-face unicode-range lines to paste into total_war/styles/tw3k.css.
"""
import glob
import sys
from pathlib import Path

from fontTools import subset

ROOT = Path(__file__).resolve().parent.parent
src = sys.argv[1]

text = ''
for f in glob.glob(str(ROOT / 'index.html')) + glob.glob(str(ROOT / 'total_war' / '*.html')) + glob.glob(str(ROOT / 'tools' / '*.html')):
    text += Path(f).read_text(encoding='utf8')
core = {c for c in text if '㐀' <= c <= '鿿'}
core |= set('三國漢魏蜀吳群雄逐鹿英傑傳旗地將法圖變書器印章史記天下大勢分合未完成漢朝黃巾董卓袁曹劉孫紫金')
names = ''
for f in ('characters.js', 'factions.js'):
    names += (ROOT / 'total_war' / 'data' / f).read_text(encoding='utf8')
ext = {c for c in names if '㐀' <= c <= '鿿'} - core


def build(chars, out):
    opts = subset.Options()
    opts.flavor = 'woff2'
    opts.layout_features = ['*']
    font = subset.load_font(src, opts)
    sub = subset.Subsetter(opts)
    sub.populate(text=''.join(sorted(chars)))
    sub.subset(font)
    subset.save_font(font, str(ROOT / 'total_war' / 'fonts' / out), opts)
    return (ROOT / 'total_war' / 'fonts' / out).stat().st_size


def ranges(chars):
    cps = sorted(ord(c) for c in chars)
    out, start, prev = [], cps[0], cps[0]
    for cp in cps[1:]:
        if cp != prev + 1:
            out.append((start, prev)); start = cp
        prev = cp
    out.append((start, prev))
    return ', '.join(f'U+{a:X}' if a == b else f'U+{a:X}-{b:X}' for a, b in out)


print('core', len(core), 'glyphs', build(core, 'MaShanZheng-core.woff2'), 'bytes')
print('names', len(ext), 'glyphs', build(ext, 'MaShanZheng-names.woff2'), 'bytes')
print('core unicode-range:', ranges(core))
print('names unicode-range:', ranges(ext))
