"""The header: an open-caseback movement beside the name, in both finishes.

The gear train is real gearing: each wheel drives the next arbor's pinion, the
centre distances are module*(N+n)/2, and every arbor turns at the ratio its
teeth dictate. The escape wheel ticks once per balance swing, the lever snaps
at each crossing, and everything upstream turns slower and slower, as it does
in a watch.
"""

from __future__ import annotations

import math

import geom as G
import kit
from palette import THEMES

W, H = 1200, 560
C = (928.0, 282.0)          # movement centre
R_MOV = 214.0               # movement radius
MOD = 2.0                   # module of the train
TICK = 0.4                  # seconds per beat (9,000 vph: slow enough to watch)
SWING = 135                 # balance amplitude, degrees


def polar(origin, dist, deg):
    a = math.radians(deg)
    return (origin[0] + dist * math.cos(a), origin[1] + dist * math.sin(a))


def capsule(p, q, r):
    """A stadium from p to q with radius r (a bridge arm)."""
    ang = math.atan2(q[1] - p[1], q[0] - p[0])
    nx, ny = -math.sin(ang) * r, math.cos(ang) * r
    a1 = (p[0] + nx, p[1] + ny)
    a2 = (q[0] + nx, q[1] + ny)
    b2 = (q[0] - nx, q[1] - ny)
    b1 = (p[0] - nx, p[1] - ny)
    f = G.n
    return (f"M{f(a1[0])},{f(a1[1])}L{f(a2[0])},{f(a2[1])}A{f(r)},{f(r)} 0 0 0 {f(b2[0])},{f(b2[1])}"
            f"L{f(b1[0])},{f(b1[1])}A{f(r)},{f(r)} 0 0 0 {f(a1[0])},{f(a1[1])}Z")


def train():
    """Arbor positions, tooth counts, starting phases and beats per revolution."""
    E = polar(C, 92, 18)                     # escape arbor
    F = polar(E, G.centre_distance(56, 8, MOD), -78)   # fourth wheel meshes the escape pinion
    T = polar(F, G.centre_distance(56, 8, MOD), -168)  # third wheel meshes the fourth pinion
    # the centre wheel (64) meshes the third pinion (8): place it on the far side of T
    Cn = polar(T, G.centre_distance(64, 8, MOD), 128)
    Bb = polar(Cn, G.centre_distance(80, 10, MOD), 150)  # barrel (80) meshes the centre pinion (10)

    def ang(a, b):
        return math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))

    rot = {"esc": 0.0}
    rot["fourth"] = G.mesh_phase(ang(E, F), rot["esc"], 8, 56)
    rot["third"] = G.mesh_phase(ang(F, T), rot["fourth"], 8, 56)
    rot["centre"] = G.mesh_phase(ang(T, Cn), rot["third"], 8, 64)
    rot["barrel"] = G.mesh_phase(ang(Cn, Bb), rot["centre"], 10, 80)
    # beats per revolution: the escape wheel turns 360/30 = 12 degrees per beat
    beats = {"esc": 30}
    beats["fourth"] = beats["esc"] * 56 / 8
    beats["third"] = beats["fourth"] * 56 / 8
    beats["centre"] = beats["third"] * 64 / 8
    beats["barrel"] = beats["centre"] * 80 / 10
    return {"E": E, "F": F, "T": T, "C": Cn, "B": Bb}, rot, beats


def build(p: dict) -> str:
    uid = f"hdr{p['name'][0]}"
    pos, rot, beats = train()
    E, F, T, Cn, Bb = pos["E"], pos["F"], pos["T"], pos["C"], pos["B"]
    BAL = polar(C, 140, 55)                  # balance, lower right, beside the escapement
    PAL = (E[0] + (BAL[0] - E[0]) * 0.45, E[1] + (BAL[1] - E[1]) * 0.45)
    pal_ang = math.atan2(BAL[1] - PAL[1], BAL[0] - PAL[0])
    f = G.n
    dark = p["name"] == "dark"

    # --- styles ---------------------------------------------------------------------
    def spin(name, beats_rev, direction, stepped):
        dur = beats_rev * TICK
        timing = f"steps({int(round(beats_rev))}, end)" if stepped else "linear"
        sign = "" if direction > 0 else "-"
        return (f".{name}{{animation:{name} {dur:.1f}s {timing} infinite;animation-delay:-{TICK / 2:.2f}s}}"
                f"@keyframes {name}{{to{{transform:rotate({sign}360deg)}}}}")

    style = (
        spin("w-esc", beats["esc"], 1, True) + spin("w-fourth", beats["fourth"], -1, True)
        + spin("w-third", beats["third"], 1, False) + spin("w-centre", beats["centre"], -1, False)
        + spin("w-barrel", beats["barrel"], 1, False)
        + f".bal{{animation:bal {TICK}s cubic-bezier(.45,0,.55,1) infinite alternate}}"
          f"@keyframes bal{{from{{transform:rotate(-{SWING}deg)}}to{{transform:rotate({SWING}deg)}}}}"
        + f".spring{{animation:spring {TICK}s cubic-bezier(.45,0,.55,1) infinite alternate}}"
          f"@keyframes spring{{from{{transform:rotate(-24deg) scale(.97)}}to{{transform:rotate(24deg) scale(1.03)}}}}"
        + f".lever{{animation:lever {2 * TICK}s linear infinite}}"
          "@keyframes lever{0%,23%{transform:rotate(-8deg)}27%,73%{transform:rotate(8deg)}77%,100%{transform:rotate(-8deg)}}"
        + ".g1{animation:g1 240s linear infinite}@keyframes g1{to{transform:rotate(360deg)}}"
          ".g2{animation:g2 300s linear infinite}@keyframes g2{to{transform:rotate(-360deg)}}"
        + ".sweep{animation:sweep 9s cubic-bezier(.5,0,.3,1) infinite}"
          "@keyframes sweep{0%,62%{transform:translateX(0)}86%,100%{transform:translateX(1020px)}}"
        + ".lume{animation:lume 6s ease-in-out infinite}@keyframes lume{0%,100%{opacity:.45}50%{opacity:1}}"
        + ".rise{animation:rise 1.4s cubic-bezier(.2,.7,.2,1) both}"
          "@keyframes rise{from{transform:translateY(8px)}to{transform:none}}"
        + ".draw{stroke-dasharray:1;animation:draw 2.4s cubic-bezier(.6,0,.2,1) .3s both}"
          "@keyframes draw{from{stroke-dashoffset:1}to{stroke-dashoffset:0}}"
    )

    def origin(pt):
        return f'style="transform-origin:{f(pt[0])}px {f(pt[1])}px"'

    # --- defs -----------------------------------------------------------------------
    gl1_defs, gl1 = G.guilloche(f"{uid}r1", 330, 286, 236, 9, 18, 10, p["steel"], 0.6, 0.12 if dark else 0.16, "g1")
    gl2_defs, gl2 = G.guilloche(f"{uid}r2", 330, 286, 236, 9, 18, 10, p["steel"], 0.6, 0.07 if dark else 0.12, "g2")
    gl3_defs, gl3 = G.guilloche(f"{uid}r3", 330, 286, 150, 6, 30, 6, p["steel"], 0.5, 0.06 if dark else 0.1, "g2")
    mov_clip = G.circle(C[0], C[1], R_MOV)
    name_s, name_size, name_track = "FEBIN K RENU", 82, 0.045
    name_w = kit.width(name_s, "bodoni-display", name_size, name_track)
    if name_w > 560:
        name_size *= 560 / name_w
        name_w = 560
    name_d = kit.T.text(name_s, "bodoni-display", name_size, 64, 236, name_track)[0]

    defs = (
        gl1_defs + gl2_defs + gl3_defs
        + f'<clipPath id="{uid}mov"><path d="{mov_clip}"/></clipPath>'
        + f'<clipPath id="{uid}name"><path d="{name_d}"/></clipPath>'
        + f'<pattern id="{uid}perl" width="12" height="10.4" patternUnits="userSpaceOnUse">'
          f'<circle cx="6" cy="5.2" r="5.6" fill="none" stroke="{p["perlage"]}" stroke-width=".8"/>'
          f'<circle cx="0" cy="0" r="5.6" fill="none" stroke="{p["perlage"]}" stroke-width=".8"/>'
          f'<circle cx="12" cy="0" r="5.6" fill="none" stroke="{p["perlage"]}" stroke-width=".8"/>'
          f'<circle cx="0" cy="10.4" r="5.6" fill="none" stroke="{p["perlage"]}" stroke-width=".8"/>'
          f'<circle cx="12" cy="10.4" r="5.6" fill="none" stroke="{p["perlage"]}" stroke-width=".8"/></pattern>'
        + f'<linearGradient id="{uid}stripe" x1="0" y1="0" x2="1" y2="0">'
          f'<stop offset="0" stop-color="{p["case_hi"]}"/><stop offset=".5" stop-color="{p["steel_faint"] if dark else "#f4f3ef"}"/>'
          f'<stop offset="1" stop-color="{p["case_hi"]}"/></linearGradient>'
        + f'<pattern id="{uid}geneva" width="18" height="18" patternUnits="userSpaceOnUse" patternTransform="rotate(-32)">'
          f'<rect width="18" height="18" fill="url(#{uid}stripe)"/></pattern>'
        + f'<linearGradient id="{uid}wheel" x1="0" y1="0" x2="1" y2="1">'
          f'<stop offset="0" stop-color="{p["silver"] if dark else "#8b9197"}"/><stop offset=".55" stop-color="{p["steel"]}"/>'
          f'<stop offset="1" stop-color="{p["steel_dim"] if dark else "#4f555b"}"/></linearGradient>'
        + f'<radialGradient id="{uid}light" cx=".3" cy=".22" r=".9">'
          f'<stop offset="0" stop-color="#ffffff" stop-opacity="{".09" if dark else ".35"}"/>'
          f'<stop offset=".6" stop-color="#ffffff" stop-opacity="0"/></radialGradient>'
        + f'<radialGradient id="{uid}vig" cx=".72" cy=".5" r=".75">'
          f'<stop offset="0" stop-color="{p["case_hi"]}"/><stop offset="1" stop-color="{p["case"]}"/></radialGradient>'
        + f'<linearGradient id="{uid}glint" x1="0" y1="0" x2="1" y2="0">'
          f'<stop offset="0" stop-color="{p["salmon"]}" stop-opacity="0"/>'
          f'<stop offset=".5" stop-color="{"#ffffff" if dark else p["salmon"]}" stop-opacity=".95"/>'
          f'<stop offset="1" stop-color="{p["salmon"]}" stop-opacity="0"/></linearGradient>'
        + f'<radialGradient id="{uid}ruby" cx=".35" cy=".35" r=".7">'
          f'<stop offset="0" stop-color="#f06a86"/><stop offset=".5" stop-color="{p["ruby"]}"/>'
          f'<stop offset="1" stop-color="#4a0b19"/></radialGradient>'
        + f'<radialGradient id="{uid}blue" cx=".35" cy=".3" r=".8">'
          f'<stop offset="0" stop-color="{p["blued_hi"]}"/><stop offset="1" stop-color="{p["blued"]}"/></radialGradient>'
    )

    # --- movement parts -------------------------------------------------------------
    wheel_fill = f'url(#{uid}wheel)'

    def arbor(key, centre, teeth, pinion, cls, arms=5):
        cx, cy = centre
        parts = G.wheel(cx, cy, teeth, MOD, arms=arms) if teeth else ""
        pin = G.teeth_outline(cx, cy, pinion, MOD) if pinion else ""
        return (f'<g class="{cls}" {origin(centre)}><g transform="rotate({f(rot[key])} {f(cx)} {f(cy)})">'
                f'<path d="{parts}" fill="{wheel_fill}" fill-rule="evenodd" stroke="{p["case"]}" stroke-width=".4"/>'
                f'<path d="{pin}" fill="{p["steel_dim"]}"/></g></g>')

    barrel = (f'<g class="w-barrel" {origin(Bb)}><g transform="rotate({f(rot["barrel"])} {f(Bb[0])} {f(Bb[1])})">'
              f'<path d="{G.teeth_outline(Bb[0], Bb[1], 80, MOD)}{G.circle_ccw(Bb[0], Bb[1], 72)}" '
              f'fill="{wheel_fill}" fill-rule="evenodd"/>'
              f'<circle cx="{f(Bb[0])}" cy="{f(Bb[1])}" r="72" fill="{p["plate"]}"/>'
              f'<path d="{G.ticks(Bb[0], Bb[1], 70, 4, 48, .6)}" stroke="{p["steel_faint"]}"/></g></g>')

    centre = arbor("centre", Cn, 64, 10, "w-centre", 4)
    third = arbor("third", T, 56, 8, "w-third", 5)
    fourth = arbor("fourth", F, 56, 8, "w-fourth", 5)
    esc = (f'<g class="w-esc" {origin(E)}>'
           f'<path d="{G.escape_wheel(E[0], E[1], 30)}" fill="{p["steel"]}" fill-rule="evenodd"/>'
           f'<path d="{G.teeth_outline(E[0], E[1], 8, MOD)}" fill="{p["steel_dim"]}"/></g>')
    lever = (f'<g class="lever" {origin(PAL)}>'
             f'<path d="{G.pallet_fork(PAL[0], PAL[1], 40, pal_ang)}" fill="{p["steel"]}"/>'
             f'<circle cx="{f(PAL[0] - 14.4 * math.cos(pal_ang) - 15.1 * math.sin(pal_ang))}" '
             f'cy="{f(PAL[1] - 14.4 * math.sin(pal_ang) + 15.1 * math.cos(pal_ang))}" r="2.2" fill="url(#{uid}ruby)"/>'
             f'<circle cx="{f(PAL[0] - 14.4 * math.cos(pal_ang) + 15.1 * math.sin(pal_ang))}" '
             f'cy="{f(PAL[1] - 14.4 * math.sin(pal_ang) - 15.1 * math.cos(pal_ang))}" r="2.2" fill="url(#{uid}ruby)"/></g>')

    bx, by = BAL
    rim = G.circle(bx, by, 50) + G.circle_ccw(bx, by, 45)
    arm = (f"M{f(bx - 46)},{f(by - 2.6)}L{f(bx + 46)},{f(by - 2.6)}L{f(bx + 46)},{f(by + 2.6)}"
           f"L{f(bx - 46)},{f(by + 2.6)}Z" + G.circle(bx, by, 6))
    screws = "".join(f'<circle cx="{f(bx + 50.5 * math.cos(a))}" cy="{f(by + 50.5 * math.sin(a))}" r="2.6" '
                     f'fill="{p["silver"] if dark else "#6c7177"}"/>'
                     for a in [i * math.tau / 12 for i in range(12)])
    balance = (f'<g class="spring" {origin(BAL)}><path d="{G.hairspring(bx, by, 7, 34, 11)}" fill="none" '
               f'stroke="{p["blued"]}" stroke-width=".9"/></g>'
               f'<g class="bal" {origin(BAL)}><path d="{rim}{arm}" fill="{wheel_fill}" fill-rule="evenodd"/>{screws}</g>')

    # bridges, as unions of rounded arms, with a cast shadow and polished bevel
    edge = lambda deg: polar(C, R_MOV - 8, deg)  # noqa: E731
    bridges = [
        G.circle(Bb[0], Bb[1], 50) + capsule(Bb, edge(172), 15) + capsule(Bb, edge(124), 12),
        capsule(Cn, T, 9) + capsule(T, F, 8.5) + capsule(F, edge(-40), 9) + capsule(Cn, edge(-122), 10),
        capsule(E, PAL, 7) + capsule(E, edge(8), 8),
        capsule(BAL, edge(84), 10) + G.circle(bx, by, 13),
    ]
    bridge_svg = ""
    for d in bridges:
        bridge_svg += (f'<path d="{d}" transform="translate(3 5)" fill="#000" opacity="{".45" if dark else ".18"}"/>'
                       f'<path d="{d}" fill="url(#{uid}geneva)" stroke="{p["steel"]}" stroke-opacity=".55" stroke-width="1"/>')

    def jewel(pt, r=4.2):
        return (f'<circle cx="{f(pt[0])}" cy="{f(pt[1])}" r="{f(r + 2.4)}" fill="{p["steel_dim"]}"/>'
                f'<circle cx="{f(pt[0])}" cy="{f(pt[1])}" r="{f(r)}" fill="url(#{uid}ruby)"/>'
                f'<circle cx="{f(pt[0])}" cy="{f(pt[1])}" r="1.1" fill="{p["case"]}"/>')

    def bscrew(pt, r=5.2, slot=0.6):
        return (f'<circle cx="{f(pt[0])}" cy="{f(pt[1])}" r="{f(r)}" fill="url(#{uid}blue)"/>'
                f'<path d="{G.screw(pt[0], pt[1], r, slot)}" fill="{p["case"]}" opacity=".8"/>')

    ratchet = (f'<path d="{G.teeth_outline(Bb[0], Bb[1], 42, 2.1)}{G.circle_ccw(Bb[0], Bb[1], 30)}" '
               f'fill="{wheel_fill}" fill-rule="evenodd"/>'
               f'<path d="{G.ticks(Bb[0], Bb[1], 29, 22, 36, 1)}" stroke="{p["steel_dim"]}" stroke-width=".7" opacity=".7"/>')
    jewels = "".join(jewel(q) for q in (Cn, T, F, E)) + jewel(PAL, 3) + jewel(BAL, 4.6)
    screws_b = "".join(bscrew(q, 4.8, a) for q, a in (
        (polar(Bb, 0, 0), 0.4), (edge(172), 1.1), (edge(124), 2.0),
        (edge(-40), 0.2), (edge(-122), 1.4), (edge(8), 2.3), (edge(84), 0.9)))
    # regulator index on the balance cock
    reg = (f'<path d="M{f(bx)},{f(by)}L{f(bx - 40)},{f(by - 30)}" stroke="{p["silver"] if dark else "#3a3e43"}" '
           f'stroke-width="1.6" stroke-linecap="round"/>'
           f'<path d="{G.arc(bx, by, 44, math.radians(205), math.radians(235))}" fill="none" stroke="{p["steel"]}" '
           f'stroke-width=".7"/><path d="{G.ticks(bx, by, 47, 4, 72, .5)}" stroke="none"/>')
    # engraved along the barrel bridge's long arm
    tip = edge(172)
    mid = ((Bb[0] + tip[0]) / 2 - 4, (Bb[1] + tip[1]) / 2)
    tilt = math.degrees(math.atan2(Bb[1] - tip[1], Bb[0] - tip[0]))
    eng = (f'<g transform="rotate({f(tilt)} {f(mid[0])} {f(mid[1])})">'
           + kit.txt("FKR·26 · MMXXVI", "martian-light", 4.6, mid[0], mid[1] + 2.3, p["ink_dim"], 0.3, "middle")
           + "</g>")

    # bezel: polished ring and a railway minute track, with lume at the cardinal points
    bezel = (f'<circle cx="{f(C[0])}" cy="{f(C[1])}" r="{f(R_MOV + 1)}" fill="none" stroke="{p["steel"]}" stroke-width="1.6"/>'
             f'<circle cx="{f(C[0])}" cy="{f(C[1])}" r="{f(R_MOV + 6)}" fill="none" stroke="{p["steel_dim"]}" stroke-width=".6"/>'
             f'<path d="{G.ticks(C[0], C[1], R_MOV + 24, 6, 60, .8, 5)}" stroke="{p["steel_dim"]}" stroke-width=".8"/>'
             f'<path d="{G.ticks(C[0], C[1], R_MOV + 26, 12, 12, 1)}" stroke="{p["steel"]}" stroke-width="1.8"/>'
             f'<circle cx="{f(C[0])}" cy="{f(C[1])}" r="{f(R_MOV + 30)}" fill="none" stroke="{p["steel_faint"]}" stroke-width=".6"/>')
    lume = "".join(f'<circle class="lume" style="animation-delay:{i * 1.5}s" cx="{f(polar(C, R_MOV + 20, a)[0])}" '
                   f'cy="{f(polar(C, R_MOV + 20, a)[1])}" r="3.2" fill="{p["lume"]}"/>'
                   for i, a in enumerate((-90, 0, 90, 180)))

    movement = (
        f'<g clip-path="url(#{uid}mov)">'
        f'<rect x="{f(C[0] - R_MOV)}" y="{f(C[1] - R_MOV)}" width="{f(2 * R_MOV)}" height="{f(2 * R_MOV)}" fill="{p["plate"]}"/>'
        f'<rect x="{f(C[0] - R_MOV)}" y="{f(C[1] - R_MOV)}" width="{f(2 * R_MOV)}" height="{f(2 * R_MOV)}" fill="url(#{uid}perl)"/>'
        f"{barrel}{centre}{third}{fourth}{esc}{lever}{balance}{bridge_svg}{ratchet}{jewels}{screws_b}{reg}{eng}"
        f'<rect x="{f(C[0] - R_MOV)}" y="{f(C[1] - R_MOV)}" width="{f(2 * R_MOV)}" height="{f(2 * R_MOV)}" fill="url(#{uid}light)"/>'
        f"</g>{bezel}{lume}"
    )

    # --- callouts: a technical drawing's annotations -------------------------------
    def callout(target, label, lx, ly, delay):
        tx, ty = target
        return (f'<g class="rise" style="animation-delay:{delay}s">'
                f'<path d="M{f(lx + 4)},{f(ly - 4)}L{f(lx + 30)},{f(ly - 4)}L{f(tx)},{f(ty)}" fill="none" '
                f'stroke="{p["steel_dim"]}" stroke-width=".6"/>'
                f'<circle cx="{f(tx)}" cy="{f(ty)}" r="2" fill="none" stroke="{p["salmon"]}" stroke-width=".8"/>'
                + kit.txt(label, "martian-light", 8, lx, ly - 8, p["ink_dim"], 0.22, "end") + "</g>")

    callouts = (callout(polar(Bb, 64, 200), "BARREL", 690, 340, 1.6)
                + callout(polar(Cn, 30, 230), "GEAR TRAIN", 700, 150, 1.8))

    # --- type -------------------------------------------------------------------------
    ink, dim, faint = p["ink"], p["ink_dim"], p["ink_faint"]
    rows = [
        ("ROLE", "Software Developer, Entarch Solutions"),
        ("ROLE", "Software Engineering Intern / Dev Lead, Grids Apps LLC"),
        ("STUDY", "B.Tech CSE, Karunya Institute · CGPA 9.39"),
        ("PUBLISHED", "SMAHI-ER · IEEE IEHNS 2026"),
        ("BASED", "Hyderabad, India"),
    ]
    spec = ""
    for i, (k, v) in enumerate(rows):
        y = 392 + i * 25
        spec += (f'<g class="rise" style="animation-delay:{0.7 + i * 0.12:.2f}s">'
                 + kit.txt(k, "martian-light", 8.6, 64, y, faint if dark else dim, 0.28)
                 + kit.txt(v, "bodoni-text", 15, 196, y + 1, ink)
                 + f'<path d="M64,{y + 9}H600" stroke="{p["steel_faint"]}" stroke-width=".6"/></g>')

    head = (
        f'<g class="rise" style="animation-delay:.1s">'
        + kit.txt("CALIBRE FKR·26", "martian", 10.5, 64, 120, p["salmon"], 0.34)
        + kit.txt("SYSTEMS THAT DECIDE UNDER UNCERTAINTY", "martian-light", 9, 64, 140, dim, 0.3)
        + "</g>"
        + f'<path class="draw" pathLength="1" d="M64,160H600" stroke="{p["steel_dim"]}" stroke-width=".8"/>'
        + f'<g class="rise" style="animation-delay:.35s"><path d="{name_d}" fill="{ink}"/>'
        + f'<g clip-path="url(#{uid}name)"><rect class="sweep" x="-260" y="150" width="200" height="110" '
          f'fill="url(#{uid}glint)" opacity="{".55" if dark else ".9"}"/></g></g>'
        + f'<g class="rise" style="animation-delay:.55s">'
        + kit.txt("and show their work.", "bodoni-display-italic", 30, 64, 330, p["salmon"])
        + kit.txt("Calibrated models, honest negatives,", "bodoni-display-italic", 30, 64, 294, dim)
        + "</g>"
    )

    body = (
        f'<rect width="{W}" height="{H}" rx="18" fill="url(#{uid}vig)"/>'
        f"{gl1}{gl2}{gl3}"
        f"{head}{spec}{callouts}{movement}"
        f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="18" fill="none" stroke="{p["steel_faint"]}"/>'
    )
    title = "Febin K Renu, Calibre FKR-26"
    desc = ("A mechanical watch movement beside the name Febin K Renu. The gear train turns at true ratios, the "
            "balance wheel swings and the escape wheel ticks with each beat. Beside it: calibrated models, honest "
            "negatives, and show their work. Software Developer at Entarch Solutions; Software Engineering Intern "
            "and Dev Lead at Grids Apps LLC; B.Tech CSE at Karunya Institute, CGPA 9.39; published SMAHI-ER at IEEE "
            "IEHNS 2026; based in Hyderabad, India.")
    return kit.doc(W, H, title, desc, style, defs, body, uid)


def main() -> None:
    for p in THEMES:
        out = kit.write(f"header-{p['name']}.svg", build(p))
        print(f"{out.name}: {out.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
