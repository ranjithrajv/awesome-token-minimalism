#!/usr/bin/env python3
"""Detect evidence stamps that are missing or stale in the list.

This is the fifth check, added because the first four catch a missing grade and
a broken anchor but not a *decaying* one. AGENTS.md already says numbers decay
and that `[measured]` entries need model, harness, date, and n. Nothing looked.
In a field where prices, model names, and context limits move weekly, a date is
the only thing that tells a reader whether to re-run the measurement, so a
missing date is the most common form of an unmeasured default.

Two gates, both off by default, both opt-in:

`FAIL_ON_STALE = True`  -- a stamp older than STALE_MONTHS fails the run.
`--strict`              -- the same, for one invocation, without editing the file.

The third gate is a ratchet and it is *on*: `MAX_UNDATED` is a ceiling on how
many entries may carry no date at all, per file. Lower it in the PR that adds the
dates; the count can only fall. A ceiling rather than a target, same idiom as
the prose budget in count_tokens.py -- it stops the 149 from becoming 160
without anyone having to notice.

Usage:
    python check_stamps.py README.md
    python check_stamps.py --strict README.md
"""

from __future__ import annotations

import pathlib
import sys
from datetime import date

# The checkers are run by path (`python .github/scripts/check_stamps.py`), so
# the script's own directory is not on sys.path and the `entryspec` import below
# would fail. The same two lines appear in every script in this directory.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from entryspec import DATE_RE, graded_entries  # noqa: E402  (needs sys.path)

# Flip to True once entry coverage is high enough that a stale date should
# block a PR rather than annotate one.
FAIL_ON_STALE = False
# A measured number older than this is a candidate for re-running, not a lie.
STALE_MONTHS = 12
# Ceilings on undated entries, per file. A file not listed here is reported but
# not gated: a new catalog can land undated and be ratified in its own PR.
#
# Recorded 2026-10-13 at README 149, TOKENMAXXING 70, RESOURCES 27 -- 246 of 251
# graded entries, which is the number worth driving to zero. The alternative to
# a ceiling was a coverage percentage, which falls as the list grows and would
# have let a PR add 20 entries and 20 missing dates at once.
#
# README's 150 came down to 149 on the commit that gave the ccusage entry a
# stamp: the ratchet caught a real gain rather than being raised past it.
MAX_UNDATED = {
    "README.md": 149,
    "TOKENMAXXING.md": 70,
    "RESOURCES.md": 27,
}


def months_old(year: int, month: int, today: date | None = None) -> int:
    today = today or date.today()
    return (today.year - year) * 12 + (today.month - month)


def entry_stamps(lines: list[str]) -> list[tuple[int, str, list[str], list[str]]]:
    """Yield (line_no, line, grades, dates) for every graded list entry."""
    out: list[tuple[int, str, list[str], list[str]]] = []
    for n, line, grades in graded_entries(lines):
        out.append((n, line, grades, DATE_RE.findall(line)))
    return out


def check_stamps(lines: list[str], path: str) -> int:
    entries = entry_stamps(lines)
    if not entries:
        print(f"{path}: no graded entries to stamp")
        return 0

    missing = within = stale = 0
    for n, line, grades, dates in entries:
        if not dates:
            missing += 1
            print(
                f"::warning file={path},line={n}::graded entry carries no date "
                f"({' '.join(grades)}); "
                f"AGENTS.md asks for model, harness, date, and n"
            )
            continue
        ages = [months_old(int(y), int(m)) for y, m in dates]
        if max(ages) > STALE_MONTHS:
            stale += 1
            print(
                f"::warning file={path},line={n}::stamp is {max(ages)} months old "
                f"(>{STALE_MONTHS}); re-run the measurement and say what changed"
            )
        else:
            within += 1

    total = len(entries)
    print(
        f"{path}: {total} graded entries, "
        f"{within} within {STALE_MONTHS} months, "
        f"{stale} stale, {missing} undated"
    )
    # The ratchet. Undated count is the quantity that can only be improved by
    # editing the entry, so a ceiling here is a floor on attention.
    ceiling = MAX_UNDATED.get(pathlib.Path(path).name)
    if ceiling is not None and missing > ceiling:
        print(
            f"::error file={path}::{missing} undated entries, over the {ceiling} "
            f"ceiling. Add the dates, and lower MAX_UNDATED in this file in the "
            f"same PR -- the ceiling is a ratchet, not a target."
        )
        return 1
    if ceiling is not None and missing <= ceiling:
        headroom = ceiling - missing
        if headroom:
            print(
                f"{path}: {headroom} under the {ceiling} ceiling -- lower "
                f"MAX_UNDATED to {missing} to lock the gain in"
            )
    if FAIL_ON_STALE and stale:
        print(f"::error file={path}::{stale} stale stamp(s) over {STALE_MONTHS} months")
        return 1
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    strict = "--strict" in sys.argv
    paths = [a for a in args if not a.startswith("--")]
    if not paths:
        print(__doc__)
        raise SystemExit(2)
    if strict:
        # One-invocation override of the module constant, so a PR can be checked
        # strictly without the file having to carry the stricter policy yet.
        globals()["FAIL_ON_STALE"] = True
    rc = 0
    for path in paths:
        rc |= check_stamps(pathlib.Path(path).read_text(encoding="utf-8").splitlines(), path)
    raise SystemExit(rc)
