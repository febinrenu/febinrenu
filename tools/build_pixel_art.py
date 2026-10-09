"""Builds the README's pixel art: assets/hero-level.svg, an auto-playing level for the
header, and assets/continue.svg, the arcade countdown at the bottom.

The runner clears failure modes (each one something a project of mine guards against)
and bumps ? blocks that pop the projects themselves. Everything is CSS keyframes in one
SVG, because GitHub renders README images without JavaScript. Timings are computed from
the scroll speed, so the jumps land wherever the obstacles are.

    python tools/build_pixel_art.py
"""

from __future__ import annotations

import random
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"

W, H = 900, 320
GROUND = 268            # y of the running surface
HERO_X = 174            # screen x of the runner's centre
SPACING = 230           # strip distance between events
EVENTS = 12
L = SPACING * EVENTS    # strip length; one loop of the level
V = 150.0               # scroll speed, px/s
T = L / V               # loop duration, s

# (obstacle, what beat it, coin the next ? block pops)
LEVEL = [
    ("HALLUCINATION", "HONEST NO", "EVORA"),
    ("PROMPT INJECTION", "QUARANTINED", "PARALLAX"),
    ("UNCALIBRATED P", "CALIBRATED", "RECLAIM"),
    ("DROPPED EXCEPTION", "COMPOSED", "SCOPECOMPOSE"),
    ("UNCITED CLAUSE", "SPAN VERIFIED", "PRISM"),
    ("STRAIGHT-LINE GUESS", "PRICED", "ASSETSTREAM"),
]

# --- 5x7 pixel font ------------------------------------------------------------

FONT = {
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    "C": [".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."],
    "D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "F": ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    "G": [".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".####"],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "I": [".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "J": ["..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."],
    "K": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    "N": ["#...#", "#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    "Q": [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "V": ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "W": ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."],
    "X": ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
    "Y": ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
    "Z": ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
    "0": [".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."],
    "1": ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "2": [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"],
    "3": ["####.", "....#", "....#", ".###.", "....#", "....#", "####."],
    "4": ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
    "5": ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
    "6": [".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."],
    "7": ["#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."],
    "8": [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
    "9": [".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."],
    " ": ["....."] * 7,
    ".": [".....", ".....", ".....", ".....", ".....", ".##..", ".##.."],
    "-": [".....", ".....", ".....", ".###.", ".....", ".....", "....."],
    ":": [".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."],
    "?": [".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."],
    "+": [".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."],
    "x": [".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"],
    ">": ["#....", "##...", "###..", "####.", "###..", "##...", "#...."],
    "/": ["....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."],
}


def runs(rows: list[str], x: float, y: float, s: float) -> str:
    """Path commands for the '#' cells of a bitmap, merging horizontal runs."""
    out = []
    for r, row in enumerate(rows):
        c = 0
        while c < len(row):
            if row[c] == "#":
                k = c
                while k < len(row) and row[k] == "#":
                    k += 1
                out.append(f"M{x + c * s:g},{y + r * s:g}h{(k - c) * s:g}v{s:g}h{-(k - c) * s:g}z")
                c = k
            else:
                c += 1
    return "".join(out)


def text_width(text: str, s: float) -> float:
    return (len(text) * 6 - 1) * s


def pixtext(text: str, x: float, y: float, s: float, anchor: str = "start") -> str:
    if anchor == "middle":
        x -= text_width(text, s) / 2
    elif anchor == "end":
        x -= text_width(text, s)
    return "".join(runs(FONT[ch], x + i * 6 * s, y, s) for i, ch in enumerate(text))


# --- sprites -------------------------------------------------------------------

HERO_TOP = [
    "...HHHHH....",
    "..HHHHHHHH..",
    "..HHSSSSS...",
    "..HSSSSESS..",
    "..HSSSSSSS..",
    "...SSSSSS...",
    "..KKKKKKK...",
    ".KKKKKKKKK..",
    ".KK.KKKKSS..",
    ".SS.KKKK....",
    "....KKKK....",
    "....PPPP....",
]
HERO_LEGS_A = ["...PP..PP...", "..PP....PP..", ".BB......BB.", "............"]
HERO_LEGS_B = ["....PPPP....", "....PPP.....", "....PBB.....", "....BB......"]
HERO_COLORS = {"H": "#2b1d14", "S": "#c68642", "E": "#0d1117", "K": "#1f6feb", "P": "#30363d", "B": "#e6edf3"}

BUG_A = ["..#.....#..", "...#...#...", "..#######..", ".##.###.##.", "###########", "#.#######.#", "#.#.....#.#", "...##.##..."]
BUG_B = ["..#.....#..", "#..#...#..#", "#.#######.#", "###.###.###", "###########", ".#########.", "..#.....#..", ".#.......#."]

QBLOCK = [
    "############",
    "#..........#",
    "#...####...#",
    "#..##..##..#",
    "#......##..#",
    "#.....##...#",
    "#....##....#",
    "#....##....#",
    "#..........#",
    "#....##....#",
    "#..........#",
    "############",
]
COIN = ["..####..", ".######.", "##.##.##", "##.##.##", "##.##.##", "##.##.##", ".######.", "..####.."]


def sprite(rows: list[str], colors: dict[str, str], x: float, y: float, s: float) -> str:
    parts = []
    for key, col in colors.items():
        mask = ["".join("#" if ch == key else "." for ch in row) for row in rows]
        d = runs(mask, x, y, s)
        if d:
            parts.append(f'<path fill="{col}" d="{d}"/>')
    return "".join(parts)


# --- animation helpers -----------------------------------------------------------

def pct(seconds: float) -> str:
    return f"{100.0 * seconds / T:.3f}%"


def event_time(x: float) -> float:
    """Seconds into the loop at which strip position x reaches the runner."""
    return ((x - HERO_X) % L) / V


JUMP_D, JUMP_H = 0.72, 84      # over an obstacle
BUMP_D, BUMP_H = 0.50, 36      # up into a ? block: head meets the block's underside


def css() -> str:
    up, down = "cubic-bezier(.2,.65,.35,1)", "cubic-bezier(.65,0,.8,.35)"
    return f"""
    .mono {{ font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace; }}
    .world {{ animation: scroll {T:g}s linear infinite; }}
    .far {{ animation: far {900 / (V * 0.22):.2f}s linear infinite; }}
    .mid {{ animation: far {900 / (V * 0.5):.2f}s linear infinite; }}
    .stars {{ animation: far {900 / (V * 0.06):.2f}s linear infinite; }}
    .tw {{ animation: tw 3s ease-in-out infinite; }}
    .fa {{ animation: fa .3s steps(1) infinite; }}
    .fb {{ animation: fb .3s steps(1) infinite; }}
    .ba {{ animation: fa .5s steps(1) infinite; }}
    .bb {{ animation: fb .5s steps(1) infinite; }}
    .jump {{ animation: jump {T:g}s infinite; }}
    .bump {{ animation: bump {T:g}s infinite; }}
    .hit {{ animation: hit {T:g}s infinite; transform-box: fill-box; }}
    .used {{ animation: used {T:g}s infinite; opacity: 0; }}
    .coin {{ animation: coin {T:g}s infinite; opacity: 0; }}
    .pop {{ animation: pop {T:g}s infinite; opacity: 0; }}
    .dust {{ animation: dust .45s linear infinite; }}
    .count {{ animation: count {T:g}s infinite; }}
    .glint {{ animation: glint 6s ease-in-out infinite; }}
    .flick {{ animation: flick 7s steps(1) infinite; }}
    @keyframes scroll {{ from {{ transform: translateX(0); }} to {{ transform: translateX(-{L}px); }} }}
    @keyframes far {{ from {{ transform: translateX(0); }} to {{ transform: translateX(-900px); }} }}
    @keyframes tw {{ 0%,100% {{ opacity: .25; }} 50% {{ opacity: 1; }} }}
    @keyframes fa {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0; }} }}
    @keyframes fb {{ 0% {{ opacity: 0; }} 50% {{ opacity: 1; }} }}
    @keyframes jump {{
      0% {{ transform: translateY(0); animation-timing-function: {up}; }}
      {pct(JUMP_D / 2)} {{ transform: translateY(-{JUMP_H}px); animation-timing-function: {down}; }}
      {pct(JUMP_D)}, 100% {{ transform: translateY(0); }} }}
    @keyframes bump {{
      0% {{ transform: translateY(0); animation-timing-function: {up}; }}
      {pct(BUMP_D / 2)} {{ transform: translateY(-{BUMP_H}px); animation-timing-function: {down}; }}
      {pct(BUMP_D)}, 100% {{ transform: translateY(0); }} }}
    @keyframes hit {{ 0% {{ transform: translateY(0); }} {pct(0.08)} {{ transform: translateY(-9px); }} {pct(0.2)}, 100% {{ transform: translateY(0); }} }}
    @keyframes used {{ 0% {{ opacity: 0; }} {pct(0.05)} {{ opacity: 1; }} {pct(2.6)} {{ opacity: 1; }} {pct(2.65)}, 100% {{ opacity: 0; }} }}
    @keyframes coin {{
      0% {{ opacity: 0; transform: translateY(0); }}
      {pct(0.05)} {{ opacity: 1; }}
      {pct(0.4)} {{ opacity: 1; transform: translateY(-34px); }}
      {pct(0.7)}, 100% {{ opacity: 0; transform: translateY(-22px); }} }}
    @keyframes pop {{
      0% {{ opacity: 0; transform: translateY(8px); }}
      {pct(0.12)} {{ opacity: 1; transform: translateY(0); }}
      {pct(1.5)} {{ opacity: 1; transform: translateY(-14px); }}
      {pct(1.9)}, 100% {{ opacity: 0; transform: translateY(-18px); }} }}
    @keyframes dust {{ 0% {{ opacity: .7; transform: translate(0,0); }} 100% {{ opacity: 0; transform: translate(-22px,-8px); }} }}
    @keyframes glint {{ 0%, 55% {{ transform: translateX(440px); }} 85%, 100% {{ transform: translateX(1000px); }} }}
    @keyframes flick {{ 0%, 96% {{ opacity: 1; }} 97% {{ opacity: .55; }} 98% {{ opacity: 1; }} 99% {{ opacity: .7; }} }}
"""


def counter_keyframes(coin_times: list[float], step: float) -> str:
    frames = ["0% { transform: translateY(0); animation-timing-function: steps(1, end); }"]
    for k, t in enumerate(sorted(coin_times), 1):
        frames.append(f"{pct(t + 0.15)} {{ transform: translateY(-{k * step:g}px); animation-timing-function: steps(1, end); }}")
    frames.append(f"100% {{ transform: translateY(-{len(coin_times) * step:g}px); }}")
    return "@keyframes count { " + " ".join(frames) + " }"


# --- scene ---------------------------------------------------------------------------

def strip(rng: random.Random) -> tuple[str, list[float]]:
    """One copy of the scrolling strip (ground + events). Returns (svg, coin times)."""
    parts = []
    # ground: a contribution graph to run on
    levels = ["#0e4429", "#006d32", "#26a641", "#39d353", "#161b22"]
    weights = [30, 25, 15, 8, 22]
    cells: dict[str, list[str]] = {c: [] for c in levels}
    for col in range(L // 12):
        for row in range(3):
            colr = rng.choices(levels, weights=weights)[0]
            if row == 0:
                colr = rng.choices(levels[:4], weights=[20, 30, 30, 20])[0]
            cells[colr].append(f"M{col * 12 + 1},{GROUND + 1 + row * 12}h10v10h-10z")
    for colr, ds in cells.items():
        parts.append(f'<path fill="{colr}" d="{"".join(ds)}"/>')
    parts.append(f'<rect x="0" y="{GROUND + 36}" width="{L}" height="12" fill="url(#cell)"/>')

    coin_times = []
    for j in range(EVENTS):
        x = (HERO_X + SPACING * (j + 1)) % L
        t = event_time(x)
        obstacle, beat, coin = LEVEL[j // 2]
        if j % 2 == 0:  # an obstacle to clear
            bx, by, s = x - 16.5, GROUND - 24, 3
            parts.append(
                f'<g class="ba">{sprite(BUG_A, {"#": "#f85149"}, bx, by, s)}</g>'
                f'<g class="bb">{sprite(BUG_B, {"#": "#f85149"}, bx, by, s)}</g>'
                f'<path fill="#f85149" opacity=".9" d="{pixtext(obstacle, x, GROUND - 52, 2, "middle")}"/>'
                f'<g class="pop" style="animation-delay:{t + 0.15:.3f}s">'
                f'<path fill="#3fb950" d="{pixtext("+" + beat, x, GROUND - 120, 2, "middle")}"/></g>'
            )
        else:  # a ? block to bump
            s = 3
            bx, by = x - 18, GROUND - 48 - BUMP_H - 36
            parts.append(
                f'<g class="hit" style="animation-delay:{t - 0.02:.3f}s">'
                f'{sprite(QBLOCK, {"#": "#7a4a12", ".": "#d29922"}, bx, by, s)}'
                f'<g class="used" style="animation-delay:{t - 0.02:.3f}s">'
                f'{sprite(QBLOCK, {"#": "#3d2a10", ".": "#6b4f1d"}, bx, by, s)}</g></g>'
                f'<g class="coin" style="animation-delay:{t:.3f}s">'
                f'{sprite(COIN, {"#": "#f2cc60"}, x - 12, by - 28, s)}</g>'
                f'<g class="pop" style="animation-delay:{t + 0.1:.3f}s">'
                f'<path fill="#f2cc60" d="{pixtext(coin, x, by - 54, 2, "middle")}"/></g>'
            )
            coin_times.append(t)
    return "".join(parts), coin_times


def jumps() -> tuple[str, str]:
    """Nested groups, one per event; each lifts the runner only during its own jump."""
    opens, closes = [], []
    for j in range(EVENTS):
        x = (HERO_X + SPACING * (j + 1)) % L
        t = event_time(x)
        if j % 2 == 0:
            opens.append(f'<g class="jump" style="animation-delay:{t - JUMP_D / 2:.3f}s">')
        else:
            opens.append(f'<g class="bump" style="animation-delay:{t - BUMP_D / 2:.3f}s">')
        closes.append("</g>")
    return "".join(opens), "".join(closes)


def build() -> str:
    rng = random.Random(2026)
    strip_svg, coin_times = strip(rng)

    stars = "".join(
        f'<rect class="tw" style="animation-delay:{rng.uniform(0, 3):.2f}s" x="{rng.uniform(0, 900):.0f}" '
        f'y="{rng.uniform(70, 200):.0f}" width="{rng.choice([2, 2, 3])}" height="{rng.choice([2, 2, 3])}" fill="#c9d1d9"/>'
        for _ in range(55))

    def skyline(seed: int, color: str, base: int, hmin: int, hmax: int, windows: bool) -> str:
        r = random.Random(seed)
        out, x = [], 0
        while x < 900:
            w = r.choice([24, 30, 36, 42])
            hgt = r.randint(hmin, hmax)
            out.append(f'<rect x="{x}" y="{base - hgt}" width="{w}" height="{hgt}" fill="{color}"/>')
            if windows:
                for wy in range(base - hgt + 8, base - 6, 10):
                    for wx in range(x + 5, x + w - 6, 8):
                        if r.random() < 0.18:
                            out.append(f'<rect x="{wx}" y="{wy}" width="3" height="4" fill="#d29922" opacity="{r.choice([".35", ".6", ".85"])}"/>')
            x += w + r.choice([0, 0, 6])
        return "".join(out)

    far = skyline(7, "#121a2c", GROUND, 30, 95, True)
    mid = skyline(11, "#0f1626", GROUND, 12, 46, False)

    hero_top = sprite(HERO_TOP, HERO_COLORS, HERO_X - 18, GROUND - 48, 3)
    legs_a = sprite(HERO_LEGS_A, HERO_COLORS, HERO_X - 18, GROUND - 12, 3)
    legs_b = sprite(HERO_LEGS_B, HERO_COLORS, HERO_X - 18, GROUND - 12, 3)
    j_open, j_close = jumps()

    title = "FEBIN RENU"
    title_d = pixtext(title, 872, 26, 5, "end")
    sub_d = pixtext("BUILDS SYSTEMS THAT DECIDE UNDER UNCERTAINTY", 872, 74, 2, "end")
    step = 18
    digits = "".join(f'<path fill="#f2cc60" d="{pixtext(str(k), 0, k * step, 2)}"/>' for k in range(len(coin_times) + 1))

    return f"""<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="t d">
  <title id="t">Febin Renu: an auto-playing pixel level</title>
  <desc id="d">A pixel-art runner crosses a scrolling city on top of a contribution graph. He jumps over bugs named after failure modes (hallucination, prompt injection, uncalibrated probability, dropped exception, uncited clause, straight-line guess) and each is answered by the fix (honest no, quarantined, calibrated, composed, span verified, priced). He bumps question blocks that pop coins named EVORA, PARALLAX, RECLAIM, SCOPECOMPOSE, PRISM and ASSETSTREAM. A coin counter ticks up in the corner.</desc>
  <defs>
    <style>{css()}
    {counter_keyframes(coin_times, step)}
    </style>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#070a12"/><stop offset=".65" stop-color="#0d1426"/><stop offset="1" stop-color="#16213d"/>
    </linearGradient>
    <pattern id="cell" width="12" height="12" patternUnits="userSpaceOnUse"><rect x="1" y="1" width="10" height="10" fill="#161b22"/></pattern>
    <pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000" opacity=".22"/></pattern>
    <clipPath id="frame"><rect x="0" y="0" width="{W}" height="{H}" rx="12"/></clipPath>
    <clipPath id="titleclip"><path d="{title_d}"/></clipPath>
    <clipPath id="digitclip"><rect x="0" y="0" width="12" height="14"/></clipPath>
  </defs>
  <g clip-path="url(#frame)">
    <rect width="{W}" height="{H}" fill="url(#sky)"/>
    <g class="stars"><g>{stars}</g><g transform="translate(900 0)">{stars}</g></g>
    <circle cx="812" cy="132" r="18" fill="#e6edf3" opacity=".9"/><circle cx="820" cy="126" r="15" fill="#0d1426"/>
    <g class="far"><g>{far}</g><g transform="translate(900 0)">{far}</g></g>
    <g class="mid"><g>{mid}</g><g transform="translate(900 0)">{mid}</g></g>
    <rect x="0" y="{GROUND}" width="{W}" height="{H - GROUND}" fill="#0b0f17"/>

    <g class="world"><g>{strip_svg}</g><g transform="translate({L} 0)">{strip_svg}</g></g>

    <g class="dust">
      <rect x="{HERO_X - 20}" y="{GROUND - 6}" width="4" height="4" fill="#8b949e"/>
      <rect x="{HERO_X - 12}" y="{GROUND - 4}" width="3" height="3" fill="#8b949e"/>
    </g>
    {j_open}
      {hero_top}
      <g class="fa">{legs_a}</g><g class="fb">{legs_b}</g>
    {j_close}

    <g class="flick">
      <path fill="#0b3d91" d="{pixtext(title, 876, 30, 5, "end")}"/>
      <path fill="#e6edf3" d="{title_d}"/>
      <g clip-path="url(#titleclip)"><rect class="glint" x="0" y="20" width="60" height="50" fill="#79c0ff" opacity=".85" transform="skewX(-20)"/></g>
      <path fill="#8b949e" d="{sub_d}"/>
    </g>
    <path fill="#8b949e" d="{pixtext("COINS", 30, 26, 2)}"/>
    <path fill="#f2cc60" d="{pixtext("x0", 102, 26, 2)}"/>
    <g transform="translate(126 26)"><g clip-path="url(#digitclip)"><g class="count">{digits}</g></g></g>
    <path fill="#8b949e" d="{pixtext("HI-SCORE", 30, 50, 2)}"/>
    <path fill="#3fb950" d="{pixtext("9.39", 138, 50, 2)}"/>

    <rect width="{W}" height="{H}" fill="url(#scan)"/>
  </g>
  <rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="12" fill="none" stroke="#30363d"/>
</svg>
"""


def build_continue() -> str:
    """CONTINUE? counting down 9 to 0, then INSERT COIN, on a 12 s loop."""
    w, h, step = 900, 120, 60
    digits = "".join(f'<path fill="#f2cc60" d="{pixtext(str(9 - k), 0, k * step, 6)}"/>' for k in range(10))
    return f"""<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="t d">
  <title id="t">Continue?</title>
  <desc id="d">An arcade continue screen counts down from 9 to 0, then flashes INSERT COIN. The links below are the coin slot.</desc>
  <defs>
    <style>
      .count {{ animation: count 12s steps(1) infinite; }}
      .cont {{ animation: cont 12s steps(1) infinite; }}
      .coin {{ animation: coin 12s steps(1) infinite; opacity: 0; }}
      @keyframes count {{ {" ".join(f"{k * 100 / 12:.3f}% {{ transform: translateY(-{k * step}px); }}" for k in range(10))} }}
      @keyframes cont {{ 0% {{ opacity: 1; }} 83.333% {{ opacity: 0; }} }}
      @keyframes coin {{ 0% {{ opacity: 0; }} 83.333% {{ opacity: 1; }} 87.5% {{ opacity: 0; }} 91.667% {{ opacity: 1; }} 95.833% {{ opacity: 0; }} }}
    </style>
    <clipPath id="digit"><rect x="0" y="0" width="30" height="42"/></clipPath>
    <pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000" opacity=".22"/></pattern>
  </defs>
  <rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="12" fill="#070a12" stroke="#30363d"/>
  <g class="cont">
    <path fill="#0b3d91" d="{pixtext("CONTINUE?", 289, 43, 5)}"/>
    <path fill="#e6edf3" d="{pixtext("CONTINUE?", 285, 39, 5)}"/>
    <g transform="translate(585 39)"><g clip-path="url(#digit)"><g class="count">{digits}</g></g></g>
    <path fill="#8b949e" d="{pixtext("THE LINKS BELOW ARE THE COIN SLOT", w / 2, 92, 2, "middle")}"/>
  </g>
  <g class="coin">
    <path fill="#f2cc60" d="{pixtext("INSERT COIN", w / 2, 39, 5, "middle")}"/>
    <path fill="#8b949e" d="{pixtext("THANKS FOR PLAYING", w / 2, 92, 2, "middle")}"/>
  </g>
  <rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="12" fill="url(#scan)"/>
</svg>
"""


if __name__ == "__main__":
    for name, svg in (("hero-level.svg", build()), ("continue.svg", build_continue())):
        out = ASSETS / name
        out.write_text(svg, encoding="utf-8")
        print(f"wrote {out} ({out.stat().st_size // 1024} KB)")
