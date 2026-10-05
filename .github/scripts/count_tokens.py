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
FILES = ("README.md", "TOKENMAXXING.md", "GLOSSARY.md", "RESOURCES.md", "CONTRIBUTING.md", "AGENTS.md")
# A ceiling, not a target. Raise it deliberately in a PR and say why.
BUDGET = 55_000
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
