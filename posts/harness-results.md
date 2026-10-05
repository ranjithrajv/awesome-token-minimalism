# Harness Results: The Measurement Surface Matters

*Published 2026-10-05. Two executors: Copilot CLI v1.0.83 and Groq `gpt-oss-120b`.*

**The finding:** A seven-word brevity instruction saves **418.25 output tokens per task** on single API calls (p=0.0001, 48 tasks) but only 9.58 on full agent sessions (p=0.52, 12 tasks). The measurement surface matters. Tool schemas (8,521 tokens) dominate the agent session cost, diluting the instruction's effect.

---

## Part 1: Copilot CLI baseline (single session)

A single agent session — task: "echo hello" — costs:

| Metric | Value |
|---|---|
| Total input tokens | 17,549 |
| Cache read | 8,704 |
| Tool schema tokens | 8,521 |
| Tool calls | 23 |
| Session duration | 8.4s |
| Estimated cost | $0.055 (Sonnet-5 list rates as a proxy) |

---

## Part 2: Groq paired A/B

The brevity instruction ("Follow YAGNI, prefer one-liners") measured against
the same baseline (no instruction) on real GitHub issues. The suite grew over
three runs; the 48-task run is the one to trust (see the
[leaderboard](../harness/LEADERBOARD.md)).

| Metric | Δ (48 tasks) | p-value |
|---|---|---|
| tokens_in | +3.44 | — |
| tokens_out | **−418.25** | **0.0001** |
| cost_usd | $0 | — |
| wall_clock_s | +1.09 | 0.2908 |
| quality guard | 0.000 | 0.4853 |

**Finding:** The brevity instruction is quality-neutral and saves 418.25 output
tokens per task, with no wall-clock penalty. `[measured]`

Earlier pilots: **−522** output tokens on 12 tasks (p=0.0004) and **−268.67**
on 24 tasks (p=0.053). The smaller samples overstated the effect; it survived
only at full size, where it is highly significant (p=0.0001).

---

## Part 3: Copilot CLI paired A/B (12 SWE-bench Lite tasks)

The brevity instruction measured against the same baseline on 12 real GitHub issues:

| Metric | Baseline | Treatment | Δ | p-value |
|---|---|---|---|---|
| tokens_in | — | — | −1,517 | 0.3069 |
| tokens_out | — | — | −9.58 | 0.5190 |
| cost_usd | — | — | −$0.01 | 0.2506 |
| wall_clock_s | — | — | −7.23 | 0.0837 |
| quality guard | 1.0 | 1.0 | 0.000 | 1.0000 |

**Finding:** The brevity instruction saves 1,517 input tokens and 9.58 output
tokens, but neither is statistically significant (p=0.31, p=0.52). The effect
is diluted by fixed overhead: tool schemas (8,521 tokens) dominate the session
cost. Wall-clock reduction (−7.23s, p=0.08) is close to significant.
`[measured]`

---

## The key insight

**Groq** (single API call): The brevity instruction saves **418.25** output tokens per task across 48 tasks (p=0.0001) — significant. Earlier pilots measured −522 (12 tasks, p=0.0004) and −268.67 (24 tasks, p=0.053); the effect held up only at full size.

**Copilot CLI** (full agent loop): The brevity instruction saves 9.58 output tokens (p=0.52) — **not significant**.

The difference: In the full agent loop, the brevity instruction's effect is **diluted by fixed overhead** — tool schemas (8,521 tokens) and cache. The instruction's effect on output tokens is real but small relative to the total session cost.

The wall-clock reduction (−7.23s, p=0.08) is close to significant — the brevity instruction may reduce agent loop time by making the model produce shorter outputs faster.

## The breakdown

| Segment | Tokens | % of input |
|---|---|---|
| tool_instructions | 7,101 | 40.5% |
| identity | 503 | 2.9% |
| custom_instructions | 797 | 4.5% |
| additional_instructions | 455 | 2.6% |
| code_change_instructions | 295 | 1.7% |
| environment_limitations | 235 | 1.3% |
| dynamic_guidelines | 201 | 1.1% |
| environment_context | 100 | 0.6% |
| model_information | 47 | 0.3% |
| tool_intro | 20 | 0.1% |
| version_information | 9 | 0.1% |

## The finding

Tool schemas cost 8,521 tokens per session — a permanent tax on every turn.
The capability those schemas provide is real; the question is whether loading
all 23 eagerly is the only way to provide it. Route them on demand and the
capability is preserved, the cost is removed.

The [breakdown above](#the-breakdown) is where the fixed cost sits —
`tool_instructions` alone is 7,101 tokens. Compact the prompt and the behavior
is preserved, the cost is removed.

The actual user message ("echo hello") is a rounding error.

## Methodology

```
executor: copilot -p "echo hello" --output-format json
model: mai-code-1.1-flash
harness: Copilot CLI v1.0.83
date: 2026-10-05
parser: tasks/copilot_cli.py
```

## Reproduce

```sh
copilot -p "echo hello" --output-format json > output.json
python -c "
from tasks.copilot_cli import _parse_copilot_output
import json
with open('output.json') as f:
    print(json.dumps(_parse_copilot_output(f.read()), indent=2))
"
```

## Context

This is the baseline for the paired A/B measurement in
[awesome-token-minimalism](https://github.com/ranjithrajv/awesome-token-minimalism).
The treatment arm adds "Follow YAGNI, prefer one-liners" to the system prompt.
The question is whether the brevity instruction reduces tokens without
degrading quality.

---

*Part of the [token ledger](https://github.com/ranjithrajv/awesome-token-minimalism#token-ledger).*
