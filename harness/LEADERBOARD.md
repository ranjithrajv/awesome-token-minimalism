# SWE-bench Lite Leaderboard

Paired A/B measurement of token-saving tools on real GitHub issues.
Task suite: 12 real bug fixes from popular Python repositories.

## How to read this

Each row is a tool or prompt technique measured against the same baseline
(no tool, no brevity instruction) on the same tasks. The measurement is
paired: each task runs under both arms, and the per-task difference is
the unit of analysis.

| Grade | Means |
|---|---|
| `[measured]` | number + stated baseline + method someone could re-run |
| `[self-reported]` | number from the tool's own authors, baseline unstated |
| `[negative]` | measured, and it did **not** work |

## The leaderboard

| Rank | Tool | Δ tokens-in | Δ tokens-out | Δ cost | Δ wall-clock | Quality | Grade |
|---|---|---|---|---|---|---|---|
| 1 | *"Follow YAGNI, prefer one-liners"* (Groq) | +10 | −522 | $0 | +2.35s | 100% safe | `[measured]` |
| 2 | *"Follow YAGNI, prefer one-liners"* (Copilot CLI) | −1,517 | −9.58 | −$0.01 | −7.23s | 100% safe | `[measured]` |
| 3 | ponytail | −22% | — | −10.3% | −27% | 100% safe | `[measured]` |
| 4 | caveman | +7% | — | +3% | +2% | 100% safe | `[negative]` |
| 5 | rtk | — | — | +7.6% | — | tie | `[negative]` |

**Groq measurement** (2026-10-05, `openai/gpt-oss-120b`, 12 SWE-bench Lite tasks):
The brevity instruction adds 10 input tokens but saves 522 output tokens.
Net effect: −512 tokens per task. No quality degradation. `[measured]`

**Copilot CLI measurement** (2026-10-05, `mai-code-1.1-flash`, 12 SWE-bench Lite tasks):
The brevity instruction saves 1,517 input tokens and 9.58 output tokens, but
neither is statistically significant (p=0.31, p=0.52). The effect is diluted
by fixed overhead: tool schemas (8,521 tokens) and system prompt (5,038 tokens)
dominate the session cost. Wall-clock reduction (−7.23s, p=0.08) is close to
significant. `[measured]`

## The baseline

| Metric | Value |
|---|---|
| Model | `mai-code-1.1-flash` via Copilot CLI v1.0.83 |
| Task | "echo hello" (simplest possible) |
| Total input tokens | 17,549 |
| Tool schema tokens | 8,521 (49%) |
| Session duration | 8.4s |
| Estimated cost | $0.055 |

## The task suite

12 real GitHub issues from: django, sympy, astropy, scikit-learn,
matplotlib, requests, flask, pandas, numpy, pytest, sphinx, tornado.

See `tasks/swebench_lite.json`.

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
token-harness run \
  --tasks tasks/swebench_lite.json \
  --config configs/copilot-cli.json \
  --output report.json
```

See [CONTRIBUTING.md](../CONTRIBUTING.md) for the entry format.

---

*Part of [awesome-token-minimalism](https://github.com/ranjithrajv/awesome-token-minimalism).*
