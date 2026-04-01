"""Tests for shared infrastructure: COMET taxonomy + outcome classifier."""
import json
import os
import pytest

SHARED_DIR = os.path.dirname(os.path.abspath(__file__))


def load_comet():
    with open(os.path.join(SHARED_DIR, "comet_outcomes.json"), "r") as f:
        return json.load(f)


class TestCometTaxonomy:
    def test_loads_valid_json(self):
        data = load_comet()
        assert isinstance(data, dict)

    def test_has_four_conditions(self):
        data = load_comet()
        conditions = [k for k in data if not k.startswith("_")]
        assert sorted(conditions) == [
            "acute_coronary_syndrome",
            "atrial_fibrillation",
            "heart_failure",
            "hypertension",
        ]

    def test_each_condition_has_core_and_surrogate(self):
        data = load_comet()
        for cond in ["heart_failure", "acute_coronary_syndrome", "atrial_fibrillation", "hypertension"]:
            assert "core_outcomes" in data[cond], f"{cond} missing core_outcomes"
            assert "surrogate_outcomes" in data[cond], f"{cond} missing surrogate_outcomes"
            assert len(data[cond]["core_outcomes"]) >= 3, f"{cond} has too few core outcomes"
            assert len(data[cond]["surrogate_outcomes"]) >= 1, f"{cond} has too few surrogate outcomes"

    def test_each_outcome_has_required_fields(self):
        data = load_comet()
        for cond in ["heart_failure", "acute_coronary_syndrome", "atrial_fibrillation", "hypertension"]:
            for outcome_type in ["core_outcomes", "surrogate_outcomes"]:
                for outcome in data[cond][outcome_type]:
                    assert "name" in outcome, f"Missing name in {cond}.{outcome_type}"
                    assert "category" in outcome, f"Missing category in {cond}.{outcome_type}"
                    assert "keywords" in outcome, f"Missing keywords in {cond}.{outcome_type}"
                    assert len(outcome["keywords"]) >= 1, f"Empty keywords in {cond}.{outcome_type}.{outcome['name']}"

    def test_all_keywords_are_lowercase(self):
        data = load_comet()
        for cond in ["heart_failure", "acute_coronary_syndrome", "atrial_fibrillation", "hypertension"]:
            for outcome_type in ["core_outcomes", "surrogate_outcomes"]:
                for outcome in data[cond][outcome_type]:
                    for kw in outcome["keywords"]:
                        assert kw == kw.lower(), f"Keyword '{kw}' not lowercase in {cond}.{outcome['name']}"

    def test_meta_section_present(self):
        data = load_comet()
        assert "_meta" in data
        assert data["_meta"]["version"] == "1.0.0"
        assert len(data["_meta"]["conditions"]) == 4


from unittest.mock import patch, MagicMock
from fetch_cv_trials import parse_study_row, build_query_url, FIELDS


class TestBuildQueryUrl:
    def test_default_url_has_cardiovascular_condition(self):
        url = build_query_url(page_token=None)
        assert "query.cond=cardiovascular" in url
        assert "pageSize=1000" in url
        assert "countTotal=true" in url

    def test_url_with_page_token(self):
        url = build_query_url(page_token="abc123")
        assert "pageToken=abc123" in url

    def test_url_without_page_token_has_no_pageToken_param(self):
        url = build_query_url(page_token=None)
        assert "pageToken" not in url


class TestParseStudyRow:
    def test_extracts_nct_id(self):
        study = {
            "protocolSection": {
                "identificationModule": {"nctId": "NCT00000001"},
                "statusModule": {"overallStatus": "COMPLETED"},
                "conditionsModule": {"conditions": ["Heart Failure"]},
                "designModule": {"phases": ["PHASE3"], "enrollmentInfo": {"count": 500}},
                "sponsorCollaboratorsModule": {"leadSponsor": {"name": "Pfizer", "class": "INDUSTRY"}},
                "outcomesModule": {
                    "primaryOutcomes": [{"measure": "All-cause mortality", "timeFrame": "1 year"}],
                    "secondaryOutcomes": [{"measure": "LVEF change", "timeFrame": "6 months"}]
                },
                "eligibilityModule": {"eligibilityCriteria": "Inclusion:\n- Age >= 18\nExclusion:\n- CKD stage 5"},
            },
            "hasResults": True,
        }
        row = parse_study_row(study)
        assert row["nct_id"] == "NCT00000001"
        assert row["status"] == "COMPLETED"
        assert row["conditions"] == "Heart Failure"
        assert row["phase"] == "PHASE3"
        assert row["enrollment"] == 500
        assert row["sponsor_name"] == "Pfizer"
        assert row["sponsor_class"] == "INDUSTRY"
        assert row["primary_outcomes"] == "All-cause mortality"
        assert row["secondary_outcomes"] == "LVEF change"
        assert "Age >= 18" in row["eligibility_criteria"]
        assert row["has_results"] is True

    def test_handles_missing_optional_fields(self):
        study = {
            "protocolSection": {
                "identificationModule": {"nctId": "NCT99999999"},
                "statusModule": {"overallStatus": "RECRUITING"},
                "conditionsModule": {},
                "designModule": {},
                "sponsorCollaboratorsModule": {},
                "outcomesModule": {},
                "eligibilityModule": {},
            },
            "hasResults": False,
        }
        row = parse_study_row(study)
        assert row["nct_id"] == "NCT99999999"
        assert row["conditions"] == ""
        assert row["phase"] == ""
        assert row["enrollment"] == 0
        assert row["sponsor_name"] == ""
        assert row["sponsor_class"] == ""
        assert row["primary_outcomes"] == ""
        assert row["secondary_outcomes"] == ""
        assert row["eligibility_criteria"] == ""
        assert row["has_results"] is False

    def test_joins_multiple_conditions(self):
        study = {
            "protocolSection": {
                "identificationModule": {"nctId": "NCT00000002"},
                "statusModule": {"overallStatus": "COMPLETED"},
                "conditionsModule": {"conditions": ["Heart Failure", "Diabetes"]},
                "designModule": {"phases": ["PHASE2", "PHASE3"], "enrollmentInfo": {"count": 100}},
                "sponsorCollaboratorsModule": {"leadSponsor": {"name": "NIH", "class": "NIH"}},
                "outcomesModule": {
                    "primaryOutcomes": [
                        {"measure": "Mortality", "timeFrame": "2y"},
                        {"measure": "HF hospitalization", "timeFrame": "2y"},
                    ],
                    "secondaryOutcomes": [],
                },
                "eligibilityModule": {"eligibilityCriteria": "Age 18-80"},
            },
            "hasResults": True,
        }
        row = parse_study_row(study)
        assert row["conditions"] == "Heart Failure|Diabetes"
        assert row["phase"] == "PHASE2|PHASE3"
        assert row["primary_outcomes"] == "Mortality|HF hospitalization"
        assert row["secondary_outcomes"] == ""
