# Harness Results: Copilot CLI Baseline + Groq Paired A/B

*Published 2026-10-05. Two executors: Copilot CLI v1.0.83 and Groq `gpt-oss-120b`.*

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
| Estimated cost | $0.055 |

---

## Part 2: Groq paired A/B (12 SWE-bench Lite tasks)

The brevity instruction ("Follow YAGNI, prefer one-liners") measured against
the same baseline (no instruction) on 12 real GitHub issues:

| Metric | Baseline | Treatment | Δ | p-value |
|---|---|---|---|---|
| tokens_in | — | — | +10 | 0.0000 |
| tokens_out | — | — | **−522** | **0.0004** |
| cost_usd | $0 | $0 | $0 | 1.0000 |
| wall_clock_s | — | — | +2.35 | 0.3620 |
| quality guard | 1.0 | 1.0 | 0.000 | 1.0000 |

**Finding:** The brevity instruction adds 10 input tokens but saves 522
output tokens. Net effect: −512 tokens per task. No quality degradation.
`[measured]`

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

The system prompt is 5,038 tokens (29%) — compact it and the behavior is
preserved, the cost is removed.

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
