#!/usr/bin/env python3
"""Validate awesome-list annotation format, internal anchors, and links.

Three checks, because each has caught a real defect in this repo:

1. Every list entry (a bullet beginning with `- **[`) carries an evidence grade
   from the controlled vocabulary.
2. Every intra-document `](#anchor)` resolves to a real heading, using
   GitHub's slug algorithm (which percent-encodes emoji, drops em dashes, and
   maps *each* space to a hyphen without collapsing runs).
3. `--urls` extracts bare URLs for the link-health job.

Usage:
    python check_annotations.py README.md
    python check_annotations.py --urls README.md
"""

from __future__ import annotations

import re
import sys
import unicodedata
import urllib.parse

GRADES = ("measured", "self-reported", "asserted", "negative")

ENTRY_RE = re.compile(r"^\s*-\s+\*\*\[")
# A grade is one of the four tags, optionally compound with `/` to signal a
# split verdict, e.g. `[measured]/[asserted]` = the independent audit is
# measured, but the tool's own headline number is not.
GRADE_TAG = r"(?:" + "|".join(GRADES) + r")"
GRADE_RE = re.compile(rf"\[{GRADE_TAG}\](?:/\[{GRADE_TAG}\])*")
URL_RE = re.compile(r"\]\((https?://[^)\s]+)\)")
HEADING_RE = re.compile(r"^#{2,4}\s+(.+)$", re.M)
ANCHOR_RE = re.compile(r"\]\(#([^)]+)\)")


def gh_slug(heading: str) -> str:
    """Reproduce github-slugger's behaviour closely enough to validate anchors.

    Notable behaviours this must match, all of which produced broken links
    when ignored:
      * a space becomes a hyphen, and runs of spaces are NOT collapsed, so
        "Leg 0 — Measure" slugs to "leg-0--measure" once the em dash is dropped
      * emoji are kept and percent-encoded, including the variation selector,
        so "🕸️ Graph engineering" slugs to "%F0%9F%95%B8%EF%B8%8F-graph-engineering"
      * em dashes and other punctuation are dropped, not encoded
    """
    s = heading.strip().lower().replace("`", "")
    # inline links collapse to their text before slugging
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)
    kept = [
        c
        for c in s
        if c.isalnum()
        or c in " -_"
        or unicodedata.category(c) in ("So", "Sk")  # emoji, e.g. 🕸️
        or unicodedata.category(c) == "Mn"  # variation selector U+FE0F
    ]
    return urllib.parse.quote("".join(kept).replace(" ", "-"), safe="-_~")


def check_entries(lines: list[str], path: str) -> int:
    entries = [(n, ln) for n, ln in enumerate(lines, 1) if ENTRY_RE.match(ln)]
    problems = 0

    if not entries:
        print(f"::error::{path}: no list entries found")
        return 1

    for n, line in entries:
        if not GRADE_RE.search(line):
            problems += 1
            print(
                f"::error file={path},line={n}::missing evidence grade "
                f"(need one of: {', '.join('[' + g + ']' for g in GRADES)})"
            )
            continue

        # Grades must appear on the entry's first line, where the linter (and a
        # reader skimming the list) will see them.
        grades = GRADE_RE.findall(line)
        if len(grades) > 1:
            problems += 1
            print(
                f"::warning file={path},line={n}::{len(grades)} separate grade "
                f"tags on one line; use a compound grade "
                f"(e.g. `[measured]/[asserted]`) if the verdict is split"
            )

        if "](http" not in line:
            problems += 1
            print(f"::warning file={path},line={n}::entry is not linked")

    print(f"{path}: {len(entries)} entries checked, {problems} problem(s)")
    return 1 if problems else 0


def check_anchors(text: str, path: str) -> int:
    have = {gh_slug(h) for h in HEADING_RE.findall(text)}
    anchors = set(ANCHOR_RE.findall(text))
    missing = sorted(a for a in anchors if a not in have)
    for a in missing:
        print(f"::error file={path}::broken internal anchor #{a}")
    print(f"{path}: {len(anchors)} internal anchors checked, {len(missing)} broken")
    return 1 if missing else 0


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
        text = pathlib_read(path)
        lines = text.splitlines()
        if want_urls:
            rc |= urls(lines)
        else:
            rc |= check_entries(lines, path)
            rc |= check_anchors(text, path)
    return rc


def pathlib_read(path: str) -> str:
    with open(path, encoding="utf-8") as fh:
        return fh.read()


if __name__ == "__main__":
    raise SystemExit(main())
