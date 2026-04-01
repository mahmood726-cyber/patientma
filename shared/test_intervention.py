"""Tests for intervention type classifier."""
import pytest
from intervention_classifier import classify_intervention, INTERVENTION_TYPES


class TestClassifyIntervention:
    def test_drug(self):
        result = classify_intervention("Dapagliflozin 10mg tablet")
        assert "drug" in result

    def test_device(self):
        result = classify_intervention("Cardiac resynchronization therapy device implant")
        assert "device" in result

    def test_procedure(self):
        result = classify_intervention("Catheter ablation for atrial fibrillation")
        assert "procedure" in result

    def test_behavioral(self):
        result = classify_intervention("Supervised exercise rehabilitation program")
        assert "behavioral" in result

    def test_diagnostic(self):
        result = classify_intervention("Cardiac MRI imaging protocol")
        assert "diagnostic" in result

    def test_multiple_types(self):
        result = classify_intervention("Drug-eluting stent implantation")
        assert "drug" in result or "device" in result

    def test_placebo_is_drug(self):
        result = classify_intervention("Placebo oral capsule")
        assert "drug" in result

    def test_empty_is_other(self):
        result = classify_intervention("")
        assert result == ["other"]

    def test_unrecognized_is_other(self):
        result = classify_intervention("Collection of biological samples")
        assert "other" in result

    def test_pipe_delimited_multiple(self):
        result = classify_intervention("Metoprolol|Cardiac rehabilitation exercise")
        assert "drug" in result
        assert "behavioral" in result
