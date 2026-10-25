"""Per-turn context-composition profiler.

This is the repo's answer to its own open problem: *nobody has an independently
audited context-window profiler.* Most of the profiler layer in the list is
`[self-reported]`, and the entries that are not audit instruction files and
bills rather than the window itself. This module measures the window.

The input is an agent session's raw event stream — newline-delimited JSON as
emitted by a headless CLI — and the output is what the context was actually made
of, turn by turn: system segments, tool schemas, tool results, cache reads, and
how each of those moved between turns.

Two design rules, both learned from things that went wrong elsewhere:

- **Tolerant of the source format.** Fields the reader does not know are ignored
  rather than fatal, and every count is stamped with the shape it came from. The
  Copilot CLI parser in `tasks/copilot_cli.py` is pinned to one CLI version; this
  one is not, because a profiler that breaks on a CLI bump measures nothing.
- **Independent of any profiler being audited.** Nothing here reads another
  tool's output. Ground truth is the session's own reported token counts, so a
  third-party profiler can be run alongside and its numbers diffed against this
  report. That comparison is the audit; this module is the baseline.

Usage:
    token-harness profile --session session.jsonl
    token-harness profile --session session.jsonl --format json
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

# A tool schema that is loaded and never called is a permanent tax on every
# turn. Above this share of the prompt, it is the largest single line item.
TOOL_SHARE_FLAG = 0.40
# Below this share, the cache is doing less than the pricing implies.
CACHE_SHARE_FLOOR = 0.10


@dataclass
class Turn:
    """One usage checkpoint: the context as billed at that point in the session."""

    index: int
    prompt_tokens: int
    cache_read: int
    cache_write: int
    tool_tokens: int
    tool_calls: int
    segments: dict[str, int] = field(default_factory=dict)

    @property
    def delta(self) -> int:
        """Change in prompt tokens from the previous turn, filled in later."""
        return getattr(self, "_delta", 0)

    @property
    def tool_share(self) -> float:
        return self.tool_tokens / self.prompt_tokens if self.prompt_tokens else 0.0

    @property
    def cache_share(self) -> float:
        return self.cache_read / self.prompt_tokens if self.prompt_tokens else 0.0

    @property
    def fixed_overhead(self) -> int:
        """System-segment tokens. These are billed on every turn and never
        shrink, which is why they get their own line in the report."""
        return sum(self.segments.values())


@dataclass
class Profile:
    turns: list[Turn]
    model: str = "unknown"
    source: str = "stdin"
    captured_on: str = ""
    warnings: list[str] = field(default_factory=list)

    # ---- derived -------------------------------------------------------

    @property
    def final(self) -> Turn | None:
        return self.turns[-1] if self.turns else None

    @property
    def growth(self) -> list[int]:
        return [t.delta for t in self.turns]

    def flags(self) -> list[str]:
        out: list[str] = []
        last = self.final
        if last is None:
            return out
        if last.tool_tokens and not last.tool_calls:
            out.append(
                f"schemas_loaded_unused: {last.tool_tokens} tool-schema tokens, "
                f"{last.tool_calls} tool calls"
            )
        if last.tool_share > TOOL_SHARE_FLAG:
            out.append(
                f"tool_share_high: schemas are {last.tool_share:.0%} of the "
                f"prompt (>{TOOL_SHARE_FLAG:.0%})"
            )
        if last.prompt_tokens and not last.cache_read:
            out.append(
                f"cache_cold: {last.prompt_tokens} prompt tokens, 0 cache reads"
            )
        elif 0 < last.cache_share < CACHE_SHARE_FLOOR:
            out.append(
                f"cache_share_low: {last.cache_share:.1%} of the prompt was a "
                f"cache read (<{CACHE_SHARE_FLOOR:.0%})"
            )
        flat = [
            t for t in self.turns if t.index > 1 and t.delta == 0
        ]
        if flat:
            out.append(
                f"no_growth_turns: {len(flat)} turn(s) billed the same prompt "
                f"as the one before — re-billing, not new work"
            )
        return out

    def provenance(self) -> dict:
        return {
            "model": self.model,
            "harness": "token-harness profile",
            "date": self.captured_on or date.today().isoformat(),
            "n_turns": len(self.turns),
            "source": self.source,
            "warnings": self.warnings,
        }


# ---- parsing -------------------------------------------------------------


def parse_events(text: str, source: str = "stdin") -> Profile:
    """Read an agent session's event stream into a Profile.

    Accepts newline-delimited JSON (a headless CLI's stdout) or a JSON array.
    Unknown event types and unknown fields are ignored; a `session.usage_checkpoint`
    with no `promptCacheBreakState` still yields a turn, with zeros, so a partial
    capture is visibly partial rather than silently empty.
    """
    events: list[dict] = []
    stripped = text.strip()
    if not stripped:
        return Profile(turns=[], source=source, warnings=["empty input"])
    if stripped.startswith("["):
        try:
            events = json.loads(stripped)
        except json.JSONDecodeError:
            return Profile(turns=[], source=source, warnings=["malformed JSON array"])
    else:
        for n, line in enumerate(stripped.splitlines(), 1):
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                # One unparseable line does not invalidate a session.
                continue

    turns: list[Turn] = []
    model = "unknown"
    warnings: list[str] = []
    checkpoints = 0

    for event in events:
        if not isinstance(event, dict):
            continue
        if event.get("type") != "session.usage_checkpoint":
            continue
        checkpoints += 1
        data = event.get("data", {})
        found = False
        for seg in data.get("promptCacheBreakState", []):
            for model_name, md in seg.get("models", {}).items():
                if not isinstance(md, dict):
                    continue
                found = True
                model = model_name or model
                segments = {}
                for s in md.get("system_segments", []) or []:
                    if not isinstance(s, dict):
                        continue
                    name = s.get("segment") or "unknown"
                    segments[name] = segments.get(name, 0) + int(s.get("tokens") or 0)
                turns.append(
                    Turn(
                        index=len(turns) + 1,
                        prompt_tokens=int(md.get("prompt_tokens") or 0),
                        cache_read=int(md.get("cache_read") or 0),
                        cache_write=int(md.get("cache_write") or 0),
                        tool_tokens=int(md.get("tool_tokens") or 0),
                        tool_calls=int(md.get("tool_count") or 0),
                        segments=segments,
                    )
                )
        if not found:
            warnings.append(
                f"checkpoint {checkpoints} carried no promptCacheBreakState; "
                f"recorded as a zero turn"
            )
            turns.append(
                Turn(
                    index=len(turns) + 1,
                    prompt_tokens=0,
                    cache_read=0,
                    cache_write=0,
                    tool_tokens=0,
                    tool_calls=0,
                    segments={},
                )
            )

    profile = Profile(turns=turns, model=model, source=source, warnings=warnings)
    _fill_deltas(profile)
    if not checkpoints:
        profile.warnings.append("no session.usage_checkpoint events found")
    return profile


def _fill_deltas(profile: Profile) -> None:
    prev = None
    for turn in profile.turns:
        turn._delta = turn.prompt_tokens if prev is None else turn.prompt_tokens - prev
        prev = turn.prompt_tokens


# ---- formatting ----------------------------------------------------------


def _bar(value: int, total: int, width: int = 40) -> str:
    if total <= 0:
        return ""
    filled = max(1, round(value / total * width)) if value else 0
    return "█" * filled + " " * (width - filled)


def format_table(profile: Profile) -> str:
    if not profile.turns:
        return "No turns captured."
    last = profile.final
    total = last.prompt_tokens or 1
    lines = [
        f"Context composition — {profile.model} — {len(profile.turns)} turn(s)",
        f"source: {profile.source}",
        "",
        f"  prompt tokens, final turn   {last.prompt_tokens:>9,}",
        (
            f"  of which fixed overhead     {last.fixed_overhead:>9,}  "
            f"({last.fixed_overhead / total:>5.1%})  system segments, billed every turn"
        ),
        (
            f"  of which tool schemas       {last.tool_tokens:>9,}  "
            f"({last.tool_share:>5.1%})"
        ),
        (
            f"  cache reads                 {last.cache_read:>9,}  "
            f"({last.cache_share:>5.1%})"
        ),
        f"  tool calls                  {last.tool_calls:>9,}",
        "",
        "  Segments, final turn:",
    ]
    for name, tokens in sorted(last.segments.items(), key=lambda kv: -kv[1]):
        lines.append(
            f"    {name:<26}{tokens:>9,}  {tokens / total:>5.1%}  "
            f"{_bar(tokens, total)}"
        )
    lines += ["", "  Growth per turn (Δ prompt tokens):"]
    for turn in profile.turns:
        marker = "  <- no growth" if turn.index > 1 and turn.delta == 0 else ""
        lines.append(f"    turn {turn.index:>3}  {turn.delta:>+9,}{marker}")
    flags = profile.flags()
    if flags:
        lines += ["", "  Flags:"]
        lines += [f"    - {f}" for f in flags]
    if profile.warnings:
        lines += ["", "  Warnings:"]
        lines += [f"    - {w}" for w in profile.warnings]
    lines += [
        "",
        (
            f"  stamp: {profile.provenance()['model']} · "
            f"{profile.provenance()['harness']} · {profile.provenance()['date']} · "
            f"n={len(profile.turns)}"
        ),
    ]
    return "\n".join(lines)


def format_json(profile: Profile) -> str:
    payload = profile.provenance()
    payload["final_turn"] = {
        "prompt_tokens": profile.final.prompt_tokens if profile.final else 0,
        "fixed_overhead_tokens": profile.final.fixed_overhead if profile.final else 0,
        "tool_schema_tokens": profile.final.tool_tokens if profile.final else 0,
        "tool_share": round(profile.final.tool_share, 4) if profile.final else 0.0,
        "cache_read_tokens": profile.final.cache_read if profile.final else 0,
        "cache_share": round(profile.final.cache_share, 4) if profile.final else 0.0,
        "tool_calls": profile.final.tool_calls if profile.final else 0,
        "segments": profile.final.segments if profile.final else {},
    }
    payload["turns"] = [
        {
            "index": t.index,
            "prompt_tokens": t.prompt_tokens,
            "delta": t.delta,
            "segments": t.segments,
        }
        for t in profile.turns
    ]
    payload["flags"] = profile.flags()
    return json.dumps(payload, indent=2)


# ---- entry point ---------------------------------------------------------


def profile_file(path: str, fmt: str = "table") -> int:
    text = Path(path).read_text(encoding="utf-8")
    profile = parse_events(text, source=path)
    print(format_json(profile) if fmt == "json" else format_table(profile))
    return 0 if profile.turns else 1


def profile_stdin(fmt: str = "table") -> int:
    text = sys.stdin.read()
    profile = parse_events(text, source="stdin")
    print(format_json(profile) if fmt == "json" else format_table(profile))
    return 0 if profile.turns else 1
