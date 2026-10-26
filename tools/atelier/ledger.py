"""The ledger: a year of public GitHub activity as a perpetual calendar, plus a language reserve.

Real data only, from the GitHub GraphQL API. Run weekly by .github/workflows/ledger.yml:

    GITHUB_TOKEN=... python tools/atelier/ledger.py

The calendar wraps the last year around a dial: each spoke is a week, each ring
a weekday, and a day's mark grows with its contribution count. The reserve arc
splits code bytes across public, non-fork repositories by language.
"""

from __future__ import annotations

import datetime as dt
import json
import math
import os
import sys
import urllib.request

import geom as G
import kit
from palette import THEMES

LOGIN = "febinrenu"
RES = "LANGUAGE RESERVE · BYTES ACROSS PUBLIC REPOSITORIES"
SNAP = "A SNAPSHOT, REDRAWN WEEKLY BY A GITHUB ACTION · NOT LIVE"
W, H = 1200, 600
f = G.n

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar { totalContributions weeks { contributionDays { date contributionCount } } }
    }
    repositories(ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC, first: 100) {
      totalCount
      nodes { languages(first: 12) { edges { size node { name } } } }
    }
  }
}"""


def fetch() -> dict:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        raise SystemExit("set GITHUB_TOKEN (or GH_TOKEN)")
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json",
                 "User-Agent": "calibre-ledger"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if "errors" in data:
        raise SystemExit(json.dumps(data["errors"]))
    return data["data"]["user"]


def summarise(user: dict) -> dict:
    cal = user["contributionsCollection"]["contributionCalendar"]
    days = [(d["date"], d["contributionCount"]) for w in cal["weeks"] for d in w["contributionDays"]]
    langs: dict[str, int] = {}
    for repo in user["repositories"]["nodes"]:
        for e in repo["languages"]["edges"]:
            langs[e["node"]["name"]] = langs.get(e["node"]["name"], 0) + e["size"]
    longest = run = 0
    for _, c in days:
        run = run + 1 if c else 0
        longest = max(longest, run)
    busiest = max(days, key=lambda d: d[1])
    return {
        "total": cal["totalContributions"], "weeks": [[d["contributionCount"] for d in w["contributionDays"]]
                                                      for w in cal["weeks"]],
        "first": days[0][0], "last": days[-1][0], "active": sum(1 for _, c in days if c),
        "longest": longest, "busiest": busiest, "repos": user["repositories"]["totalCount"], "langs": langs,
    }


def build(p: dict, s: dict) -> str:
    uid = f"lg{p['name'][0]}"
    dark = p["name"] == "dark"
    cx, cy = 330, H / 2 + 6
    r_in, r_out = 92, 238
    weeks = s["weeks"]
    nw = len(weeks)
    counts = sorted(c for w in weeks for c in w if c)
    q = [counts[int(len(counts) * k)] if counts else 1 for k in (0.25, 0.5, 0.75)] if counts else [1, 2, 3]

    def level(c):
        if not c:
            return 0
        return 1 + sum(c > t for t in q)

    style = (f".hand{{transform-origin:{cx}px {f(cy)}px;animation:hand 36s linear infinite}}"
             "@keyframes hand{to{transform:rotate(360deg)}}"
             ".rise{animation:rise 1.2s cubic-bezier(.2,.7,.2,1) both}"
             "@keyframes rise{from{opacity:.35}to{opacity:1}}"
             ".lume{animation:lume 4s ease-in-out infinite}@keyframes lume{0%,100%{opacity:.4}50%{opacity:1}}")
    defs = (f'<radialGradient id="{uid}vig" cx=".3" cy=".5" r=".8"><stop offset="0" stop-color="{p["case_hi"]}"/>'
            f'<stop offset="1" stop-color="{p["case"]}"/></radialGradient>')
    body = f'<rect width="{W}" height="{H}" rx="18" fill="url(#{uid}vig)"/>'
    # the dial
    body += (f'<circle cx="{cx}" cy="{f(cy)}" r="{r_out + 26}" fill="{p["plate"]}" stroke="{p["steel"]}" stroke-width="1.2"/>'
             f'<circle cx="{cx}" cy="{f(cy)}" r="{r_out + 20}" fill="none" stroke="{p["steel_faint"]}" stroke-width=".6"/>'
             f'<circle cx="{cx}" cy="{f(cy)}" r="{r_in - 12}" fill="none" stroke="{p["steel_faint"]}" stroke-width=".6"/>')
    ring_w = (r_out - r_in) / 7
    marks = {lv: [] for lv in range(5)}
    for wi, week in enumerate(weeks):
        a = -math.pi / 2 + wi / nw * math.tau
        for di, c in enumerate(week):
            r = r_in + (di + 0.5) * ring_w
            lv = level(c)
            x, y = cx + r * math.cos(a), cy + r * math.sin(a)
            size = (1.1, 2.0, 2.7, 3.4, 4.2)[lv]
            marks[lv].append(f"M{f(x - size)},{f(y)}a{f(size)},{f(size)} 0 1 0 {f(2 * size)},0a{f(size)},{f(size)} 0 1 0 {f(-2 * size)},0")
    fills = {0: (p["steel_faint"], 1), 1: (p["lume"], .35), 2: (p["lume"], .6), 3: (p["lume"], .85), 4: (p["lume"], 1)}
    for lv, ds in marks.items():
        col, op = fills[lv]
        body += f'<path class="rise" style="animation-delay:{0.2 + lv * 0.25}s" d="{"".join(ds)}" fill="{col}" opacity="{op}"/>'
    # months around the rim
    first = dt.date.fromisoformat(s["first"])
    seen = set()
    for wi in range(nw):
        d = first + dt.timedelta(weeks=wi)
        if d.month in seen or d.day > 7:
            continue
        seen.add(d.month)
        a = -math.pi / 2 + wi / nw * math.tau
        tx, ty = cx + (r_out + 13) * math.cos(a), cy + (r_out + 13) * math.sin(a)
        body += (f'<path d="M{G.pt(cx, cy, r_out + 3, a)}L{G.pt(cx, cy, r_out + 8, a)}" stroke="{p["steel"]}" stroke-width=".8"/>'
                 + f'<g transform="rotate({f(math.degrees(a) + (90 if math.sin(a) <= 0.05 else -90))} {f(tx)} {f(ty)})">'
                 + kit.txt(d.strftime("%b").upper(), "martian-light", 7, tx, ty + 2.5, p["ink_dim"], 0.2, "middle") + "</g>")
    # the hand that sweeps the year, and the centre
    body += (f'<g class="hand"><path d="M{cx},{f(cy + 14)}L{cx},{f(cy - r_out - 18)}" stroke="{p["blued"] if not dark else p["blued_hi"]}" '
             f'stroke-width="1.6" stroke-linecap="round"/><circle cx="{cx}" cy="{f(cy - r_out - 18)}" r="3" fill="{p["lume"]}"/></g>'
             f'<circle cx="{cx}" cy="{f(cy)}" r="{r_in - 16}" fill="{p["case"]}" stroke="{p["steel_dim"]}" stroke-width=".7"/>'
             + kit.txt(f"{s['total']:,}", "bodoni-display", 46, cx, cy + 10, p["ink"], 0.0, "middle")
             + kit.txt("CONTRIBUTIONS", "martian-light", 6.8, cx, cy + 30, p["ink_dim"], 0.26, "middle")
             + kit.txt("LAST 12 MONTHS", "martian-light", 6.8, cx, cy - 38, p["ink_dim"], 0.26, "middle"))

    # the right-hand column: figures and the language reserve
    x0 = 640
    body += (kit.txt("PERPETUAL CALENDAR", "martian", 9.5, x0, 72, p["salmon"], 0.32)
             + kit.txt(f"AS OF {dt.date.fromisoformat(s['last']).strftime('%d %b %Y').upper()}", "martian-light", 9,
                       W - 64, 72, p["ink_dim"], 0.3, "end")
             + f'<path d="M{x0},86H{W - 64}" stroke="{p["steel_dim"]}" stroke-width=".7"/>')
    busiest_date = dt.date.fromisoformat(s["busiest"][0]).strftime("%d %b %Y")
    figures = [("ACTIVE DAYS", f"{s['active']} of {sum(len(w) for w in weeks)}"),
               ("LONGEST RUN", f"{s['longest']} consecutive days"),
               ("BUSIEST DAY", f"{s['busiest'][1]} contributions, {busiest_date}"),
               ("PUBLIC REPOS", f"{s['repos']} owned, not forks")]
    y = 128
    for k, v in figures:
        body += (kit.txt(k, "martian-light", 8, x0, y, p["ink_faint"] if dark else p["ink_dim"], 0.26)
                 + kit.txt(v, "bodoni-text", 17, x0 + 168, y + 1, p["ink"])
                 + f'<path d="M{x0},{y + 11}H{W - 64}" stroke="{p["steel_faint"]}" stroke-width=".6"/>')
        y += 32
    # language reserve: one arc, segmented by bytes
    langs = sorted(s["langs"].items(), key=lambda kv: -kv[1])
    total = sum(v for _, v in langs) or 1
    top = langs[:6]
    other = total - sum(v for _, v in top)
    if other > 0:
        top.append(("Other", other))
    tones = [p["salmon"], p["blued"] if not dark else p["blued_hi"], p["lume"], p["silver"] if dark else p["steel"],
             p["copper"], p["steel_dim"], p["ink_faint"]]
    ax, ay, ar = x0 + 120, 470, 104
    a0, a1 = math.radians(180), math.radians(360)
    acc = a0
    body += (kit.txt(RES, "martian-light", kit.fit(RES, "martian-light", 8, W - 64 - x0, 0.26), x0, 300, p["ink_dim"], 0.26)
             + f'<path d="M{x0},{311}H{W - 64}" stroke="{p["steel_faint"]}" stroke-width=".6"/>')
    ly = 340
    for i, (name, v) in enumerate(top):
        span = (a1 - a0) * v / total
        gap = 0.012 if span > 0.03 else 0
        body += (f'<path class="rise" style="animation-delay:{0.6 + i * 0.15:.2f}s" d="{G.arc(ax, ay, ar, acc + gap, acc + span - gap)}" '
                 f'fill="none" stroke="{tones[i]}" stroke-width="16"/>')
        acc += span
        pct = 100 * v / total
        body += (f'<circle cx="{x0 + 270}" cy="{ly - 4}" r="4" fill="{tones[i]}"/>'
                 + kit.txt(name, "bodoni-text", 16, x0 + 284, ly + 1, p["ink"])
                 + kit.txt(f"{pct:.1f}%", "martian-light", 8.6, W - 64, ly, p["ink_dim"], 0.2, "end"))
        ly += 27
    body += (f'<path d="{G.ticks(ax, ay, ar + 14, 5, 40, .5)}" stroke="{p["steel_dim"]}" stroke-width=".5" '
             f'clip-path="url(#{uid}half)"/>')
    defs += f'<clipPath id="{uid}half"><rect x="{ax - ar - 30}" y="{ay - ar - 30}" width="{2 * ar + 60}" height="{ar + 30}"/></clipPath>'
    body += (kit.txt(SNAP, "martian-light", kit.fit(SNAP, "martian-light", 7.4, W - 64 - x0, 0.24), x0, H - 40,
                     p["ink_faint"] if dark else p["ink_dim"], 0.24)
             + f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="18" fill="none" stroke="{p["steel_faint"]}"/>')
    langs_desc = ", ".join(f"{n} {100 * v / total:.1f}%" for n, v in top)
    desc = (f"Ledger as of {s['last']}: {s['total']} public contributions in the last twelve months, drawn as a "
            f"perpetual calendar with one spoke per week and one ring per weekday. {s['active']} active days, a longest "
            f"run of {s['longest']} days, busiest day {s['busiest'][1]} contributions on {s['busiest'][0]}, "
            f"{s['repos']} public repositories. Languages by bytes: {langs_desc}. Redrawn weekly, not live.")
    return kit.doc(W, H, "Ledger: a year of public work", desc, style, defs, body, uid)


def main() -> None:
    user = fetch() if "--data" not in sys.argv else json.load(open(sys.argv[sys.argv.index("--data") + 1]))
    s = summarise(user)
    for p in THEMES:
        out = kit.write(f"ledger-{p['name']}.svg", build(p, s))
    print(f"ledger: {s['total']} contributions, {s['repos']} repos, {out.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
