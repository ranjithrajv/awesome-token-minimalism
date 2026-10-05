# token-harness

Paired A/B measurement harness for token-saving tools. Built for
[awesome-token-minimalism](https://github.com/ranjithrajv/awesome-token-minimalism).

Every claim in the list needs a baseline, a method, and a re-runnable
harness. This package provides the harness.

## TL;DR

**Most token-savings claims fail independent measurement.** Of three popular
tools put through one paired A/B harness, one delivered −8.5% against a −65%
claim, one was *more expensive* than baseline, and one underdelivered on code
size but did deliver on cost. A seven-word prompt — "Follow YAGNI, prefer
one-liners" — matched the best tool on cost and time. Every entry in the list
carries an evidence grade: `[measured]`, `[self-reported]`, `[asserted]`, or
`[negative]`. Read the [token ledger](../README.md#token-ledger) before buying
anything.

**Measure it yourself:**
- [`token-receipt`](https://github.com/ranjithrajv/token-receipt) — audit instruction files in any repo
- [`token-harness`](.) — paired A/B measurement for token-saving tools (this package)
- [`count_tokens.py`](../.github/scripts/count_tokens.py) — the list meters its own prose; CI fails if it crosses budget

**Copilot CLI baseline** (v1.0.83, `mai-code-1.1-flash`, task: "echo hello"):
17,549 tokens ($0.055, computed at Sonnet-5 list rates as a proxy — `mai-code`
rates are not published), of which tool schemas are 8,521 — a permanent tax on
every session. Full breakdown in
[the Copilot CLI executor](#copilot-cli-full-agent-loop).

**Paired A/B finding** (2026-10-05, same instruction, two surfaces): the
seven-word prompt "Follow YAGNI, prefer one-liners" cuts output **418.25 tokens
per task** on single Groq API calls across the full **48-task** suite
(**p=0.0001**), but only **9.58** on full Copilot CLI agent sessions
(**p=0.52**). Earlier Groq pilots measured −522 (12 tasks, p=0.0004) and
−268.67 (24 tasks, p=0.053); the 48-task run is the one to trust. The
measurement surface *and* the sample size matter. See
[LEADERBOARD.md](LEADERBOARD.md) and [the writeup](../posts/harness-results.md).

## Design

- **Paired design**: each task runs under both arms; the per-task difference
  is the unit of analysis. Controls for task difficulty.
- **Pinned model**: all runs stamp the model, harness version, date, and seed.
- **Quality guard**: a separate metric that must not degrade. A token-saving
  tool that breaks quality is `[negative]`, not `[measured]`.
- **Provenance stamp**: every report carries enough metadata to re-run.
- **Exact input token counting**: `tiktoken` (the tokenizer for OpenAI/Anthropic
  models) rather than regex approximation. Output tokens from the Copilot CLI
  executor are estimated at 4 chars/token because the CLI does not report them.

## Install

Run from the `harness/` directory; the `--tasks`/`--config` paths below resolve
against it.

```sh
cd harness
pip install -e ".[dev]"
```

## Run

```sh
token-harness run \
  --tasks tasks/example.json \
  --config configs/example.json \
  --output report.json

token-harness report --input report.json
```

## Task suites

### SWE-bench Lite (real tasks)

`tasks/swebench_lite.json` — 48 real GitHub issues (four each from django,
sympy, astropy, scikit-learn, matplotlib, requests, flask, pandas, numpy,
pytest, sphinx, and tornado). Each task is a real bug fix with a real
repository context.

```sh
token-harness run --tasks tasks/swebench_lite.json --config configs/copilot-cli.json --output report.json
```

### Synthetic (placeholder)

`tasks/example.json` — 20 simple prompts for smoke testing. Not real
tasks; use SWE-bench Lite for actual measurements.

## Task executors

### Anthropic API (direct)

`tasks/example.py` — calls `claude-sonnet-5` directly. Measures a single
API call. Requires `ANTHROPIC_API_KEY`.

```sh
export ANTHROPIC_API_KEY=sk-ant-...
token-harness run --tasks tasks/swebench_lite.json --config configs/example.json --output report.json
```

### Copilot CLI (full agent loop)

`tasks/copilot_cli.py` — runs tasks via GitHub Copilot CLI in headless mode.
Measures the **full agent loop**: system prompt + tool schemas + N tool calls
+ N tool results + final output. This is the real number the list cares about.

```sh
token-harness run --tasks tasks/swebench_lite.json --config configs/copilot-cli.json --output report.json
```

The Copilot CLI executor parses the JSON output and extracts:
- `prompt_tokens` — total input tokens
- `cache_read` / `cache_write` — cache token usage
- `tool_tokens` — tokens spent on tool schemas
- `tool_calls` — number of tool invocations
- `system_segments` — per-segment breakdown (identity, tool_instructions, etc.)

**Format dependency**: The parser is coupled to the Copilot CLI JSON output
format (pinned to v1.0.83). See [docs/copilot-cli-format.md](docs/copilot-cli-format.md)
for the pinned format and fallback strategy.

**Authentication**: The Copilot CLI needs `GH_TOKEN` set as an environment
variable. The executor automatically extracts it from `gh auth token` if
not already set. Run `gh auth login` first if you haven't authenticated.

### Groq (free-tier CI)

`tasks/groq.py` — calls Groq's OpenAI-compatible API. Free tier: 30 req/min,
14,400 req/day. Replacement for the retired GitHub Models.

```sh
export GROQ_API_KEY=gsk_...
token-harness run --tasks tasks/swebench_lite.json --config configs/groq.json --output report.json
```

**Available models** (as of 2026-10, free tier):
`openai/gpt-oss-120b`, `openai/gpt-oss-20b`, `qwen/qwen3.8-27b`,
`allam-2-7b`, `whisper-large-v3`, `whisper-large-v3-turbo`.

The default is `openai/gpt-oss-120b` — the most capable general-purpose
model on the free tier.

**Rate limits:** The free tier has per-model TPM limits (e.g. 8,000 TPM
for `gpt-oss-120b`). The executor retries with exponential backoff
(2s, 4s, 8s, 16s, 32s) on rate limit errors. For large task suites,
expect the run to take several minutes.

**Measured baseline** (Copilot CLI v1.0.83, model `mai-code-1.1-flash`, task: "echo hello"):

| Metric | Value |
|---|---|
| Total input tokens | 17,549 |
| Cache read | 8,704 |
| Tool schema tokens | 8,521 |
| Tool calls | 23 |
| Session duration | 8.4s |
| Estimated cost | $0.055 |

Per-system-segment breakdown:

| Segment | Tokens |
|---|---|
| tool_instructions | 7,101 |
| identity | 503 |
| custom_instructions | 797 |
| additional_instructions | 455 |
| code_change_instructions | 295 |
| environment_limitations | 235 |
| dynamic_guidelines | 201 |
| environment_context | 100 |
| model_information | 47 |
| tool_intro | 20 |
| version_information | 9 |

**Key finding:** Tool schemas cost 8,521 tokens per session — a permanent tax on every turn. The capability those schemas provide is real; the question is whether loading all 23 eagerly is the only way to provide it. Route them on demand and the capability is preserved, the cost is removed. The per-segment table above is where the rest of the fixed cost sits — `tool_instructions` is the single largest segment at 7,101 tokens. The actual user message ("echo hello") is a rounding error.

### Write your own

A tool plugs in as a task executor — a function
`(task: dict, arm: str) -> TaskResult`, referenced from your config's `task_fn`.
Return the measured `tokens_in`, `tokens_out`, `cost_usd`, `wall_clock_s`, and
`quality_score`; the runner pairs the arms and computes the statistics for you.
See `tasks/copilot_cli.py` for a full agent-loop executor and
`tasks/example.py` for a single-call one.

## Add your tool

1. Implement a `(task: dict, arm: str) -> TaskResult` executor — see
   [Write your own](#write-your-own).
2. Point a config's `task_fn` at it, alongside the task suite you ran.
3. `cd harness && token-harness run --tasks tasks/swebench_lite.json --config configs/your-tool.json --output report.json`.
4. Open a PR with the report and the config. The [leaderboard](LEADERBOARD.md)
   only admits a run with a baseline, a method, and a quality guard.

## Output

```json
{
  "provenance": {
    "model": "claude-sonnet-5",
    "n_tasks": 20,
    "confidence": 0.95,
    "seed": 42,
    "timestamp": "2026-10-05T..."
  },
  "paired": {
    "tokens_in": { "n": 20, "mean_diff": -400, "p_value": 0.001, ... },
    "tokens_out": { "n": 20, "mean_diff": -50, "p_value": 0.02, ... },
    "cost_usd": { "n": 20, "mean_diff": -0.002, "p_value": 0.003, ... }
  },
  "quality_guard": { "n": 20, "mean_diff": 0.0, "p_value": 0.8, ... }
}
```

## License

CC0 1.0, same as the list.
