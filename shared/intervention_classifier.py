"""Classify trial interventions into types (drug, device, procedure, behavioral, diagnostic)."""

INTERVENTION_TYPES = {
    "drug": ["drug", "pharmaceutical", "medication", "tablet", "capsule", "injection", "infusion", "dose", "mg ", "placebo", "oral", "intravenous", "subcutaneous", "pill", "solution", "suspension", "patch", "inhaler", "spray", "olol", "sartan", "pril", "statin", "mab", "nib", "afil", "gliflozin", "gliptin", "parin", "xaban", "dipine", "flozin", "azole", "mycin", "cillin", "oxacin"],
    "device": ["device", "implant", "pacemaker", "stent", "catheter", "icd", "crt", "lead", "generator", "valve", "prosthesis", "electrode", "sensor", "wearable", "monitor device"],
    "procedure": ["surgery", "ablation", "revascularization", "pci", "cabg", "transplant", "bypass", "angioplasty", "thrombectomy", "endarterectomy", "denervation", "cardioversion", "implantation"],
    "behavioral": ["exercise", "rehabilitation", "lifestyle", "diet", "counseling", "education", "self-management", "cognitive behavioral", "mindfulness", "physical activity", "walking", "yoga", "meditation", "telehealth", "coaching", "training program"],
    "diagnostic": ["imaging", "biomarker", "monitoring", "screening", "echocardiography", "mri", "ct scan", "ultrasound", "holter", "angiography", "pet scan"],
}


def classify_intervention(text):
    """Classify intervention text into one or more types.

    Args:
        text: Intervention description string. Pipe-delimited for multiple.

    Returns:
        Sorted list of matched types, or ["other"] if none match.
    """
    if not text or not text.strip():
        return ["other"]
    text_lower = text.lower()
    found = set()
    for itype, keywords in INTERVENTION_TYPES.items():
        for kw in keywords:
            if kw in text_lower:
                found.add(itype)
                break
    return sorted(found) if found else ["other"]
