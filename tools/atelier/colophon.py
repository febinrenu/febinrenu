"""The colophon: the caseback seen from behind, its winding rotor swinging, and how this was made."""

from __future__ import annotations

import math

import geom as G
import kit
from palette import THEMES

W, H = 1200, 340
f = G.n


def build(p: dict) -> str:
    uid = f"co{p['name'][0]}"
    dark = p["name"] == "dark"
    cx, cy, R = 230, H / 2, 132
    g_defs, g_body = G.guilloche(f"{uid}g", cx, cy, 70, 7, 16, 8, p["steel"], 0.5, 0.35 if dark else 0.5)
    defs = (g_defs
            + f'<clipPath id="{uid}win"><path d="{G.circle(cx, cy, R)}"/></clipPath>'
            + f'<linearGradient id="{uid}st" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{p["case_hi"]}"/>'
              f'<stop offset=".5" stop-color="{p["steel_faint"] if dark else "#f6f5f1"}"/><stop offset="1" stop-color="{p["case_hi"]}"/></linearGradient>'
              f'<pattern id="{uid}gv" width="16" height="16" patternUnits="userSpaceOnUse" patternTransform="rotate(90)">'
              f'<rect width="16" height="16" fill="url(#{uid}st)"/></pattern>'
            + f'<radialGradient id="{uid}vig" cx=".2" cy=".5" r=".8"><stop offset="0" stop-color="{p["case_hi"]}"/>'
              f'<stop offset="1" stop-color="{p["case"]}"/></radialGradient>'
            + f'<radialGradient id="{uid}bl" cx=".35" cy=".3" r=".8"><stop offset="0" stop-color="{p["blued_hi"]}"/>'
              f'<stop offset="1" stop-color="{p["blued"]}"/></radialGradient>')
    style = (f".rotor{{transform-origin:{cx}px {f(cy)}px;animation:rotor 14s cubic-bezier(.45,0,.4,1) infinite}}"
             "@keyframes rotor{0%{transform:rotate(-40deg)}22%{transform:rotate(130deg)}40%{transform:rotate(70deg)}"
             "68%{transform:rotate(220deg)}84%{transform:rotate(190deg)}100%{transform:rotate(320deg)}}"
             ".rise{animation:rise 1.2s cubic-bezier(.2,.7,.2,1) both}"
             "@keyframes rise{from{transform:translateY(6px)}to{transform:none}}")
    # the rotor: a half disc with a heavy rim, striped, engraved
    rotor_d = (f"M{f(cx - R + 6)},{f(cy)}A{f(R - 6)},{f(R - 6)} 0 0 1 {f(cx + R - 6)},{f(cy)}"
               f"L{f(cx + 20)},{f(cy)}A20,20 0 0 0 {f(cx - 20)},{f(cy)}Z")
    rim_d = (f"M{f(cx - R + 6)},{f(cy)}A{f(R - 6)},{f(R - 6)} 0 0 1 {f(cx + R - 6)},{f(cy)}"
             f"L{f(cx + R - 22)},{f(cy)}A{f(R - 22)},{f(R - 22)} 0 0 0 {f(cx - R + 22)},{f(cy)}Z")
    engraving = kit.txt("FKR·26", "martian-light", 9, cx, cy - 52, p["ink_dim"], 0.5, "middle")
    rotor = (f'<g class="rotor"><path d="{rotor_d}" transform="translate(3 4)" fill="#000" opacity="{".45" if dark else ".15"}"/>'
             f'<path d="{rotor_d}" fill="url(#{uid}gv)" stroke="{p["steel"]}" stroke-opacity=".6"/>'
             f'<path d="{rim_d}" fill="{p["steel_dim"] if dark else p["steel"]}" opacity=".9"/>{engraving}</g>')
    window = (f'<circle cx="{cx}" cy="{f(cy)}" r="{R + 14}" fill="{p["case_hi"]}" stroke="{p["steel"]}" stroke-width="1.4"/>'
              f'<path d="{G.ticks(cx, cy, R + 12, 5, 60, .5)}" stroke="{p["steel_dim"]}" stroke-width=".6"/>'
              f'<g clip-path="url(#{uid}win)"><rect x="{cx - R}" y="{f(cy - R)}" width="{2 * R}" height="{2 * R}" fill="{p["plate"]}"/>'
              f'{g_body}{rotor}</g>'
              f'<circle cx="{cx}" cy="{f(cy)}" r="{R}" fill="none" stroke="{p["steel_dim"]}" stroke-width=".8"/>'
              f'<circle cx="{cx}" cy="{f(cy)}" r="9" fill="url(#{uid}bl)"/>'
              f'<path d="{G.screw(cx, cy, 9, 0.5)}" fill="{p["case"]}" opacity=".8"/>')
    x0 = 470
    lines = ["Drawn as SVG by Python that ships in this repository.",
             "Set in Bodoni Moda and Martian Mono (SIL OFL), outlined into paths.",
             "Figures come from each project's own README; illustrations say so.",
             "The ledger is redrawn weekly; the wager moves with every visitor."]
    text = (f'<g class="rise">' + kit.txt("COLOPHON", "martian", 9.5, x0, 78, p["salmon"], 0.34)
            + f'<path d="M{x0},92H{W - 64}" stroke="{p["steel_dim"]}" stroke-width=".7"/>'
            + kit.txt("Every image above is typeset code.", "bodoni-display-italic", 30, x0, 140, p["ink"]) + "</g>")
    for i, line in enumerate(lines):
        text += (f'<g class="rise" style="animation-delay:{0.3 + i * 0.15:.2f}s">'
                 + kit.txt(line, "bodoni-text", 15.5, x0, 182 + i * 27, p["ink_dim"]) + "</g>")
    text += (kit.txt("CALIBRE FKR·26 · MMXXVI · HYDERABAD", "martian-light", 8.6, x0, H - 40,
                     p["ink_faint"] if dark else p["ink_dim"], 0.3)
             + kit.txt("FEBIN K RENU", "martian", 8.6, W - 64, H - 40, p["ink_dim"], 0.34, "end"))
    body = (f'<rect width="{W}" height="{H}" rx="18" fill="url(#{uid}vig)"/>{window}{text}'
            f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="18" fill="none" stroke="{p["steel_faint"]}"/>')
    desc = ("Colophon: a caseback window with the winding rotor swinging. Every image above is typeset code: drawn as "
            "SVG by Python that ships in this repository, set in Bodoni Moda and Martian Mono under the SIL Open Font "
            "License and outlined into paths. Figures come from each project's own README and illustrations say so. "
            "The ledger is redrawn weekly and the wager moves with every visitor. Calibre FKR-26, 2026, Hyderabad.")
    return kit.doc(W, H, "Colophon", desc, style, defs, body, uid)


def main() -> None:
    for p in THEMES:
        out = kit.write(f"colophon-{p['name']}.svg", build(p))
    print(f"colophon: {out.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
