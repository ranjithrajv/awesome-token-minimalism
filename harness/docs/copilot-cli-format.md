# Copilot CLI Output Format Dependency

The `tasks/copilot_cli.py` executor parses the JSON output from
`copilot -p "prompt" --output-format json`. This document pins the
format and version so breakage is detectable.

## Pinned version

- **Copilot CLI**: v1.0.83
- **Date**: 2026-10-05
- **Model**: `mai-code-1.1-flash`

## Output format

The CLI outputs newline-delimited JSON events. The executor parses:

### `session.usage_checkpoint` event

```json
{
  "type": "session.usage_checkpoint",
  "data": {
    "promptCacheBreakState": [{
      "conversation": "main",
      "models": {
        "<model_name>": {
          "model": "<model_name>",
          "prompt_tokens": 17549,
          "cache_read": 8704,
          "cache_write": 0,
          "tool_tokens": 8521,
          "tool_count": 23,
          "system_segments": [
            {"segment": "identity", "tokens": 503},
            {"segment": "tool_instructions", "tokens": 7101},
            ...
          ]
        }
      }
    }]
  }
}
```

### `result` event

```json
{
  "type": "result",
  "exitCode": 0,
  "usage": {
    "premiumRequests": 1,
    "totalApiDurationMs": 2760,
    "sessionDurationMs": 7479,
    "codeChanges": {"linesAdded": 0, "linesRemoved": 0, "filesModified": []}
  }
}
```

`sessionDurationMs` is illustrative (one session); the published baseline
reports 8.4s for a different run. The executor computes cost at Claude Sonnet-5
list rates as a proxy, because `mai-code-1.1-flash` rates are not published.

## Fields the executor depends on

| Field path | Used for | Breakage risk |
|---|---|---|
| `data.promptCacheBreakState[].models[].prompt_tokens` | `tokens_in` | High — nested deeply |
| `data.promptCacheBreakState[].models[].cache_read` | `cache_read` | High |
| `data.promptCacheBreakState[].models[].cache_write` | `cache_write` | High |
| `data.promptCacheBreakState[].models[].tool_tokens` | `tool_tokens` | High |
| `data.promptCacheBreakState[].models[].tool_count` | `tool_calls` | High |
| `data.promptCacheBreakState[].models[].system_segments` | per-segment breakdown | Medium |
| `exitCode` | quality guard | Low — top-level |
| `usage.sessionDurationMs` | `session_duration_ms` | Low — top-level |

## Fallback strategy

If the format changes:

1. **Detect**: The parser returns `tokens_in: 0` when `prompt_tokens` is missing.
2. **Alert**: A zero `tokens_in` yields `quality_score = 0.0`; the runner must
   treat a zero-quality arm as invalid, not as a measured zero.
3. **Fallback**: Use `tasks/example.py` (direct Anthropic API) which has a stable, documented response format.
4. **Fix**: Update `_parse_copilot_output()` in `tasks/copilot_cli.py`.

## Why this matters

The Copilot CLI is closed-source. The JSON output format is not a public API
and can change without notice. The executor is coupled to this format —
pinning it here makes the dependency explicit and breakage detectable.

## Alternative: direct API

For a stable, documented format, use `tasks/example.py` which calls the
Anthropic API directly. The response format is versioned and documented.
The tradeoff: it measures a single API call, not the full agent loop.
