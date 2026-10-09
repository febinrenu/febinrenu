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
CARD = ROOT / "assets" / "game" / "case.svg"
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


def render_card(s: dict) -> str:
    c = case(s["case"])
    mono = "font-family:'SFMono-Regular',Consolas,'Liberation Mono',Menlo,monospace"
    reason = c["reason"].replace("_", " ")
    h, m = s["humans"], s["model"]
    span = max(abs(h), abs(m), 1.0)
    bar = lambda v: max(4.0, 250.0 * abs(v) / span)  # noqa: E731
    r = s["rounds"]
    last = s["moves"][0] if s["moves"] else None
    if last:
        d = last["human_ev"] - last["model_ev"]
        last_line = (f"last: @{last['user']} chose {LABEL[last['action']]} on #{last['case']}, "
                     f"model chose {LABEL[last['model_action']]} → humans {signed(d)}")
    else:
        last_line = "no moves yet: the first person to play sets the scoreboard"
    fields = [("prior retries", str(c["attempts"])), ("customer for", f"{c['tenure']} mo"),
              ("past payments ok", str(c["past_paid"])), ("channel", c["channel"])]
    rows = "".join(
        f'<text x="{36 + (i % 2) * 210}" y="{168 + (i // 2) * 40}" class="k">{esc(k)}</text>'
        f'<text x="{36 + (i % 2) * 210}" y="{186 + (i // 2) * 40}" class="v">{esc(v)}</text>'
        for i, (k, v) in enumerate(fields))
    return f"""<svg width="900" height="330" viewBox="0 0 900 330" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="t d">
  <title id="t">Out-decide my model, case {c['n']}</title>
  <desc id="d">Case {c['n']}: a failed payment of {rupees(c['amount'])}, reason {reason}, {retries(c['attempts'])}, customer for {c['tenure']} months, {c['past_paid']} past payments succeeded, paid by {c['channel']}. Note on file: {esc(c['note'])}. Scoreboard: humans {signed(h)}, model {signed(m)}, rounds won {r['won']}, tied {r['tied']}, lost {r['lost']}.</desc>
  <defs>
    <style>
      .bg {{ fill: #0d1117; }} .edge {{ fill: none; stroke: #30363d; }}
      text {{ {mono}; }}
      .tag {{ font-size: 11px; fill: #6e7681; letter-spacing: 2px; }}
      .amt {{ font-size: 40px; font-weight: 700; fill: #e6edf3; }}
      .k {{ font-size: 10.5px; fill: #6e7681; }} .v {{ font-size: 15px; fill: #e6edf3; font-weight: 700; }}
      .chip {{ font-size: 12px; fill: #0d1117; font-weight: 700; }}
      .note {{ font-size: 12.5px; fill: #f0e6c8; font-style: italic; }}
      .noteh {{ font-size: 10px; fill: #d29922; letter-spacing: 1px; }}
      .big {{ font-size: 13px; fill: #e6edf3; font-weight: 700; }} .sm {{ font-size: 11px; fill: #8b949e; }}
      .live {{ animation: blink 1.1s steps(2, start) infinite; }}
      .grow {{ transform-box: fill-box; transform-origin: left; animation: grow 1.6s cubic-bezier(.2,.8,.2,1) both; }}
      .scan {{ animation: scan 5s linear infinite; }}
      .glow {{ animation: glow 2.6s ease-in-out infinite; }}
      @keyframes blink {{ to {{ visibility: hidden; }} }}
      @keyframes grow {{ from {{ transform: scaleX(0); }} }}
      @keyframes scan {{ from {{ transform: translateY(-40px); }} to {{ transform: translateY(340px); }} }}
      @keyframes glow {{ 0%,100% {{ stroke-opacity: .35; }} 50% {{ stroke-opacity: 1; }} }}
    </style>
    <linearGradient id="sl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#58a6ff" stop-opacity="0"/><stop offset="1" stop-color="#58a6ff" stop-opacity=".07"/></linearGradient>
  </defs>
  <rect class="bg" x="1" y="1" width="898" height="328" rx="12"/>
  <rect class="scan" x="1" y="0" width="898" height="40" fill="url(#sl)"/>
  <rect class="edge" x="1" y="1" width="898" height="328" rx="12"/>

  <text x="36" y="40" class="tag">CASE #{c['n']:04d} · FAILED PAYMENT</text>
  <circle cx="545" cy="36" r="5" fill="#f85149" class="live"/>
  <text x="557" y="40" class="tag" style="fill:#f85149">YOUR MOVE</text>
  <text x="36" y="92" class="amt">{rupees(c['amount'])}</text>
  <rect x="36" y="108" width="{len(reason) * 7.6 + 20:.0f}" height="24" rx="12" fill="#d29922"/>
  <text x="46" y="124" class="chip">{esc(reason)}</text>
  {rows}

  <rect x="36" y="252" width="424" height="56" rx="8" fill="#1c1a12" stroke="#d29922" stroke-opacity=".5" class="glow"/>
  <text x="50" y="272" class="noteh">NOTE ON FILE · THE MODEL CAN'T READ THIS</text>
  <text x="50" y="294" class="note">{esc(c['note'])}</text>

  <line x1="490" y1="60" x2="490" y2="300" stroke="#21262d" stroke-width="2"/>
  <text x="520" y="92" class="tag">HUMANS vs MODEL · NET RECOVERED</text>
  <text x="520" y="128" class="big">humans</text>
  <text x="864" y="128" class="big" text-anchor="end">{signed(h)}</text>
  <rect x="520" y="138" width="344" height="12" rx="6" fill="#161b22"/>
  <rect x="520" y="138" width="{bar(h):.1f}" height="12" rx="6" fill="{'#3fb950' if h >= 0 else '#f85149'}" class="grow"/>
  <text x="520" y="182" class="big">model</text>
  <text x="864" y="182" class="big" text-anchor="end">{signed(m)}</text>
  <rect x="520" y="192" width="344" height="12" rx="6" fill="#161b22"/>
  <rect x="520" y="192" width="{bar(m):.1f}" height="12" rx="6" fill="{'#58a6ff' if m >= 0 else '#f85149'}" class="grow"/>
  <text x="520" y="236" class="sm">rounds · humans won {r['won']} · tied {r['tied']} · lost {r['lost']}</text>
  <text x="520" y="262" class="sm">{esc(last_line[:58])}</text>
  <text x="520" y="280" class="sm">{esc(last_line[58:116])}</text>
  <text x="520" y="306" class="tag">PICK BELOW ↓</text>
</svg>
"""


def render_block(s: dict) -> str:
    n = s["case"]
    c = case(n)
    buttons = "".join(
        f'<a href="{issue_url(a, n)}"><img src="assets/game/btn-{a}.svg" width="32%" alt="{LABEL[a]}"/></a>'
        for a in ACTIONS)
    alt = (f"Case {n}: {rupees(c['amount'])} failed payment, {c['reason'].replace('_', ' ')}, "
           f"{retries(c['attempts'])}, customer for {c['tenure']} months, {c['past_paid']} past payments ok, "
           f"via {c['channel']}. Note: {c['note']}. Humans {signed(s['humans'])}, model {signed(s['model'])}.")
    lines = [START,
             f'<img src="assets/game/case.svg?v={n}" width="100%" alt="{esc(alt)}"/>',
             "",
             f'<p align="center">{buttons}</p>',
             ""]
    if s["moves"]:
        lines += ["| case | player | their call | model's call | edge |", "|---|---|---|---|---|"]
        for mv in s["moves"]:
            lines.append(f"| #{mv['case']} | @{mv['user']} | {LABEL[mv['action']]} | {LABEL[mv['model_action']]} "
                         f"| {signed(mv['human_ev'] - mv['model_ev'])} |")
        board = sorted(s["players"].items(), key=lambda kv: (-kv[1]["edge"], -kv[1]["moves"], kv[0]))[:10]
        lines += ["", "<details><summary><b>Leaderboard</b>: total edge over the model</summary>", "",
                  "| # | player | edge | moves | wins |", "|---|---|---|---|---|"]
        for i, (u, p) in enumerate(board, 1):
            lines.append(f"| {i} | @{u} | {signed(p['edge'])} | {p['moves']} | {p['won']} |")
        lines += ["", "</details>"]
    else:
        lines.append("_No moves yet. The first click sets the scoreboard._")
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
    CARD.parent.mkdir(parents=True, exist_ok=True)
    CARD.write_text(render_card(s), encoding="utf-8", newline="\n")
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
