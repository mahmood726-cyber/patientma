"""Tests for Transparency Angles 5, 7, 12."""
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "shared"))

from analyze_transparency import (
    analyze_sponsor_comparison,
    analyze_results_transparency,
    analyze_publication_gap,
)

SAMPLE_CLASSIFIED = [
    {"nct_id": "NCT001", "sponsor_class": "INDUSTRY", "phase": "PHASE3", "era": "2015-2019", "core_count": 3, "surrogate_count": 1, "has_PRO": True, "gap_score": 0.25, "has_results": "True", "enrollment": 500, "start_date": "2018-01", "completion_date": "2021-06", "detected_condition": "heart_failure"},
    {"nct_id": "NCT002", "sponsor_class": "OTHER", "phase": "PHASE2", "era": "2015-2019", "core_count": 0, "surrogate_count": 2, "has_PRO": False, "gap_score": 1.0, "has_results": "False", "enrollment": 100, "start_date": "2015-03", "completion_date": "2017-09", "detected_condition": "heart_failure"},
    {"nct_id": "NCT003", "sponsor_class": "INDUSTRY", "phase": "PHASE3", "era": "2010-2014", "core_count": 2, "surrogate_count": 0, "has_PRO": False, "gap_score": 0.0, "has_results": "True", "enrollment": 2000, "start_date": "2012-06", "completion_date": "2016-01", "detected_condition": "atrial_fibrillation"},
    {"nct_id": "NCT004", "sponsor_class": "NIH", "phase": "PHASE3", "era": "2020-2025", "core_count": 0, "surrogate_count": 2, "has_PRO": False, "gap_score": 1.0, "has_results": "False", "enrollment": 300, "start_date": "2020-01", "completion_date": "2022-12", "detected_condition": "hypertension"},
]

SAMPLE_FIT = [
    {"nct_id": "NCT001", "sponsor_class": "INDUSTRY", "generalizability_index": 75, "exclusion_count": 2},
    {"nct_id": "NCT002", "sponsor_class": "OTHER", "generalizability_index": 90, "exclusion_count": 0},
    {"nct_id": "NCT003", "sponsor_class": "INDUSTRY", "generalizability_index": 70, "exclusion_count": 3},
    {"nct_id": "NCT004", "sponsor_class": "NIH", "generalizability_index": 85, "exclusion_count": 1},
]


class TestSponsorComparison:
    def test_returns_sponsor_groups(self):
        result = analyze_sponsor_comparison(SAMPLE_CLASSIFIED, SAMPLE_FIT)
        assert "INDUSTRY" in result["by_sponsor"]
        assert "OTHER" in result["by_sponsor"]

    def test_industry_stats(self):
        result = analyze_sponsor_comparison(SAMPLE_CLASSIFIED, SAMPLE_FIT)
        ind = result["by_sponsor"]["INDUSTRY"]
        assert ind["count"] == 2
        assert "mean_gap_score" in ind
        assert "pct_with_results" in ind

    def test_has_statistical_comparison(self):
        result = analyze_sponsor_comparison(SAMPLE_CLASSIFIED, SAMPLE_FIT)
        assert "comparisons" in result


class TestResultsTransparency:
    def test_patient_centered_vs_surrogate(self):
        result = analyze_results_transparency(SAMPLE_CLASSIFIED)
        assert "patient_centered" in result
        assert "surrogate_only" in result

    def test_posting_rates(self):
        result = analyze_results_transparency(SAMPLE_CLASSIFIED)
        assert "posting_rate" in result["patient_centered"]
        assert "posting_rate" in result["surrogate_only"]

    def test_by_era(self):
        result = analyze_results_transparency(SAMPLE_CLASSIFIED)
        assert "by_era" in result

    def test_chi_squared_reported(self):
        result = analyze_results_transparency(SAMPLE_CLASSIFIED)
        assert "chi2_test" in result


class TestPublicationGap:
    def test_by_centricity_level(self):
        result = analyze_publication_gap(SAMPLE_CLASSIFIED)
        assert "high" in result["by_centricity"]

    def test_evidence_waste(self):
        result = analyze_publication_gap(SAMPLE_CLASSIFIED)
        assert "evidence_waste" in result

    def test_logistic_model(self):
        result = analyze_publication_gap(SAMPLE_CLASSIFIED)
        assert "logistic_model" in result
