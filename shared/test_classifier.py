"""Tests for COMET outcome classifier."""
import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from outcome_classifier import classify_outcome, classify_trial, compute_gap_score


class TestClassifyOutcome:
    """Test single outcome measure text classification."""

    def test_exact_core_match(self):
        result = classify_outcome("All-cause mortality", "heart_failure")
        assert result["classification"] == "core"
        assert result["matched_name"] == "All-cause mortality"
        assert result["category"] == "survival"

    def test_keyword_match_case_insensitive(self):
        result = classify_outcome("Change in KCCQ total symptom score", "heart_failure")
        assert result["classification"] == "core"
        assert result["matched_name"] == "Quality of life"
        assert result["category"] == "patient_reported"

    def test_surrogate_match(self):
        result = classify_outcome("Change in left ventricular ejection fraction", "heart_failure")
        assert result["classification"] == "surrogate"
        assert result["matched_name"] == "LVEF"

    def test_unclassified_outcome(self):
        result = classify_outcome("Pharmacokinetic profile of drug X", "heart_failure")
        assert result["classification"] == "unclassified"
        assert result["matched_name"] == ""

    def test_acs_troponin_is_surrogate(self):
        result = classify_outcome("Peak troponin I levels at 48 hours", "acute_coronary_syndrome")
        assert result["classification"] == "surrogate"
        assert result["matched_name"] == "Troponin levels"

    def test_af_stroke_is_core(self):
        result = classify_outcome("Time to first stroke or systemic embolism", "atrial_fibrillation")
        assert result["classification"] == "core"
        assert result["matched_name"] == "Stroke/systemic embolism"

    def test_htn_blood_pressure_is_surrogate(self):
        result = classify_outcome("Change in office systolic blood pressure from baseline", "hypertension")
        assert result["classification"] == "surrogate"
        assert result["matched_name"] == "Blood pressure reduction"

    def test_cross_condition_mortality(self):
        for cond in ["heart_failure", "acute_coronary_syndrome", "atrial_fibrillation", "hypertension"]:
            result = classify_outcome("Death from any cause", cond)
            assert result["classification"] == "core", f"Failed for {cond}"

    def test_multi_condition_match_picks_best(self):
        result = classify_outcome(
            "Composite of cardiovascular death and heart failure hospitalization",
            "heart_failure",
        )
        assert result["classification"] == "core"


class TestClassifyTrial:
    """Test full trial classification."""

    def test_trial_with_core_primary(self):
        result = classify_trial(
            primary_outcomes="All-cause mortality|Heart failure hospitalization",
            secondary_outcomes="LVEF change|NT-proBNP change",
            condition="heart_failure",
        )
        assert result["core_count"] >= 2
        assert result["surrogate_count"] >= 1
        assert result["has_PRO"] is False

    def test_trial_with_pro(self):
        result = classify_trial(
            primary_outcomes="KCCQ total symptom score",
            secondary_outcomes="6-minute walk distance",
            condition="heart_failure",
        )
        assert result["has_PRO"] is True
        assert result["core_count"] >= 2

    def test_surrogate_only_trial(self):
        result = classify_trial(
            primary_outcomes="Change in systolic blood pressure",
            secondary_outcomes="24-hour ambulatory BP monitoring",
            condition="hypertension",
        )
        assert result["core_count"] == 0
        assert result["surrogate_count"] >= 1

    def test_empty_outcomes(self):
        result = classify_trial(
            primary_outcomes="",
            secondary_outcomes="",
            condition="heart_failure",
        )
        assert result["core_count"] == 0
        assert result["surrogate_count"] == 0
        assert result["has_PRO"] is False


class TestGapScore:
    def test_all_core_is_zero(self):
        score = compute_gap_score(core_count=3, surrogate_count=0, total_count=3)
        assert score == 0.0

    def test_no_core_is_one(self):
        score = compute_gap_score(core_count=0, surrogate_count=2, total_count=2)
        assert score == 1.0

    def test_mixed_is_between(self):
        score = compute_gap_score(core_count=1, surrogate_count=1, total_count=2)
        assert 0.0 < score < 1.0

    def test_no_outcomes_is_one(self):
        score = compute_gap_score(core_count=0, surrogate_count=0, total_count=0)
        assert score == 1.0
