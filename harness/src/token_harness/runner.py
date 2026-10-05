"""Paired A/B runner: executes tasks under both arms and collects measurements.

The runner is model-agnostic. It takes a callable that performs one task
under a given arm and returns a measurement dict. The harness handles
pairing, statistics, and reporting.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from .statistics import PairedResult, paired_test


@dataclass
class TaskResult:
    """Measurement for one task under one arm."""

    task_id: str
    arm: str
    tokens_in: int
    tokens_out: int
    cost_usd: float
    wall_clock_s: float
    quality_score: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class HarnessConfig:
    """Configuration for a harness run."""

    model: str
    n_tasks: int
    confidence: float = 0.95
    seed: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


# A task function takes (task: dict, arm: str) -> TaskResult
TaskFn = Callable[[dict, str], TaskResult]


def run_paired(
    tasks: list[dict],
    task_fn: TaskFn,
    config: HarnessConfig,
) -> dict[str, Any]:
    """Run a paired A/B experiment.

    Args:
        tasks: List of task descriptors (at least 2).
        task_fn: Callable that executes one task under one arm.
        config: Harness configuration.

    Returns:
        Dict with per-task results, paired statistics, and a provenance stamp.
    """
    if len(tasks) < 2:
        raise ValueError(f"Need at least 2 tasks, got {len(tasks)}")

    results: list[TaskResult] = []

    for task in tasks:
        task_id = task["id"]
        for arm in ("baseline", "treatment"):
            result = task_fn(task, arm)
            results.append(result)

    # Group by metric and run paired tests
    metrics = ["tokens_in", "tokens_out", "cost_usd", "wall_clock_s"]
    paired: dict[str, PairedResult] = {}

    for metric in metrics:
        baseline_vals = [
            getattr(r, metric)
            for r in results
            if r.arm == "baseline" and r.task_id in {t["id"] for t in tasks}
        ]
        treatment_vals = [
            getattr(r, metric)
            for r in results
            if r.arm == "treatment" and r.task_id in {t["id"] for t in tasks}
        ]
        # Ensure ordering matches
        task_ids = [t["id"] for t in tasks]
        baseline_vals = [
            next(getattr(r, metric) for r in results if r.arm == "baseline" and r.task_id == tid)
            for tid in task_ids
        ]
        treatment_vals = [
            next(getattr(r, metric) for r in results if r.arm == "treatment" and r.task_id == tid)
            for tid in task_ids
        ]
        paired[metric] = paired_test(baseline_vals, treatment_vals, config.confidence)

    # Quality guard (if provided)
    quality_result = None
    baseline_quality = [
        r.quality_score
        for r in results
        if r.arm == "baseline" and r.quality_score is not None
    ]
    treatment_quality = [
        r.quality_score
        for r in results
        if r.arm == "treatment" and r.quality_score is not None
    ]
    if baseline_quality and treatment_quality:
        quality_result = paired_test(baseline_quality, treatment_quality, config.confidence)

    stamp = {
        "model": config.model,
        "n_tasks": len(tasks),
        "confidence": config.confidence,
        "seed": config.seed,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        **config.metadata,
    }

    return {
        "provenance": stamp,
        "tasks": [
            {
                "id": r.task_id,
                "arm": r.arm,
                "tokens_in": r.tokens_in,
                "tokens_out": r.tokens_out,
                "cost_usd": r.cost_usd,
                "wall_clock_s": r.wall_clock_s,
                "quality_score": r.quality_score,
                "metadata": r.metadata,
            }
            for r in results
        ],
        "paired": {k: v.to_dict() for k, v in paired.items()},
        "quality_guard": quality_result.to_dict() if quality_result else None,
    }


def save_report(report: dict[str, Any], path: str | Path) -> None:
    """Write a harness report to disk as JSON."""
    Path(path).write_text(json.dumps(report, indent=2), encoding="utf-8")
