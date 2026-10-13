"""Tests for the annotation checker.

Every case here is an anchor shape that actually appears in this repo, because
the failure mode is silent: `gh_slug` produces a *plausible* wrong answer, the
emoji anchors in the README stop resolving, and nothing else in CI notices. The
docs already pass these cases; the point is that they keep passing.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / ".github" / "scripts" / "check_annotations.py"

spec = importlib.util.spec_from_file_location("check_annotations", SCRIPT)
check_annotations = importlib.util.module_from_spec(spec)
sys.modules["check_annotations"] = check_annotations
spec.loader.exec_module(check_annotations)

gh_slug = check_annotations.gh_slug


def test_em_dash_slugs_to_two_hyphens():
    """AGENTS.md calls this out: spaces are not collapsed, the dash is dropped."""
    assert gh_slug("Leg 1 — Input") == "leg-1--input"
    assert gh_slug("Leg 0 — Measure") == "leg-0--measure"
    assert gh_slug("Leg 3 — Lifetime") == "leg-3--lifetime"


def test_emoji_is_percent_encoded_with_variation_selector():
    # The anchors the README uses for its section links, byte for byte.
    assert gh_slug("🕸️ Graph engineering") == "%F0%9F%95%B8%EF%B8%8F-graph-engineering"
    assert gh_slug("🧠 Agent memory & reuse what you emitted") == (
        "%F0%9F%A7%A0-agent-memory--reuse-what-you-emitted"
    )
    assert gh_slug("🎯 Budget") == "%F0%9F%8E%AF-budget"
    assert gh_slug("🧮 Break-even") == "%F0%9F%A7%AE-break-even"


def test_punctuation_is_dropped_not_encoded():
    assert gh_slug("Serve-side: cost and latency, *not* token count") == (
        "serve-side-cost-and-latency-not-token-count"
    )


def test_inline_link_collapses_to_its_text():
    assert gh_slug("[The three legs](README.md) — a frame") == "the-three-legs--a-frame"


def test_ampersand_and_apostrophes_are_dropped():
    assert gh_slug("Leg 2 — Output") == "leg-2--output"
    assert gh_slug("What can't be measured") == "what-cant-be-measured"


def test_fenced_code_is_not_list_content():
    lines = [
        "- **[real](https://example.com)** `[measured]`",
        "```",
        "- **[template](https://example.com)** `[measured]`",
        "```",
    ]
    stripped = check_annotations.strip_fences(lines)
    entry_lines = [line for line in stripped if line.startswith("- **[")]
    assert len(entry_lines) == 1
    # Line numbers survive, so a reported line still points at the source.
    assert len(stripped) == len(lines)


def test_local_link_check_catches_a_missing_file(tmp_path, capsys):
    doc = tmp_path / "doc.md"
    doc.write_text("see [the rig](harness/README.md)\n", encoding="utf-8")
    rc = check_annotations.check_local_links(
        doc.read_text(encoding="utf-8"), str(doc)
    )
    out = capsys.readouterr().out
    assert rc == 1
    assert "does not exist" in out


def test_local_link_check_catches_a_broken_fragment(tmp_path, capsys):
    (tmp_path / "target.md").write_text("## Real heading\n", encoding="utf-8")
    doc = tmp_path / "doc.md"
    doc.write_text("see [x](target.md#no-such-heading)\n", encoding="utf-8")
    rc = check_annotations.check_local_links(
        doc.read_text(encoding="utf-8"), str(doc)
    )
    assert rc == 1
    assert "broken local anchor" in capsys.readouterr().out


def test_local_link_check_passes_a_good_relative_link(tmp_path):
    (tmp_path / "target.md").write_text("## Real heading\n", encoding="utf-8")
    doc = tmp_path / "doc.md"
    doc.write_text("see [x](target.md#real-heading)\n", encoding="utf-8")
    rc = check_annotations.check_local_links(
        doc.read_text(encoding="utf-8"), str(doc)
    )
    assert rc == 0


def test_local_link_check_ignores_external_and_same_file_links(tmp_path):
    doc = tmp_path / "doc.md"
    doc.write_text(
        "[ext](https://example.com) [mail](mailto:a@b.c) [self](#local)\n",
        encoding="utf-8",
    )
    rc = check_annotations.check_local_links(
        doc.read_text(encoding="utf-8"), str(doc)
    )
    assert rc == 0
