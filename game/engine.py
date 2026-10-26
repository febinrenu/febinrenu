"""Out-decide my model: a Reclaim-style recovery game played through GitHub issues.

Every case is a failed payment. The visitor picks RECOVER, ESCALATE or LEAVE; a toy
version of Reclaim's model picks too. Both picks are scored by their true expected
value on the same case, so nobody wins on a lucky coin flip.

The model sees every structured field on the card. It cannot read the free-text
note, and the note moves the true recovery probability. That is the whole game:
a human who reads the note can beat a calibrated model that cannot.

Stdlib only. Usage:
    python game/engine.py play --title "reclaim|leave|3" --user octocat --comment-out out.md
    python game/engine.py render      # rebuild README block + case card from state
    python game/engine.py selftest
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import random
import re
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "game" / "state.json"
README = ROOT / "README.md"
WAGER = ROOT / "assets" / "calibre" / "wager"
WAGER_URL = "assets/calibre/wager"
REPO = "febinrenu/febinrenu"

START, END = "<!-- GAME:START -->", "<!-- GAME:END -->"
TITLE_RE = re.compile(r"^reclaim\|(recover|escalate|leave)\|(\d{1,6})$")
ACTIONS = ("recover", "escalate", "leave")
LABEL = {"recover": "RECOVER", "escalate": "ESCALATE", "leave": "LEAVE IT"}

# --- the world ---------------------------------------------------------------

REASONS = [  # (code, weight, logit effect)
    ("insufficient_funds", 35, 0.35),
    ("do_not_honor", 20, -0.40),
    ("card_expired", 15, -0.10),
    ("network_error", 15, 1.10),
    ("suspected_fraud", 15, -0.90),
]
CHANNELS = [("UPI", 0.25), ("card", 0.0), ("netbanking", -0.15)]

# Free-text notes: the model cannot read these. Their effect goes straight into
# the true probability.
NOTES = [
    ("“salary comes on the 1st, please retry then”", 1.6),
    ("updated their card in the profile yesterday", 1.9),
    ("opened the payment-link email three times", 1.0),
    ("replied: “didn't mean to cancel, fix it?”", 1.4),
    ("no reply to two reminders", -0.3),
    ("email hard-bounced, phone unreachable", -1.6),
    ("said on chat they're switching providers", -2.0),
    ("same device paid for three other accounts today", -2.4),
    ("no notes on file", 0.0),
    ("no notes on file", 0.0),
]

RETRY_FIXED, RETRY_RATE = 20.0, 0.03        # gateway + messaging cost of a retry
FAILED_RETRY = 0.40                         # goodwill and churn a failed retry burns, as a share of the amount
REVIEW_COST = 1200.0                        # a human's time on one case
REVIEW_LIFT = 0.20                          # share of the remaining gap a human closes
FAILED_REVIEW = 0.10                        # a failed human follow-up burns far less goodwill
FRAUD_CLAWBACK = 0.5                        # share of a recovered suspected-fraud payment later charged back


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def case(n: int) -> dict:
    """Deterministic case for case number n."""
    rng = random.Random(hashlib.sha256(f"reclaim-case-{n}".encode()).hexdigest())
    amount = int(round(math.exp(rng.uniform(math.log(299), math.log(42000))) / 10.0) * 10)
    reason = rng.choices([r[0] for r in REASONS], weights=[r[1] for r in REASONS])[0]
    attempts = rng.choices([0, 1, 2, 3], weights=[40, 30, 20, 10])[0]
    tenure = rng.randint(0, 48)
    past_paid = rng.randint(0, min(tenure, 24))
    channel = rng.choice([c[0] for c in CHANNELS])
    note, note_effect = rng.choice(NOTES)
    noise = rng.gauss(0.0, 0.35)
    return {
        "n": n, "amount": amount, "reason": reason, "attempts": attempts,
        "tenure": tenure, "past_paid": past_paid, "channel": channel,
        "note": note, "_hidden": note_effect + noise,
    }


def model_logit(c: dict) -> float:
    reason = dict((r[0], r[2]) for r in REASONS)[c["reason"]]
    channel = dict(CHANNELS)[c["channel"]]
    return (-1.10 + reason + channel - 0.55 * c["attempts"] + 0.02 * c["tenure"]
            + 0.07 * c["past_paid"] - 0.35 * math.log10(c["amount"] / 1000.0))


def p_model(c: dict) -> float:
    return _sigmoid(model_logit(c))


def p_true(c: dict) -> float:
    return _sigmoid(model_logit(c) + c["_hidden"])


def ev(action: str, c: dict, p: float) -> float:
    a = c["amount"]
    clawback = FRAUD_CLAWBACK if c["reason"] == "suspected_fraud" else 0.0
    if action == "recover":
        return p * a * (1 - clawback) - RETRY_RATE * a - RETRY_FIXED - (1 - p) * FAILED_RETRY * a
    if action == "escalate":
        ph = p + REVIEW_LIFT * (1 - p)  # a human also catches the fraud, so no clawback
        return ph * a - RETRY_RATE * a - REVIEW_COST - (1 - ph) * FAILED_REVIEW * a
    return 0.0


def model_action(c: dict) -> str:
    p = p_model(c)
    return max(ACTIONS, key=lambda act: (round(ev(act, c, p), 6), -ACTIONS.index(act)))


# --- state -------------------------------------------------------------------

def fresh_state() -> dict:
    return {"case": 1, "humans": 0.0, "model": 0.0,
            "rounds": {"won": 0, "tied": 0, "lost": 0},
            "moves": [], "players": {}, "updated": None}


def load_state() -> dict:
    return json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else fresh_state()


def save_state(s: dict) -> None:
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(s, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def apply_move(s: dict, title: str, user: str, now: str | None = None) -> tuple[dict, str]:
    """Return (new_state, comment). State is unchanged for invalid or stale moves."""
    m = TITLE_RE.match(title.strip())
    if not m:
        return s, ("That title isn't a move. Pick a button on the "
                   f"[profile](https://github.com/{REPO}) and submit the issue as it opens.")
    action, n = m.group(1), int(m.group(2))
    if n != s["case"]:
        return s, (f"Case #{n} has already been played. Someone got there first. "
                   f"Case #{s['case']} is live now on the [profile](https://github.com/{REPO}#out-decide-my-model).")

    c = case(n)
    pt, pm = p_true(c), p_model(c)
    mine, theirs = action, model_action(c)
    ev_h, ev_m = round(ev(mine, c, pt)), round(ev(theirs, c, pt))
    delta = ev_h - ev_m
    result = "won" if delta > 0 else "lost" if delta < 0 else "tied"

    s = json.loads(json.dumps(s))
    s["case"] = n + 1
    s["humans"] += ev_h
    s["model"] += ev_m
    s["rounds"][result] += 1
    s["moves"] = ([{"case": n, "user": user, "action": mine, "model_action": theirs,
                    "human_ev": ev_h, "model_ev": ev_m, "p_true": round(pt, 2),
                    "p_model": round(pm, 2)}] + s["moves"])[:5]
    pl = s["players"].setdefault(user, {"edge": 0, "moves": 0, "won": 0})
    pl["edge"] += delta
    pl["moves"] += 1
    pl["won"] += result == "won"
    s["updated"] = now or dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    verdict = {"won": f"**You beat the model by {rupees(delta)}.**",
               "lost": f"**The model beat you by {rupees(-delta)}.**",
               "tied": "**A tie.** Same call, or the same value."}[result]
    hint = ""
    if abs(pt - pm) >= 0.15:
        hint = (f" The note (_{c['note']}_) moved the real odds "
                f"{'up' if pt > pm else 'down'} by {abs(pt - pm) * 100:.0f} points, and the model can't read notes.")
    comment = (
        f"### Case #{n}: {rupees(c['amount'])}, {c['reason'].replace('_', ' ')}\n\n"
        f"You chose **{LABEL[mine]}**. The model chose **{LABEL[theirs]}**.\n\n"
        f"| | your call | model's call |\n|---|---|---|\n"
        f"| action | {LABEL[mine]} | {LABEL[theirs]} |\n"
        f"| expected value at the true odds | {signed(ev_h)} | {signed(ev_m)} |\n\n"
        f"True recovery probability was **{pt:.0%}**. The model estimated {pm:.0%}.{hint}\n\n"
        f"{verdict} Humans are now at {signed(s['humans'])}, the model at {signed(s['model'])}.\n\n"
        f"Case #{s['case']} is dealt: [play it](https://github.com/{REPO}#out-decide-my-model)."
    )
    return s, comment


# --- rendering ---------------------------------------------------------------

def rupees(x: float) -> str:
    return f"₹{abs(int(round(x))):,}"


def signed(x: float) -> str:
    x = int(round(x))
    return ("+" if x > 0 else "−" if x < 0 else "±") + rupees(x)


def retries(k: int) -> str:
    return f"{k} prior {'retry' if k == 1 else 'retries'}"


def esc(t: str) -> str:
    return (str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def issue_url(action: str, n: int) -> str:
    title = f"reclaim|{action}|{n}"
    body = ("Just press **Create** (or **Submit new issue**). A bot scores your call against "
            "the model in about a minute, comments with the result and closes this.")
    return f"https://github.com/{REPO}/issues/new?title={quote(title, safe='')}&body={quote(body, safe='')}"


def _themes():
    sys.path.insert(0, str(ROOT / "tools" / "atelier"))
    import kit  # noqa: E402  (stdlib-only typesetting shared with the rest of the profile)
    from palette import THEMES  # noqa: E402
    return kit, THEMES


def render_card(s: dict, p: dict) -> str:
    """The case as an engraved placard, in the profile's movement finish (dark or light)."""
    kit, _ = _themes()
    W, H = 1200, 420
    dark = p["name"] == "dark"
    uid = f"wg{p['name'][0]}"
    c = case(s["case"])
    reason = c["reason"].replace("_", " ")
    h, m = s["humans"], s["model"]
    span = max(abs(h), abs(m), 1.0)
    r = s["rounds"]
    last = s["moves"][0] if s["moves"] else None
    if last:
        d = last["human_ev"] - last["model_ev"]
        last_line = (f"LAST · @{last['user']} chose {LABEL[last['action']]} on N° {last['case']}, "
                     f"the model {LABEL[last['model_action']]} · humans {signed(d)}")
    else:
        last_line = "NO MOVES YET · THE FIRST VISITOR SETS THE SCOREBOARD"
    blue = p["blued_hi"] if dark else p["blued"]
    style = (".lume{animation:lume 2.4s ease-in-out infinite}@keyframes lume{0%,100%{opacity:.3}50%{opacity:1}}"
             ".grow{transform-box:fill-box;transform-origin:left;animation:grow 1.6s cubic-bezier(.2,.8,.2,1) both}"
             "@keyframes grow{from{transform:scaleX(0)}}")
    defs = (f'<radialGradient id="{uid}v" cx=".3" cy=".5" r=".8"><stop offset="0" stop-color="{p["case_hi"]}"/>'
            f'<stop offset="1" stop-color="{p["case"]}"/></radialGradient>')
    t = kit.txt
    body = (f'<rect width="{W}" height="{H}" rx="18" fill="url(#{uid}v)"/>'
            + t(f"THE WAGER · CASE N° {c['n']:04d}", "martian", 9.5, 64, 66, p["salmon"], 0.32)
            + f'<circle class="lume" cx="560" cy="62" r="3.6" fill="{p["lume"]}"/>'
            + t("YOUR MOVE", "martian", 9, 574, 66, p["ink"], 0.32)
            + f'<path d="M64,80H640" stroke="{p["steel_dim"]}" stroke-width=".7"/>'
            + t("FAILED PAYMENT", "martian-light", 8.4, 64, 112, p["ink_dim"], 0.3)
            + t(rupees(c["amount"]), "bodoni-text", 72, 60, 184, p["ink"])
            + t(reason, "bodoni-display-italic", 26, 64, 222, p["salmon"] if dark else p["copper"]))
    fields = [("PRIOR RETRIES", str(c["attempts"])), ("CUSTOMER FOR", f"{c['tenure']} months"),
              ("PAST PAYMENTS OK", str(c["past_paid"])), ("CHANNEL", c["channel"])]
    for i, (k, v) in enumerate(fields):
        x = 64 + (i % 2) * 300
        y = 262 + (i // 2) * 34
        body += (t(k, "martian-light", 7.8, x, y, p["ink_faint"] if dark else p["ink_dim"], 0.26)
                 + t(v, "bodoni-text", 17, x + 150, y + 1, p["ink"])
                 + f'<path d="M{x},{y + 11}H{x + 270}" stroke="{p["steel_faint"]}" stroke-width=".6"/>')
    body += (f'<rect x="64" y="{H - 82}" width="576" height="50" rx="10" fill="none" stroke="{p["lume"]}" '
             f'stroke-opacity=".55"/>'
             + t("NOTE ON FILE · THE MODEL CAN'T READ THIS", "martian-light", 7.6, 82, H - 61, p["lume"], 0.26)
             + t(c["note"], "bodoni-text-italic", 16, 82, H - 42, p["ink"]))
    # the scoreboard
    x0 = 720
    body += (t("HUMANS AGAINST THE MODEL · NET RECOVERED", "martian-light", 8.4, x0, 112, p["ink_dim"], 0.28)
             + f'<path d="M{x0},124H{W - 64}" stroke="{p["steel_faint"]}" stroke-width=".6"/>')
    for i, (who, v, col) in enumerate((("Humans", h, p["salmon"] if dark else p["copper"]), ("The model", m, blue))):
        y = 170 + i * 70
        bar = max(4.0, 416 * abs(v) / span)
        body += (t(who, "bodoni-display", 26, x0, y, p["ink"])
                 + t(signed(v), "martian", 12, W - 64, y - 4, p["ink"], 0.1, "end")
                 + f'<rect x="{x0}" y="{y + 12}" width="416" height="6" rx="3" fill="{p["steel_faint"]}"/>'
                 + f'<rect class="grow" x="{x0}" y="{y + 12}" width="{bar:.1f}" height="6" rx="3" '
                   f'fill="{col if v >= 0 else p["ruby"]}"/>')
    body += (t(f"ROUNDS · HUMANS WON {r['won']} · TIED {r['tied']} · LOST {r['lost']}", "martian-light", 8.4, x0,
               H - 112, p["ink_dim"], 0.26)
             + "".join(t(ln, "martian-light", 7.6, x0, H - 86 + 16 * i, p["ink_dim"], 0.2)
                       for i, ln in enumerate(wrap(kit, last_line, 416)[:2]))
             + t("PICK A PLAQUE BELOW", "martian", 8.4, x0, H - 40, p["ink"], 0.3)
             + f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="18" fill="none" stroke="{p["steel_faint"]}"/>')
    desc = (f"Case {c['n']}: a failed payment of {rupees(c['amount'])}, reason {reason}, {retries(c['attempts'])}, "
            f"customer for {c['tenure']} months, {c['past_paid']} past payments succeeded, paid by {c['channel']}. "
            f"Note on file, which the model cannot read: {c['note']}. Scoreboard: humans {signed(h)}, model {signed(m)}; "
            f"rounds won {r['won']}, tied {r['tied']}, lost {r['lost']}.")
    return kit.doc(W, H, f"The Wager, case {c['n']}", desc, style, defs, body, uid)


def wrap(kit, text: str, width: float) -> list[str]:
    """Greedy word wrap by measured width in the engraved micro-type."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = f"{cur} {word}".strip()
        if cur and kit.width(trial, "martian-light", 7.6, 0.2) > width:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    return lines + [cur]


def render_plaque(action: str, p: dict) -> str:
    """An engraved steel plaque for one move. Static apart from a slow glint."""
    kit, _ = _themes()
    W, H = 380, 110
    dark = p["name"] == "dark"
    uid = f"pq{action[0]}{p['name'][0]}"
    words = {"recover": ("Recover", "RETRY THE PAYMENT"), "escalate": ("Escalate", "SEND IT TO A HUMAN"),
             "leave": ("Leave it", "DO NOTHING, ON PURPOSE")}[action]
    delay = {"recover": 0, "escalate": 1.2, "leave": 2.4}[action]
    style = (f".gl{{animation:gl 7s ease-in-out {delay}s infinite}}"
             "@keyframes gl{0%,70%{transform:translateX(-120px)}90%,100%{transform:translateX(520px)}}")
    defs = (f'<linearGradient id="{uid}m" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{p["case_hi"]}"/>'
            f'<stop offset="1" stop-color="{p["case"]}"/></linearGradient>'
            f'<linearGradient id="{uid}g" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
            f'<stop offset=".5" stop-color="#fff" stop-opacity="{".08" if dark else ".5"}"/>'
            f'<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
            f'<clipPath id="{uid}c"><rect x="4" y="4" width="{W - 8}" height="{H - 8}" rx="14"/></clipPath>'
            f'<radialGradient id="{uid}b" cx=".35" cy=".3" r=".8"><stop offset="0" stop-color="{p["blued_hi"]}"/>'
            f'<stop offset="1" stop-color="{p["blued"]}"/></radialGradient>')
    screws = "".join(f'<circle cx="{x}" cy="{y}" r="4.4" fill="url(#{uid}b)"/>'
                     f'<path d="M{x - 3.4},{y - .8}h6.8v1.6h-6.8z" fill="{p["case"]}" opacity=".8" '
                     f'transform="rotate({(x * 13 + y) % 90} {x} {y})"/>'
                     for x, y in ((22, 22), (W - 22, 22), (22, H - 22), (W - 22, H - 22)))
    body = (f'<rect x="4" y="7" width="{W - 8}" height="{H - 8}" rx="14" fill="#000" opacity="{".45" if dark else ".14"}"/>'
            f'<rect x="4" y="4" width="{W - 8}" height="{H - 8}" rx="14" fill="url(#{uid}m)" stroke="{p["steel"]}" '
            f'stroke-opacity=".7"/>'
            f'<rect x="10" y="10" width="{W - 20}" height="{H - 20}" rx="10" fill="none" stroke="{p["steel_faint"]}"/>'
            + screws
            + kit.txt(words[0], "bodoni-display", 32, W / 2, 62, p["ink"], 0.01, "middle")
            + kit.txt(words[1], "martian-light", 7.6, W / 2, 84, p["ink_dim"], 0.3, "middle")
            + f'<g clip-path="url(#{uid}c)"><rect class="gl" x="0" y="0" width="90" height="{H}" fill="url(#{uid}g)" '
              f'transform="skewX(-20)"/></g>')
    return kit.doc(W, H, f"{words[0]}: {words[1].lower()}", f"Play this case: {words[0].lower()}.", style, defs, body, uid)


def picture(src_dark: str, src_light: str, alt: str, width: str) -> str:
    return (f'<picture><source media="(prefers-color-scheme: dark)" srcset="{src_dark}"/>'
            f'<img src="{src_light}" width="{width}" alt="{esc(alt)}"/></picture>')


def render_block(s: dict) -> str:
    n = s["case"]
    c = case(n)
    plaques = "".join(
        f'<a href="{issue_url(a, n)}">'
        + picture(f"{WAGER_URL}/plaque-{a}-dark.svg", f"{WAGER_URL}/plaque-{a}-light.svg", LABEL[a], "32%")
        + "</a>"
        for a in ACTIONS)
    alt = (f"Case {n}: {rupees(c['amount'])} failed payment, {c['reason'].replace('_', ' ')}, "
           f"{retries(c['attempts'])}, customer for {c['tenure']} months, {c['past_paid']} past payments ok, "
           f"via {c['channel']}. Note: {c['note']}. Humans {signed(s['humans'])}, model {signed(s['model'])}.")
    lines = [START,
             picture(f"{WAGER_URL}/case-dark.svg?v={n}", f"{WAGER_URL}/case-light.svg?v={n}", alt, "100%"),
             "",
             f'<p align="center">{plaques}</p>',
             ""]
    if s["moves"]:
        lines += ["| case | player | their call | model's call | edge |", "|---|---|---|---|---|"]
        for mv in s["moves"]:
            lines.append(f"| N° {mv['case']} | @{mv['user']} | {LABEL[mv['action']]} | {LABEL[mv['model_action']]} "
                         f"| {signed(mv['human_ev'] - mv['model_ev'])} |")
        board = sorted(s["players"].items(), key=lambda kv: (-kv[1]["edge"], -kv[1]["moves"], kv[0]))[:10]
        lines += ["", "<details><summary><b>Leaderboard</b>: total edge over the model</summary>", "",
                  "| # | player | edge | moves | wins |", "|---|---|---|---|---|"]
        for i, (u, p) in enumerate(board, 1):
            lines.append(f"| {i} | @{u} | {signed(p['edge'])} | {p['moves']} | {p['won']} |")
        lines += ["", "</details>"]
    else:
        lines.append('<p align="center"><sub>No moves yet. The first visitor sets the scoreboard.</sub></p>')
    lines.append(END)
    return "\n".join(lines)


def write_readme(s: dict) -> None:
    text = README.read_text(encoding="utf-8")
    if START not in text or END not in text:
        raise SystemExit("README is missing the game markers")
    head, rest = text.split(START, 1)
    _, tail = rest.split(END, 1)
    README.write_text(head + render_block(s) + tail, encoding="utf-8", newline="\n")


def render_all(s: dict) -> None:
    _, themes = _themes()
    WAGER.mkdir(parents=True, exist_ok=True)
    for p in themes:
        (WAGER / f"case-{p['name']}.svg").write_text(render_card(s, p), encoding="utf-8", newline="\n")
        for a in ACTIONS:
            (WAGER / f"plaque-{a}-{p['name']}.svg").write_text(render_plaque(a, p), encoding="utf-8", newline="\n")
    write_readme(s)


# --- cli ---------------------------------------------------------------------

def selftest() -> None:
    assert case(7) == case(7) and case(7) != case(8)
    for n in range(1, 400):
        c = case(n)
        assert 299 <= c["amount"] <= 42000 and 0 < p_true(c) < 1
        assert model_action(c) in ACTIONS and ev("leave", c, 0.5) == 0
    acts = [model_action(case(n)) for n in range(1, 400)]
    assert all(acts.count(a) > 20 for a in ACTIONS), {a: acts.count(a) for a in ACTIONS}
    s = fresh_state()
    s2, msg = apply_move(s, "reclaim|leave|2", "a", now="t")
    assert s2 == s and "already been played" in msg
    s2, msg = apply_move(s, "hello", "a", now="t")
    assert s2 == s and "isn't a move" in msg
    s2, msg = apply_move(s, "reclaim|leave|1", "a", now="t")
    assert s2["case"] == 2 and sum(s2["rounds"].values()) == 1 and "Case #1" in msg
    assert s2["humans"] - s2["model"] == s2["players"]["a"]["edge"]
    block = render_block(s2)
    assert block.startswith(START) and block.endswith(END) and "reclaim%7Crecover%7C2" in block
    # the card and plaques render, as outlines only, in both finishes
    import xml.dom.minidom
    _, themes = _themes()
    for p in themes:
        for svg in [render_card(s2, p)] + [render_plaque(a, p) for a in ACTIONS]:
            xml.dom.minidom.parseString(svg.encode())
            assert "<text" not in svg and "<script" not in svg
    # a reader of the note should beat the model on average
    edge = 0.0
    for n in range(1, 2000):
        c = case(n)
        pe = _sigmoid(model_logit(c) + dict(NOTES)[c["note"]])
        edge += ev(max(ACTIONS, key=lambda a: ev(a, c, pe)), c, p_true(c)) - ev(model_action(c), c, p_true(c))
    assert edge > 0, edge
    print("selftest ok; note-reader edge over 2k cases:", rupees(edge))


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("play")
    p.add_argument("--title", required=True)
    p.add_argument("--user", required=True)
    p.add_argument("--comment-out", required=True)
    sub.add_parser("render")
    sub.add_parser("selftest")
    a = ap.parse_args()
    if a.cmd == "selftest":
        selftest()
    elif a.cmd == "render":
        render_all(load_state())
    else:
        s = load_state()
        s2, comment = apply_move(s, a.title, a.user)
        Path(a.comment_out).write_text(comment + "\n", encoding="utf-8")
        if s2 is not s:
            save_state(s2)
            render_all(s2)
        print(comment)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
