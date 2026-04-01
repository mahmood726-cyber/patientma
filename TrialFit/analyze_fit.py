"""CardioTrialFit: parse eligibility criteria and compute generalizability index."""
import csv
import json
import os
import re
import sys
from statistics import median

csv.field_size_limit(10 * 1024 * 1024)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "shared"))
from outcome_classifier import _detect_condition

SHARED_DIR = os.path.join(os.path.dirname(__file__), "..", "shared")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")

COMORBIDITY_WEIGHTS = {
    "ckd": 8, "diabetes": 7, "cancer": 4, "liver": 3, "cognitive": 5,
    "frailty": 6, "obesity": 5, "copd": 4, "pregnancy": 1, "anemia": 3, "bleeding": 4,
}


def parse_age_range(text):
    """Extract minimum and maximum age from eligibility criteria text."""
    if not text:
        return None, None
    text_lower = text.lower()
    min_age = None
    max_age = None

    m = re.search(r'between\s+(\d+)\s+and\s+(\d+)\s*(?:years?|yrs?)', text_lower)
    if m:
        return int(m.group(1)), int(m.group(2))

    m = re.search(r'age\s*(?:of\s*)?(\d+)\s*[-\u2013to]+\s*(\d+)', text_lower)
    if m:
        return int(m.group(1)), int(m.group(2))

    for pattern in [
        r'(?:>=|≥|at least|older than)\s*(\d+)\s*(?:years?|yrs?)?',
        r'(\d+)\s*(?:years?|yrs?)\s*(?:or older|and older|of age or older)',
        r'age\s*(?:>=|≥)\s*(\d+)',
    ]:
        m = re.search(pattern, text_lower)
        if m:
            min_age = int(m.group(1))
            break

    for pattern in [
        r'(?:<=|≤|younger than|not older than|no older than)\s*(\d+)',
        r'(?:age|aged?)\s*(?:<=|≤|<|less than|under)\s*(\d+)',
    ]:
        m = re.search(pattern, text_lower)
        if m:
            max_age = int(m.group(1))
            break

    # "greater than X" / "older than X" in EXCLUSION context = max_age
    if max_age is None:
        _, excl_text = _split_inclusion_exclusion(text)
        if excl_text:
            excl_lower = excl_text.lower()
            m = re.search(r'(?:greater than|>|older than)\s*(\d+)', excl_lower)
            if m:
                max_age = int(m.group(1))

    if min_age is None and re.search(r'\badults?\b', text_lower):
        min_age = 18

    return min_age, max_age


def parse_sex_restriction(text):
    """Detect sex restriction: 'male', 'female', or 'both'."""
    if not text:
        return "both"
    text_lower = text.lower()
    male_only = re.search(r'\bmale\s*(only|patients only|subjects only)\b', text_lower)
    female_only = re.search(r'\bfemale\s*(only|patients only|subjects only)\b', text_lower)
    if male_only and not female_only:
        return "male"
    if female_only and not male_only:
        return "female"
    return "both"


def _split_inclusion_exclusion(text):
    """Split eligibility text into inclusion and exclusion sections."""
    text_lower = text.lower()
    excl_start = None
    for marker in ["exclusion criteria", "exclusion:", "exclude:"]:
        idx = text_lower.find(marker)
        if idx != -1:
            excl_start = idx
            break
    if excl_start is not None:
        return text[:excl_start], text[excl_start:]
    return text, ""


def parse_comorbidity_exclusions(text):
    """Extract comorbidity exclusion categories from eligibility text (exclusion section only)."""
    if not text:
        return []
    _, exclusion_text = _split_inclusion_exclusion(text)
    if not exclusion_text:
        return []
    excl_lower = exclusion_text.lower()
    found = []
    patterns = {
        "ckd": [r"renal\s+(?:insufficiency|failure|impairment|disease)", r"egfr\s*[<≤]", r"creatinine\s+clearance", r"dialysis", r"kidney\s+disease", r"ckd"],
        "diabetes": [r"diabetes\s+mellitus", r"type\s*[12]\s*diabetes", r"diabetic", r"\bdiabetes\b"],
        "cancer": [r"malignancy", r"cancer", r"neoplasm", r"carcinoma", r"tumor", r"tumour"],
        "liver": [r"liver\s+(?:disease|cirrhosis|failure|impairment)", r"hepatic\s+(?:disease|cirrhosis|failure|impairment)", r"ast\s*>\s*\d", r"alt\s*>\s*\d"],
        "cognitive": [r"dementia", r"cognitive\s+impairment", r"alzheimer", r"mental\s+(?:disorder|illness)"],
        "frailty": [r"frail", r"bed\s*bound", r"life\s+expectancy\s*<", r"terminal"],
        "obesity": [r"bmi\s*[>≥]\s*\d", r"morbid\s+obes", r"obesity"],
        "copd": [r"copd", r"chronic\s+obstructive", r"pulmonary\s+disease", r"severe\s+lung"],
        "pregnancy": [r"pregnan", r"breast\s*feeding", r"lactating"],
        "anemia": [r"anemia", r"anaemia", r"hemoglobin\s*[<≤]"],
        "bleeding": [r"bleeding\s+(?:risk|history|disorder)", r"hemorrhag", r"haemorrhag", r"active\s+bleeding"],
    }
    for category, regexes in patterns.items():
        for rx in regexes:
            if re.search(rx, excl_lower):
                found.append(category)
                break
    return found


def parse_functional_requirement(text):
    """Extract functional status requirement (NYHA class or ECOG)."""
    if not text:
        return {"type": None}
    text_lower = text.lower()
    m = re.search(r'nyha\s*(?:class\s*)?(i{1,4}|[1-4])(?:\s*[-\u2013]\s*(?:class\s*)?(i{1,4}|[1-4]))?', text_lower)
    if m:
        roman_map = {"i": 1, "ii": 2, "iii": 3, "iv": 4}
        raw = m.group(1)
        min_class = roman_map.get(raw, int(raw) if raw.isdigit() else 1)
        return {"type": "NYHA", "min_class": min_class}
    m = re.search(r'ecog\s*(?:performance\s*)?(?:status\s*)?(?:<=?|≤)?\s*(\d)', text_lower)
    if m:
        return {"type": "ECOG", "max_score": int(m.group(1))}
    return {"type": None}


def compute_age_score(min_age, max_age):
    """Age breadth score (0-20). Wider range = higher. Penalize upper cutoff < 75."""
    if min_age is None and max_age is None:
        return 10
    if max_age is None:
        return 20
    if min_age is None:
        min_age = 18
    age_range = max_age - min_age
    base = min(15, int(15 * age_range / 70))
    if max_age >= 85:
        cutoff_bonus = 5
    elif max_age >= 75:
        cutoff_bonus = 3
    elif max_age >= 65:
        cutoff_bonus = 0
    else:
        cutoff_bonus = -3
    return max(0, min(20, base + cutoff_bonus))


def compute_sex_score(sex):
    """Sex inclusivity score (0-10)."""
    return 10 if sex == "both" else 5


def compute_comorbidity_score(exclusions):
    """Comorbidity tolerance score (0-40). Fewer exclusions = higher."""
    if not exclusions:
        return 40
    total_weight = sum(COMORBIDITY_WEIGHTS.get(e, 3) for e in exclusions)
    return max(0, min(40, 40 - int(40 * total_weight / 50)))


def compute_functional_score(functional):
    """Functional threshold score (0-15). Less restrictive = higher."""
    if functional["type"] is None:
        return 15
    if functional["type"] == "NYHA":
        min_class = functional.get("min_class", 1)
        if min_class >= 3:
            return 5
        elif min_class >= 2:
            return 10
        else:
            return 15
    if functional["type"] == "ECOG":
        max_score = functional.get("max_score", 2)
        if max_score <= 1:
            return 8
        else:
            return 12
    return 15


def compute_generalizability_index(age_score, sex_score, comorbidity_score,
                                    functional_score, representation_score):
    """Sum all component scores for generalizability index (0-100)."""
    return age_score + sex_score + comorbidity_score + functional_score + representation_score


def compute_era(start_date):
    """Map start date to 5-year era bin."""
    if not start_date:
        return "Unknown"
    try:
        year = int(start_date[:4])
    except (ValueError, IndexError):
        return "Unknown"
    if year < 2000:
        return "Pre-2000"
    elif year <= 2004:
        return "2000-2004"
    elif year <= 2009:
        return "2005-2009"
    elif year <= 2014:
        return "2010-2014"
    elif year <= 2019:
        return "2015-2019"
    else:
        return "2020-2025"


def classify_all_trials(trials):
    """Parse eligibility and compute generalizability for all trials."""
    results = []
    for trial in trials:
        elig = trial.get("eligibility_criteria", "")
        min_age, max_age = parse_age_range(elig)
        sex = parse_sex_restriction(elig)
        exclusions = parse_comorbidity_exclusions(elig)
        functional = parse_functional_requirement(elig)
        age_score = compute_age_score(min_age, max_age)
        sex_score = compute_sex_score(sex)
        comorbidity_score = compute_comorbidity_score(exclusions)
        functional_score = compute_functional_score(functional)
        representation_score = 10
        gi = compute_generalizability_index(
            age_score, sex_score, comorbidity_score,
            functional_score, representation_score,
        )
        detected = _detect_condition(trial.get("conditions", ""))
        results.append({
            "nct_id": trial["nct_id"],
            "conditions": trial.get("conditions", ""),
            "detected_condition": detected if detected else "other",
            "phase": trial.get("phase", "").split("|")[0] if trial.get("phase") else "",
            "enrollment": int(trial.get("enrollment", 0) or 0),
            "sponsor_class": trial.get("sponsor_class", ""),
            "era": compute_era(trial.get("start_date", "")),
            "min_age": min_age, "max_age": max_age, "sex": sex,
            "exclusions": exclusions, "exclusion_count": len(exclusions),
            "functional_type": functional["type"],
            "age_score": age_score, "sex_score": sex_score,
            "comorbidity_score": comorbidity_score, "functional_score": functional_score,
            "representation_score": representation_score,
            "generalizability_index": gi,
        })
    return results


def aggregate_by_field(results, field):
    """Group results by field and compute aggregate GI stats."""
    groups = {}
    for r in results:
        key = r.get(field, "Unknown")
        if key not in groups:
            groups[key] = {"count": 0, "gi_values": [], "excl_counts": []}
        g = groups[key]
        g["count"] += 1
        g["gi_values"].append(r["generalizability_index"])
        g["excl_counts"].append(r["exclusion_count"])
    for key, g in groups.items():
        vals = g["gi_values"]
        g["mean_gi"] = round(sum(vals) / len(vals), 1) if vals else 0
        g["median_gi"] = round(median(vals), 1) if vals else 0
        g["mean_excl"] = round(sum(g["excl_counts"]) / len(g["excl_counts"]), 2) if g["excl_counts"] else 0
        del g["gi_values"]
        del g["excl_counts"]
    return groups


def build_exclusion_ranking(results):
    """Rank exclusion criteria by frequency and real-world impact."""
    counts = {}
    for r in results:
        for excl in r["exclusions"]:
            counts[excl] = counts.get(excl, 0) + 1
    n = len(results) if results else 1
    ranking = []
    for excl, count in sorted(counts.items(), key=lambda x: -x[1]):
        ranking.append({
            "exclusion": excl, "count": count,
            "pct_of_trials": round(100 * count / n, 1),
            "real_world_weight": COMORBIDITY_WEIGHTS.get(excl, 3),
            "impact_score": round(count / n * COMORBIDITY_WEIGHTS.get(excl, 3), 3),
        })
    ranking.sort(key=lambda x: -x["impact_score"])
    return ranking


def build_summary(results):
    """Build full summary dict for dashboard embedding."""
    n = len(results)
    gi_values = [r["generalizability_index"] for r in results]
    excl_age75 = sum(1 for r in results if r["max_age"] is not None and r["max_age"] < 75)
    excl_ckd = sum(1 for r in results if "ckd" in r["exclusions"])
    return {
        "total_trials": n,
        "mean_gi": round(sum(gi_values) / n, 1) if n else 0,
        "median_gi": round(median(gi_values), 1) if n else 0,
        "pct_exclude_age75": round(100 * excl_age75 / n, 1) if n else 0,
        "pct_exclude_ckd": round(100 * excl_ckd / n, 1) if n else 0,
        "by_condition": aggregate_by_field(results, "detected_condition"),
        "by_phase": aggregate_by_field(results, "phase"),
        "by_era": aggregate_by_field(results, "era"),
        "by_sponsor_class": aggregate_by_field(results, "sponsor_class"),
        "exclusion_ranking": build_exclusion_ranking(results),
        "dimension_averages": {
            "age": round(sum(r["age_score"] for r in results) / n, 1) if n else 0,
            "sex": round(sum(r["sex_score"] for r in results) / n, 1) if n else 0,
            "comorbidity": round(sum(r["comorbidity_score"] for r in results) / n, 1) if n else 0,
            "functional": round(sum(r["functional_score"] for r in results) / n, 1) if n else 0,
            "representation": round(sum(r["representation_score"] for r in results) / n, 1) if n else 0,
        },
    }


def load_trials(csv_path=None):
    """Load trials from shared CSV."""
    if csv_path is None:
        csv_path = os.path.join(SHARED_DIR, "cv_trials.csv")
    with open(csv_path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save_outputs(results, summary):
    """Save parsed trials CSV and summary JSON."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    csv_path = os.path.join(OUTPUT_DIR, "trial_fit_results.csv")
    if results:
        csv_rows = []
        for r in results:
            row = {k: v for k, v in r.items() if k != "exclusions"}
            row["exclusions"] = "|".join(r["exclusions"])
            csv_rows.append(row)
        fieldnames = list(csv_rows[0].keys())
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_rows)
    json_path = os.path.join(OUTPUT_DIR, "summary.json")
    with open(json_path, "w") as f:
        json.dump(summary, f, indent=2)
    return csv_path, json_path


def main():
    """Run the full TrialFit analysis pipeline."""
    print("Loading CV trials...", file=sys.stderr)
    trials = load_trials()
    print(f"Loaded {len(trials)} trials", file=sys.stderr)
    print("Parsing eligibility and computing generalizability...", file=sys.stderr)
    results = classify_all_trials(trials)
    print("Building summary...", file=sys.stderr)
    summary = build_summary(results)
    print("Saving outputs...", file=sys.stderr)
    csv_path, json_path = save_outputs(results, summary)
    print(f"\nResults:", file=sys.stderr)
    print(f"  Total trials: {summary['total_trials']}", file=sys.stderr)
    print(f"  Median GI: {summary['median_gi']}", file=sys.stderr)
    print(f"  % excluding age > 75: {summary['pct_exclude_age75']}%", file=sys.stderr)
    print(f"  % excluding CKD: {summary['pct_exclude_ckd']}%", file=sys.stderr)
    print(f"  Output: {csv_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
