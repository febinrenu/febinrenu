"""Build every asset of the profile: python tools/atelier/build.py [--ledger]

--ledger also refetches the contribution data (needs GITHUB_TOKEN); otherwise the
ledger keeps whatever was last drawn, since the weekly Action owns it.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "game"))

import colophon  # noqa: E402
import dividers  # noqa: E402
import engine  # noqa: E402
import header  # noqa: E402
import plates  # noqa: E402
import specification  # noqa: E402

if __name__ == "__main__":
    header.main()
    dividers.main()
    plates.main()
    specification.main()
    colophon.main()
    engine.render_all(engine.load_state())
    print("wager: card, plaques and README block")
    if "--ledger" in sys.argv:
        import ledger  # noqa: E402
        ledger.main()
