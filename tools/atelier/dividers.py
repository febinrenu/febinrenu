"""Section dividers: a turning guilloché rosette, a Roman numeral, the title, a hairline.

Transparent, so each comes in a dark and a light finish for GitHub's two themes.
"""

from __future__ import annotations

import geom as G
import kit
from palette import THEMES

W, H = 1200, 120

SECTIONS = [
    ("i", "I", "Calibration", "WHAT I BUILD, AND HOW I DECIDE"),
    ("ii", "II", "Provenance", "WHAT IS REAL, AND HOW YOU CAN CHECK"),
    ("iii", "III", "Complications", "EACH WORK, DRAWN AS THE MECHANISM IT IS"),
    ("iv", "IV", "In the vault", "REAL, NOT YET PUBLIC"),
    ("v", "V", "The Wager", "OUT-DECIDE MY MODEL, LIVE"),
    ("vi", "VI", "Specification", "INSTRUMENTS IN DAILY USE"),
    ("vii", "VII", "Ledger", "A YEAR OF PUBLIC WORK, REFRESHED WEEKLY"),
]


def build(p: dict, key: str, numeral: str, title: str, caption: str) -> str:
    uid = f"dv{key}{p['name'][0]}"
    cx, cy = 52, 62
    r1_defs, r1 = G.guilloche(f"{uid}a", cx, cy, 30, 3.2, 12, 6, p["steel"], 0.5, 0.75, "spin")
    r2_defs, r2 = G.guilloche(f"{uid}b", cx, cy, 20, 2.4, 9, 5, p["copper"], 0.45, 0.8, "spin2")
    title_x = 120
    tw = kit.width(title, "bodoni-display", 40, 0.01)
    line_x0 = title_x + tw + 28
    style = (".spin{animation:spin 90s linear infinite}@keyframes spin{to{transform:rotate(360deg)}}"
             ".spin2{animation:spin2 60s linear infinite}@keyframes spin2{to{transform:rotate(-360deg)}}"
             f".spin,.spin2{{transform-origin:{cx}px {cy}px}}"
             ".lume{animation:lume 5s ease-in-out infinite}@keyframes lume{0%,100%{opacity:.3}50%{opacity:1}}"
             ".rule{stroke-dasharray:1;stroke-dashoffset:1;animation:rule 1.8s cubic-bezier(.6,0,.2,1) .2s forwards}"
             "@keyframes rule{to{stroke-dashoffset:0}}")
    body = (
        f'<circle cx="{cx}" cy="{cy}" r="38" fill="none" stroke="{p["steel_dim"]}" stroke-width=".6"/>'
        f'<path d="{G.ticks(cx, cy, 38, 3, 60, .5)}" stroke="{p["steel_dim"]}" stroke-width=".5"/>'
        f"{r1}{r2}"
        f'<circle cx="{cx}" cy="{cy}" r="3" fill="{p["lume"]}" class="lume"/>'
        + kit.txt(f"N° {numeral}", "martian", 10, title_x + 2, 40, p["salmon"], 0.3)
        + kit.txt(title, "bodoni-display", 40, title_x, 84, p["ink"], 0.01)
        + f'<path class="rule" pathLength="1" d="M{line_x0:.0f},{cy + 8}H{W - 8}" stroke="{p["steel_dim"]}" stroke-width=".8"/>'
        + f'<path d="M{W - 8},{cy + 3}v10" stroke="{p["steel"]}" stroke-width="1"/>'
        + kit.txt(caption, "martian-light", 9, W - 8, cy + 30, p["ink_dim"], 0.26, "end")
    )
    desc = f"Section {numeral}: {title}. {caption.capitalize()}."
    return kit.doc(W, H, f"{numeral}. {title}", desc, style, r1_defs + r2_defs, body, uid)


def main() -> None:
    for key, numeral, title, caption in SECTIONS:
        for p in THEMES:
            kit.write(f"dividers/{key}-{p['name']}.svg", build(p, key, numeral, title, caption))
    print(f"{len(SECTIONS) * len(THEMES)} dividers")


if __name__ == "__main__":
    main()
