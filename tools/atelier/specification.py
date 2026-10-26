"""The tech stack as a movement's specification sheet: eight registers, no logos, no badges.

Only tools already claimed in this profile or the portfolio are listed.
"""

from __future__ import annotations

import kit
from palette import THEMES

W = 1200

REGISTERS = [
    ("LANGUAGES", ["TypeScript", "Python", "JavaScript", "Java", "PHP", "SQL", "C", "HTML & CSS"]),
    ("INTERFACES", ["React", "Next.js", "Vue.js", "Angular", "Tailwind CSS"]),
    ("SERVICES", ["Node.js", "Express", "NestJS", "Django", "FastAPI", "Flask", "Laravel"]),
    ("DATA", ["PostgreSQL", "MySQL", "MongoDB", "Redis", "SQLite"]),
    ("INTELLIGENCE", ["PyTorch", "TensorFlow", "Keras", "scikit-learn", "OpenCV", "Pandas", "NumPy",
                      "LangChain", "Hugging Face", "AWS Bedrock"]),
    ("CLOUD", ["AWS · Lambda, SQS, CDK", "Google Cloud", "Oracle Cloud"]),
    ("DELIVERY", ["Docker", "Kubernetes", "Helm", "Terraform", "Ansible", "GitHub Actions"]),
    ("OBSERVATORY", ["Prometheus", "Grafana", "Nginx", "Git", "Jupyter", "Streamlit"]),
]

COLS, COL_W, X0 = 4, 268, 64
ROW_H = 26


def build(p: dict) -> str:
    uid = f"sp{p['name'][0]}"
    rows_per = [max(len(REGISTERS[r * COLS + c][1]) for c in range(COLS)) for r in range(2)]
    top = 108
    block_tops = [top, top + 70 + rows_per[0] * ROW_H + 30]
    H = block_tops[1] + 70 + rows_per[1] * ROW_H + 40
    total = sum(len(items) for _, items in REGISTERS)
    style = (".rise{opacity:0;animation:rise 1s cubic-bezier(.2,.7,.2,1) forwards}"
             "@keyframes rise{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}"
             ".lume{animation:lume 8s ease-in-out infinite;opacity:.25}"
             "@keyframes lume{0%,100%{opacity:.25}6%,14%{opacity:1}22%{opacity:.25}}")
    body = (kit.txt("MOVEMENT SPECIFICATION", "martian", 10, X0, 52, p["salmon"], 0.34)
            + kit.txt(f"CALIBRE FKR·26 · {total} COMPONENTS · {len(REGISTERS)} REGISTERS", "martian-light", 9,
                      W - X0, 52, p["ink_dim"], 0.3, "end")
            + f'<path d="M{X0},66H{W - X0}" stroke="{p["steel_dim"]}" stroke-width=".8"/>'
            + f'<path d="M{X0},70H{W - X0}" stroke="{p["steel_faint"]}" stroke-width=".5"/>')
    n = 0
    for idx, (name, items) in enumerate(REGISTERS):
        r, c = divmod(idx, COLS)
        x = X0 + c * (COL_W + 8)
        y = block_tops[r]
        body += (f'<circle class="lume" style="animation-delay:{idx}s" cx="{x + 4}" cy="{y - 4}" r="3" fill="{p["lume"]}"/>'
                 + kit.txt(name, "martian", 9, x + 16, y, p["ink"], 0.3)
                 + kit.txt(f"{len(items):02d}", "martian-light", 9, x + COL_W - 22, y, p["ink_dim"], 0.2, "end")
                 + f'<path d="M{x},{y + 14}H{x + COL_W - 22}" stroke="{p["steel_dim"]}" stroke-width=".7"/>')
        for i, item in enumerate(items):
            iy = y + 44 + i * ROW_H
            n += 1
            body += (f'<g class="rise" style="animation-delay:{0.15 + idx * 0.12 + i * 0.05:.2f}s">'
                     + kit.txt(f"{n:02d}", "martian-light", 7.4, x, iy, p["ink_faint"] if p["name"] == "dark" else p["ink_dim"], 0.2)
                     + kit.txt(item, "bodoni-text", 17, x + 30, iy + 1, p["ink"])
                     + f'<path d="M{x + 30},{iy + 9}H{x + COL_W - 22}" stroke="{p["steel_faint"]}" stroke-width=".5"/></g>')
    body += (f'<path d="M{X0},{H - 22}H{W - X0}" stroke="{p["steel_faint"]}" stroke-width=".5"/>'
             + kit.txt("NO SKILL BARS, NO PERCENTAGES · WHAT IS PROVEN IS IN THE PROVENANCE TABLE",
                       "martian-light", 7.4, X0, H - 6, p["ink_dim"], 0.22))
    desc = "Movement specification, the tech stack in eight registers: " + "; ".join(
        f"{name.lower()}: {', '.join(items)}" for name, items in REGISTERS) + "."
    return kit.doc(W, H, "Specification: the tools in use", desc, style, "", body, uid)


def main() -> None:
    for p in THEMES:
        out = kit.write(f"specification-{p['name']}.svg", build(p))
    print(f"specification: {out.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
