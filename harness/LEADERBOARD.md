# Leaderboard

Paired A/B measurement of token-saving tools and prompts. Rows are grouped by
harness: a SWE-bench Lite suite (`tasks/swebench_lite.json`, 48 tasks) for runs
through this harness, and JetBrains' independent SkillsBench harness for the
rest. The two groups are not comparable to each other.

## How to read this

Each row is a tool or prompt technique measured against a paired baseline (no
tool, no brevity instruction): each task runs under both arms, and the per-task
difference is the unit of analysis. Rows are grouped by harness; do not compare
across groups.

| Grade | Means |
|---|---|
| `[measured]` | number + stated baseline + method someone could re-run |
| `[self-reported]` | number from the tool's own authors, baseline unstated |
| `[negative]` | measured, and it did **not** work |
| `[asserted]` | claim with no number — not admitted to this leaderboard |

## The leaderboard

### SWE-bench Lite — this harness

| Rank | Arm | Suite | Δ tokens-in | Δ tokens-out | Δ cost | Δ wall-clock | Quality | Grade |
|---|---|---|---|---|---|---|---|---|
| 1 | *"Follow YAGNI, prefer one-liners"* | Groq, 48 tasks | +3.44 | **−418.25** | $0 | +1.09s | 100% safe | `[measured]` |
| 2 | *"Follow YAGNI, prefer one-liners"* | Copilot CLI, 12 tasks | −1,517 | −9.58 | −$0.01 | −7.23s | 100% safe | `[measured]` |

**Groq measurement** (2026-10-05, `openai/gpt-oss-120b`, 48 SWE-bench Lite tasks):
The brevity instruction saves 418.25 output tokens per task (p=0.0001).
No quality degradation (p=0.4853). No wall-clock penalty (p=0.2908).
Earlier pilots measured −522 (12 tasks, p=0.0004) and −268.67 (24 tasks,
p=0.0531); the 48-task run is the one to trust. `[measured]`

**Copilot CLI measurement** (2026-10-05, `mai-code-1.1-flash`, 12 SWE-bench Lite tasks):
The brevity instruction saves 1,517 input tokens and 9.58 output tokens, but
neither is statistically significant (p=0.31, p=0.52). The effect is diluted
by fixed overhead: tool schemas (8,521 tokens) dominate the session cost.
Wall-clock reduction (−7.23s, p=0.08) is close to significant. `[measured]`

### SkillsBench — JetBrains' independent Claude Code harness

Different suite, model, and harness from the rows above; measured by
[JetBrains](https://blog.jetbrains.com/ai/2026/07/ponytail-skill-claude-tested),
not by this repo. These are the numbers in the README
[token ledger](../README.md#token-ledger).

| Tool | Δ code | Δ output tokens | Δ cost | Quality | Grade |
|---|---|---|---|---|---|
| ponytail | −15.4% (p=0.088) | — | −10.3% (p=0.004) | 65/80 identical | `[measured]/[self-reported]` |
| caveman | — | −8.5% (p=0.82) | — | flat | `[measured]/[asserted]` |
| rtk | — | — | +7.6% (p=0.004, 425 trials) | tie | `[negative]` |

## The baseline

| Metric | Value |
|---|---|
| Model | `mai-code-1.1-flash` via Copilot CLI v1.0.83 |
| Task | "echo hello" (simplest possible) |
| Total input tokens | 17,549 |
| Tool schema tokens | 8,521 (49%) |
| Session duration | 8.4s |
| Estimated cost | $0.055 (Sonnet-5 list rates as a proxy; `mai-code` rates unpublished) |

## The task suite

`tasks/swebench_lite.json` holds 48 real GitHub issues — four each from django,
sympy, astropy, scikit-learn, matplotlib, requests, flask, pandas, numpy,
pytest, sphinx, and tornado. The Groq row above ran all 48; the Copilot CLI row
ran the first 12.

## Methodology

```
executor: copilot -p "prompt" --output-format json
harness: token-harness (paired A/B, paired t-test)
confidence: 0.95
date: 2026-10-05
```

## Contribute

Run the harness with your tool and publish the number:

```sh
cd harness
token-harness run \
  --tasks tasks/swebench_lite.json \
  --config configs/your-tool.json \
  --output report.json
```

See [Add your tool](README.md#add-your-tool) for the executor contract. List
entries follow [CONTRIBUTING.md](../CONTRIBUTING.md).

---

*Part of [awesome-token-minimalism](https://github.com/ranjithrajv/awesome-token-minimalism).*
