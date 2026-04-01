"""Tests for Temporal Evolution (Angle 4)."""
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "shared"))

from analyze_evolution import (
    compute_yearly_trends,
    detect_changepoints,
    POLICY_EVENTS,
)

SAMPLE_DATA = [
    {"start_date": "2005-01", "gap_score": "0.95", "core_count": "0", "has_PRO": "False", "generalizability_index": "78", "max_age": "75", "sex": "both"},
    {"start_date": "2005-06", "gap_score": "0.90", "core_count": "1", "has_PRO": "False", "generalizability_index": "80", "max_age": "70", "sex": "both"},
    {"start_date": "2010-01", "gap_score": "0.85", "core_count": "1", "has_PRO": "True", "generalizability_index": "82", "max_age": "None", "sex": "both"},
    {"start_date": "2010-06", "gap_score": "0.80", "core_count": "2", "has_PRO": "True", "generalizability_index": "85", "max_age": "80", "sex": "male"},
    {"start_date": "2015-01", "gap_score": "0.70", "core_count": "2", "has_PRO": "True", "generalizability_index": "88", "max_age": "None", "sex": "both"},
    {"start_date": "2015-06", "gap_score": "0.75", "core_count": "1", "has_PRO": "False", "generalizability_index": "83", "max_age": "80", "sex": "both"},
    {"start_date": "2020-01", "gap_score": "0.65", "core_count": "3", "has_PRO": "True", "generalizability_index": "90", "max_age": "None", "sex": "both"},
    {"start_date": "2020-06", "gap_score": "0.60", "core_count": "2", "has_PRO": "True", "generalizability_index": "87", "max_age": "85", "sex": "both"},
]


class TestYearlyTrends:
    def test_returns_yearly_data(self):
        result = compute_yearly_trends(SAMPLE_DATA)
        assert "years" in result
        assert len(result["years"]) > 0

    def test_has_gap_score_series(self):
        result = compute_yearly_trends(SAMPLE_DATA)
        assert "mean_gap_score" in result["years"][0]

    def test_has_core_pct_series(self):
        result = compute_yearly_trends(SAMPLE_DATA)
        assert "pct_with_core" in result["years"][0]

    def test_has_pro_pct_series(self):
        result = compute_yearly_trends(SAMPLE_DATA)
        assert "pct_with_PRO" in result["years"][0]

    def test_has_gi_series(self):
        result = compute_yearly_trends(SAMPLE_DATA)
        assert "mean_gi" in result["years"][0]

    def test_moving_average(self):
        result = compute_yearly_trends(SAMPLE_DATA)
        assert "ma5_gap_score" in result["years"][0]


class TestChangepoints:
    def test_returns_breakpoints(self):
        years = list(range(2000, 2024))
        values = [0.95 - 0.001 * (y - 2000) for y in range(2000, 2010)] + \
                 [0.85 - 0.01 * (y - 2010) for y in range(2010, 2024)]
        result = detect_changepoints(years, values)
        assert "breakpoints" in result
        assert "n_breakpoints" in result

    def test_constant_has_no_breakpoints(self):
        years = list(range(2000, 2024))
        values = [0.9] * 24
        result = detect_changepoints(years, values)
        assert result["n_breakpoints"] == 0


class TestPolicyEvents:
    def test_events_defined(self):
        assert len(POLICY_EVENTS) >= 4
        assert any("COMET" in e["label"] for e in POLICY_EVENTS)
