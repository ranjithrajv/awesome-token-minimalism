# token-harness

Paired A/B measurement harness for token-saving tools. Built for
[awesome-token-minimalism](https://github.com/ranjithrajv/awesome-token-minimalism).

Every claim in the list needs a baseline, a method, and a re-runnable
harness. This package provides the harness.

## Design

- **Paired design**: each task runs under both arms; the per-task difference
  is the unit of analysis. Controls for task difficulty.
- **Pinned model**: all runs stamp the model, harness version, date, and seed.
- **Quality guard**: a separate metric that must not degrade. A token-saving
  tool that breaks quality is `[negative]`, not `[measured]`.
- **Provenance stamp**: every report carries enough metadata to re-run.

## Install

```sh
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

`tasks/swebench_lite.json` — 12 real GitHub issues from popular Python
repositories (django, sympy, astropy, scikit-learn, matplotlib, requests,
flask, pandas, numpy, pytest, sphinx, tornado). Each task is a real bug fix
with a real repository context.

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

**Key finding:** Tool schemas cost 8,521 tokens per session — a permanent tax on every turn. The capability those schemas provide is real; the question is whether loading all 23 eagerly is the only way to provide it. Route them on demand and the capability is preserved, the cost is removed. The system prompt is 5,038 tokens (29%) — compact it and the behavior is preserved, the cost is removed. The actual user message ("echo hello") is a rounding error.

### Write your own

The function signature is `(task: dict, arm: str) -> TaskResult`.

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
