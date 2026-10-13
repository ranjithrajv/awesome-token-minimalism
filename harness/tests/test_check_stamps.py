"""Tests for the evidence-stamp check.

Three properties matter, and each has caught a real defect in this family of
checks before: fenced code is not list content, a bare year is not a stamp, and
the gate reports rather than fails until coverage justifies enforcing.
"""

from __future__ import annotations

import importlib.util
import sys
from datetime import date
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / ".github" / "scripts" / "check_stamps.py"

spec = importlib.util.spec_from_file_location("check_stamps", SCRIPT)
check_stamps = importlib.util.module_from_spec(spec)
sys.modules["check_stamps"] = check_stamps
spec.loader.exec_module(check_stamps)


def test_fenced_code_is_not_an_entry():
    """A quoted entry template inside a fence must not be graded or flagged."""
    lines = [
        "- **[real](https://example.com)** `[measured]` — 2026-09",
        "```",
        "- **[template](https://example.com)** `[measured]` — 2026-09",
        "```",
    ]
    entries = check_stamps.entry_stamps(lines)
    assert len(entries) == 1
    assert "real" in entries[0][1]


def test_bare_year_is_not_a_stamp():
    """A bare year cannot go stale, so it must not count as a date stamp."""
    lines = ["- **[paper](https://example.com)** — ICML 2023. `[measured]`"]
    (n, _line, grades, dates) = check_stamps.entry_stamps(lines)[0]
    assert grades == ["[measured]"]
    assert dates == []


def test_month_stamp_is_parseable():
    lines = ["- **[tool](https://example.com)** — 2026-07. `[measured]`"]
    (_n, _line, _grades, dates) = check_stamps.entry_stamps(lines)[0]
    assert dates == [("2026", "07")]


def test_versioned_identifier_is_not_a_stamp():
    """A versioned identifier is a name, not a measurement date.

    The beta header `context-management-2025-06-27` contains `2025-06`, and
    matching it flagged a fresh entry as a sixteen-month-old stamp.
    """
    lines = [
        (
            "- **[API](https://example.com)** — beta header "
            "`context-management-2025-06-27`. `[measured]` — verified 2026-10-13."
        )
    ]
    (_n, _line, _grades, dates) = check_stamps.entry_stamps(lines)[0]
    assert dates == [("2026", "10")]


def test_months_old():
    assert check_stamps.months_old(2026, 7, today=date(2026, 10, 1)) == 3
    assert check_stamps.months_old(2025, 1, today=date(2026, 10, 1)) == 21


def test_reports_rather_than_fails(capsys):
    """The default gate annotates. Failing 198 of 250 entries on day one would
    teach everyone to ignore it, so the exit code stays 0 until the constant is
    flipped deliberately."""
    lines = [
        "- **[old](https://example.com)** — 2024-01. `[measured]`",
        "- **[fresh](https://example.com)** — 2026-10. `[measured]`",
        "- **[undated](https://example.com)** `[measured]`",
    ]
    rc = check_stamps.check_stamps(lines, "TEST.md")
    out = capsys.readouterr().out
    assert rc == 0
    assert "1 stale" in out
    assert "1 undated" in out
    assert "1 within" in out
    assert "TEST.md" in out


def test_fail_on_stale_is_optin(monkeypatch, capsys):
    monkeypatch.setattr(check_stamps, "FAIL_ON_STALE", True)
    rc = check_stamps.check_stamps(
        ["- **[old](https://example.com)** — 2024-01. `[measured]`"], "TEST.md"
    )
    assert rc == 1
