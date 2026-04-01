"""Tests for Geographic Disparities (Angle 6)."""
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "shared"))

from analyze_geographic import (
    analyze_geographic_disparities,
    WHO_REGIONS,
    CV_MORTALITY_BY_REGION,
)


SAMPLE_LOCATIONS = [
    {"nct_id": "NCT001", "countries": "United States"},
    {"nct_id": "NCT002", "countries": "United States|United Kingdom"},
    {"nct_id": "NCT003", "countries": "China"},
    {"nct_id": "NCT004", "countries": "India"},
    {"nct_id": "NCT005", "countries": ""},
]

SAMPLE_CLASSIFIED = [
    {"nct_id": "NCT001", "core_count": "2", "gap_score": "0.3"},
    {"nct_id": "NCT002", "core_count": "0", "gap_score": "1.0"},
    {"nct_id": "NCT003", "core_count": "1", "gap_score": "0.5"},
    {"nct_id": "NCT004", "core_count": "0", "gap_score": "1.0"},
    {"nct_id": "NCT005", "core_count": "0", "gap_score": "1.0"},
]


class TestGeographic:
    def test_country_counts(self):
        result = analyze_geographic_disparities(SAMPLE_LOCATIONS, SAMPLE_CLASSIFIED)
        assert "United States" in result["by_country"]
        assert result["by_country"]["United States"]["trial_count"] == 2

    def test_region_counts(self):
        result = analyze_geographic_disparities(SAMPLE_LOCATIONS, SAMPLE_CLASSIFIED)
        assert "by_region" in result

    def test_trials_per_cv_death(self):
        result = analyze_geographic_disparities(SAMPLE_LOCATIONS, SAMPLE_CLASSIFIED)
        assert "by_region" in result
        for region, data in result["by_region"].items():
            if data["trial_count"] > 0:
                assert "trials_per_million_cv_deaths" in data

    def test_missing_countries_handled(self):
        result = analyze_geographic_disparities(SAMPLE_LOCATIONS, SAMPLE_CLASSIFIED)
        assert result["total_with_location"] == 4  # NCT005 has no country

    def test_patient_centricity_by_region(self):
        result = analyze_geographic_disparities(SAMPLE_LOCATIONS, SAMPLE_CLASSIFIED)
        for region, data in result["by_region"].items():
            if data["trial_count"] > 0:
                assert "mean_gap_score" in data

    def test_who_regions_defined(self):
        assert len(WHO_REGIONS) > 0
        assert "United States" in WHO_REGIONS

    def test_cv_mortality_defined(self):
        assert len(CV_MORTALITY_BY_REGION) > 0
