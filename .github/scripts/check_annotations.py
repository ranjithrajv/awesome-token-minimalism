#!/usr/bin/env python3
"""Validate awesome-list annotation format and extract links.

Checks that every list entry (a bullet beginning with `- **[`) carries an
evidence grade from the controlled vocabulary, and flags common formatting
drift that makes the README harder to scan than it needs to be.

Usage:
    python check_annotations.py README.md
    python check_annotations.py --urls README.md   # print bare URLs, one per line
"""

from __future__ import annotations

import re
import sys

GRADES = ("[measured]", "[self-reported]", "[asserted]", "[negative]")

ENTRY_RE = re.compile(r"^\s*-\s+\*\*\[")
# A grade is one of the four tags, optionally compound with `/` to signal a
# split verdict, e.g. `[measured]/[asserted]` = the independent audit is
# measured, but the tool's own headline number is not.
GRADE_TAG = r"(?:measured|self-reported|asserted|negative)"
GRADE_RE = re.compile(rf"\[{GRADE_TAG}\](?:/\[{GRADE_TAG}\])*")
URL_RE = re.compile(r"\]\((https?://[^)\s]+)\)")


def extract_entries(lines: list[str]) -> list[tuple[int, str]]:
    out = []
    for n, line in enumerate(lines, start=1):
        if ENTRY_RE.match(line):
            out.append((n, line))
    return out


def check(lines: list[str], path: str) -> int:
    entries = extract_entries(lines)
    problems = 0

    if not entries:
        print(f"::error::{path}: no list entries found")
        return 1

    for n, line in entries:
        if not GRADE_RE.search(line):
            problems += 1
            print(f"::error file={path},line={n}::missing evidence grade "
                  f"(need one of: {', '.join(GRADES)})")
            continue

        # Grades must appear at the end of the line so the rendered list reads
        # consistently. Compound grades (`[measured]/[asserted]`) are allowed
        # and count as one annotation.
        grades = GRADE_RE.findall(line)
        if len(grades) > 1:
            problems += 1
            print(f"::warning file={path},line={n}::{len(grades)} separate grade "
                  f"tags on one line; use a compound grade "
                  f"(e.g. `[measured]/[asserted]`) if the verdict is split")

        if "](http" not in line and "](https" not in line:
            problems += 1
            print(f"::warning file={path},line={n}::entry is not linked")

    print(f"{path}: {len(entries)} entries checked, {problems} problem(s)")
    return 1 if problems else 0


def urls(lines: list[str]) -> int:
    seen: set[str] = set()
    for line in lines:
        for u in URL_RE.findall(line):
            if u not in seen:
                seen.add(u)
                print(u)
    return 0


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    want_urls = "--urls" in sys.argv

    if not args:
        print(__doc__)
        return 2

    rc = 0
    for path in args:
        with open(path, encoding="utf-8") as fh:
            lines = fh.read().splitlines()
        rc |= urls(lines) if want_urls else check(lines, path)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
