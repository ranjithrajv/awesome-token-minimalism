"""Real LLM task function for token-harness.

Calls the Anthropic API under each arm and measures actual token usage,
cost, and latency. The treatment arm adds a brevity instruction to the
system prompt; the baseline arm uses the same prompt without it.

Set ANTHROPIC_API_KEY in your environment before running.
"""

from __future__ import annotations

import os
import time
from pathlib import Path

from token_harness.runner import TaskResult

# Pricing per million tokens (Anthropic claude-sonnet-5, 2026-10)
# Update these when pricing changes.
PRICING = {
    "input": 3.0,
    "output": 15.0,
    "cache_write": 3.75,
    "cache_read": 0.30,
}

# The brevity instruction added to the treatment arm.
# This is the "seven-word baseline" from the token ledger.
BREVIITY_INSTRUCTION = "Follow YAGNI, prefer one-liners."


def _load_tasks(tasks_path: str | Path) -> list[dict]:
    """Load task descriptors from a JSON file."""
    import json

    return json.loads(Path(tasks_path).read_text(encoding="utf-8"))


def run_task(task: dict, arm: str, model: str = "claude-sonnet-5") -> TaskResult:
    """Execute one task under one arm using the Anthropic API.

    Args:
        task: Task descriptor with "id", "prompt", and optionally "text".
        arm: "baseline" or "treatment".
        model: Anthropic model ID.

    Returns:
        TaskResult with real measurements from the API response.
    """
    import anthropic

    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    # Build system prompt
    system_parts = ["You are a helpful coding assistant."]
    if arm == "treatment":
        system_parts.append(BREVIITY_INSTRUCTION)
    system = "\n".join(system_parts)

    # Build user message
    user_msg = task["prompt"]
    if task.get("text"):
        user_msg = f"{task['prompt']}\n\n{task['text']}"

    # Call the API
    start = time.monotonic()
    response = client.messages.create(
        model=model,
        max_tokens=4096,
        system=system,
        messages=[{"role": "user", "content": user_msg}],
    )
    wall_clock = time.monotonic() - start

    # Extract measurements
    usage = response.usage
    tokens_in = usage.input_tokens
    tokens_out = usage.output_tokens
    cache_write = getattr(usage, "cache_creation_input_tokens", 0) or 0
    cache_read = getattr(usage, "cache_read_input_tokens", 0) or 0

    # Calculate cost
    cost = (
        tokens_in * PRICING["input"]
        + tokens_out * PRICING["output"]
        + cache_write * PRICING["cache_write"]
        + cache_read * PRICING["cache_read"]
    ) / 1_000_000

    # Quality score: 1.0 if response has content, 0.0 if empty
    quality_score = 1.0 if response.content else 0.0

    return TaskResult(
        task_id=task["id"],
        arm=arm,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        cost_usd=cost,
        wall_clock_s=wall_clock,
        quality_score=quality_score,
        metadata={
            "model": model,
            "cache_write_tokens": cache_write,
            "cache_read_tokens": cache_read,
            "stop_reason": response.stop_reason,
        },
    )
