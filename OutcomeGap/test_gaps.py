"""Tests for OutcomeGap analysis pipeline."""
import json
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "shared"))

from analyze_gaps import (
    classify_all_trials,
    aggregate_by_field,
    compute_era,
    build_summary,
)

SAMPLE_TRIALS = [
    {
        "nct_id": "NCT001", "title": "HF Trial 1", "status": "COMPLETED",
        "conditions": "Heart Failure", "phase": "PHASE3", "enrollment": 500,
        "sponsor_name": "Pfizer", "sponsor_class": "INDUSTRY",
        "primary_outcomes": "All-cause mortality|Heart failure hospitalization",
        "secondary_outcomes": "KCCQ total score|LVEF change",
        "eligibility_criteria": "", "start_date": "2018-01", "completion_date": "2021-06",
        "has_results": True, "interventions": "Dapagliflozin",
    },
    {
        "nct_id": "NCT002", "title": "HF Trial 2", "status": "COMPLETED",
        "conditions": "Heart Failure", "phase": "PHASE2", "enrollment": 100,
        "sponsor_name": "University of Oxford", "sponsor_class": "OTHER",
        "primary_outcomes": "NT-proBNP change from baseline",
        "secondary_outcomes": "LVEF change",
        "eligibility_criteria": "", "start_date": "2015-03", "completion_date": "2017-09",
        "has_results": True, "interventions": "Drug X",
    },
    {
        "nct_id": "NCT003", "title": "AF Trial 1", "status": "COMPLETED",
        "conditions": "Atrial Fibrillation", "phase": "PHASE3", "enrollment": 2000,
        "sponsor_name": "Bayer", "sponsor_class": "INDUSTRY",
        "primary_outcomes": "Stroke or systemic embolism",
        "secondary_outcomes": "Major bleeding|All-cause mortality",
        "eligibility_criteria": "", "start_date": "2012-06", "completion_date": "2016-01",
        "has_results": True, "interventions": "Rivaroxaban",
    },
    {
        "nct_id": "NCT004", "title": "HTN Trial 1", "status": "COMPLETED",
        "conditions": "Hypertension", "phase": "PHASE3", "enrollment": 300,
        "sponsor_name": "NIH", "sponsor_class": "NIH",
        "primary_outcomes": "Change in systolic blood pressure",
        "secondary_outcomes": "24-hour ambulatory BP",
        "eligibility_criteria": "", "start_date": "2020-01", "completion_date": "2022-12",
        "has_results": True, "interventions": "Chlorthalidone",
    },
]


class TestComputeEra:
    def test_2018_is_2015_2019(self):
        assert compute_era("2018-01") == "2015-2019"

    def test_2003_is_2000_2004(self):
        assert compute_era("2003-06") == "2000-2004"

    def test_2020_is_2020_2025(self):
        assert compute_era("2020-01") == "2020-2025"

    def test_empty_is_unknown(self):
        assert compute_era("") == "Unknown"

    def test_pre_2000(self):
        assert compute_era("1998-01") == "Pre-2000"


class TestClassifyAllTrials:
    def test_returns_list_of_dicts(self):
        results = classify_all_trials(SAMPLE_TRIALS)
        assert len(results) == 4
        assert all("nct_id" in r for r in results)
        assert all("gap_score" in r for r in results)
        assert all("core_count" in r for r in results)
        assert all("has_PRO" in r for r in results)

    def test_hf_trial_1_has_core(self):
        results = classify_all_trials(SAMPLE_TRIALS)
        hf1 = next(r for r in results if r["nct_id"] == "NCT001")
        assert hf1["core_count"] >= 2
        assert hf1["has_PRO"] is True
        assert hf1["gap_score"] < 0.5

    def test_htn_surrogate_only_trial(self):
        results = classify_all_trials(SAMPLE_TRIALS)
        htn = next(r for r in results if r["nct_id"] == "NCT004")
        assert htn["core_count"] == 0
        assert htn["gap_score"] == 1.0

    def test_unmatched_condition_gets_gap_1(self):
        trial = {**SAMPLE_TRIALS[0], "nct_id": "NCT999", "conditions": "Rare Genetic Disorder"}
        results = classify_all_trials([trial])
        assert results[0]["gap_score"] == 1.0


class TestAggregateByField:
    def test_by_condition(self):
        results = classify_all_trials(SAMPLE_TRIALS)
        agg = aggregate_by_field(results, "detected_condition")
        assert "heart_failure" in agg
        assert "atrial_fibrillation" in agg
        assert agg["heart_failure"]["count"] == 2

    def test_by_phase(self):
        results = classify_all_trials(SAMPLE_TRIALS)
        agg = aggregate_by_field(results, "phase")
        assert "PHASE3" in agg
        assert agg["PHASE3"]["count"] == 3

    def test_by_sponsor_class(self):
        results = classify_all_trials(SAMPLE_TRIALS)
        agg = aggregate_by_field(results, "sponsor_class")
        assert "INDUSTRY" in agg
        assert agg["INDUSTRY"]["count"] == 2


class TestBuildSummary:
    def test_summary_has_required_keys(self):
        results = classify_all_trials(SAMPLE_TRIALS)
        summary = build_summary(results)
        assert "total_trials" in summary
        assert "pct_with_core" in summary
        assert "pct_with_PRO" in summary
        assert "mean_gap_score" in summary
        assert "by_condition" in summary
        assert "by_phase" in summary
        assert "by_era" in summary
        assert "by_sponsor_class" in summary
        assert summary["total_trials"] == 4
