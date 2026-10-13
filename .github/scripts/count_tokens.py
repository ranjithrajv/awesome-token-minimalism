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
    # The index an agent reads before it decides what to load. Metered for the
    # same reason the catalogs are: it is prose an agent loads, even though it
    # is the smallest file here.
    "llms.txt",
    # Split out of the README as one-file-each catalogs. Metered here rather
    # than left out: an agent that is asked about an anti-pattern or an open
    # problem loads the file, so the tax is real even though it is not the
    # always-loaded one. The README's always-loaded surface is what shrank.
    "ANTI-PATTERNS.md",
    "OPEN-PROBLEMS.md",
)
# A ceiling, not a target. Raise it deliberately in a PR and say why.
#
# Raised three times in 2026-10: 55000 -> 63000 when the two catalogs split out
# of the README, -> 63500 when llms.txt and the stamp gate landed, -> 64000 when
# the profiler entry and the open-problem-5 rewrite landed. Every raise is a
# real cost, not drift:
#
# 1. The meter was already ~5.4k over 55000 before the split, from content growth
#    on the Leg 3 (agent memory) and Output (run, don't generate) legs. Nobody
#    noticed, which is the failure mode this counter exists to catch. Saying so
#    here is the fix; doing it silently would have been the anti-pattern.
# 2. The split added ANTI-PATTERNS.md and OPEN-PROBLEMS.md to the metered set,
#    because an agent asked about an anti-pattern loads that file. Leaving them
#    out would have made the number smaller by not counting a real cost.
# 3. llms.txt is a third such file (~400 tokens): the machine-readable index
#    over the content docs, read to decide what to load. Same reasoning.
# 4. The stamp gate (check_stamps.py) needs two documented lines, in AGENTS.md
#    and CONTRIBUTING.md. A check nobody is told about is a check nobody runs.
# 5. The profiler entry in Leg 0 and the rewrite of open problem 5, both added
#    when token-harness profile landed. A tool that measures the window is the
#    thing the list said nobody had, so it gets an entry; the question it
#    answers gets narrowed to what an audit would still have to show.
#
# The alternative to (3), (4) and (5) was trimming llms.txt's descriptions until
# the repo had five tokens of headroom. That is the wrong trade: the meter exists
# to keep the always-loaded surface honest, and the always-loaded README is
# exactly what it was before this PR.
BUDGET = 64_000
# On-demand payload, printed for visibility but *not* charged to the budget.
#
# `entries.jsonl` is the machine-readable index over the entries -- name, URL,
# section, grade, date -- generated from README.md by build_entries.py and kept
# in sync by CI. It is excluded for the same reason code and tests are excluded
# further up: it is loaded when an agent asks a qualification question, not on
# every turn. An agent that asks spends ~10k tokens (chars/4) on it instead of
# ~37k on the README; an agent that does not ask spends nothing.
#
# That is a trade worth stating rather than hiding, because the alternative --
# metering it into the always-loaded ceiling -- would push the badge up by 10k
# for a file most readers never load. The number is printed below the total so
# nobody has to guess what the exclusion costs.
ON_DEMAND = ("entries.jsonl",)
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

    for name in ON_DEMAND:
        n, _ = count((root / name).read_text(encoding="utf-8"))
        print(f"  {'+ ' + name:<18} {n:>6}  (on-demand index, not metered above)")

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
