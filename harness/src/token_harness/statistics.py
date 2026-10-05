"""Statistical primitives for paired A/B measurement.

The harness uses a paired design: each task runs under both arms, and the
per-task difference is the unit of analysis. This controls for task
difficulty and gives a valid p-value with far fewer trials than an
unpaired design.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import stats


def count_tokens(text: str, model: str = "cl100k_base") -> int:
    """Count tokens using tiktoken (exact, no approximation).

    Args:
        text: The text to tokenize.
        model: The tokenizer to use. Default is cl100k_base (GPT-4).

    Returns:
        Exact token count.
    """
    import tiktoken

    encoding = tiktoken.get_encoding(model)
    return len(encoding.encode(text))


@dataclass(frozen=True)
class PairedResult:
    """Result of a paired A/B comparison."""

    n: int
    mean_diff: float
    ci_low: float
    ci_high: float
    p_value: float
    baseline_mean: float
    treatment_mean: float
    effect_pct: float

    def to_dict(self) -> dict:
        return {
            "n": self.n,
            "mean_diff": self.mean_diff,
            "ci_low": self.ci_low,
            "ci_high": self.ci_high,
            "p_value": self.p_value,
            "baseline_mean": self.baseline_mean,
            "treatment_mean": self.treatment_mean,
            "effect_pct": self.effect_pct,
        }


def paired_test(
    baseline: list[float],
    treatment: list[float],
    confidence: float = 0.95,
) -> PairedResult:
    """Run a paired t-test on per-task measurements.

    Args:
        baseline: Per-task metric under the baseline arm.
        treatment: Per-task metric under the treatment arm.
        confidence: Confidence level for the interval (default 0.95).

    Returns:
        PairedResult with n, mean difference, CI, p-value, and effect size.

    Raises:
        ValueError: If the two arms have different lengths or n < 2.
    """
    if len(baseline) != len(treatment):
        raise ValueError(
            f"Paired design requires equal lengths: {len(baseline)} vs {len(treatment)}"
        )
    n = len(baseline)
    if n < 2:
        raise ValueError(f"Need at least 2 paired samples, got {n}")

    b = np.asarray(baseline, dtype=float)
    t = np.asarray(treatment, dtype=float)
    diff = t - b

    mean_diff = float(np.mean(diff))
    baseline_mean = float(np.mean(b))
    treatment_mean = float(np.mean(t))

    # Paired t-test
    # When all differences are identical (e.g. all zeros), the t-statistic
    # is undefined (0/0). scipy returns nan; we report p=1.0 (no evidence
    # of a difference) which is the correct interpretation.
    if np.all(diff == diff[0]):
        # All differences are the same value
        if diff[0] == 0:
            # No difference at all
            return PairedResult(
                n=n,
                mean_diff=0.0,
                ci_low=0.0,
                ci_high=0.0,
                p_value=1.0,
                baseline_mean=baseline_mean,
                treatment_mean=treatment_mean,
                effect_pct=0.0,
            )
        else:
            # Constant non-zero difference — infinitely significant
            # but we can't compute a CI without variance
            return PairedResult(
                n=n,
                mean_diff=float(diff[0]),
                ci_low=float(diff[0]),
                ci_high=float(diff[0]),
                p_value=0.0,
                baseline_mean=baseline_mean,
                treatment_mean=treatment_mean,
                effect_pct=(diff[0] / baseline_mean * 100) if baseline_mean != 0 else 0.0,
            )

    t_stat, p_value = stats.ttest_rel(t, b)

    # Confidence interval for the mean difference
    se = float(np.std(diff, ddof=1) / np.sqrt(n))
    alpha = 1 - confidence
    t_crit = float(stats.t.ppf(1 - alpha / 2, df=n - 1))
    ci_low = mean_diff - t_crit * se
    ci_high = mean_diff + t_crit * se

    # Effect size as percentage of baseline mean
    effect_pct = (mean_diff / baseline_mean * 100) if baseline_mean != 0 else 0.0

    return PairedResult(
        n=n,
        mean_diff=mean_diff,
        ci_low=ci_low,
        ci_high=ci_high,
        p_value=float(p_value),
        baseline_mean=baseline_mean,
        treatment_mean=treatment_mean,
        effect_pct=effect_pct,
    )
