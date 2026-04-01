"""Tests for TrialFit eligibility parser and generalizability index."""
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "shared"))

from analyze_fit import (
    parse_age_range,
    parse_sex_restriction,
    parse_comorbidity_exclusions,
    parse_functional_requirement,
    compute_age_score,
    compute_sex_score,
    compute_comorbidity_score,
    compute_functional_score,
    compute_generalizability_index,
    classify_all_trials,
    compute_era,
    aggregate_by_field,
    build_summary,
)


class TestParseAgeRange:
    def test_standard_range(self):
        text = "Inclusion Criteria:\n- Age >= 18 and <= 80 years"
        mn, mx = parse_age_range(text)
        assert mn == 18
        assert mx == 80

    def test_between_pattern(self):
        text = "Age between 21 and 75 years"
        mn, mx = parse_age_range(text)
        assert mn == 21
        assert mx == 75

    def test_only_minimum(self):
        text = "Inclusion:\n- Age 18 years or older"
        mn, mx = parse_age_range(text)
        assert mn == 18
        assert mx is None

    def test_only_maximum(self):
        text = "Exclusion:\n- Age > 85 years"
        mn, mx = parse_age_range(text)
        assert mn is None
        assert mx == 85

    def test_no_age_mentioned(self):
        text = "Must have heart failure with reduced ejection fraction"
        mn, mx = parse_age_range(text)
        assert mn is None
        assert mx is None

    def test_adult_keyword(self):
        text = "Adult patients with hypertension"
        mn, mx = parse_age_range(text)
        assert mn == 18
        assert mx is None

    def test_elderly_excluded(self):
        text = "Exclusion:\n- Age greater than 70"
        mn, mx = parse_age_range(text)
        assert mx == 70


class TestParseSexRestriction:
    def test_both_sexes(self):
        assert parse_sex_restriction("Male and female patients eligible") == "both"

    def test_male_only(self):
        assert parse_sex_restriction("Male patients only") == "male"

    def test_female_only(self):
        assert parse_sex_restriction("Female patients only\nPregnancy excluded") == "female"

    def test_no_mention_defaults_both(self):
        assert parse_sex_restriction("Adults with heart failure") == "both"


class TestParseComorbidityExclusions:
    def test_ckd_exclusion(self):
        text = "Exclusion:\n- eGFR < 30 mL/min\n- Dialysis"
        excl = parse_comorbidity_exclusions(text)
        assert "ckd" in excl

    def test_diabetes_exclusion(self):
        text = "Exclusion:\n- Type 1 or Type 2 diabetes mellitus"
        excl = parse_comorbidity_exclusions(text)
        assert "diabetes" in excl

    def test_cancer_exclusion(self):
        text = "Exclusion:\n- Active malignancy within 5 years"
        excl = parse_comorbidity_exclusions(text)
        assert "cancer" in excl

    def test_no_exclusions(self):
        text = "Inclusion:\n- Heart failure\n- Age >= 18"
        excl = parse_comorbidity_exclusions(text)
        assert len(excl) == 0

    def test_multiple_exclusions(self):
        text = """Exclusion Criteria:
        - Severe renal insufficiency (eGFR < 15)
        - Active cancer
        - Dementia or cognitive impairment
        - Liver cirrhosis
        - Pregnancy
        """
        excl = parse_comorbidity_exclusions(text)
        assert "ckd" in excl
        assert "cancer" in excl
        assert "cognitive" in excl
        assert "liver" in excl

    def test_diabetes_in_inclusion_not_counted(self):
        text = "Inclusion:\n- Diagnosis of type 2 diabetes\nExclusion:\n- None"
        excl = parse_comorbidity_exclusions(text)
        assert "diabetes" not in excl


class TestParseFunctionalRequirement:
    def test_nyha_class(self):
        text = "Inclusion: NYHA class II-IV heart failure"
        result = parse_functional_requirement(text)
        assert result["type"] == "NYHA"
        assert result["min_class"] == 2

    def test_nyha_class_iii_iv(self):
        text = "NYHA class III or IV"
        result = parse_functional_requirement(text)
        assert result["min_class"] == 3

    def test_no_functional_requirement(self):
        text = "Adults with hypertension"
        result = parse_functional_requirement(text)
        assert result["type"] is None


class TestComputeAgeScore:
    def test_wide_range_scores_high(self):
        score = compute_age_score(18, None)
        assert score == 20

    def test_narrow_range_scores_low(self):
        score = compute_age_score(40, 65)
        assert score < 10

    def test_upper_cutoff_below_75_penalized(self):
        score_75 = compute_age_score(18, 75)
        score_65 = compute_age_score(18, 65)
        assert score_75 > score_65

    def test_no_info_gets_middle(self):
        score = compute_age_score(None, None)
        assert score == 10


class TestComputeSexScore:
    def test_both_sexes_max(self):
        assert compute_sex_score("both") == 10

    def test_single_sex(self):
        assert compute_sex_score("male") == 5
        assert compute_sex_score("female") == 5


class TestComputeComorbidityScore:
    def test_no_exclusions_max(self):
        assert compute_comorbidity_score([]) == 40

    def test_many_exclusions_low(self):
        excl = ["ckd", "diabetes", "cancer", "liver", "cognitive", "frailty"]
        score = compute_comorbidity_score(excl)
        assert score < 15

    def test_one_exclusion_moderate(self):
        score = compute_comorbidity_score(["ckd"])
        assert 25 <= score <= 35


class TestComputeFunctionalScore:
    def test_no_requirement_max(self):
        assert compute_functional_score({"type": None}) == 15

    def test_nyha_iii_iv_restrictive(self):
        score = compute_functional_score({"type": "NYHA", "min_class": 3})
        assert score < 10


class TestComputeGeneralizabilityIndex:
    def test_full_score_range(self):
        gi = compute_generalizability_index(
            age_score=20, sex_score=10, comorbidity_score=40,
            functional_score=15, representation_score=15,
        )
        assert gi == 100

    def test_zero_components(self):
        gi = compute_generalizability_index(
            age_score=0, sex_score=0, comorbidity_score=0,
            functional_score=0, representation_score=0,
        )
        assert gi == 0


class TestTrialFitIntegration:
    SAMPLE_TRIALS = [
        {
            "nct_id": "NCT001", "conditions": "Heart Failure", "phase": "PHASE3",
            "enrollment": 500, "sponsor_class": "INDUSTRY", "start_date": "2018-01",
            "eligibility_criteria": "Inclusion:\n- Age >= 18\n- NYHA II-IV\nExclusion:\n- eGFR < 30\n- Active cancer",
        },
        {
            "nct_id": "NCT002", "conditions": "Hypertension", "phase": "PHASE3",
            "enrollment": 1000, "sponsor_class": "NIH", "start_date": "2020-06",
            "eligibility_criteria": "Inclusion:\n- Age 21-80\nExclusion:\n- None",
        },
    ]

    def test_classify_returns_correct_count(self):
        results = classify_all_trials(self.SAMPLE_TRIALS)
        assert len(results) == 2

    def test_restrictive_trial_lower_gi(self):
        results = classify_all_trials(self.SAMPLE_TRIALS)
        nct001 = next(r for r in results if r["nct_id"] == "NCT001")
        nct002 = next(r for r in results if r["nct_id"] == "NCT002")
        assert nct001["generalizability_index"] < nct002["generalizability_index"]

    def test_summary_has_required_keys(self):
        results = classify_all_trials(self.SAMPLE_TRIALS)
        summary = build_summary(results)
        assert "total_trials" in summary
        assert "median_gi" in summary
        assert "by_condition" in summary
        assert "by_era" in summary
        assert "exclusion_ranking" in summary
