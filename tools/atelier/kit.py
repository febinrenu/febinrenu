"""Small helpers shared by every builder: documents, outlined text, writing files."""

from __future__ import annotations

import html
from pathlib import Path

import typeset as T

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "assets" / "calibre"


def esc(s: str) -> str:
    return html.escape(s, quote=True)


REDUCED = "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"


def doc(w: int, h: int, title: str, desc: str, style: str, defs: str, body: str, uid: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-labelledby="{uid}-t {uid}-d">'
            f'<title id="{uid}-t">{esc(title)}</title><desc id="{uid}-d">{esc(desc)}</desc>'
            f"<defs><style>{style}{REDUCED}</style>{defs}</defs>{body}</svg>\n")


# README images are shown at roughly 0.7x their 1200-unit width, and Martian Mono
# carries the engraved micro-type, so it is set larger than its nominal size.
MICRO = 1.3


def _size(font: str, size: float) -> float:
    return size * MICRO if font.startswith("martian") else size


def txt(s: str, font: str, size: float, x: float, y: float, fill: str, tracking: float = 0.0,
        anchor: str = "start", extra: str = "") -> str:
    d, _ = T.text(s, font, _size(font, size), x, y, tracking, anchor)
    return f'<path d="{d}" fill="{fill}"{(" " + extra) if extra else ""}/>'


def width(s: str, font: str, size: float, tracking: float = 0.0) -> float:
    return T.measure(s, font, _size(font, size), tracking)


def fit(s: str, font: str, size: float, max_width: float, tracking: float = 0.0) -> float:
    """The largest size up to `size` at which s fits in max_width."""
    w = width(s, font, size, tracking)
    return size if w <= max_width else size * max_width / w


def write(rel: str, svg: str) -> Path:
    out = ASSETS / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(svg, encoding="utf-8", newline="\n")
    return out
