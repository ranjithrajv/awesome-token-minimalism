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

Undated entries are reported as *one* file-level annotation, not one per entry:
150 annotations on every PR is the per-turn tax this repo argues against, and it
trains reviewers to ignore the gate. `--report` emits the full roster as
markdown for the weekly `date-rot` issue, which is where it gets triaged.

Usage:
    python check_stamps.py README.md
    python check_stamps.py --strict README.md
    python check_stamps.py --report README.md TOKENMAXXING.md RESOURCES.md
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


def classify(
    lines: list[str], path: str
) -> tuple[int, int, list[tuple[int, int, list[str]]], list[int]]:
    """Split entries into (total, fresh, stale, undated).

    `stale` rows are (line_no, age_in_months, grades); `undated` is line numbers.
    Shared by the gate and the `--report` body so the two cannot disagree.
    """
    within = 0
    stale: list[tuple[int, int, list[str]]] = []
    missing: list[int] = []
    entries = entry_stamps(lines)
    for n, _line, grades, dates in entries:
        if not dates:
            missing.append(n)
            continue
        age = max(months_old(int(y), int(m)) for y, m in dates)
        if age > STALE_MONTHS:
            stale.append((n, age, grades))
        else:
            within += 1
    return len(entries), within, stale, missing


def check_stamps(lines: list[str], path: str) -> int:
    total, within, stale, missing = classify(lines, path)
    if not total:
        print(f"{path}: no graded entries to stamp")
        return 0

    print(
        f"{path}: {total} graded entries, "
        f"{within} within {STALE_MONTHS} months, "
        f"{len(stale)} stale, {len(missing)} undated"
    )

    # Stale stamps are few and each is actionable, so they stay per-entry.
    for n, age, grades in stale:
        print(
            f"::warning file={path},line={n}::stamp is {age} months old "
            f"(>{STALE_MONTHS}); re-run the measurement and say what changed"
        )

    # Undated entries run to the hundreds, and one annotation each is the
    # per-turn tax this repo argues against. One file-level annotation names
    # the count and a sample; the weekly date sweep carries the full roster.
    if missing:
        shown = ", ".join(str(n) for n in missing[:12])
        tail = "" if len(missing) <= 12 else f", +{len(missing) - 12} more"
        print(
            f"::warning file={path}::{len(missing)} undated entries "
            f"(lines {shown}{tail}); triaged in the weekly date-rot issue"
        )

    # The ratchet. Undated count is the quantity that can only be improved by
    # editing the entry, so a ceiling here is a floor on attention.
    ceiling = MAX_UNDATED.get(pathlib.Path(path).name)
    if ceiling is not None and len(missing) > ceiling:
        print(
            f"::error file={path}::{len(missing)} undated entries, over the "
            f"{ceiling} ceiling. Add the dates, and lower MAX_UNDATED in this "
            f"file in the same PR -- the ceiling is a ratchet, not a target."
        )
        return 1
    if ceiling is not None and len(missing) <= ceiling:
        headroom = ceiling - len(missing)
        if headroom:
            print(
                f"{path}: {headroom} under the {ceiling} ceiling -- lower "
                f"MAX_UNDATED to {len(missing)} to lock the gain in"
            )
    if FAIL_ON_STALE and stale:
        print(
            f"::error file={path}::{len(stale)} stale stamp(s) over "
            f"{STALE_MONTHS} months"
        )
        return 1
    return 0


def build_report(paths: list[str]) -> str:
    """Markdown date-coverage report for the weekly date-rot issue."""
    rows: list[tuple[str, int, int, int, int, int | None]] = []
    stale_all: list[tuple[str, int, int, str]] = []
    for path in paths:
        name = pathlib.Path(path).name
        lines = pathlib.Path(path).read_text(encoding="utf-8").splitlines()
        total, within, stale, missing = classify(lines, path)
        if not total:
            continue
        rows.append((name, total, within, len(stale), len(missing), MAX_UNDATED.get(name)))
        for n, age, grades in stale:
            stale_all.append((name, n, age, " ".join(grades)))

    out = ["## Date coverage", ""]
    out.append("| File | Graded | Fresh | Stale | Undated | Ceiling |")
    out.append("|---|---|---|---|---|---|")
    for name, total, within, n_stale, n_missing, ceiling in rows:
        out.append(
            f"| `{name}` | {total} | {within} | {n_stale} | {n_missing} | "
            f"{ceiling if ceiling is not None else '—'} |"
        )
    out.append("")
    if stale_all:
        out.append(f"### Stale stamps (> {STALE_MONTHS} months)")
        out.append("")
        for name, n, age, grades in stale_all:
            out.append(f"- `{name}:{n}` — {age} months old ({grades})")
        out.append("")
    else:
        out.append("No stale stamps. ")
        out.append("")
    out.append(
        "An undated entry is the repo's biggest credibility gap: a number with no "
        "date cannot be re-run. Adding a date — or lowering the `MAX_UNDATED` "
        "ceiling — is a high-value PR. See `AGENTS.md` for the stamp rules."
    )
    return "\n".join(out)


if __name__ == "__main__":
    args = sys.argv[1:]
    paths = [a for a in args if not a.startswith("--")]
    if not paths:
        print(__doc__)
        raise SystemExit(2)
    if "--report" in args:
        print(build_report(paths))
        raise SystemExit(0)
    if "--strict" in args:
        # One-invocation override of the module constant, so a PR can be checked
        # strictly without the file having to carry the stricter policy yet.
        globals()["FAIL_ON_STALE"] = True
    rc = 0
    for path in paths:
        rc |= check_stamps(pathlib.Path(path).read_text(encoding="utf-8").splitlines(), path)
    raise SystemExit(rc)
