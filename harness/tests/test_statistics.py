"""Tests for paired A/B statistics."""

from __future__ import annotations

import pytest

from token_harness.statistics import paired_test


def test_paired_test_basic():
    """Test that paired_test detects a clear difference."""
    baseline = [100.0] * 20
    treatment = [80.0] * 20
    result = paired_test(baseline, treatment)
    assert result.n == 20
    assert result.mean_diff == pytest.approx(-20.0)
    assert result.p_value < 0.001
    assert result.effect_pct == pytest.approx(-20.0)


def test_paired_test_no_difference():
    """Test that paired_test reports no significant difference when arms match."""
    baseline = [100.0] * 20
    treatment = [100.0] * 20
    result = paired_test(baseline, treatment)
    assert result.p_value == pytest.approx(1.0)
    assert result.effect_pct == pytest.approx(0.0)


def test_paired_test_unequal_lengths():
    """Test that paired_test raises on unequal arm lengths."""
    with pytest.raises(ValueError, match="equal lengths"):
        paired_test([1.0, 2.0], [1.0])


def test_paired_test_too_few_samples():
    """Test that paired_test raises with fewer than 2 samples."""
    with pytest.raises(ValueError, match="at least 2"):
        paired_test([1.0], [2.0])


def test_paired_test_with_noise():
    """Test paired_test with realistic noisy data."""
    import numpy as np

    rng = np.random.default_rng(42)
    baseline = rng.normal(100, 10, 50).tolist()
    treatment = (rng.normal(95, 10, 50)).tolist()
    result = paired_test(baseline, treatment)
    assert result.n == 50
    assert result.ci_low < result.mean_diff < result.ci_high
