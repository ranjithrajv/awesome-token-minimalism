# The context profiler

Per-turn context composition, measured independently of any profiler you might
want to audit.

This closes — or narrows to something answerable — the repo's own
[open problem 5](../../OPEN-PROBLEMS.md): *nobody has an
independently audited context-window profiler.* The profiler layer in
[Leg 0](../../README.md#leg-0--measure) is mostly `[self-reported]`, and the entries
that are not audit instruction files and bills rather than the window itself.
This module measures the window, in this repo, with a method anyone can re-run.

## What it measures

One agent session, turn by turn:

| Line | What it is | Why it is its own line |
|---|---|---|
| Fixed overhead | sum of system segments | billed on every turn and never shrinks |
| Tool schemas | `tool_tokens` | loaded whether or not they are called |
| Cache reads | `cache_read` | the 0.1× line on the bill |
| Tool calls | `tool_count` | the capability the schemas buy |
| Growth per turn | Δ prompt tokens | zero growth is re-billing, not work |
| Flags | derived | `schemas_loaded_unused`, `tool_share_high`, `cache_cold`, `cache_share_low`, `no_growth_turns` |

The flags are the point. A percentage table tells you the window is 35% schemas;
the flag tells you those schemas were never called.

## Running it

```sh
cd harness
pip install -e ".[dev]"

# Capture a session, then profile it.
copilot -p "echo hello" --output-format json > /tmp/session.jsonl
token-harness profile --session /tmp/session.jsonl

# Or pipe, and emit machine-readable output.
cat /tmp/session.jsonl | token-harness profile --format json
```

Exit code is 1 when no turns were captured, so it is safe in a pipeline.

## The one number to sanity-check against

The reference session in [the harness README](../../README.md) — Copilot CLI
v1.0.83, `mai-code-1.1-flash`, task `echo hello` — measured **17,549** total
input tokens, of which **8,704** cache reads and **8,521** tool schemas across
**23** tool calls, with `tool_instructions` the single largest system segment at
**7,101**. The profiler reproduces all of those from the same event stream. If
yours disagrees, the parse is wrong, not the session.

## Auditing a third-party profiler against it

This module reads an agent's own event stream and never reads another tool's
output. That is what makes it a baseline rather than a competitor:

1. Run your session through the profiler of your choice and save its report.
2. Run the same session through `token-harness profile --format json`.
3. Diff the two, per segment and per turn.

A profiler that agrees is audited. One that disagrees on a segment is either
measuring a different boundary (instruction files are not the window) or is
wrong — and the diff says which. Either way you have a number instead of a
claim, which is all `[measured]` means here.

## Format tolerance, and why it is not optional

The parser ignores event types and fields it does not recognize, records a
checkpoint that carries no `promptCacheBreakState` as a zero turn with a warning,
and defaults a missing count to `0` rather than guessing. A profiler that dies
on a CLI bump measures nothing at all, and this repo pinned a parser to one CLI
version once already (`tasks/copilot_cli.py` is still pinned to v1.0.83 for the
A/B rig). If the event shape changes, the report degrades visibly instead of
silently.

## What it does not measure

- **Re-billing across turns.** It reports zero-growth turns, which is the
  signature, but it cannot see *which* prior content was re-sent — that needs
  the message list, which `contextwatch` reads and this does not.
- **Server-side compaction.** `clear_tool_uses` and `compact` happen above the
  client, so they never appear in a captured event stream.
- **Recall.** What the model lost to all of the above is a different metric and
  a different suite.

All three are named rather than glossed because an unaudited profiler is the
thing the list is arguing against.

---

Part of [Awesome Token Minimalism](../../README.md) ·
[submit-a-run](submit-a-run.md) · [the rig](../../harness/README.md)
