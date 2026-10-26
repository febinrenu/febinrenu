"""Typesetting as outlines. Stdlib only: reads glyphs/*.json made by fonts_to_glyphs.py.

    d, width = text("FEBIN K RENU", "bodoni-display", size=64, x=100, y=200, tracking=0.08)

`y` is the baseline. `tracking` is in em. Kerning comes from the font's GPOS pairs.
Characters a font lacks fall back to Martian Mono, and the rupee sign, which
neither font has, is constructed here.
"""

from __future__ import annotations

import json
import math
from functools import lru_cache
from pathlib import Path

GLYPHS = Path(__file__).resolve().parent / "glyphs"


@lru_cache(maxsize=None)
def font(name: str) -> dict:
    data = json.loads((GLYPHS / f"{name}.json").read_text(encoding="utf-8"))
    if "₹" not in data["glyphs"]:
        data["glyphs"]["₹"] = _rupee(data["upm"], data["capHeight"] or 0.7 * data["upm"],
                                          didone=name.startswith("bodoni"))
    return data


def _rupee(upm: int, cap: float, didone: bool = False) -> dict:
    """A rupee sign built from stroked segments, unioned by the nonzero fill rule.

    For the Didone it takes Bodoni's contrast: hairline bars, a heavy bowl, a firm leg.
    """
    k = cap / 700.0
    bars, bowl_w, leg = (22, 112, 64) if didone else (74, 74, 74)
    bowl = [(300 + 225 * math.cos(math.radians(a)), 515 + 185 * math.sin(math.radians(a)))
            for a in range(90, -91, -10)]
    centrelines = [([(110, 700), (650, 700)], bars), ([(110, 520), (650, 520)], bars), (bowl, None),
                   ([(300, 330), (160, 330)], bars), ([(200, 334), (575, 0)], leg)]
    ops: list[list] = []
    for line, width in centrelines:
        pts = [(x * k, y * k) for x, y in line]
        for j, ((x1, y1), (x2, y2)) in enumerate(zip(pts, pts[1:])):
            if width is None:  # the bowl swells to full weight at its rightmost point
                t = abs(j + 0.5 - (len(pts) - 1) / 2) / ((len(pts) - 1) / 2)
                wd = bars + (bowl_w - bars) * (1 - t) ** 1.5
            else:
                wd = width
            ops += _segment(x1, y1, x2, y2, wd * k / 2)
    return {"a": round(760 * k), "d": ops}


def _segment(x1: float, y1: float, x2: float, y2: float, w: float) -> list[list]:
    dx, dy = x2 - x1, y2 - y1
    n = math.hypot(dx, dy) or 1
    ux, uy = dx / n, dy / n
    px, py = -uy * w, ux * w
    ex, ey = ux * w * 0.5, uy * w * 0.5  # overlap neighbours so joints close
    quad = [(x1 - ex + px, y1 - ey + py), (x1 - ex - px, y1 - ey - py),
            (x2 + ex - px, y2 + ey - py), (x2 + ex + px, y2 + ey + py)]
    area = sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(quad, quad[1:] + quad[:1]))
    if area < 0:
        quad.reverse()
    return [["M", *quad[0]], *[["L", *p] for p in quad[1:]], ["Z"]]


def _glyph(f: dict, ch: str) -> tuple[dict, float]:
    """Glyph and the scale factor that maps it into f's units (for fallbacks)."""
    g = f["glyphs"].get(ch)
    if g is not None:
        return g, 1.0
    fb = font("martian")
    g = fb["glyphs"].get(ch) or fb["glyphs"]["?"]
    return g, f["upm"] / fb["upm"]


def measure(s: str, name: str, size: float, tracking: float = 0.0) -> float:
    f = font(name)
    scale = size / f["upm"]
    total = 0.0
    for i, ch in enumerate(s):
        g, k = _glyph(f, ch)
        total += g["a"] * k * scale
        if i + 1 < len(s):
            total += f["kern"].get(ch + s[i + 1], 0) * scale + tracking * size
    return total


def _num(v: float) -> str:
    """Compact number: one decimal, no trailing zero, no leading zero."""
    r = round(v, 1)
    if r == int(r):
        return str(int(r))
    s = f"{r:.1f}"
    return s.replace("0.", ".", 1) if s.startswith(("0.", "-0.")) else s


def _join(nums: list[str]) -> str:
    """Join numbers with the fewest separators SVG path syntax allows."""
    out = ""
    for v in nums:
        out += v if (not out or v.startswith("-")) else " " + v
    return out


def text(s: str, name: str, size: float, x: float = 0.0, y: float = 0.0,
         tracking: float = 0.0, anchor: str = "start") -> tuple[str, float]:
    """Path data for s with its baseline at y. anchor: start | middle | end."""
    f = font(name)
    scale = size / f["upm"]
    width = measure(s, name, size, tracking)
    if anchor == "middle":
        x -= width / 2
    elif anchor == "end":
        x -= width
    out: list[str] = []
    pen = x
    for i, ch in enumerate(s):
        g, k = _glyph(f, ch)
        sc = scale * k
        cx = cy = 0.0  # current point, in rounded absolute units, so relative steps never drift
        for op in g["d"]:
            c, vals = op[0], op[1:]
            if c == "Z":
                out.append("z")
                continue
            nums = []
            for j in range(0, len(vals), 2):
                ax = round(pen + vals[j] * sc, 1)
                ay = round(y - vals[j + 1] * sc, 1)
                if c == "M":
                    nums += [_num(ax), _num(ay)]
                else:
                    nums += [_num(ax - cx), _num(ay - cy)]
                if j == len(vals) - 2:
                    last = (ax, ay)
            out.append((c if c == "M" else c.lower()) + _join(nums))
            cx, cy = last
        pen += g["a"] * sc
        if i + 1 < len(s):
            pen += f["kern"].get(ch + s[i + 1], 0) * scale + tracking * size
    return "".join(out), width


def cap_height(name: str, size: float) -> float:
    f = font(name)
    return (f["capHeight"] or 0.7 * f["upm"]) * size / f["upm"]
