"""Angles 9 (Sex & Gender Gap) + 10 (Elderly Exclusion Deep-Dive) for TrialFit."""
import csv
import json
import os
import re
import sys
from statistics import median

csv.field_size_limit(2**30)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "shared"))
from outcome_classifier import _detect_condition

SHARED_DIR = os.path.join(os.path.dirname(__file__), "..", "shared")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")

# Real-world age distribution: % of patients > 75 by condition
# Source: ESC registries, NHANES, published meta-analyses
ELDERLY_PREVALENCE = {
    "heart_failure": 0.50,
    "acute_coronary_syndrome": 0.35,
    "atrial_fibrillation": 0.60,
    "hypertension": 0.40,
    "other": 0.30,
}

SEX_STRATIFIED_KEYWORDS = [
    "sex-stratified", "sex stratified", "subgroup by sex", "subgroup by gender",
    "gender-specific", "gender specific", "men and women separately",
    "stratified by sex", "stratified by gender", "sex differences",
    "gender differences", "in women", "in men", "female subgroup", "male subgroup",
]


def _compute_era(start_date):
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


def analyze_sex_gap(trials):
    """Angle 9: sex restriction and stratification analysis."""
    total = len(trials)
    sex_restricted = 0
    sex_stratified_mention = 0
    by_era = {}
    by_condition = {}
    by_sponsor = {}

    for trial in trials:
        sex = trial.get("sex", "both")
        is_restricted = sex in ("male", "female")
        if is_restricted:
            sex_restricted += 1

        # Check for sex-stratified analysis mention
        all_text = (trial.get("primary_outcomes", "") + " " +
                    trial.get("secondary_outcomes", "") + " " +
                    trial.get("eligibility_criteria", "")).lower()
        has_stratified = any(kw in all_text for kw in SEX_STRATIFIED_KEYWORDS)
        if has_stratified:
            sex_stratified_mention += 1

        era = trial.get("era") or _compute_era(trial.get("start_date", ""))
        if era not in by_era:
            by_era[era] = {"count": 0, "restricted": 0, "stratified": 0}
        by_era[era]["count"] += 1
        by_era[era]["restricted"] += 1 if is_restricted else 0
        by_era[era]["stratified"] += 1 if has_stratified else 0

        cond = _detect_condition(trial.get("conditions", ""))
        cond_key = cond if cond else "other"
        if cond_key not in by_condition:
            by_condition[cond_key] = {"count": 0, "restricted": 0, "stratified": 0}
        by_condition[cond_key]["count"] += 1
        by_condition[cond_key]["restricted"] += 1 if is_restricted else 0
        by_condition[cond_key]["stratified"] += 1 if has_stratified else 0

        sponsor = trial.get("sponsor_class", "UNKNOWN")
        if sponsor not in by_sponsor:
            by_sponsor[sponsor] = {"count": 0, "restricted": 0, "stratified": 0}
        by_sponsor[sponsor]["count"] += 1
        by_sponsor[sponsor]["restricted"] += 1 if is_restricted else 0
        by_sponsor[sponsor]["stratified"] += 1 if has_stratified else 0

    # Compute percentages
    for d in [by_era, by_condition, by_sponsor]:
        for k, v in d.items():
            n = v["count"]
            v["pct_restricted"] = round(100 * v["restricted"] / n, 1) if n else 0
            v["pct_stratified"] = round(100 * v["stratified"] / n, 1) if n else 0

    return {
        "total_trials": total,
        "total_sex_restricted": sex_restricted,
        "pct_sex_restricted": round(100 * sex_restricted / total, 1) if total else 0,
        "total_sex_stratified_mention": sex_stratified_mention,
        "pct_sex_stratified_mention": round(100 * sex_stratified_mention / total, 1) if total else 0,
        "by_era": by_era,
        "by_condition": by_condition,
        "by_sponsor": by_sponsor,
    }


def analyze_elderly_exclusion(trials):
    """Angle 10: deep-dive into upper age cutoffs and exclusion burden."""
    total = len(trials)
    cutoff_bins = {"no_limit": 0, "85+": 0, "80-84": 0, "75-79": 0, "70-74": 0, "65-69": 0, "<65": 0}
    by_condition = {}
    by_era = {}
    by_sponsor = {}
    cutoff_values = []

    for trial in trials:
        max_age = trial.get("max_age")
        if isinstance(max_age, str):
            try:
                max_age = int(max_age) if max_age else None
            except ValueError:
                max_age = None

        if max_age is None:
            cutoff_bins["no_limit"] += 1
        elif max_age >= 85:
            cutoff_bins["85+"] += 1
            cutoff_values.append(max_age)
        elif max_age >= 80:
            cutoff_bins["80-84"] += 1
            cutoff_values.append(max_age)
        elif max_age >= 75:
            cutoff_bins["75-79"] += 1
            cutoff_values.append(max_age)
        elif max_age >= 70:
            cutoff_bins["70-74"] += 1
            cutoff_values.append(max_age)
        elif max_age >= 65:
            cutoff_bins["65-69"] += 1
            cutoff_values.append(max_age)
        else:
            cutoff_bins["<65"] += 1
            cutoff_values.append(max_age)

        cond = _detect_condition(trial.get("conditions", ""))
        cond_key = cond if cond else "other"
        era = trial.get("era") or _compute_era(trial.get("start_date", ""))
        sponsor = trial.get("sponsor_class", "UNKNOWN")

        for group_dict, key in [(by_condition, cond_key), (by_era, era), (by_sponsor, sponsor)]:
            if key not in group_dict:
                group_dict[key] = {"count": 0, "has_cutoff": 0, "below_75": 0, "cutoff_values": []}
            g = group_dict[key]
            g["count"] += 1
            if max_age is not None:
                g["has_cutoff"] += 1
                g["cutoff_values"].append(max_age)
                if max_age < 75:
                    g["below_75"] += 1

    # Compute exclusion burden per condition
    exclusion_burden = {}
    for cond_key, prevalence in ELDERLY_PREVALENCE.items():
        if cond_key in by_condition:
            n = by_condition[cond_key]["count"]
            below_75 = by_condition[cond_key]["below_75"]
            pct_below = below_75 / n if n else 0
            exclusion_burden[cond_key] = {
                "pct_trials_excluding_elderly": round(100 * pct_below, 1),
                "real_world_elderly_pct": round(100 * prevalence, 1),
                "estimated_exclusion_impact": round(100 * pct_below * prevalence, 1),
            }

    # Summarize group dicts
    for group_dict in [by_condition, by_era, by_sponsor]:
        for k, g in group_dict.items():
            n = g["count"]
            g["pct_has_cutoff"] = round(100 * g["has_cutoff"] / n, 1) if n else 0
            g["pct_below_75"] = round(100 * g["below_75"] / n, 1) if n else 0
            g["median_cutoff"] = round(median(g["cutoff_values"]), 1) if g["cutoff_values"] else None
            del g["cutoff_values"]

    trials_below_75 = sum(1 for t in trials if (t.get("max_age") is not None and (int(t["max_age"]) if isinstance(t["max_age"], str) and t["max_age"] else (t["max_age"] or 999)) < 75))

    return {
        "total_trials": total,
        "cutoff_distribution": cutoff_bins,
        "pct_cutoff_below_75": round(100 * trials_below_75 / total, 1) if total else 0,
        "median_cutoff": round(median(cutoff_values), 1) if cutoff_values else None,
        "exclusion_burden": exclusion_burden,
        "by_condition": by_condition,
        "by_era": by_era,
        "by_sponsor": by_sponsor,
    }


def load_trialfit_results(csv_path=None):
    """Load already-parsed TrialFit results (with sex, min_age, max_age fields)."""
    if csv_path is None:
        csv_path = os.path.join(OUTPUT_DIR, "trial_fit_results.csv")
    with open(csv_path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    # Convert numeric fields
    for r in rows:
        for field in ["min_age", "max_age", "enrollment", "exclusion_count", "generalizability_index"]:
            val = r.get(field, "")
            if val == "" or val == "None":
                r[field] = None
            else:
                try:
                    r[field] = int(float(val))
                except (ValueError, TypeError):
                    r[field] = None
    return rows


def load_raw_trials(csv_path=None):
    """Load raw trials CSV for outcome text scanning."""
    if csv_path is None:
        csv_path = os.path.join(SHARED_DIR, "cv_trials.csv")
    with open(csv_path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save_outputs(sex_result, elderly_result):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(os.path.join(OUTPUT_DIR, "sex_gap.json"), "w") as f:
        json.dump(sex_result, f, indent=2)
    with open(os.path.join(OUTPUT_DIR, "elderly_exclusion.json"), "w") as f:
        json.dump(elderly_result, f, indent=2)


def main():
    print("Loading TrialFit results...", file=sys.stderr)
    fit_results = load_trialfit_results()
    raw_trials = load_raw_trials()
    print(f"Loaded {len(fit_results)} parsed + {len(raw_trials)} raw trials", file=sys.stderr)

    # Merge raw outcome text into fit results for sex stratification scanning
    raw_by_id = {t["nct_id"]: t for t in raw_trials}
    for r in fit_results:
        raw = raw_by_id.get(r["nct_id"], {})
        r["primary_outcomes"] = raw.get("primary_outcomes", "")
        r["secondary_outcomes"] = raw.get("secondary_outcomes", "")
        r["eligibility_criteria"] = raw.get("eligibility_criteria", "")

    print("Analyzing sex gap (Angle 9)...", file=sys.stderr)
    sex_result = analyze_sex_gap(fit_results)
    print(f"  Sex-restricted: {sex_result['pct_sex_restricted']}%", file=sys.stderr)
    print(f"  Sex-stratified mention: {sex_result['pct_sex_stratified_mention']}%", file=sys.stderr)

    print("Analyzing elderly exclusion (Angle 10)...", file=sys.stderr)
    elderly_result = analyze_elderly_exclusion(fit_results)
    print(f"  Cutoff <75: {elderly_result['pct_cutoff_below_75']}%", file=sys.stderr)
    print(f"  Median cutoff: {elderly_result['median_cutoff']}", file=sys.stderr)

    save_outputs(sex_result, elderly_result)
    print("Done.", file=sys.stderr)


if __name__ == "__main__":
    main()
