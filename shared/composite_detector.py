"""Detect and decompose composite endpoints in trial outcome measures."""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from outcome_classifier import classify_outcome

COMPOSITE_PATTERNS = [
    r"composite\s+of\b",
    r"\bmace\b",
    r"combined\s+(?:endpoint|outcome|primary)",
    r"co-?primary",
    r"defined\s+as\s+.+(?:,|and|or)",
    r"first\s+occurrence\s+of\s+.+(?:,|and|or)",
]

def detect_composite(outcome_text):
    if not outcome_text:
        return {"is_composite": False}
    text_lower = outcome_text.lower()
    for pattern in COMPOSITE_PATTERNS:
        if re.search(pattern, text_lower):
            return {"is_composite": True}
    return {"is_composite": False}

def _split_components(text):
    text_lower = text.lower()
    text_lower = re.sub(r"^.*?composite\s+of\s+", "", text_lower)
    text_lower = re.sub(r"^.*?defined\s+as\s+", "", text_lower)
    text_lower = re.sub(r"^.*?(?:combined|co-?primary)\s*:?\s*", "", text_lower)
    parts = re.split(r",\s*(?:and\s+)?|\s+and\s+|\s+or\s+", text_lower)
    return [p.strip() for p in parts if p.strip() and len(p.strip()) > 2]

def decompose_composite(outcome_text, condition):
    parts = _split_components(outcome_text)
    components = []
    for part in parts:
        result = classify_outcome(part, condition)
        components.append({"text": part, "classification": result["classification"], "matched_name": result["matched_name"]})
    classifications = set(c["classification"] for c in components if c["classification"] != "unclassified")
    mixed = "core" in classifications and "surrogate" in classifications
    return {"components": components, "mixed_relevance": mixed}
