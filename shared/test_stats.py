"""Tests for stats_utils — 12 tests covering all statistical functions."""

import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from stats_utils import (
    normal_cdf,
    chi_squared_2x2,
    cramers_v,
    mann_whitney_u,
    rank_biserial,
    segmented_regression,
    logistic_regression_simple,
)


class TestNormalCDF:
    def test_zero(self):
        assert abs(normal_cdf(0) - 0.5) < 1e-6

    def test_positive_196(self):
        assert abs(normal_cdf(1.96) - 0.975) < 1e-3

    def test_negative_196(self):
        assert abs(normal_cdf(-1.96) - 0.025) < 1e-3


class TestChiSquared2x2:
    def test_significant(self):
        chi2, p = chi_squared_2x2(80, 20, 60, 40)
        assert chi2 > 3.84, f"chi2={chi2} should be > 3.84"
        assert p < 0.05, f"p={p} should be < 0.05"

    def test_not_significant(self):
        chi2, p = chi_squared_2x2(50, 50, 50, 50)
        assert chi2 < 1.0, f"chi2={chi2} should be ~0"
        assert p > 0.9, f"p={p} should be > 0.9"


class TestCramersV:
    def test_perfect_association(self):
        v = cramers_v(100, 0, 0, 100)
        assert v > 0.9, f"v={v} should be > 0.9"

    def test_no_association(self):
        v = cramers_v(50, 50, 50, 50)
        assert v < 0.05, f"v={v} should be < 0.05"


class TestMannWhitneyU:
    def test_identical_groups(self):
        _, p = mann_whitney_u([1, 2, 3, 4, 5], [1, 2, 3, 4, 5])
        assert p > 0.5, f"p={p} should be > 0.5 for identical groups"

    def test_separated_groups(self):
        _, p = mann_whitney_u([1, 2, 3, 4, 5], [10, 11, 12, 13, 14])
        assert p < 0.05, f"p={p} should be < 0.05 for separated groups"


class TestRankBiserial:
    def test_strong_effect(self):
        rb = rank_biserial([1, 2, 3], [10, 11, 12])
        assert rb < -0.5, f"rb={rb} should be < -0.5"


class TestSegmentedRegression:
    def test_linear_data_zero_breakpoints(self):
        x = list(range(20))
        y = [2.0 * xi + 1.0 for xi in x]
        result = segmented_regression(x, y)
        assert result["n_breakpoints"] == 0, (
            f"Expected 0 breakpoints for linear data, got {result['n_breakpoints']}"
        )

    def test_kinked_data_finds_breakpoint(self):
        # Kink at x=10: slope 1 before, slope 5 after
        x = list(range(21))
        y = []
        for xi in x:
            if xi <= 10:
                y.append(float(xi))
            else:
                y.append(10.0 + 5.0 * (xi - 10))
        result = segmented_regression(x, y)
        assert result["n_breakpoints"] >= 1, "Should find at least 1 breakpoint"
        # Breakpoint should be near x=10
        bp = result["breakpoints"][0]
        assert 8 <= bp <= 12, f"Breakpoint {bp} should be near 10"


class TestLogisticRegression:
    def test_separable_data(self):
        # X values: low values -> y=0, high values -> y=1
        X = [[1], [2], [3], [4], [5], [10], [11], [12], [13], [14]]
        y = [0, 0, 0, 0, 0, 1, 1, 1, 1, 1]
        result = logistic_regression_simple(X, y, max_iter=50)
        assert result["coefficients"][0] > 0, (
            f"Coefficient {result['coefficients'][0]} should be positive for separable data"
        )
