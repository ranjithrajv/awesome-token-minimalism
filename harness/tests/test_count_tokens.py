"""Tests for the token meter's reproducibility.

The meter is only reproducible with one fixed tokenizer, so the property under
test is that it has no fallback: a missing `tiktoken` is a hard error, never a
silent switch to a chars/4 estimate. Two methods are two numbers, and a budget
gate that checks one against the other is worse than no gate.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / ".github" / "scripts" / "count_tokens.py"

spec = importlib.util.spec_from_file_location("count_tokens", SCRIPT)
count_tokens = importlib.util.module_from_spec(spec)
sys.modules["count_tokens"] = count_tokens
spec.loader.exec_module(count_tokens)


def test_missing_tokenizer_is_a_hard_error(monkeypatch, capsys):
    """No tiktoken -> exit 2 with install instructions, never a fallback count."""
    # `import tiktoken` raises ImportError when the module is None in sys.modules.
    monkeypatch.setitem(sys.modules, "tiktoken", None)
    try:
        count_tokens.load_encoding()
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError("load_encoding() must exit when tiktoken is missing")
    assert "requirements.txt" in capsys.readouterr().err


def test_count_is_deterministic():
    """The same text and the same pinned encoder give the same number twice."""
    encoding, _version = count_tokens.load_encoding()
    text = "The quick brown fox — 16× 🕸️ `cl100k_base`"
    assert count_tokens.count(text, encoding) == count_tokens.count(text, encoding)


def test_encoding_is_pinned():
    assert count_tokens.ENCODING == "cl100k_base"
