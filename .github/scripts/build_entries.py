#!/usr/bin/env python3
"""Generate the entry index, and prove it is still true.

The list's own thesis is progressive disclosure: hold an identifier and load the
payload when the task needs it. An agent asked "which of these tools are
`[measured]`" currently pays ~40k tokens of README to find out. `entries.jsonl`
is the index for that question -- name, section, grade, and any date, one line each --
and this script is what keeps it honest.

Regenerate rather than hand-edit, and let CI prove it:

    python .github/scripts/build_entries.py              # write entries.jsonl
    python .github/scripts/build_entries.py --check      # fail if it has drifted

The fields are deliberately the ones the README already states in a machine-
readable place, and nothing else. Mechanism, baseline, and the additive clause
are prose, and summarising prose into a field is how a list starts lying to
itself; that payload stays in the entry, reached by URL and line.

`section` is the nearest preceding heading, which is the placement rule a
contributor used anyway, and `line` is the 1-based line in README.md, so a
reader can jump straight to the full entry.
"""

from __future__ import annotations

import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from entryspec import DATE_RE, strip_fences  # needs the sys.path line above

ROOT = pathlib.Path(__file__).resolve().parents[2]
README = ROOT / "README.md"
INDEX = ROOT / "entries.jsonl"

# The entry header, e.g. `- **[Serena](https://github.com/oraios/serena)** —`.
# Some entries link several providers in one bullet (the batch APIs, for one),
# so the name is matched separately from the URL list: a multi-link entry is one
# entry with several identifiers, not an entry to skip.
HEADER_RE = re.compile(r"^\s*-\s+\*\*\[([^\]]*)\]")
# Every markdown link inside the entry line, first one being the name's target.
LINK_RE = re.compile(r"\[[^\]]*\]\((https?://[^)\s]+)\)")
# `## Leg 1 — Input` and `### 📏 Effective context` are both sections worth
# recording; a `####` sub-heading is not, because entries do not sit under one.
HEADING_RE = re.compile(r"^##\s+(.*)$|^###\s+(.*)$")


def build(readme: pathlib.Path) -> list[dict]:
    lines = readme.read_text(encoding="utf-8").splitlines()
    # Fences are blanked first: a quoted entry template is documentation, not an
    # entry, the same rule the two linters already enforce.
    section = ""
    out: list[dict] = []
    for n, line in enumerate(strip_fences(lines), 1):
        m = HEADING_RE.match(line)
        if m:
            section = (m.group(1) or m.group(2) or "").strip()
            continue
        h = HEADER_RE.match(line)
        if not h:
            continue
        from entryspec import GRADE_RE

        links = LINK_RE.findall(line)
        if not links:
            # A graded entry with no link is still an entry; the linter only
            # warns about it, so keep it and carry the line number instead.
            links = []
        name = h.group(1)
        grades = GRADE_RE.findall(line)
        dates = [f"{y}-{m}" for y, m in DATE_RE.findall(line)]
        out.append(
            {
                "name": name,
                "url": links[0] if links else None,
                # `urls` is present only when an entry links more than one
                # resource; a single-link entry stays compact.
                "urls": links or None,
                "section": section,
                "grades": grades,
                # One date is the stamp; a second appears only when an entry
                # re-states a figure from elsewhere in the list. Keep the
                # oldest-and-newest pair so a reader can see both.
                "dates": dates,
                "line": n,
            }
        )
    return out


def render(entries: list[dict]) -> str:
    return "".join(json.dumps(e, ensure_ascii=False) + "\n" for e in entries)


def main() -> int:
    check = "--check" in sys.argv
    entries = build(README)
    if not entries:
        print("::error::no entries parsed from README.md; the header regex is stale")
        return 1
    text = render(entries)
    if not check:
        INDEX.write_text(text, encoding="utf-8")
        undated = sum(1 for e in entries if not e["dates"])
        print(f"{INDEX.name}: {len(entries)} entries, {undated} undated")
        return 0

    current = INDEX.read_text(encoding="utf-8") if INDEX.exists() else ""
    if current == text:
        print(f"{INDEX.name}: {len(entries)} entries, in sync with README.md")
        return 0
    print(
        f"::error file={INDEX.name}::index is out of date for README.md. "
        f"Run `python .github/scripts/build_entries.py` and commit the result -- "
        f"the index is generated, not edited."
    )
    # Show the first few disagreements rather than the whole diff: a rename and
    # a re-grade are the two things that happen, and both are visible in three
    # lines.
    old = current.splitlines()
    new = text.splitlines()
    for i, line in enumerate(new):
        if i >= len(old) or old[i] != line:
            print(f"  line {i + 1}: {line[:160]}")
            break
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
