"""Colour tokens for Calibre FKR-26.

Two finishes of the same movement: a graphite case for dark mode and a silvered
opaline dial for light mode. The heat-blued steel and the lume are shared.
"""

DARK = {
    "name": "dark",
    "case": "#111214",        # graphite case
    "case_hi": "#1b1d20",     # gunmetal
    "plate": "#17191c",
    "perlage": "#24272b",
    "steel": "#9ba2a9",       # brushed steel
    "steel_dim": "#5d636a",
    "steel_faint": "#2e3237",
    "silver": "#dfe2e5",      # polished silver
    "ink": "#dfe2e5",         # primary type
    "ink_dim": "#8d949b",
    "ink_faint": "#4a4f55",
    "salmon": "#e3a387",      # dial
    "copper": "#b86f4f",
    "blued": "#2f56c9",       # heat-blued steel
    "blued_hi": "#6f8ff0",
    "lume": "#d8f5b2",        # Super-LumiNova
    "ruby": "#a3223f",        # jewels
    "shadow": "#000000",
}

LIGHT = {
    "name": "light",
    "case": "#efeee9",        # silvered opaline
    "case_hi": "#f7f6f2",
    "plate": "#e6e4de",
    "perlage": "#d9d6ce",
    "steel": "#6f767d",
    "steel_dim": "#9aa0a6",
    "steel_faint": "#d3d1ca",
    "silver": "#2a2d31",
    "ink": "#1d1f22",
    "ink_dim": "#5f656b",
    "ink_faint": "#a4a8ac",
    "salmon": "#c9775a",
    "copper": "#a35a3c",
    "blued": "#2447b3",
    "blued_hi": "#3b63d6",
    "lume": "#5d8f2c",        # lume reads as its daylight green on a light dial
    "ruby": "#9b1d38",
    "shadow": "#8c8a83",
}

THEMES = (DARK, LIGHT)
