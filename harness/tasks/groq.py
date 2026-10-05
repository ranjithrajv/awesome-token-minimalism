"""Groq task executor for token-harness.

Free-tier replacement for the retired GitHub Models. Uses the OpenAI-compatible
endpoint at https://api.groq.com/openai/v1 with GROQ_API_KEY.

Free tier: 30 requests/min, 14,400 requests/day (as of 2026-10).
"""

from __future__ import annotations

import os
import time

from token_harness.runner import TaskResult

# Groq pricing (free tier — $0.00)
PRICING = {
    "input": 0.0,
    "output": 0.0,
}

# Default model — free tier (as of 2026-10)
DEFAULT_MODEL = "openai/gpt-oss-120b"


def run_task(task: dict, arm: str, model: str = DEFAULT_MODEL) -> TaskResult:
    """Execute one task via Groq's OpenAI-compatible API.

    Args:
        task: Task descriptor with "id" and "prompt" keys.
        arm: "baseline" or "treatment". Treatment adds brevity instruction.
        model: Groq model ID.

    Returns:
        TaskResult with measurements from the API response.
    """
    from openai import OpenAI

    client = OpenAI(
        api_key=os.environ.get("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1",
    )

    # Build system prompt
    system_parts = ["You are a helpful coding assistant."]
    if arm == "treatment":
        system_parts.append("Follow YAGNI, prefer one-liners.")
    system = "\n".join(system_parts)

    # Build user message
    user_msg = task["prompt"]
    if task.get("text"):
        user_msg = f"{task['prompt']}\n\n{task['text']}"

    # Call the API with retry and exponential backoff
    max_retries = 5
    base_delay = 2.0
    start = time.monotonic()

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user_msg},
                ],
                max_tokens=4096,
            )
            wall_clock = time.monotonic() - start
            break
        except Exception as e:
            if "rate_limit" in str(e).lower() and attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)
                time.sleep(delay)
                continue
            wall_clock = time.monotonic() - start
            return TaskResult(
                task_id=task["id"],
                arm=arm,
                tokens_in=0,
                tokens_out=0,
                cost_usd=0.0,
                wall_clock_s=wall_clock,
                quality_score=0.0,
                metadata={"error": str(e), "arm": arm, "model": model},
            )

    # Extract measurements
    usage = response.usage
    tokens_in = usage.prompt_tokens
    tokens_out = usage.completion_tokens

    # Calculate cost (free tier)
    cost = (
        tokens_in * PRICING["input"]
        + tokens_out * PRICING["output"]
    ) / 1_000_000

    # Quality score: 1.0 if response has content, 0.0 if empty
    quality_score = 1.0 if response.choices and response.choices[0].message.content else 0.0

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
            "provider": "groq",
            "arm": arm,
            "finish_reason": response.choices[0].finish_reason if response.choices else None,
        },
    )
