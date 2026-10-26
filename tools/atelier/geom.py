"""Geometry for the movement: wheels, escapement parts, hairspring, guilloché, dial furniture.

Everything returns SVG path data in user units. Wheels mesh at true ratios:
two wheels of module m and tooth counts N1, N2 sit m*(N1+N2)/2 apart, and
`mesh_phase` gives the second wheel's starting angle so a tooth meets a gap.
"""

from __future__ import annotations

import math

TAU = math.tau


def n(v: float) -> str:
    r = round(v, 2)
    return str(int(r)) if r == int(r) else f"{r:.2f}".rstrip("0")


def pt(cx: float, cy: float, r: float, a: float) -> str:
    return f"{n(cx + r * math.cos(a))},{n(cy + r * math.sin(a))}"


def circle(cx: float, cy: float, r: float) -> str:
    """A circle as a path (two arcs), clockwise."""
    return (f"M{n(cx + r)},{n(cy)}A{n(r)},{n(r)} 0 1 1 {n(cx - r)},{n(cy)}"
            f"A{n(r)},{n(r)} 0 1 1 {n(cx + r)},{n(cy)}Z")


def circle_ccw(cx: float, cy: float, r: float) -> str:
    return (f"M{n(cx + r)},{n(cy)}A{n(r)},{n(r)} 0 1 0 {n(cx - r)},{n(cy)}"
            f"A{n(r)},{n(r)} 0 1 0 {n(cx + r)},{n(cy)}Z")


def arc(cx: float, cy: float, r: float, a0: float, a1: float) -> str:
    """Open arc from angle a0 to a1 (radians, clockwise on screen when a1 > a0)."""
    large = 1 if abs(a1 - a0) % TAU > math.pi else 0
    sweep = 1 if a1 > a0 else 0
    return f"M{pt(cx, cy, r, a0)}A{n(r)},{n(r)} 0 {large} {sweep} {pt(cx, cy, r, a1)}"


# --- wheels ------------------------------------------------------------------------

def pitch_radius(teeth: int, module: float) -> float:
    return module * teeth / 2


def centre_distance(t1: int, t2: int, module: float) -> float:
    return module * (t1 + t2) / 2


def mesh_phase(alpha_deg: float, rot1_deg: float, t1: int, t2: int) -> float:
    """Starting rotation (deg) of wheel 2, placed at angle alpha from wheel 1, so they mesh.

    Tooth k of a wheel sits at k*360/N + rotation. At the contact line a tooth of
    wheel 1 must face a gap of wheel 2.
    """
    p1, p2 = 360 / t1, 360 / t2
    u1 = ((alpha_deg - rot1_deg) / p1) % 1.0
    return (alpha_deg + 180 - p2 * (0.5 - u1)) % 360


def teeth_outline(cx: float, cy: float, teeth: int, module: float) -> str:
    """Closed outline of a watch wheel's teeth: ogival tips, as in cycloidal gearing."""
    r = pitch_radius(teeth, module)
    ra, rr = r + 0.95 * module, r - 1.2 * module
    p = TAU / teeth
    parts = []
    for k in range(teeth):
        c = k * p
        a = [c - 0.5 * p, c - 0.26 * p, c - 0.2 * p, c, c + 0.2 * p, c + 0.26 * p]
        if k == 0:
            parts.append(f"M{pt(cx, cy, rr, a[0])}")
        else:
            parts.append(f"L{pt(cx, cy, rr, a[0])}")
        parts.append(f"L{pt(cx, cy, rr, a[1])}")
        parts.append(f"L{pt(cx, cy, r, a[2])}")
        parts.append(f"Q{pt(cx, cy, ra * 1.04, c - 0.13 * p)} {pt(cx, cy, ra, a[3])}")
        parts.append(f"Q{pt(cx, cy, ra * 1.04, c + 0.13 * p)} {pt(cx, cy, r, a[4])}")
        parts.append(f"L{pt(cx, cy, rr, a[5])}")
    parts.append("Z")
    return "".join(parts)


def internal_teeth_outline(cx: float, cy: float, teeth: int, module: float) -> str:
    """Inner outline of a ring gear: the teeth point inward. Pair with an outer circle."""
    r = pitch_radius(teeth, module)
    ra, rr = r - 0.95 * module, r + 1.2 * module
    p = TAU / teeth
    parts = []
    for k in range(teeth):
        c = k * p
        if k == 0:
            parts.append(f"M{pt(cx, cy, rr, c - 0.5 * p)}")
        else:
            parts.append(f"L{pt(cx, cy, rr, c - 0.5 * p)}")
        parts.append(f"L{pt(cx, cy, rr, c - 0.26 * p)}")
        parts.append(f"L{pt(cx, cy, r, c - 0.2 * p)}")
        parts.append(f"Q{pt(cx, cy, ra * 0.97, c - 0.13 * p)} {pt(cx, cy, ra, c)}")
        parts.append(f"Q{pt(cx, cy, ra * 0.97, c + 0.13 * p)} {pt(cx, cy, r, c + 0.2 * p)}")
        parts.append(f"L{pt(cx, cy, rr, c + 0.26 * p)}")
    parts.append("Z")
    return "".join(parts)


def rack(x0: float, x1: float, y: float, module: float, depth: float) -> str:
    """A straight rack, teeth up, from x0 to x1 with its pitch line at y, body below."""
    pitch = math.pi * module
    out = [f"M{n(x0)},{n(y + depth)}L{n(x0)},{n(y + 1.2 * module)}"]
    x = x0
    while x + pitch <= x1:
        out.append(f"L{n(x + 0.24 * pitch)},{n(y + 1.2 * module)}L{n(x + 0.36 * pitch)},{n(y - module)}"
                   f"L{n(x + 0.64 * pitch)},{n(y - module)}L{n(x + 0.76 * pitch)},{n(y + 1.2 * module)}")
        x += pitch
    out.append(f"L{n(x1)},{n(y + 1.2 * module)}L{n(x1)},{n(y + depth)}Z")
    return "".join(out)


def crossings(cx: float, cy: float, r_in: float, hub: float, arms: int, width: float,
              curve: float = 0.35) -> str:
    """Curved wheel arms (the 'crossings') from hub to rim, as filled shapes."""
    out = []
    for i in range(arms):
        a = i * TAU / arms
        w0 = width / hub / 2
        w1 = width / r_in / 2
        bend = curve
        p0a, p0b = pt(cx, cy, hub * 0.8, a - w0), pt(cx, cy, hub * 0.8, a + w0)
        p1a, p1b = pt(cx, cy, r_in * 1.02, a + bend - w1), pt(cx, cy, r_in * 1.02, a + bend + w1)
        ma = pt(cx, cy, (hub + r_in) / 2, a + bend * 0.25 - w0 * 0.6)
        mb = pt(cx, cy, (hub + r_in) / 2, a + bend * 0.25 + w0 * 0.6)
        out.append(f"M{p0a}Q{ma} {p1a}L{p1b}Q{mb} {p0b}Z")
    return "".join(out)


def wheel(cx: float, cy: float, teeth: int, module: float, arms: int = 5,
          rim: float = 0.16, hub_frac: float = 0.16) -> str:
    """A complete wheel (teeth + rim + crossings + hub) for fill-rule evenodd.

    Returned as two parts so the caller can fill them: (ring_d, arms_d).
    """
    r = pitch_radius(teeth, module)
    rr = r - 1.2 * module
    r_in = rr * (1 - rim)
    ring = teeth_outline(cx, cy, teeth, module) + circle_ccw(cx, cy, r_in)
    hub = max(r * hub_frac, 3)
    spokes = crossings(cx, cy, r_in, hub, arms, max(r * 0.07, 2.2)) + circle(cx, cy, hub)
    return ring + spokes


def escape_wheel(cx: float, cy: float, r: float, teeth: int = 15, arms: int = 4) -> str:
    """Swiss club-tooth escape wheel: leaning teeth with a flat impulse face."""
    p = TAU / teeth
    rb = r * 0.74
    parts = []
    for k in range(teeth):
        a = k * p
        if k == 0:
            parts.append(f"M{pt(cx, cy, rb, a)}")
        else:
            parts.append(f"L{pt(cx, cy, rb, a)}")
        parts.append(f"L{pt(cx, cy, r * 0.98, a + 0.42 * p)}")
        parts.append(f"L{pt(cx, cy, r, a + 0.5 * p)}")
        parts.append(f"L{pt(cx, cy, r * 0.9, a + 0.62 * p)}")
        parts.append(f"L{pt(cx, cy, rb, a + 0.7 * p)}")
    parts.append("Z")
    r_in = rb * 0.84
    hub = r * 0.14
    return ("".join(parts) + circle_ccw(cx, cy, r_in)
            + crossings(cx, cy, r_in, hub, arms, r * 0.08, 0.0) + circle(cx, cy, hub))


def pallet_fork(cx: float, cy: float, length: float, angle: float) -> str:
    """Pallet lever: a T with the fork toward the balance, pivot at (cx, cy)."""
    ca, sa = math.cos(angle), math.sin(angle)

    def rot(x: float, y: float) -> str:
        return f"{n(cx + x * ca - y * sa)},{n(cy + x * sa + y * ca)}"
    w = length * 0.07
    L = length
    return (f"M{rot(-L * 0.08, -w)}L{rot(L * 0.86, -w)}L{rot(L, -w * 2.4)}L{rot(L * 1.04, -w * 1.2)}"
            f"L{rot(L * 0.94, 0)}L{rot(L * 1.04, w * 1.2)}L{rot(L, w * 2.4)}L{rot(L * 0.86, w)}"
            f"L{rot(-L * 0.08, w)}Z"
            # the pallet arms across the escape wheel
            f"M{rot(-L * 0.36, -L * 0.42)}L{rot(-L * 0.02, -w * 1.2)}L{rot(-L * 0.02, w * 1.2)}"
            f"L{rot(-L * 0.36, L * 0.42)}L{rot(-L * 0.44, L * 0.38)}L{rot(-L * 0.14, 0)}"
            f"L{rot(-L * 0.44, -L * 0.38)}Z")


def hairspring(cx: float, cy: float, r0: float, r1: float, turns: float, pts_per_turn: int = 48) -> str:
    """Archimedean spiral from r0 to r1."""
    total = int(turns * pts_per_turn)
    out = []
    for i in range(total + 1):
        t = i / total
        a = t * turns * TAU
        r = r0 + (r1 - r0) * t
        out.append(("M" if i == 0 else "L") + pt(cx, cy, r, a))
    return "".join(out)


# --- engraving -----------------------------------------------------------------------

def rose_curve(cx: float, cy: float, R: float, amp: float, lobes: int, samples: int = 240) -> str:
    """One rose-engine pass: r = R + amp*sin(lobes*theta). Rotated copies make guilloché."""
    out = []
    for i in range(samples):
        a = i * TAU / samples
        r = R + amp * math.sin(lobes * a)
        out.append(("M" if i == 0 else "L") + pt(cx, cy, r, a))
    return "".join(out) + "Z"


def guilloche(cid: str, cx: float, cy: float, R: float, amp: float, lobes: int, copies: int,
              stroke: str, width: float, opacity: float, cls: str = "") -> tuple[str, str]:
    """(defs, body): one rose curve in defs and `copies` rotated <use>s of it.

    Rotating r = R + a*sin(k*theta) by b shifts its phase by k*b, so a fan of
    rotated copies is exactly the phase family a rose engine cuts.
    """
    defs = f'<path id="{cid}" d="{rose_curve(cx, cy, R, amp, lobes)}"/>'
    step = 360 / lobes / copies
    uses = "".join(f'<use href="#{cid}" transform="rotate({n(i * step)} {n(cx)} {n(cy)})"/>' for i in range(copies))
    body = (f'<g class="{cls}" fill="none" stroke="{stroke}" stroke-width="{width}" '
            f'stroke-opacity="{opacity}">{uses}</g>')
    return defs, body


def ticks(cx: float, cy: float, r_out: float, length: float, count: int, width: float,
          skip_every: int = 0) -> str:
    out = []
    for i in range(count):
        if skip_every and i % skip_every == 0:
            continue
        a = i * TAU / count - math.pi / 2
        out.append(f"M{pt(cx, cy, r_out, a)}L{pt(cx, cy, r_out - length, a)}")
    return "".join(out)


def screw(cx: float, cy: float, r: float, slot_angle: float) -> str:
    """Screw head slot as a thin rectangle path (draw over a filled circle)."""
    w = r * 0.2
    ca, sa = math.cos(slot_angle), math.sin(slot_angle)
    pts = [(-r * 0.86, -w), (r * 0.86, -w), (r * 0.86, w), (-r * 0.86, w)]
    return "M" + "L".join(f"{n(cx + x * ca - y * sa)},{n(cy + x * sa + y * ca)}" for x, y in pts) + "Z"
