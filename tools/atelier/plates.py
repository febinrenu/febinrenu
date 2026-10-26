"""Complication plates: each project drawn as the mechanism it actually is.

Every plate shares a case, an engraved data column and a reference number; the
mechanism on the other side is specific to the project. Numbers on the plates
are only ones the project's own README reports. Illustrations say so.
"""

from __future__ import annotations

import math

import geom as G
import kit
from palette import THEMES

W, H = 1200, 500
f = G.n


# --- the shared case -----------------------------------------------------------------

def frame(p: dict, uid: str, side: str, no: int, ref: str, title: str, tagline: str, mech_name: str,
          rows: list[tuple[str, str]], status: list[str], note: str = "") -> tuple[str, str, float]:
    """(body, defs, mechanism centre x) for the engraved data column on `side`."""
    dark = p["name"] == "dark"
    x0 = 64 if side == "left" else W - 64 - 460
    x1 = x0 + 460
    ink, dim, faint = p["ink"], p["ink_dim"], p["ink_faint"]
    defs = (f'<radialGradient id="{uid}vig" cx="{".72" if side == "left" else ".28"}" cy=".5" r=".8">'
            f'<stop offset="0" stop-color="{p["case_hi"]}"/><stop offset="1" stop-color="{p["case"]}"/></radialGradient>')
    body = (f'<rect width="{W}" height="{H}" rx="18" fill="url(#{uid}vig)"/>'
            + kit.txt(f"COMPLICATION N° {no:02d}", "martian", 9.5, x0, 72, p["salmon"], 0.32)
            + kit.txt(f"REF. {ref}", "martian-light", 9, x1, 72, dim, 0.3, "end")
            + f'<path d="M{x0},{86}H{x1}" stroke="{p["steel_dim"]}" stroke-width=".7"/>'
            + kit.txt(title, "bodoni-display", 60, x0 - 3, 160, ink, 0.0)
            + kit.txt(tagline, "bodoni-display-italic", 23, x0, 198, p["salmon"] if dark else p["copper"])
            + kit.txt(mech_name, "martian-light", 8.6, x0, 232, dim, 0.3))
    y = 276
    for k, v in rows:
        body += (kit.txt(k, "martian-light", 8, x0, y, faint if dark else dim, 0.26)
                 + kit.txt(v, "bodoni-text", 15.5, x0 + 132, y + 1, ink)
                 + f'<path d="M{x0},{y + 10}H{x1}" stroke="{p["steel_faint"]}" stroke-width=".6"/>')
        y += 28
    sx = x0
    if note:
        body += kit.txt(note, "martian-light", 7.6, x0, H - 34, faint if dark else dim, 0.24)
    for s in status:
        live = s.startswith("LIVE")
        if live:
            body += f'<circle class="lume" cx="{sx + 4}" cy="{H - 66}" r="3.4" fill="{p["lume"]}"/>'
            sx += 14
        body += kit.txt(s, "martian", 8.6, sx, H - 62.5, ink if live else dim, 0.3)
        sx += kit.width(s, "martian", 8.6, 0.3) + 26
    mech_cx = (W - 64 - 330) if side == "left" else (64 + 330)
    return body, defs, mech_cx


def finish(p, uid, title, desc, style, defs, body):
    base_style = (".lume{animation:lume 4s ease-in-out infinite}@keyframes lume{0%,100%{opacity:.35}50%{opacity:1}}")
    body += f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="18" fill="none" stroke="{p["steel_faint"]}"/>'
    return kit.doc(W, H, title, desc, base_style + style, defs, body, uid)


def dial(p, cx, cy, r, uid, ticks=60, guill=True, lobes=14):
    """A sub-dial: rim, railway track, optional guilloché centre."""
    out = (f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r)}" fill="{p["plate"]}" stroke="{p["steel"]}" stroke-width="1.2"/>'
           f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r - 5)}" fill="none" stroke="{p["steel_faint"]}" stroke-width=".6"/>'
           f'<path d="{G.ticks(cx, cy, r - 6, 5, ticks, .6, 5)}" stroke="{p["steel_dim"]}" stroke-width=".6"/>'
           f'<path d="{G.ticks(cx, cy, r - 6, 9, 12, 1)}" stroke="{p["steel"]}" stroke-width="1.4"/>')
    defs = ""
    if guill:
        d, g = G.guilloche(f"{uid}", cx, cy, r * 0.5, r * 0.06, lobes, 6, p["steel"], 0.45,
                           0.35 if p["name"] == "dark" else 0.5)
        defs, out = d, out + g
    return out, defs


def bed(p, uid, x, y, w, h, rx=26):
    """A Geneva-striped bridge plate with blued screws at the corners."""
    dark = p["name"] == "dark"
    defs = (f'<linearGradient id="{uid}st" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{p["case_hi"]}"/>'
            f'<stop offset=".5" stop-color="{p["steel_faint"] if dark else "#f6f5f1"}"/><stop offset="1" stop-color="{p["case_hi"]}"/>'
            f'</linearGradient><pattern id="{uid}gv" width="22" height="22" patternUnits="userSpaceOnUse" '
            f'patternTransform="rotate(-32)"><rect width="22" height="22" fill="url(#{uid}st)"/></pattern>'
            f'<radialGradient id="{uid}bl" cx=".35" cy=".3" r=".8"><stop offset="0" stop-color="{p["blued_hi"]}"/>'
            f'<stop offset="1" stop-color="{p["blued"]}"/></radialGradient>')
    out = (f'<rect x="{f(x + 3)}" y="{f(y + 5)}" width="{f(w)}" height="{f(h)}" rx="{rx}" fill="#000" opacity="{".4" if dark else ".12"}"/>'
           f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="{rx}" fill="url(#{uid}gv)" '
           f'stroke="{p["steel"]}" stroke-opacity=".5"/>')
    i = max(16, rx * 0.7)
    for sx, sy in ((x + i, y + i), (x + w - i, y + i), (x + i, y + h - i), (x + w - i, y + h - i)):
        out += (f'<circle cx="{f(sx)}" cy="{f(sy)}" r="5" fill="url(#{uid}bl)"/>'
                f'<path d="{G.screw(sx, sy, 5, (sx * 7 + sy) % 3)}" fill="{p["case"]}" opacity=".8"/>')
    return out, defs


def hand(p, cx, cy, length, color, width=2.2, tail=0.18):
    return (f'<path d="M{f(cx)},{f(cy + length * tail)}L{f(cx)},{f(cy - length)}" stroke="{color}" '
            f'stroke-width="{width}" stroke-linecap="round"/>'
            f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(width * 1.8)}" fill="{color}"/>')


# --- I. EVORA: four sub-dials -------------------------------------------------------

def evora(p):
    uid = f"ev{p['name'][0]}"
    body, defs, mx = frame(
        p, uid, "left", 1, "EVR·4C", "Evora", "Ask a room of cameras a question.",
        "FOUR SUB-DIALS · ONE QUESTION · EVIDENCE OR SILENCE",
        [("HIT@5", "0.72 dev · 0.69 test (MEVA, one site)"),
         ("NEGATIVES", "precision 1.00 on dev; the baseline scores 0.00"),
         ("ANSWER", "camera, time, a circled clip, and the reasons"),
         ("PRIVACY", "one laptop, 8 GB GPU; faces blurred")],
        ["LIVE", "SOURCE", "HACKATHON TEAM BUILD"], "SMALL SETS · STATED IN THE REPO")
    cams = [("CAM 1 · MAIN GATE", -1, -1, 7.0), ("CAM 2 · LOBBY", 1, -1, 9.0),
            ("CAM 3 · ROOM", -1, 1, 11.0), ("CAM 4 · CORRIDOR", 1, 1, 8.0)]
    cy = H / 2 + 6
    gap, r = 96, 78
    style = ""
    mech, bdefs = bed(p, uid, mx - gap - r - 22, cy - gap - r - 22, 2 * (gap + r + 22), 2 * (gap + r + 22), 40)
    defs += bdefs
    for i, (label, sx, sy, period) in enumerate(cams):
        cx, ccy = mx + sx * gap, cy + sy * gap
        d_svg, d_defs = dial(p, cx, ccy, r, f"{uid}g{i}", lobes=10 + i * 2)
        defs += d_defs
        mech += d_svg
        mech += kit.txt(label, "martian-light", 7, cx, ccy + r * 0.62, p["ink_dim"], 0.22, "middle")
        if i == 0:
            # the hit: the hand finds the red car and holds while the lume ring blooms
            style += (f".h{i}{{transform-origin:{f(cx)}px {f(ccy)}px;animation:h{i} 10s cubic-bezier(.5,0,.3,1) infinite}}"
                      f"@keyframes h{i}{{0%{{transform:rotate(0)}}45%{{transform:rotate(312deg)}}"
                      f"88%{{transform:rotate(312deg)}}100%{{transform:rotate(360deg)}}}}"
                      f".hit{{transform-origin:{f(cx)}px {f(ccy)}px;animation:hit 10s ease-out infinite}}"
                      f"@keyframes hit{{0%,44%{{opacity:0;transform:scale(1.6)}}50%{{opacity:1;transform:scale(1)}}"
                      f"86%{{opacity:1}}92%,100%{{opacity:0}}}}")
            mark = G.pt(cx, ccy, r * 0.7, math.radians(312 - 90))
            mx_, my_ = (float(v) for v in mark.split(","))
            mech += (f'<g class="hit"><circle cx="{f(mx_)}" cy="{f(my_)}" r="9" fill="none" stroke="{p["lume"]}" '
                     f'stroke-width="1.6"/><circle cx="{f(mx_)}" cy="{f(my_)}" r="2.6" fill="{p["lume"]}"/></g>'
                     f'<circle cx="{f(mx_)}" cy="{f(my_)}" r="2" fill="{p["copper"]}"/>')
            mech += f'<g class="h{i}">{hand(p, cx, ccy, r * 0.74, p["blued_hi"] if p["name"] == "dark" else p["blued"])}</g>'
        else:
            style += (f".h{i}{{transform-origin:{f(cx)}px {f(ccy)}px;animation:spin {period}s linear infinite}}")
            mech += f'<g class="h{i}">{hand(p, cx, ccy, r * 0.74, p["steel"] if p["name"] == "dark" else p["steel"], 1.6)}</g>'
    style += "@keyframes spin{to{transform:rotate(360deg)}}"
    # one person, followed from CAM 2 to CAM 4: a dotted trace between dials
    c2 = (mx + gap, cy - gap)
    c4 = (mx + gap, cy + gap)
    style += (".trace{stroke-dasharray:2 6;animation:march 1.4s linear infinite,tr 10s ease-in-out infinite}"
              "@keyframes march{to{stroke-dashoffset:-16}}"
              "@keyframes tr{0%,55%{opacity:0}62%,92%{opacity:.9}98%,100%{opacity:0}}")
    mech += (f'<path class="trace" d="M{f(c2[0] + 40)},{f(c2[1] + 30)}C{f(c2[0] + 150)},{f(c2[1] + 80)} '
             f'{f(c4[0] + 150)},{f(c4[1] - 80)} {f(c4[0] + 40)},{f(c4[1] - 30)}" fill="none" stroke="{p["lume"]}" stroke-width="1.4"/>')
    # the answer, engraved when the hand holds
    style += ".ans{animation:ans 10s ease-out infinite}@keyframes ans{0%,48%{opacity:0}54%,88%{opacity:1}94%,100%{opacity:0}}"
    mech += (f'<g class="ans">'
             + kit.txt("FOUND · CAM 1 · 14:32:07 · CLIP 0:06", "martian", 8, mx, cy + gap + r + 44, p["lume"], 0.26, "middle")
             + "</g>")
    mech += kit.txt("“did a red car pass the main gate in the last hour?”", "bodoni-text-italic", 14, mx,
                    cy - gap - r - 34, p["ink_dim"], 0.0, "middle")
    body += mech
    desc = ("Plate one, Evora: four camera sub-dials, each with a sweeping scan hand. On camera 1, main gate, the hand "
            "finds a red car and holds while a lume ring blooms; a dotted trace follows one person from camera 2 to "
            "camera 4; the answer reads found, camera 1, 14:32:07, clip 0:06. Measured on one MEVA site: Hit@5 0.72 dev, "
            "0.69 test; negative precision 1.00 on dev against 0.00 for a frame-similarity baseline. Runs on one laptop "
            "with an 8 GB GPU, faces blurred. Live, source public, hackathon team build.")
    return finish(p, uid, "Evora: four sub-dials, one question", desc, style, defs, body)


def window(name, period, on, off, a="opacity:.18", b="opacity:1"):
    """Keyframes that hold state a, switch to b at `on` seconds, and back at `off`."""
    p0, p1 = 100 * on / period, 100 * off / period
    e = 0.6
    return (f"@keyframes {name}{{0%,{p0:.2f}%{{{a}}}{min(p0 + e, 100):.2f}%,{p1:.2f}%{{{b}}}"
            f"{min(p1 + e, 100):.2f}%,100%{{{a}}}}}")


def blued(p):
    return p["blued_hi"] if p["name"] == "dark" else p["blued"]


# --- II. PARALLAX: the certification ring -------------------------------------------

def parallax(p):
    uid = f"px{p['name'][0]}"
    body, defs, mx = frame(
        p, uid, "right", 2, "PLX·8J", "Parallax", "A finding has to prove itself.",
        "EIGHT-JEWEL CERTIFICATION · WHAT FAILS IS WITHHELD",
        [("DELETION TEST", "~42% brain, ~44% skin findings pass"),
         ("THE REST", "withheld, and shown as withheld"),
         ("LEAKAGE AUDIT", "71% of an “external” set were duplicates"),
         ("SCOPE", "X-ray, MRI, dermoscopy; notes with spans")],
        ["LIVE", "SOURCE", "HACKATHON TEAM BUILD"], "DECISION SUPPORT ONLY · NOT A MEDICAL DEVICE")
    cx, cy, R = mx, H / 2 + 4, 150
    period, step = 12.0, 1.0
    labels = ["IT POINTS", "IT MATTERS", "STABLE ×8", "CALIBRATED", "SECOND READER", "NOTES TESTIFY",
              "REPORT CAN'T LIE", "RECEIPT"]
    d_svg, d_defs = dial(p, cx, cy, R, f"{uid}g", ticks=48, lobes=16)
    defs += d_defs + (f'<radialGradient id="{uid}ruby" cx=".35" cy=".35" r=".7"><stop offset="0" stop-color="#f06a86"/>'
                      f'<stop offset=".5" stop-color="{p["ruby"]}"/><stop offset="1" stop-color="#4a0b19"/></radialGradient>')
    style = ""
    mech = d_svg
    for i, lab in enumerate(labels):
        a = math.radians(-90 + i * 45)
        jx, jy = cx + 118 * math.cos(a), cy + 118 * math.sin(a)
        lx, ly = cx + (R + 18) * math.cos(a), cy + (R + 18) * math.sin(a)
        anchor = "middle" if abs(math.cos(a)) < 0.3 else ("start" if math.cos(a) > 0 else "end")
        on = 0.6 + i * step
        style += window(f"st{i}", period, on, period - 0.8) + f".st{i}{{animation:st{i} {period}s infinite}}"
        mech += (f'<circle cx="{f(jx)}" cy="{f(jy)}" r="10" fill="{p["steel_dim"]}"/>'
                 f'<circle cx="{f(jx)}" cy="{f(jy)}" r="6.4" fill="url(#{uid}ruby)"/>'
                 f'<circle class="st{i}" cx="{f(jx)}" cy="{f(jy)}" r="13.5" fill="none" stroke="{p["lume"]}" stroke-width="1.6"/>'
                 + kit.txt(f"{i + 1} {lab}", "martian-light", 7.4, lx, ly + 3, p["ink_dim"], 0.2, anchor))
    # hand A visits all eight; hand B stops at the deletion test
    a_frames = "".join(f"{100 * (0.6 + i * step) / period:.2f}%,{100 * (0.6 + i * step + 0.7) / period:.2f}%"
                       f"{{transform:rotate({i * 45}deg)}}" for i in range(8))
    style += (f".ha{{transform-origin:{f(cx)}px {f(cy)}px;animation:ha {period}s cubic-bezier(.6,0,.3,1) infinite}}"
              f"@keyframes ha{{0%{{transform:rotate(-10deg)}}{a_frames}96%{{transform:rotate(315deg)}}100%{{transform:rotate(350deg)}}}}"
              f".hb{{transform-origin:{f(cx)}px {f(cy)}px;animation:hb {period}s cubic-bezier(.6,0,.3,1) infinite}}"
              f"@keyframes hb{{0%{{transform:rotate(-20deg)}}{100 * 0.6 / period:.2f}%,{100 * 1.3 / period:.2f}%{{transform:rotate(0deg)}}"
              f"{100 * 1.6 / period:.2f}%{{transform:rotate(45deg)}}{100 * 1.9 / period:.2f}%{{transform:rotate(39deg)}}"
              f"{100 * 2.1 / period:.2f}%,92%{{transform:rotate(45deg)}}100%{{transform:rotate(340deg)}}}}")
    style += window("wh", period, 2.1, period - 0.8, "opacity:0", "opacity:1") + ".wh{animation:wh 12s infinite}"
    style += window("ok", period, 8.4, period - 0.8, "opacity:0", "opacity:1") + ".ok{animation:ok 12s infinite}"
    mech += (f'<g class="hb">{hand(p, cx, cy, 86, p["copper"], 2.4)}'
             + kit.txt("B", "martian", 8, cx + 7, cy - 70, p["copper"], 0.2) + "</g>"
             f'<g class="ha">{hand(p, cx, cy, 104, blued(p), 2.6)}'
             + kit.txt("A", "martian", 8, cx + 7, cy - 92, blued(p), 0.2) + "</g>"
             f'<circle cx="{f(cx)}" cy="{f(cy)}" r="3" fill="{p["silver"] if p["name"] == "dark" else "#3a3e43"}"/>')
    mech += (f'<g class="wh">' + kit.txt("B · WITHHELD", "martian", 8.4, cx, cy + 46, p["copper"], 0.3, "middle")
             + kit.txt("the heatmap was decoration", "bodoni-text-italic", 12, cx, cy + 62, p["ink_dim"], 0, "middle")
             + "</g>"
             + f'<g class="ok">' + kit.txt("A · 8 OF 8 · DOCTOR, CONSIDER", "martian", 7.6, cx, cy - 40, p["lume"], 0.26, "middle")
             + "</g>")
    body += mech
    desc = ("Plate two, Parallax: a certification dial with eight ruby jewels, one per check: it points, it matters, "
            "stable under eight perturbations, calibrated, a second reader, the notes testify, the report can't lie, "
            "a receipt. Hand A visits all eight and reaches 'Doctor, consider'. Hand B stops at the second jewel, the "
            "deletion test, and is withheld: the heatmap was decoration. About 42% of brain and 44% of skin findings "
            "pass the deletion test; the rest are withheld. A leakage audit found 71% of an external set were "
            "near-duplicates. Decision support only. Live, source public, hackathon team build.")
    return finish(p, uid, "Parallax: the eight-jewel certification", desc, style, defs, body)


# --- III. RECLAIM: the escapement --------------------------------------------------

def reclaim(p):
    uid = f"rc{p['name'][0]}"
    dark = p["name"] == "dark"
    body, defs, mx = frame(
        p, uid, "left", 3, "RCL·EV", "Reclaim", "Every recovery action has a price.",
        "ESCAPEMENT · EVERY RELEASE IS METERED",
        [("MODEL", "calibrated logistic regression"),
         ("DECISION", "expected value, with doing nothing allowed"),
         ("RESULT", "1.42× the net recovery of retrying all"),
         ("ROC-AUC", "0.69 · 574 automated tests, CI")],
        ["LIVE", "SOURCE"], "THE GAME FURTHER DOWN IS A TOY OF THIS MODEL")
    cy = H / 2 + 20
    E = (mx - 108, cy + 20)
    BAL = (mx + 112, cy + 20)
    PAL = (mx - 20, cy + 20)
    tick = 0.5
    defs += (f'<linearGradient id="{uid}w" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{p["silver"] if dark else "#8b9197"}"/>'
             f'<stop offset="1" stop-color="{p["steel_dim"] if dark else "#4f555b"}"/></linearGradient>'
             f'<radialGradient id="{uid}ruby" cx=".35" cy=".35" r=".7"><stop offset="0" stop-color="#f06a86"/>'
             f'<stop offset=".5" stop-color="{p["ruby"]}"/><stop offset="1" stop-color="#4a0b19"/></radialGradient>')
    bed_svg, bdefs = bed(p, uid, mx - 262, cy - 150, 560, 330, 30)
    defs += bdefs
    style = (f".esc{{transform-origin:{f(E[0])}px {f(E[1])}px;animation:esc {30 * tick}s steps(30,end) infinite;animation-delay:-{tick / 2}s}}"
             "@keyframes esc{to{transform:rotate(360deg)}}"
             f".bal{{transform-origin:{f(BAL[0])}px {f(BAL[1])}px;animation:bal {tick}s cubic-bezier(.45,0,.55,1) infinite alternate}}"
             "@keyframes bal{from{transform:rotate(-140deg)}to{transform:rotate(140deg)}}"
             f".spr{{transform-origin:{f(BAL[0])}px {f(BAL[1])}px;animation:spr {tick}s cubic-bezier(.45,0,.55,1) infinite alternate}}"
             "@keyframes spr{from{transform:rotate(-22deg) scale(.97)}to{transform:rotate(22deg) scale(1.03)}}"
             f".lev{{transform-origin:{f(PAL[0])}px {f(PAL[1])}px;animation:lev {2 * tick}s linear infinite}}"
             "@keyframes lev{0%,23%{transform:rotate(-7deg)}27%,73%{transform:rotate(7deg)}77%,100%{transform:rotate(-7deg)}}")
    bx, by = BAL
    screws = "".join(f'<circle cx="{f(bx + 92 * math.cos(a))}" cy="{f(by + 92 * math.sin(a))}" r="4" '
                     f'fill="{p["silver"] if dark else "#6c7177"}"/>' for a in [i * math.tau / 16 for i in range(16)])
    mech = (bed_svg
            + f'<g class="esc"><path d="{G.escape_wheel(E[0], E[1], 74, 15, 5)}" fill="url(#{uid}w)" fill-rule="evenodd"/></g>'
            + f'<g class="lev"><path d="{G.pallet_fork(PAL[0], PAL[1], 92, 0)}" fill="{p["steel"]}"/>'
              f'<circle cx="{f(PAL[0] - 33)}" cy="{f(PAL[1] - 35)}" r="4" fill="url(#{uid}ruby)"/>'
              f'<circle cx="{f(PAL[0] - 33)}" cy="{f(PAL[1] + 35)}" r="4" fill="url(#{uid}ruby)"/></g>'
            + f'<g class="spr"><path d="{G.hairspring(bx, by, 10, 64, 12, 40)}" fill="none" stroke="{p["blued"]}" stroke-width="1.1"/></g>'
            + f'<g class="bal"><path d="{G.circle(bx, by, 92)}{G.circle_ccw(bx, by, 84)}'
              f'M{f(bx - 86)},{f(by - 4)}H{f(bx + 86)}V{f(by + 4)}H{f(bx - 86)}Z{G.circle(bx, by, 10)}" '
              f'fill="url(#{uid}w)" fill-rule="evenodd"/>{screws}</g>'
            + f'<circle cx="{f(bx)}" cy="{f(by)}" r="5" fill="url(#{uid}ruby)"/>'
            + f'<circle cx="{f(E[0])}" cy="{f(E[1])}" r="5" fill="url(#{uid}ruby)"/>'
            + f'<circle cx="{f(PAL[0])}" cy="{f(PAL[1])}" r="4" fill="url(#{uid}ruby)"/>')
    # the decision: a three-position selector above the escapement
    sx, sy, sr = mx, cy - 118, 64
    positions = [("RECOVER", -150), ("ESCALATE", -90), ("LEAVE IT", -30)]
    mech += (f'<path d="{G.arc(sx, sy + 40, sr, math.radians(-160), math.radians(-20))}" fill="none" '
             f'stroke="{p["steel_dim"]}" stroke-width=".8"/>')
    for lab, deg in positions:
        a = math.radians(deg)
        mech += (f'<path d="M{G.pt(sx, sy + 40, sr - 6, a)}L{G.pt(sx, sy + 40, sr + 6, a)}" stroke="{p["steel"]}" stroke-width="1.4"/>'
                 + kit.txt(lab, "martian-light", 7.2, sx + (sr + 14) * math.cos(a), sy + 40 + (sr + 14) * math.sin(a) - 2,
                           p["ink_dim"], 0.22, "middle"))
    seq = [-150, -30, -90, -30, -150, -30]   # one decision per beat of the cases
    per = 2.0
    frames = "".join(f"{100 * i / len(seq):.2f}%,{100 * (i + 0.8) / len(seq):.2f}%{{transform:rotate({deg + 90}deg)}}"
                     for i, deg in enumerate(seq))
    style += (f".sel{{transform-origin:{f(sx)}px {f(sy + 40)}px;animation:sel {per * len(seq)}s cubic-bezier(.7,0,.2,1) infinite}}"
              f"@keyframes sel{{{frames}100%{{transform:rotate({seq[0] + 90}deg)}}}}")
    mech += (f'<g class="sel"><path d="M{f(sx)},{f(sy + 46)}L{f(sx)},{f(sy + 40 - sr + 10)}" stroke="{blued(p)}" '
             f'stroke-width="2.4" stroke-linecap="round"/></g>'
             f'<circle cx="{f(sx)}" cy="{f(sy + 40)}" r="4.5" fill="{blued(p)}"/>')
    body += mech
    desc = ("Plate three, Reclaim: a Swiss lever escapement, the escape wheel ticking under the pallet lever as the "
            "balance swings, with a three-position selector above it moving between recover, escalate and leave it. "
            "A calibrated logistic regression and an expected-value decision in which doing nothing is allowed: "
            "1.42 times the net recovery of retrying every payment, 0.69 ROC-AUC, 574 automated tests with CI. Live, "
            "source public.")
    return finish(p, uid, "Reclaim: the escapement", desc, style, defs, body)


# --- IV. SCOPECOMPOSE: the differential ---------------------------------------------

def scopecompose(p):
    uid = f"sc{p['name'][0]}"
    dark = p["name"] == "dark"
    body, defs, mx = frame(
        p, uid, "right", 4, "SCP·DF", "ScopeCompose", "A rule and its exception are both true.",
        "DIFFERENTIAL · ONE INPUT, BOTH BRANCHES KEPT",
        [("FAILURE", "conflict-aware RAG deletes exceptions"),
         ("METHOD", "detect, recover the scope, compose"),
         ("METRIC", "Suppression Rate measures the deletion"),
         ("STATUS", "pipeline built, 501 tests; no results yet")],
        ["SOURCE", "FINAL-YEAR RESEARCH · TWO MEMBERS"], "RESEARCH IN PROGRESS")
    cx, cy = mx - 30, H / 2 + 10
    m = 2.6
    Ns, Np, Nr = 24, 24, 72
    rs, rp, rr = m * Ns / 2, m * Np / 2, m * Nr / 2
    a_dist = rs + rp
    defs += (f'<linearGradient id="{uid}w" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{p["silver"] if dark else "#8b9197"}"/>'
             f'<stop offset="1" stop-color="{p["steel_dim"] if dark else "#4f555b"}"/></linearGradient>')
    # Willis: (ws - wc)/(wr - wc) = -Nr/Ns. Carrier is the input; sun and ring both turn.
    wc, wr = 1.0, 0.5
    ws = wc - (Nr / Ns) * (wr - wc)
    wp_rel = -(Ns / Np) * (ws - wc)          # planet spin relative to the carrier
    base = 40.0                              # seconds per carrier turn
    dur = lambda w: base / abs(w)            # noqa: E731
    sgn = lambda w: "" if w > 0 else "-"     # noqa: E731
    style = (f".car{{transform-origin:{f(cx)}px {f(cy)}px;animation:car {dur(wc):.1f}s linear infinite}}"
             "@keyframes car{to{transform:rotate(360deg)}}"
             f".sun{{transform-origin:{f(cx)}px {f(cy)}px;animation:sun {dur(ws):.1f}s linear infinite}}"
             f"@keyframes sun{{to{{transform:rotate({sgn(ws)}360deg)}}}}"
             f".ring{{transform-origin:{f(cx)}px {f(cy)}px;animation:ring {dur(wr):.1f}s linear infinite}}"
             f"@keyframes ring{{to{{transform:rotate({sgn(wr)}360deg)}}}}")
    sun = G.teeth_outline(cx, cy, Ns, m) + G.circle_ccw(cx, cy, rs * 0.42) + G.crossings(cx, cy, rs * 0.42, 6, 4, 4, .2) + G.circle(cx, cy, 6)
    ring = G.circle(cx, cy, rr + 18) + G.internal_teeth_outline(cx, cy, Nr, m)
    planets = ""
    for k in range(3):
        th = k * 120 - 90
        px, py = cx + a_dist * math.cos(math.radians(th)), cy + a_dist * math.sin(math.radians(th))
        rot = G.mesh_phase(th, 0, Ns, Np)
        style += (f".pl{k}{{transform-origin:{f(px)}px {f(py)}px;animation:pl{k} {dur(wp_rel):.1f}s linear infinite}}"
                  f"@keyframes pl{k}{{to{{transform:rotate({sgn(wp_rel)}360deg)}}}}")
        planets += (f'<g class="pl{k}"><g transform="rotate({f(rot)} {f(px)} {f(py)})">'
                    f'<path d="{G.wheel(px, py, Np, m, arms=3)}" fill="url(#{uid}w)" fill-rule="evenodd"/></g></g>'
                    f'<circle cx="{f(px)}" cy="{f(py)}" r="4" fill="{p["ruby"]}"/>')
    carrier = "".join(f'<path d="M{f(cx)},{f(cy)}L{G.pt(cx, cy, a_dist, math.radians(k * 120 - 90))}" '
                      f'stroke="{p["steel_faint"] if dark else p["steel_dim"]}" stroke-width="7" stroke-linecap="round"/>'
                      for k in range(3))
    ring_phase = (180 / Nr)
    mech = (f'<g class="ring"><g transform="rotate({f(ring_phase)} {f(cx)} {f(cy)})">'
            f'<path d="{ring}" fill="url(#{uid}w)" fill-rule="evenodd"/>'
            f'<path d="{G.ticks(cx, cy, rr + 16, 6, 72, .6)}" stroke="{p["case"]}" stroke-width=".8" opacity=".6"/></g></g>'
            f'<g class="sun"><path d="{sun}" fill="url(#{uid}w)" fill-rule="evenodd"/></g>'
            f'<g class="car">{carrier}{planets}</g>'
            f'<circle cx="{f(cx)}" cy="{f(cy)}" r="5" fill="{blued(p)}"/>')
    # the two outputs, both turning, both kept
    out_y1, out_y2 = cy - 70, cy + 70
    lx = cx + rr + 34
    style += ".flow{stroke-dasharray:3 6;animation:march 1.2s linear infinite}@keyframes march{to{stroke-dashoffset:-18}}"
    mech += (f'<path class="flow" d="M{f(cx + rs + 4)},{f(cy - 8)}C{f(cx + 80)},{f(cy - 40)} {f(lx - 40)},{f(out_y1)} {f(lx)},{f(out_y1)}" '
             f'fill="none" stroke="{blued(p)}" stroke-width="1.4"/>'
             f'<path class="flow" d="M{f(cx + rr + 18)},{f(cy + 30)}C{f(lx - 10)},{f(cy + 40)} {f(lx - 30)},{f(out_y2)} {f(lx)},{f(out_y2)}" '
             f'fill="none" stroke="{p["copper"]}" stroke-width="1.4"/>'
             f'<circle class="lume" cx="{f(lx + 6)}" cy="{f(out_y1)}" r="3.2" fill="{p["lume"]}"/>'
             f'<circle class="lume" cx="{f(lx + 6)}" cy="{f(out_y2)}" r="3.2" fill="{p["lume"]}" style="animation-delay:-2s"/>'
             + kit.txt("SUN · GENERAL RULE", "martian-light", 7.4, lx + 16, out_y1 - 6, p["ink_dim"], 0.22)
             + kit.txt("3% fee on international", "bodoni-text-italic", 13.5, lx + 16, out_y1 + 12, p["ink"])
             + kit.txt("RING · EXCEPTION", "martian-light", 7.4, lx + 16, out_y2 - 6, p["ink_dim"], 0.22)
             + kit.txt("waived for premium-tier", "bodoni-text-italic", 13.5, lx + 16, out_y2 + 12, p["ink"])
             + kit.txt("CARRIER · THE QUERY", "martian-light", 7.4, cx, cy + rr + 46, p["ink_dim"], 0.22, "middle")
             + kit.txt("A SELECTOR KEEPS ONE BRANCH. A DIFFERENTIAL KEEPS BOTH.", "martian-light", 7.4, cx + 40,
                       cy - rr - 40, p["salmon"] if dark else p["copper"], 0.22, "middle"))
    body += mech
    desc = ("Plate four, ScopeCompose: a planetary differential. The carrier, the query, drives three planets; the sun "
            "and the ring both turn, one carrying the general rule (a 3% fee on international transactions), the other "
            "the exception (waived for premium-tier cardholders). A selector keeps one branch; a differential keeps both. "
            "Conflict-aware RAG deletes valid exceptions; ScopeCompose detects the conflict, recovers its scope and "
            "composes both, with Suppression Rate to measure the deletion. Final-year research, two members: pipeline "
            "built with 501 tests, no results yet.")
    return finish(p, uid, "ScopeCompose: the differential", desc, style, defs, body)


# --- V. PRISM: rack and decile gauges ---------------------------------------------

def prism(p):
    uid = f"pr{p['name'][0]}"
    dark = p["name"] == "dark"
    body, defs, mx = frame(
        p, uid, "left", 5, "PRS·10", "Prism", "Same law, same conclusions?",
        "RACK AND TEN DECILE GAUGES · TRACED TO THE CLAUSE",
        [("READS", "Indian statutes into a legal AST"),
         ("EXTRACTS", "rules grounded to exact spans"),
         ("SIMULATES", "a population matching official ITR data"),
         ("TRACES", "each divergence to its clause")],
        ["SOURCE"], "ILLUSTRATIVE DIVERGENCE · NOT A REPORTED RESULT")
    cy = H / 2
    expert = [0, 0, 0, 0, 0, 0, 0.6, 2.1, 4.8, 11.5]
    llm = [0, 0, 0, 0, 1.4, 2.6, 3.1, 2.1, 4.8, 11.5]
    period = 12.0
    style = (".rack{animation:rack 6s ease-in-out infinite alternate}@keyframes rack{from{transform:translateX(-18px)}to{transform:translateX(18px)}}")
    x0, x1 = mx - 256, mx + 270
    defs += (f'<linearGradient id="{uid}w" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{p["silver"] if dark else "#8b9197"}"/>'
             f'<stop offset="1" stop-color="{p["steel_dim"] if dark else "#4f555b"}"/></linearGradient>')
    # the clause plaque
    mech = (f'<rect x="{f(x0)}" y="{f(cy - 178)}" width="{f(x1 - x0)}" height="56" rx="8" fill="{p["plate"]}" stroke="{p["steel_dim"]}" stroke-width=".7"/>'
            + kit.txt("S.87A · REBATE (PARAPHRASED)", "martian-light", 7.4, x0 + 16, cy - 158, p["ink_dim"], 0.24)
            + kit.txt("a resident with income up to ₹7,00,000 gets a rebate of up to", "bodoni-text-italic", 13.5,
                      x0 + 16, cy - 136, p["ink"]))
    hl_x = x0 + 16 + kit.width("a resident with income up to ₹7,00,000 gets a rebate of up to ", "bodoni-text-italic", 13.5)
    mech += kit.txt("₹25,000", "bodoni-text-italic", 13.5, hl_x, cy - 136, p["copper"])
    hl_w = kit.width("₹25,000", "bodoni-text-italic", 13.5)
    style += window("hl", period, 6.0, period - 0.8, "opacity:0", "opacity:1") + ".hl{animation:hl 12s infinite}"
    mech += f'<path class="hl" d="M{f(hl_x)},{f(cy - 131)}h{f(hl_w)}" stroke="{p["copper"]}" stroke-width="1.4"/>'
    # the rack, reading the statute
    mech += (f'<g class="rack"><path d="{G.rack(x0 - 20, x1 + 20, cy - 92, 2.4, 12)}" fill="url(#{uid}w)"/></g>'
             f'<path d="M{f(x0)},{f(cy - 74)}H{f(x1)}" stroke="{p["steel_faint"]}" stroke-width=".6"/>')
    gap = (x1 - x0) / 10
    gr = 22
    for i, (e, l) in enumerate(zip(expert, llm)):
        gx = x0 + gap * (i + 0.5)
        gy = cy + 30
        ang = lambda v: -120 + v / 12 * 240  # noqa: E731
        diverge = abs(e - l) > 0.3
        mech += (f'<circle cx="{f(gx)}" cy="{f(gy)}" r="{gr}" fill="{p["plate"]}" stroke="{p["steel"]}" stroke-width=".9"/>'
                 f'<path d="{G.ticks(gx, gy, gr - 3, 3, 24, .4, 0)}" stroke="{p["steel_dim"]}" stroke-width=".5"/>'
                 + kit.txt(str(i + 1), "martian-light", 7, gx, gy + gr + 14, p["ink_dim"], 0.2, "middle"))
        for who, v, col, w, ln in (("e", e, blued(p), 1.8, gr - 5), ("l", l, p["copper"], 1.4, gr - 8)):
            k = f"n{who}{i}"
            style += (f".{k}{{transform-origin:{f(gx)}px {f(gy)}px;animation:{k} {period}s cubic-bezier(.3,.7,.3,1) infinite}}"
                      f"@keyframes {k}{{0%,{100 * 1.5 / period:.1f}%{{transform:rotate(-120deg)}}"
                      f"{100 * (3 + i * 0.12) / period:.1f}%,92%{{transform:rotate({ang(v):.1f}deg)}}100%{{transform:rotate(-120deg)}}}}")
            mech += (f'<g class="{k}"><path d="M{f(gx)},{f(gy + 3)}L{f(gx)},{f(gy - ln)}" stroke="{col}" '
                     f'stroke-width="{w}" stroke-linecap="round"/></g>')
        mech += f'<circle cx="{f(gx)}" cy="{f(gy)}" r="2.2" fill="{p["silver"] if dark else "#3a3e43"}"/>'
        if diverge:
            mech += f'<circle class="hl" cx="{f(gx)}" cy="{f(gy)}" r="{gr + 5}" fill="none" stroke="{p["lume"]}" stroke-width="1.2"/>'
    # the trace, from the diverging gauges back to the words
    g6 = x0 + gap * 5.5
    style += ".tr{stroke-dasharray:420;stroke-dashoffset:420;animation:tr 12s ease-in-out infinite}@keyframes tr{0%,52%{stroke-dashoffset:420}68%,92%{stroke-dashoffset:0;opacity:1}100%{opacity:0;stroke-dashoffset:0}}"
    mech += (f'<path class="tr" d="M{f(g6)},{f(cy + 60)}C{f(g6)},{f(cy + 140)} {f(x1 + 10)},{f(cy + 130)} {f(x1 + 10)},{f(cy - 60)}'
             f'S{f(hl_x + hl_w + 30)},{f(cy - 120)} {f(hl_x + hl_w / 2)},{f(cy - 128)}" fill="none" stroke="{p["copper"]}" stroke-width="1.2"/>')
    mech += (kit.txt("EFFECTIVE RATE BY INCOME DECILE", "martian-light", 7.4, x0, cy + 92, p["ink_dim"], 0.24)
             + f'<circle cx="{f(x0 + 4)}" cy="{f(cy + 108)}" r="3" fill="{blued(p)}"/>'
             + kit.txt("EXPERT CODING", "martian-light", 7.4, x0 + 14, cy + 111, p["ink_dim"], 0.22)
             + f'<circle cx="{f(x0 + 134)}" cy="{f(cy + 108)}" r="3" fill="{p["copper"]}"/>'
             + kit.txt("LLM EXTRACTION", "martian-light", 7.4, x0 + 144, cy + 111, p["ink_dim"], 0.22)
             + f'<g class="hl">' + kit.txt("DECILES 5–7 DIVERGE → “₹25,000”", "martian", 7.6, x0, cy + 134, p["copper"], 0.24)
             + "</g>")
    body += mech
    desc = ("Plate five, Prism, illustrative and not a reported result: a rack reads a paraphrased section 87A rebate "
            "clause and drives ten income-decile gauges, each with an expert-coding needle and an LLM-extraction needle. "
            "They agree except in deciles 5 to 7, and a trace runs from those gauges back to the words '₹25,000' in the "
            "clause. Prism parses Indian statutes into a legal AST, extracts rules grounded to exact spans, simulates "
            "them on a population matching official Income Tax Return statistics, and traces each divergence to its clause.")
    return finish(p, uid, "Prism: rack and decile gauges", desc, style, defs, body)


# --- VI. ASSETSTREAM: the power reserve ----------------------------------------------

def assetstream(p):
    uid = f"as{p['name'][0]}"
    body, defs, mx = frame(
        p, uid, "right", 6, "AST·PR", "AssetStream", "Price the machine before it retires.",
        "POWER RESERVE · AGE ALONE AGAINST TELEMETRY",
        [("BILLING", "Django, Celery and Redis, from IoT usage"),
         ("RESALE", "a scikit-learn model prices remarketing"),
         ("FRONT", "Next.js and TypeScript, Groq LLM"),
         ("SHIP", "fully Dockerized")],
        ["LIVE", "SOURCE"], "CURVES ILLUSTRATIVE")
    cx, cy, R = mx, H / 2 + 52, 176
    a0, a1 = -210, 30     # the reserve arc, degrees
    period = 10.0
    mech = (f'<path d="{G.arc(cx, cy, R, math.radians(a0), math.radians(a1))}" fill="none" stroke="{p["steel"]}" stroke-width="1.4"/>'
            f'<path d="{G.arc(cx, cy, R - 10, math.radians(a0), math.radians(a1))}" fill="none" stroke="{p["steel_faint"]}" stroke-width="10"/>')
    for i in range(41):
        a = math.radians(a0 + (a1 - a0) * i / 40)
        ln = 14 if i % 10 == 0 else 6
        mech += f'<path d="M{G.pt(cx, cy, R - 2, a)}L{G.pt(cx, cy, R - 2 - ln, a)}" stroke="{p["steel_dim"]}" stroke-width="{1.4 if ln > 6 else .6}"/>'
        if i % 10 == 0:
            mech += kit.txt(f"{100 - i * 100 // 40}", "martian-light", 8, cx + (R - 34) * math.cos(a),
                            cy + (R - 34) * math.sin(a) + 3, p["ink_dim"], 0.1, "middle")
    mech += (kit.txt("RETAINED VALUE %", "martian-light", 7.4, cx, cy - R - 18, p["ink_dim"], 0.24, "middle")
             + kit.txt("NEW", "martian", 7.4, cx + R * math.cos(math.radians(a0)) - 6, cy + R * math.sin(math.radians(a0)) + 20, p["ink_dim"], 0.24, "middle")
             + kit.txt("RETIRE", "martian", 7.4, cx + R * math.cos(math.radians(a1)) + 4, cy + R * math.sin(math.radians(a1)) + 20, p["ink_dim"], 0.24, "middle"))

    def ang(v):  # value 100..0 -> angle
        return a0 + (a1 - a0) * (100 - v) / 100

    style = ""
    for k, end, col, w, ln in (("sl", 22, p["steel"], 2.0, R - 30), ("tm", 38, blued(p), 2.8, R - 22)):
        style += (f".{k}{{transform-origin:{f(cx)}px {f(cy)}px;animation:{k} {period}s cubic-bezier(.4,0,.3,1) infinite}}"
                  f"@keyframes {k}{{0%,8%{{transform:rotate({ang(100) + 90:.1f}deg)}}70%,92%{{transform:rotate({ang(end) + 90:.1f}deg)}}"
                  f"100%{{transform:rotate({ang(100) + 90:.1f}deg)}}}}")
        mech += (f'<g class="{k}"><path d="M{f(cx)},{f(cy + 14)}L{f(cx)},{f(cy - ln)}" stroke="{col}" stroke-width="{w}" '
                 f'stroke-linecap="round"/></g>')
    mech += f'<circle cx="{f(cx)}" cy="{f(cy)}" r="6" fill="{blued(p)}"/>'
    style += window("lab", period, 7.0, period - 0.8, "opacity:0", "opacity:1") + ".lab{animation:lab 10s infinite}"
    mech += (f'<g class="lab">' + kit.txt("TELEMETRY · 38", "martian", 7.6, cx + 76, cy - 112, blued(p), 0.22)
             + kit.txt("AGE ONLY · 22", "martian", 7.6, cx + 112, cy - 40, p["ink_dim"], 0.22) + "</g>")
    # the billing cycle: a small seconds-style sub-dial that never stops
    sx, sy, sr = cx, cy + 62, 34
    d_svg, d_defs = dial(p, sx, sy, sr, f"{uid}g", ticks=30, lobes=8)
    defs += d_defs
    style += f".bc{{transform-origin:{f(sx)}px {f(sy)}px;animation:bc 6s steps(30,end) infinite}}@keyframes bc{{to{{transform:rotate(360deg)}}}}"
    mech += (d_svg + f'<g class="bc">{hand(p, sx, sy, sr - 8, p["copper"], 1.4)}</g>'
             + kit.txt("BILLING CYCLE", "martian-light", 7, sx, sy + sr + 14, p["ink_dim"], 0.24, "middle"))
    body += mech
    desc = ("Plate six, AssetStream, curves illustrative: a power-reserve gauge of retained value from new to retire. "
            "An age-only hand falls to 22 while the telemetry-informed hand stops at 38, and a billing-cycle sub-dial "
            "ticks below. Django, Celery and Redis turn IoT usage into invoices; a scikit-learn model prices resale; "
            "Next.js and TypeScript front end with a Groq LLM; fully Dockerized. Live, source public.")
    return finish(p, uid, "AssetStream: the power reserve", desc, style, defs, body)


# --- VII. COMPUTATIONAL ENTROPY LAB: twin oscillators -------------------------------

def entropy(p):
    uid = f"en{p['name'][0]}"
    body, defs, mx = frame(
        p, uid, "left", 7, "ENT·2X", "Entropy Lab", "Does an unstable prompt cost energy?",
        "TWIN OSCILLATORS · AN OPEN QUESTION",
        [("QUESTION", "instability vs inference energy"),
         ("PLATFORM", "FastAPI and React, for measuring it"),
         ("HONESTY", "synthetic data is flagged in the API"),
         ("STATUS", "a hypothesis under test, not a result")],
        ["SOURCE"], "THE TRACES ARE ILLUSTRATIONS")
    x0, x1 = mx - 262, mx + 190
    rows = [("LOW INSTABILITY", H / 2 - 70, 0.0), ("HIGH INSTABILITY", H / 2 + 60, 1.0)]
    style = ""
    mech = ""
    import random
    rng = random.Random(7)
    for k, (lab, y, jag) in enumerate(rows):
        span, period = 120.0, 2 if jag else 3.4
        pts = []
        steps = 240
        noise = [rng.uniform(-1, 1) for _ in range(steps)]
        noise.append(noise[0])  # so the tile joins itself
        for i in range(steps + 1):
            x = i * span * 4 / steps
            v = math.sin(i / steps * 4 * math.tau)
            if jag:
                v = 0.55 * v + 0.6 * noise[i] * (0.4 + 0.6 * abs(math.sin(i * math.tau * 9 / steps)))
            pts.append((x, v))
        # make it tile: blend the last stretch into the first
        d = "M" + "L".join(f"{f(x)},{f(-v * 36)}" for x, v in pts)
        clip = f"{uid}c{k}"
        defs += f'<clipPath id="{clip}"><rect x="{f(x0)}" y="{f(y - 50)}" width="{f(x1 - x0)}" height="100" rx="10"/></clipPath>'
        style += (f".tp{k}{{animation:tp{k} {period * 4}s linear infinite}}"
                  f"@keyframes tp{k}{{to{{transform:translateX(-{span * 4:g}px)}}}}")
        tile = f'<path d="{d}" fill="none" stroke="{p["lume"] if k == 0 else p["copper"]}" stroke-width="1.6"/>'
        mech += (f'<rect x="{f(x0)}" y="{f(y - 50)}" width="{f(x1 - x0)}" height="100" rx="10" fill="{p["plate"]}" stroke="{p["steel_dim"]}" stroke-width=".7"/>'
                 f'<g clip-path="url(#{clip})">'
                 + "".join(f'<path d="M{f(x0 + j * 40)},{f(y - 50)}V{f(y + 50)}" stroke="{p["steel_faint"]}" stroke-width=".5"/>'
                           for j in range(int((x1 - x0) / 40) + 1))
                 + f'<path d="M{f(x0)},{f(y)}H{f(x1)}" stroke="{p["steel_faint"]}" stroke-width=".6"/>'
                 + f'<g transform="translate({f(x0)} {f(y)})"><g class="tp{k}">{tile}'
                   f'<g transform="translate({f(span * 4)} 0)">{tile}</g></g></g></g>'
                 + kit.txt(lab, "martian-light", 7.4, x0, y - 58, p["ink_dim"], 0.24))
        # an energy gauge beside each trace, its needle uncertain
        gx, gy = x1 + 56, y
        mech += (f'<circle cx="{f(gx)}" cy="{f(gy)}" r="34" fill="{p["plate"]}" stroke="{p["steel"]}"/>'
                 f'<path d="{G.ticks(gx, gy, 30, 4, 20, .5)}" stroke="{p["steel_dim"]}" stroke-width=".6"/>'
                 + kit.txt("ENERGY", "martian-light", 6.4, gx, gy + 20, p["ink_dim"], 0.22, "middle"))
        lo, hi = (-60, -30) if k == 0 else (-20, 60)
        style += (f".eg{k}{{transform-origin:{f(gx)}px {f(gy)}px;animation:eg{k} 3.2s ease-in-out infinite alternate}}"
                  f"@keyframes eg{k}{{from{{transform:rotate({lo}deg)}}to{{transform:rotate({hi}deg)}}}}")
        mech += f'<g class="eg{k}">{hand(p, gx, gy, 24, blued(p), 1.6)}</g>'
    mech += kit.txt("?", "bodoni-display", 44, x1 + 56, H / 2 + 12, p["salmon"], 0, "middle")
    body += mech
    desc = ("Plate seven, Computational Entropy Lab, traces illustrative: two oscillator traces scroll side by side, "
            "a smooth low-instability prompt signal and a jagged high-instability one, each beside an energy gauge whose "
            "needle wanders, with a question mark between them. The open question: does semantic instability in a prompt "
            "cost inference energy? A FastAPI and React research platform; synthetic demo data is flagged in the API.")
    return finish(p, uid, "Entropy Lab: twin oscillators", desc, style, defs, body)


PLATES = {"01-evora": evora, "02-parallax": parallax, "03-reclaim": reclaim, "04-scopecompose": scopecompose,
          "05-prism": prism, "06-assetstream": assetstream, "07-entropy": entropy}


def main() -> None:
    for key, fn in PLATES.items():
        for p in THEMES:
            out = kit.write(f"plates/{key}-{p['name']}.svg", fn(p))
        print(f"{key}: {out.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
