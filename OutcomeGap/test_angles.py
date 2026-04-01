"""Tests for OutcomeGap Angles 8 (Intervention) + 11 (Composite)."""
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "shared"))

from analyze_angles import (
    analyze_intervention_landscape,
    analyze_composites,
)

SAMPLE_TRIALS = [
    {"nct_id": "NCT001", "interventions": "Dapagliflozin 10mg", "primary_outcomes": "Composite of CV death and HF hospitalization", "secondary_outcomes": "KCCQ score", "conditions": "Heart Failure", "sponsor_class": "INDUSTRY", "phase": "PHASE3", "start_date": "2018-01"},
    {"nct_id": "NCT002", "interventions": "Cardiac rehabilitation exercise", "primary_outcomes": "6-minute walk distance", "secondary_outcomes": "Quality of life", "conditions": "Heart Failure", "sponsor_class": "OTHER", "phase": "PHASE3", "start_date": "2019-01"},
    {"nct_id": "NCT003", "interventions": "Drug-eluting stent", "primary_outcomes": "MACE at 1 year", "secondary_outcomes": "Angiographic late lumen loss", "conditions": "Coronary Artery Disease", "sponsor_class": "INDUSTRY", "phase": "PHASE3", "start_date": "2017-01"},
    {"nct_id": "NCT004", "interventions": "Amlodipine tablet", "primary_outcomes": "Change in systolic blood pressure", "secondary_outcomes": "24-hour ambulatory BP", "conditions": "Hypertension", "sponsor_class": "NIH", "phase": "PHASE3", "start_date": "2020-01"},
]


class TestInterventionLandscape:
    def test_returns_type_counts(self):
        result = analyze_intervention_landscape(SAMPLE_TRIALS)
        assert "by_type" in result
        assert "drug" in result["by_type"]
        assert result["by_type"]["drug"]["count"] >= 2

    def test_cross_tab_has_gap_score(self):
        result = analyze_intervention_landscape(SAMPLE_TRIALS)
        assert "drug" in result["by_type"]
        assert "mean_gap_score" in result["by_type"]["drug"]

    def test_behavioral_detected(self):
        result = analyze_intervention_landscape(SAMPLE_TRIALS)
        assert "behavioral" in result["by_type"]
        assert result["by_type"]["behavioral"]["count"] >= 1


class TestCompositeAnalysis:
    def test_detects_composites(self):
        result = analyze_composites(SAMPLE_TRIALS)
        assert result["total_with_composite"] >= 2  # NCT001 and NCT003

    def test_pct_composite(self):
        result = analyze_composites(SAMPLE_TRIALS)
        assert result["pct_composite"] > 0

    def test_mixed_relevance_detected(self):
        result = analyze_composites(SAMPLE_TRIALS)
        assert "pct_mixed" in result

    def test_common_composites(self):
        result = analyze_composites(SAMPLE_TRIALS)
        assert "common_composites" in result
        assert isinstance(result["common_composites"], list)
