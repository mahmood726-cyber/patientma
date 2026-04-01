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
