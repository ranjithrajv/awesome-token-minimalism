"""Copilot CLI task executor for token-harness.

Runs tasks via GitHub Copilot CLI in headless mode and measures the full
agent loop: system prompt + tool schemas + N tool calls + N tool results +
final output. This is the real number the list cares about — not a single
API call, but an actual agent session.

Requires:
    - GitHub Copilot CLI installed (`copilot --version`)
    - Authenticated (`copilot -i "auth status"`)
    - A GitHub repository context (run from within a git repo)

Usage:
    token-harness run --tasks tasks/example.json --config configs/copilot-cli.json
"""

from __future__ import annotations

import json
import os
import subprocess
import time

from token_harness.runner import TaskResult


def _parse_copilot_output(stdout: str) -> dict:
    """Parse Copilot CLI JSON output and extract token usage.

    The CLI outputs newline-delimited JSON events. We care about:
    - session.usage_checkpoint: prompt_tokens, cache_read, cache_write, tool_tokens
    - result: exitCode, usage (premiumRequests, sessionDurationMs)

    Args:
        stdout: Raw JSON output from `copilot -p`.

    Returns:
        Dict with tokens_in, tokens_out, cost_usd, wall_clock_s, tool_calls,
        system_segments, and metadata.
    """
    events = []
    for line in stdout.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue

    result = {
        "tokens_in": 0,
        "tokens_out": 0,
        "cache_read": 0,
        "cache_write": 0,
        "tool_tokens": 0,
        "tool_calls": 0,
        "system_segments": {},
        "exit_code": 0,
        "session_duration_ms": 0,
        "model": "unknown",
    }

    for event in events:
        etype = event.get("type", "")

        if etype == "session.usage_checkpoint":
            data = event.get("data", {})

            # Extract per-system-segment breakdown
            # prompt_tokens is nested inside promptCacheBreakState
            for seg in data.get("promptCacheBreakState", []):
                for model_name, model_data in seg.get("models", {}).items():
                    result["model"] = model_name
                    result["tokens_in"] = model_data.get("prompt_tokens", 0)
                    result["cache_read"] = model_data.get("cache_read", 0)
                    result["cache_write"] = model_data.get("cache_write", 0)
                    result["tool_tokens"] = model_data.get("tool_tokens", 0)
                    result["tool_calls"] = model_data.get("tool_count", 0)
                    for segment in model_data.get("system_segments", []):
                        seg_name = segment.get("segment", "unknown")
                        seg_tokens = segment.get("tokens", 0)
                        result["system_segments"][seg_name] = seg_tokens

        elif etype == "result":
            # result event has fields at top level, not under "data"
            result["exit_code"] = event.get("exitCode", 0)
            usage = event.get("usage", {})
            result["session_duration_ms"] = usage.get("sessionDurationMs", 0)

    # Extract output tokens from assistant.message events.
    # The CLI doesn't report output token counts directly, but each
    # assistant.message event has a content field. We estimate output
    # tokens from the content length using the same ~4 chars/token heuristic
    # as token-receipt.
    output_chars = 0
    for event in events:
        if event.get("type") == "assistant.message":
            content = event.get("data", {}).get("content", "")
            output_chars += len(content)
    result["tokens_out"] = output_chars // 4 if output_chars > 0 else 0

    # Calculate cost from token counts
    # Claude Sonnet 5 pricing: $3/M input, $15/M output, $3.75/M cache write, $0.30/M cache read
    result["cost_usd"] = (
        result["tokens_in"] * 3.0
        + result["tokens_out"] * 15.0
        + result["cache_write"] * 3.75
        + result["cache_read"] * 0.30
    ) / 1_000_000

    return result


def run_task(task: dict, arm: str) -> TaskResult:
    """Execute one task via Copilot CLI and measure the full agent loop.

    Args:
        task: Task descriptor with "id" and "prompt" keys.
        arm: "baseline" or "treatment". Treatment adds brevity instruction.

    Returns:
        TaskResult with measurements from the Copilot session.
    """
    # Build the prompt
    prompt = task["prompt"]
    if task.get("text"):
        prompt = f"{task['prompt']}\n\n{task['text']}"

    if arm == "treatment":
        prompt = f"Follow YAGNI, prefer one-liners.\n\n{prompt}"

    # Ensure GH_TOKEN is set for Copilot CLI authentication.
    # The Copilot CLI cannot read the gh keyring directly; it needs the
    # token as an environment variable.
    env = os.environ.copy()
    if not env.get("GH_TOKEN"):
        try:
            token = subprocess.run(
                ["gh", "auth", "token"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if token.returncode == 0 and token.stdout.strip():
                env["GH_TOKEN"] = token.stdout.strip().splitlines()[-1]
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

    # Run Copilot CLI in headless mode
    start = time.monotonic()
    try:
        result = subprocess.run(
            ["copilot", "-p", prompt, "--output-format", "json"],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=os.getcwd(),
            env=env,
        )
        wall_clock = time.monotonic() - start
    except subprocess.TimeoutExpired:
        wall_clock = time.monotonic() - start
        return TaskResult(
            task_id=task["id"],
            arm=arm,
            tokens_in=0,
            tokens_out=0,
            cost_usd=0.0,
            wall_clock_s=wall_clock,
            quality_score=0.0,
            metadata={"error": "timeout", "arm": arm},
        )
    except FileNotFoundError:
        raise RuntimeError(
            "Copilot CLI not found. Install it from https://github.com/features/copilot/cli"
        )

    # Parse the JSON output
    usage = _parse_copilot_output(result.stdout)

    # Quality score: 1.0 if exit code 0 and we got tokens, 0.0 otherwise
    quality_score = 1.0 if usage["exit_code"] == 0 and usage["tokens_in"] > 0 else 0.0

    return TaskResult(
        task_id=task["id"],
        arm=arm,
        tokens_in=usage["tokens_in"],
        tokens_out=usage["tokens_out"],
        cost_usd=usage["cost_usd"],
        wall_clock_s=wall_clock,
        quality_score=quality_score,
        metadata={
            "arm": arm,
            "model": usage["model"],
            "tool_calls": usage["tool_calls"],
            "tool_tokens": usage["tool_tokens"],
            "cache_read": usage["cache_read"],
            "cache_write": usage["cache_write"],
            "system_segments": usage["system_segments"],
            "session_duration_ms": usage["session_duration_ms"],
            "copilot_exit_code": usage["exit_code"],
        },
    )
