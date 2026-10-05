"""CLI for token-harness.

Usage:
    token-harness run --tasks tasks/example.json --config config.json --output report.json
    token-harness report --input report.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def cmd_run(args: argparse.Namespace) -> int:
    """Run a paired A/B experiment from task and config files."""
    from .runner import HarnessConfig, run_paired, save_report

    tasks = json.loads(Path(args.tasks).read_text(encoding="utf-8"))
    config_dict = json.loads(Path(args.config).read_text(encoding="utf-8"))

    config = HarnessConfig(
        model=config_dict["model"],
        n_tasks=len(tasks),
        confidence=config_dict.get("confidence", 0.95),
        seed=config_dict.get("seed"),
        metadata=config_dict.get("metadata", {}),
    )

    # Import the task function dynamically
    task_fn_path = config_dict.get("task_fn", "tasks.example:run_task")
    module_name, fn_name = task_fn_path.split(":")
    import importlib

    task_fn = getattr(importlib.import_module(module_name), fn_name)

    report = run_paired(tasks, task_fn, config)
    save_report(report, args.output)
    print(f"Report written to {args.output}")
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    """Pretty-print a harness report."""
    report = json.loads(Path(args.input).read_text(encoding="utf-8"))

    print(f"Model: {report['provenance']['model']}")
    print(f"Tasks: {report['provenance']['n_tasks']}")
    print(f"Date:  {report['provenance']['timestamp']}")
    print()

    for metric, stats_dict in report["paired"].items():
        sig = "*" if stats_dict["p_value"] < 0.05 else " "
        print(
            f"  {metric:14s}  Δ {stats_dict['mean_diff']:+.2f}  "
            f"[{stats_dict['ci_low']:+.2f}, {stats_dict['ci_high']:+.2f}]  "
            f"p={stats_dict['p_value']:.4f} {sig}"
        )

    if report.get("quality_guard"):
        qg = report["quality_guard"]
        print()
        print(
            f"  quality guard   Δ {qg['mean_diff']:+.3f}  "
            f"[{qg['ci_low']:+.3f}, {qg['ci_high']:+.3f}]  "
            f"p={qg['p_value']:.4f}"
        )

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="token-harness")
    sub = parser.add_subparsers(dest="command", required=True)

    run_p = sub.add_parser("run", help="Run a paired A/B experiment")
    run_p.add_argument("--tasks", required=True, help="Path to tasks JSON file")
    run_p.add_argument("--config", required=True, help="Path to config JSON file")
    run_p.add_argument("--output", default="report.json", help="Output report path")
    run_p.set_defaults(func=cmd_run)

    report_p = sub.add_parser("report", help="Pretty-print a report")
    report_p.add_argument("--input", required=True, help="Path to report JSON")
    report_p.set_defaults(func=cmd_report)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
