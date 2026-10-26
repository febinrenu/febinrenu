"""One-off: export glyph outlines from the OFL fonts into tools/atelier/glyphs/*.json.

GitHub serves README SVGs with a CSP that blocks fonts, so every word in this
profile is drawn as outlines. This script is the only place that needs fontTools;
everything that typesets at build or CI time reads the JSON with the stdlib.

    python tools/atelier/fonts_to_glyphs.py <dir with the downloaded .ttf files>

Fonts (SIL Open Font License 1.1, see glyphs/OFL.txt):
    Bodoni Moda  https://github.com/google/fonts/tree/main/ofl/bodonimoda
    Martian Mono https://github.com/google/fonts/tree/main/ofl/martianmono
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from fontTools.pens.basePen import BasePen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

OUT = Path(__file__).resolve().parent / "glyphs"
CHARS = [chr(c) for c in range(32, 127)] + list("·—–×→‘’“”…°±≤≥≈−")

# name: (file, axis location)
STYLES = {
    "bodoni-display": ("BodoniModa.ttf", {"wght": 430, "opsz": 30}),
    "bodoni-display-italic": ("BodoniModa-Italic.ttf", {"wght": 430, "opsz": 30}),
    "bodoni-text": ("BodoniModa.ttf", {"wght": 450, "opsz": 14}),
    "bodoni-text-italic": ("BodoniModa-Italic.ttf", {"wght": 450, "opsz": 14}),
    "martian": ("MartianMono.ttf", {"wght": 440, "wdth": 112.5}),
    "martian-light": ("MartianMono.ttf", {"wght": 330, "wdth": 112.5}),
    "martian-bold": ("MartianMono.ttf", {"wght": 600, "wdth": 112.5}),
}


class Recorder(BasePen):
    """Absolute M/L/Q/C/Z commands in font units, with quadratic runs decomposed."""

    def __init__(self, glyph_set):
        super().__init__(glyph_set)
        self.ops: list[list] = []

    def _moveTo(self, p):
        self.ops.append(["M", round(p[0]), round(p[1])])

    def _lineTo(self, p):
        self.ops.append(["L", round(p[0]), round(p[1])])

    def _qCurveToOne(self, p1, p2):
        self.ops.append(["Q", round(p1[0]), round(p1[1]), round(p2[0]), round(p2[1])])

    def _curveToOne(self, p1, p2, p3):
        self.ops.append(["C", *(round(v) for pt in (p1, p2, p3) for v in pt)])

    def _closePath(self):
        self.ops.append(["Z"])


def kerning(font: TTFont, names: dict[str, str]) -> dict[str, int]:
    """Pair kerning between the exported characters, read from GPOS PairPos lookups."""
    if "GPOS" not in font:
        return {}
    by_glyph = {g: ch for ch, g in names.items()}
    pairs: dict[str, int] = {}
    gpos = font["GPOS"].table
    for lookup in gpos.LookupList.Lookup:
        subs = lookup.SubTable
        if lookup.LookupType == 9:
            subs = [s.ExtSubTable for s in subs]
        for st in subs:
            if getattr(st, "LookupType", 2) != 2:
                continue
            cov = st.Coverage.glyphs
            if st.Format == 1:
                for i, first in enumerate(cov):
                    if first not in by_glyph:
                        continue
                    for rec in st.PairSet[i].PairValueRecord:
                        if rec.SecondGlyph in by_glyph and rec.Value1 and getattr(rec.Value1, "XAdvance", 0):
                            pairs.setdefault(by_glyph[first] + by_glyph[rec.SecondGlyph], rec.Value1.XAdvance)
            elif st.Format == 2:
                c1, c2 = st.ClassDef1.classDefs, st.ClassDef2.classDefs
                for first in cov:
                    if first not in by_glyph:
                        continue
                    row = st.Class1Record[c1.get(first, 0)]
                    for second, ch2 in by_glyph.items():
                        v = row.Class2Record[c2.get(second, 0)].Value1
                        adv = getattr(v, "XAdvance", 0) if v else 0
                        if adv:
                            pairs.setdefault(by_glyph[first] + ch2, adv)
    return pairs


def export(src: Path, name: str, file: str, loc: dict) -> None:
    font = instancer.instantiateVariableFont(TTFont(src / file), loc)
    cmap = font.getBestCmap()
    gs = font.getGlyphSet()
    names = {ch: cmap[ord(ch)] for ch in CHARS if ord(ch) in cmap}
    glyphs = {}
    for ch, g in names.items():
        pen = Recorder(gs)
        gs[g].draw(pen)
        glyphs[ch] = {"a": gs[g].width, "d": pen.ops}
    data = {
        "name": name, "upm": font["head"].unitsPerEm,
        "ascender": font["hhea"].ascent, "descender": font["hhea"].descent,
        "capHeight": getattr(font["OS/2"], "sCapHeight", 0), "xHeight": getattr(font["OS/2"], "sxHeight", 0),
        "glyphs": glyphs, "kern": kerning(font, names),
    }
    out = OUT / f"{name}.json"
    out.write_text(json.dumps(data, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")
    print(f"{name:24} {len(glyphs):3} glyphs {len(data['kern']):5} kern pairs {out.stat().st_size // 1024} KB")


if __name__ == "__main__":
    src = Path(sys.argv[1])
    OUT.mkdir(exist_ok=True)
    for name, (file, loc) in STYLES.items():
        export(src, name, file, loc)
