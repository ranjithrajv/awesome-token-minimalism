#!/usr/bin/env python3
"""The shared entry grammar for the annotation checks.

Every checker in this directory needs the same three answers: what is a list
entry, which grades exist, and what counts as a fenced code block. They used to
answer them with two independent copies of the same regular expressions, which
is exactly the failure mode this repo catalogues everywhere else -- a rule that
can drift between its two implementations. So the grammar lives here once.

Delete nothing from this file without changing both callers.
"""

from __future__ import annotations

import re

GRADES = ("measured", "self-reported", "asserted", "negative")

ENTRY_RE = re.compile(r"^\s*-\s+\*\*\[")
# A grade is one of the four tags, optionally compound with `/` to signal a
# split verdict, e.g. `[measured]/[asserted]` = the independent audit is
# measured, but the tool's own headline number is not.
GRADE_TAG = r"(?:" + "|".join(GRADES) + r")"
GRADE_RE = re.compile(rf"\[{GRADE_TAG}\](?:/\[{GRADE_TAG}\])*")
# "2026-07", "(2026-07)", "2026-07-01". A bare year is deliberately *not* a
# stamp: it cannot go stale, so it cannot prompt a re-run.
DATE_RE = re.compile(r"\b(20[0-9]{2})-([01][0-9])\b")
FENCE_RE = re.compile(r"^\s*(```|~~~)")


def strip_fences(lines: list[str]) -> list[str]:
    """Blank out fenced code blocks, preserving line numbers.

    A fenced block is example or command text, not a graded entry. The entry
    format in SHOWCASE.md and CONTRIBUTING.md is quoted inside a fence, and a
    fence-blind linter flags its own documentation. Blanking rather than
    dropping keeps every reported line number pointing at the real source.
    """
    out: list[str] = []
    fence: str | None = None
    for line in lines:
        stripped = line.lstrip()
        if fence is None:
            m = FENCE_RE.match(line)
            if m:
                fence = m.group(1)
                out.append("")
                continue
            out.append(line)
        else:
            # Inside a fence: close on a matching delimiter, then blank it.
            if stripped.startswith(fence):
                fence = None
            out.append("")
    return out


def graded_entries(lines: list[str]) -> list[tuple[int, str, list[str]]]:
    """Every graded entry as (line_no, line, grades), fences excluded."""
    out: list[tuple[int, str, list[str]]] = []
    for n, line in enumerate(strip_fences(lines), 1):
        if not ENTRY_RE.match(line):
            continue
        grades = GRADE_RE.findall(line)
        if not grades:
            continue
        out.append((n, line, grades))
    return out
