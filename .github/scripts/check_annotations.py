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
    python check_annotations.py --anchors-only GLOSSARY.md
    python check_annotations.py --allow-empty SHOWCASE.md
"""

from __future__ import annotations

import os
import pathlib
import re
import sys
import unicodedata
import urllib.parse

# The checkers are run by path (`python .github/scripts/check_annotations.py`),
# so the script's own directory is not on sys.path and the `entryspec` import
# below would fail. The same two lines appear in every script in this directory.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from entryspec import (  # needs the sys.path line above
    ENTRY_RE,
    GRADE_RE,
    GRADES,
    strip_fences,
)

# URL and heading shapes are specific to this checker, so they stay here rather
# than moving into the shared grammar.
URL_RE = re.compile(r"\]\((https?://[^)\s]+)\)")
HEADING_RE = re.compile(r"^#{2,4}\s+(.+)$", re.MULTILINE)
ANCHOR_RE = re.compile(r"\]\(#([^)]+)\)")
# [text](other.md#anchor) — validated against the target file, not this one.
CROSS_RE = re.compile(r"\]\((?!https?://)([^)#\s]+\.md)#([^)\s]+)\)")




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


def check_entries(lines: list[str], path: str, required: bool = True) -> int:
    entries = [(n, ln) for n, ln in enumerate(lines, 1) if ENTRY_RE.match(ln)]
    problems = 0

    if not entries:
        if required:
            print(f"::error::{path}: no list entries found")
            return 1
        print(f"{path}: no graded entries (file is not a list index)")
        return 0

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


def check_cross_anchors(text: str, path: str) -> int:
    """Validate `](other.md#anchor)` links against the target file's headings."""
    base = os.path.dirname(os.path.abspath(path))
    cache: dict[str, set[str]] = {}
    missing = 0
    seen = set()
    for target, anchor in CROSS_RE.findall(text):
        if (target, anchor) in seen:
            continue
        seen.add((target, anchor))
        full = os.path.normpath(os.path.join(base, target))
        if not os.path.exists(full):
            print(f"::error file={path}::link target does not exist: {target}")
            missing += 1
            continue
        if target not in cache:
            with open(full, encoding="utf-8") as fh:
                cache[target] = {gh_slug(h) for h in HEADING_RE.findall(fh.read())}
        if anchor not in cache[target]:
            print(f"::error file={path}::broken cross-file anchor {target}#{anchor}")
            missing += 1
    print(f"{path}: {len(seen)} cross-file anchors checked, {missing} broken")
    return 1 if missing else 0


# A relative link to a file in this repo: `](other.md)`, `](../README.md#leg)`,
# `](harness/)`, `](entries.jsonl)`. Everything with a scheme, every `#anchor`
# to this file, and every non-path target is excluded.
LOCAL_RE = re.compile(r"\]\((?!https?:|#|mailto:|tel:)([^)\s]+)\)")


def check_local_links(text: str, path: str) -> int:
    """Every relative markdown link must point at a file that exists.

    This is the check that was missing, and it cost a broken link: the two
    anchor checks only see `](file.md#anchor)`, so a link *without* a fragment
    -- the majority of them -- was never validated at all. `llms.txt` shipped
    pointing at `harness/docs/context-profiler.md`, a file that does not exist,
    for as long as the file had no anchor check applied to it.
    """
    base = os.path.dirname(os.path.abspath(path))
    headings: dict[str, set[str]] = {}
    missing = 0
    seen: set[tuple[str, str]] = set()
    for target in LOCAL_RE.findall(text):
        path_part, _, fragment = target.partition("#")
        if (path_part, fragment) in seen:
            continue
        seen.add((path_part, fragment))
        full = os.path.normpath(os.path.join(base, path_part))
        if not os.path.exists(full):
            print(f"::error file={path}::relative link target does not exist: {target}")
            missing += 1
            continue
        if not fragment:
            continue
        # A fragment on a local link is validated against the target's headings,
        # which is what CROSS_RE above does for the `.md#anchor` shape.
        if path_part not in headings:
            with open(full, encoding="utf-8") as fh:
                headings[path_part] = {gh_slug(h) for h in HEADING_RE.findall(fh.read())}
        if fragment not in headings[path_part]:
            print(f"::error file={path}::broken local anchor {path_part}#{fragment}")
            missing += 1
    print(f"{path}: {len(seen)} relative links checked, {missing} broken")
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
    anchors_only = "--anchors-only" in sys.argv
    allow_empty = "--allow-empty" in sys.argv

    if not args:
        print(__doc__)
        return 2

    rc = 0
    for path in args:
        text = pathlib.Path(path).read_text(encoding="utf-8")
        lines = strip_fences(text.splitlines())
        if want_urls:
            # Link collection wants real URLs, and a fenced block can contain
            # one the author quoted as an example. Keep the raw lines here.
            rc |= urls(text.splitlines())
        else:
            # Fences are blanked before grading and anchoring: quoted entry
            # templates must not be graded, and a heading inside a fence is not
            # an anchor target.
            fenced_text = "\n".join(lines)
            if not anchors_only:
                rc |= check_entries(lines, path, required=not allow_empty)
            rc |= check_anchors(fenced_text, path)
            rc |= check_local_links(fenced_text, path)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
