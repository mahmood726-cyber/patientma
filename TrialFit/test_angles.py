"""Tests for TrialFit Angles 9 (Sex Gap) + 10 (Elderly Exclusion)."""
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "shared"))

from analyze_angles import analyze_sex_gap, analyze_elderly_exclusion

SAMPLE_TRIALS = [
    {"nct_id": "NCT001", "conditions": "Heart Failure", "phase": "PHASE3", "sponsor_class": "INDUSTRY", "start_date": "2018-01", "eligibility_criteria": "Inclusion:\n- Age >= 18\n- Male patients only\nExclusion:\n- eGFR < 30", "primary_outcomes": "All-cause mortality", "secondary_outcomes": "Subgroup by sex analysis planned", "sex": "male", "min_age": 18, "max_age": None},
    {"nct_id": "NCT002", "conditions": "Hypertension", "phase": "PHASE3", "sponsor_class": "NIH", "start_date": "2020-06", "eligibility_criteria": "Inclusion:\n- Age 21-75\n- Men and women\nExclusion:\n- None", "primary_outcomes": "BP change", "secondary_outcomes": "", "sex": "both", "min_age": 21, "max_age": 75},
    {"nct_id": "NCT003", "conditions": "Atrial Fibrillation", "phase": "PHASE3", "sponsor_class": "OTHER", "start_date": "2015-03", "eligibility_criteria": "Inclusion:\n- Age >= 18\nExclusion:\n- Pregnancy", "primary_outcomes": "Stroke", "secondary_outcomes": "", "sex": "both", "min_age": 18, "max_age": None},
    {"nct_id": "NCT004", "conditions": "Heart Failure", "phase": "PHASE2", "sponsor_class": "OTHER", "start_date": "2010-01", "eligibility_criteria": "Inclusion:\n- Age 50-65\nExclusion:\n- Cancer", "primary_outcomes": "LVEF", "secondary_outcomes": "", "sex": "both", "min_age": 50, "max_age": 65},
]


class TestSexGap:
    def test_counts_sex_restricted(self):
        result = analyze_sex_gap(SAMPLE_TRIALS)
        assert result["total_sex_restricted"] >= 1

    def test_pct_sex_restricted(self):
        result = analyze_sex_gap(SAMPLE_TRIALS)
        assert result["pct_sex_restricted"] > 0

    def test_stratified_mention(self):
        result = analyze_sex_gap(SAMPLE_TRIALS)
        assert result["pct_sex_stratified_mention"] > 0  # NCT001 mentions subgroup by sex

    def test_by_era(self):
        result = analyze_sex_gap(SAMPLE_TRIALS)
        assert "by_era" in result


class TestElderlyExclusion:
    def test_age_cutoff_distribution(self):
        result = analyze_elderly_exclusion(SAMPLE_TRIALS)
        assert "cutoff_distribution" in result
        assert "no_limit" in result["cutoff_distribution"]

    def test_pct_exclude_75(self):
        result = analyze_elderly_exclusion(SAMPLE_TRIALS)
        assert result["pct_cutoff_below_75"] > 0  # NCT002 (75) and NCT004 (65)

    def test_exclusion_burden(self):
        result = analyze_elderly_exclusion(SAMPLE_TRIALS)
        assert "exclusion_burden" in result

    def test_by_condition(self):
        result = analyze_elderly_exclusion(SAMPLE_TRIALS)
        assert "by_condition" in result
