"""Classify trial outcome measures against COMET core outcome taxonomy."""
import json
import os
import re

SHARED_DIR = os.path.dirname(os.path.abspath(__file__))
_TAXONOMY = None


def _load_taxonomy():
    global _TAXONOMY
    if _TAXONOMY is None:
        with open(os.path.join(SHARED_DIR, "comet_outcomes.json"), "r") as f:
            _TAXONOMY = json.load(f)
    return _TAXONOMY


def classify_outcome(measure_text, condition):
    """
    Classify a single outcome measure text against the COMET taxonomy for a condition.

    Returns dict: {classification, matched_name, category}
    - classification: "core", "surrogate", or "unclassified"
    """
    taxonomy = _load_taxonomy()
    if condition not in taxonomy:
        return {"classification": "unclassified", "matched_name": "", "category": ""}

    text_lower = measure_text.lower()
    cond_data = taxonomy[condition]

    # Check core outcomes first (priority over surrogate)
    for outcome in cond_data["core_outcomes"]:
        for keyword in outcome["keywords"]:
            if keyword in text_lower:
                return {
                    "classification": "core",
                    "matched_name": outcome["name"],
                    "category": outcome["category"],
                }

    # Check surrogate outcomes
    for outcome in cond_data["surrogate_outcomes"]:
        for keyword in outcome["keywords"]:
            if keyword in text_lower:
                return {
                    "classification": "surrogate",
                    "matched_name": outcome["name"],
                    "category": outcome["category"],
                }

    return {"classification": "unclassified", "matched_name": "", "category": ""}


def _detect_condition(conditions_text):
    """Map trial condition text to a COMET taxonomy key. Returns first match."""
    text_lower = conditions_text.lower()
    mapping = [
        ("heart_failure", ["heart failure", "cardiac failure", "cardiomyopathy", "hfref", "hfpef", "hfmref"]),
        ("acute_coronary_syndrome", ["acute coronary", "myocardial infarction", "unstable angina", "nstemi", "stemi", "coronary artery disease", "coronary heart disease", "ischemic heart", "ischaemic heart"]),
        ("atrial_fibrillation", ["atrial fibrillation", "atrial flutter", "af ", "afib"]),
        ("hypertension", ["hypertension", "high blood pressure", "elevated blood pressure"]),
    ]
    for cond_key, keywords in mapping:
        for kw in keywords:
            if kw in text_lower:
                return cond_key
    return None


def classify_trial(primary_outcomes, secondary_outcomes, condition):
    """
    Classify all outcomes for a trial.

    Args:
        primary_outcomes: pipe-delimited string of primary outcome measures
        secondary_outcomes: pipe-delimited string of secondary outcome measures
        condition: COMET taxonomy key or raw condition text

    Returns dict with core_count, surrogate_count, has_PRO, gap_score, etc.
    """
    # Resolve condition to taxonomy key if raw text
    if condition not in ["heart_failure", "acute_coronary_syndrome", "atrial_fibrillation", "hypertension"]:
        resolved = _detect_condition(condition)
        if resolved is None:
            return {
                "core_count": 0, "surrogate_count": 0, "unclassified_count": 0,
                "has_PRO": False, "gap_score": 1.0,
                "core_names": [], "surrogate_names": [], "classifications": [],
            }
        condition = resolved

    all_measures = []
    for text in [primary_outcomes, secondary_outcomes]:
        if text:
            all_measures.extend([m.strip() for m in text.split("|") if m.strip()])

    core_names = set()
    surrogate_names = set()
    unclassified_count = 0
    has_PRO = False
    classifications = []

    for measure in all_measures:
        result = classify_outcome(measure, condition)
        classifications.append(result)
        if result["classification"] == "core":
            core_names.add(result["matched_name"])
            if result["category"] == "patient_reported":
                has_PRO = True
        elif result["classification"] == "surrogate":
            surrogate_names.add(result["matched_name"])
        else:
            unclassified_count += 1

    core_count = len(core_names)
    surrogate_count = len(surrogate_names)
    total = core_count + surrogate_count + unclassified_count
    gap = compute_gap_score(core_count, surrogate_count, total)

    return {
        "core_count": core_count,
        "surrogate_count": surrogate_count,
        "unclassified_count": unclassified_count,
        "has_PRO": has_PRO,
        "gap_score": gap,
        "core_names": sorted(core_names),
        "surrogate_names": sorted(surrogate_names),
        "classifications": classifications,
    }


def compute_gap_score(core_count, surrogate_count, total_count):
    """
    Compute patient-relevance gap score: 0 (all core) to 1 (no core).
    Formula: 1 - (core_count / total_count) when total > 0, else 1.0.
    """
    if total_count == 0:
        return 1.0
    return round(1.0 - (core_count / total_count), 4)
