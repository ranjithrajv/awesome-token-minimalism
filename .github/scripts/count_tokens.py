#!/usr/bin/env python3
"""Meter the list's own always-loaded prose.

This repo argues that every byte an agent auto-loads is a per-turn tax, so it
meters its own instruction surface. Counts the tracked prose files a reader or
contributor's agent loads, writes a shields.io endpoint badge, and optionally
fails when the total crosses a budget.

Tokenization uses `tiktoken` (cl100k_base) when importable, else a ~chars/4
estimate; the method used is printed so the number is never unstamped.

Usage:
    python count_tokens.py                 # print counts, write the badge
    python count_tokens.py --fail-over     # also exit 1 above BUDGET
"""

from __future__ import annotations

import json
import pathlib
import sys

# The prose an agent (or a reader) pays for. Code, tests, and CI are excluded:
# they run, they are not loaded into a context window on every turn.
FILES = (
    "README.md",
    "TOKENMAXXING.md",
    "GLOSSARY.md",
    "RESOURCES.md",
    "CONTRIBUTING.md",
    "AGENTS.md",
    # Split out of the README as one-file-each catalogs. Metered here rather
    # than left out: an agent that is asked about an anti-pattern or an open
    # problem loads the file, so the tax is real even though it is not the
    # always-loaded one. The README's always-loaded surface is what shrank.
    "ANTI-PATTERNS.md",
    "OPEN-PROBLEMS.md",
)
# A ceiling, not a target. Raise it deliberately in a PR and say why.
#
# Raised 55000 -> 63000 in the PR that split the two catalogs out of the README
# (2026-10), for three reasons, in order of size:
#
# 1. The meter was already ~5.4k over the old number before that PR, from
#    content growth on the Leg 3 (agent memory) and Output (run, don't generate)
#    legs. Nobody noticed, which is the failure mode this counter exists to
#    catch. Raising it silently would have been the wrong fix; saying so here
#    is the fix.
# 2. The split added ANTI-PATTERNS.md and OPEN-PROBLEMS.md to the metered set,
#    because an agent asked about an anti-pattern loads that file. Leaving them
#    out would have made the number smaller by not counting a real cost.
# 3. Net of the split itself, the metered set grew ~1.7k: two on-demand files
#    plus their index stubs and the doc updates, against a README that lost
#    ~2.7k of always-loaded prose.
#
# The always-loaded surface is the number worth holding down. README.md is now
# 38.9k of the 62.4k total; the two catalogs are 2.9k and are only paid when
# someone follows the link.
BUDGET = 63_000
BADGE_PATH = (".github", "badges", "tokens.json")


def count(text: str) -> tuple[int, str]:
    try:
        import tiktoken  # type: ignore[import-not-found]
    except ImportError:
        return len(text) // 4, "chars/4 estimate"
    return len(tiktoken.get_encoding("cl100k_base").encode(text)), "tiktoken/cl100k_base"


def main() -> int:
    root = pathlib.Path(__file__).resolve().parents[2]
    total = 0
    method = "chars/4 estimate"
    print("list prose token counts:")
    for name in FILES:
        text = (root / name).read_text(encoding="utf-8")
        n, method = count(text)
        total += n
        print(f"  {name:<18} {n:>6}")
    print(f"  {'TOTAL':<18} {total:>6}  ({method})")

    badge = {
        "schemaVersion": 1,
        "label": "list tokens",
        "message": f"{total / 1000:.1f}k",
        "color": "blue",
    }
    out = root.joinpath(*BADGE_PATH)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(badge) + "\n", encoding="utf-8")

    if "--fail-over" in sys.argv and total > BUDGET:
        print(f"::error::list prose is {total} tokens, over the {BUDGET} budget")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
