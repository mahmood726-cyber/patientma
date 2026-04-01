"""Tests for composite endpoint detector."""
import os, sys, pytest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from composite_detector import detect_composite, decompose_composite

class TestDetectComposite:
    def test_explicit_composite(self):
        result = detect_composite("Composite of cardiovascular death, MI, and stroke")
        assert result["is_composite"] is True
    def test_mace(self):
        result = detect_composite("MACE (major adverse cardiovascular events)")
        assert result["is_composite"] is True
    def test_simple_endpoint(self):
        result = detect_composite("All-cause mortality")
        assert result["is_composite"] is False
    def test_combined_keyword(self):
        result = detect_composite("Combined endpoint of death or hospitalization")
        assert result["is_composite"] is True
    def test_defined_as(self):
        result = detect_composite("Primary endpoint defined as CV death, MI, or stroke")
        assert result["is_composite"] is True
    def test_coprimary(self):
        result = detect_composite("Co-primary: change in LVEF and NT-proBNP")
        assert result["is_composite"] is True
    def test_bp_is_not_composite(self):
        result = detect_composite("Change in systolic blood pressure")
        assert result["is_composite"] is False

class TestDecomposeComposite:
    def test_cv_death_mi_stroke(self):
        result = decompose_composite("Composite of cardiovascular death, myocardial infarction, and stroke", "acute_coronary_syndrome")
        assert len(result["components"]) >= 2
        assert any(c["classification"] == "core" for c in result["components"])
    def test_mixed_composite(self):
        result = decompose_composite("Composite of death, hospitalization, and change in NT-proBNP", "heart_failure")
        has_core = any(c["classification"] == "core" for c in result["components"])
        has_surrogate = any(c["classification"] == "surrogate" for c in result["components"])
        assert result["mixed_relevance"] == (has_core and has_surrogate)
    def test_pure_core_composite(self):
        result = decompose_composite("Composite of all-cause mortality and heart failure hospitalization", "heart_failure")
        assert result["mixed_relevance"] is False
        assert all(c["classification"] == "core" for c in result["components"] if c["classification"] != "unclassified")
