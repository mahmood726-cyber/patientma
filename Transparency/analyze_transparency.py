"""Angles 5 (Industry vs Academia), 7 (Results Transparency), 12 (Publication Gap)."""
import csv
import json
import math
import os
import sys
from statistics import median

csv.field_size_limit(2**30)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "shared"))
from stats_utils import chi_squared_2x2, cramers_v, mann_whitney_u, rank_biserial, logistic_regression_simple

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")


def _to_int(val, default=0):
    if val is None or val == "" or val == "None":
        return default
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return default


def _to_float(val, default=0.0):
    if val is None or val == "" or val == "None":
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def _to_bool(val):
    if isinstance(val, bool):
        return val
    return str(val).lower() in ("true", "1", "yes")


def analyze_sponsor_comparison(classified_trials, fit_trials):
    """Angle 5: Industry vs. academia comparison on patient-centricity metrics."""
    # Build fit lookup
    fit_by_id = {}
    for t in fit_trials:
        fit_by_id[t["nct_id"]] = t

    sponsor_groups = {}
    for t in classified_trials:
        sponsor = t.get("sponsor_class", "UNKNOWN")
        if sponsor not in sponsor_groups:
            sponsor_groups[sponsor] = {
                "count": 0, "gap_scores": [], "gi_values": [],
                "core_any": 0, "pro_any": 0, "has_results": 0,
                "enrollments": [],
            }
        g = sponsor_groups[sponsor]
        g["count"] += 1
        g["gap_scores"].append(_to_float(t.get("gap_score")))
        g["core_any"] += 1 if _to_int(t.get("core_count")) > 0 else 0
        g["pro_any"] += 1 if _to_bool(t.get("has_PRO")) else 0
        g["has_results"] += 1 if _to_bool(t.get("has_results")) else 0
        g["enrollments"].append(_to_int(t.get("enrollment")))

        fit = fit_by_id.get(t["nct_id"])
        if fit:
            gi = _to_int(fit.get("generalizability_index"))
            if gi:
                g["gi_values"].append(gi)

    by_sponsor = {}
    for sponsor, g in sponsor_groups.items():
        n = g["count"]
        by_sponsor[sponsor] = {
            "count": n,
            "mean_gap_score": round(sum(g["gap_scores"]) / n, 4) if n else 1.0,
            "pct_with_core": round(100 * g["core_any"] / n, 1) if n else 0,
            "pct_with_PRO": round(100 * g["pro_any"] / n, 1) if n else 0,
            "pct_with_results": round(100 * g["has_results"] / n, 1) if n else 0,
            "mean_gi": round(sum(g["gi_values"]) / len(g["gi_values"]), 1) if g["gi_values"] else 0,
            "median_enrollment": round(median(g["enrollments"]), 0) if g["enrollments"] else 0,
        }

    # Statistical comparison: INDUSTRY vs OTHER (academic)
    ind = sponsor_groups.get("INDUSTRY", {"core_any": 0, "count": 0, "gap_scores": [], "gi_values": []})
    oth = sponsor_groups.get("OTHER", {"core_any": 0, "count": 0, "gap_scores": [], "gi_values": []})
    comparisons = {}
    if ind["count"] > 0 and oth["count"] > 0:
        a, b = ind["core_any"], ind["count"] - ind["core_any"]
        c, d = oth["core_any"], oth["count"] - oth["core_any"]
        chi2, p = chi_squared_2x2(a, b, c, d)
        comparisons["core_outcome_chi2"] = {"chi2": round(chi2, 2), "p": round(p, 4), "cramers_v": round(cramers_v(a, b, c, d), 4)}

        if ind["gap_scores"] and oth["gap_scores"]:
            U, p_mw = mann_whitney_u(ind["gap_scores"], oth["gap_scores"])
            comparisons["gap_score_mann_whitney"] = {"U": round(U, 1), "p": round(p_mw, 4), "rank_biserial": round(rank_biserial(ind["gap_scores"], oth["gap_scores"]), 4)}

    return {"by_sponsor": by_sponsor, "comparisons": comparisons}


def analyze_results_transparency(classified_trials):
    """Angle 7: Are patient-centered trials more likely to post results?"""
    patient_centered = {"count": 0, "posted": 0}
    surrogate_only = {"count": 0, "posted": 0}
    unclassified = {"count": 0, "posted": 0}
    by_era = {}

    for t in classified_trials:
        core = _to_int(t.get("core_count"))
        surr = _to_int(t.get("surrogate_count"))
        has_results = _to_bool(t.get("has_results"))
        era = t.get("era", "Unknown")

        if core > 0:
            group = patient_centered
            group_key = "patient_centered"
        elif surr > 0:
            group = surrogate_only
            group_key = "surrogate_only"
        else:
            group = unclassified
            group_key = "unclassified"

        group["count"] += 1
        group["posted"] += 1 if has_results else 0

        if era not in by_era:
            by_era[era] = {"patient_centered": {"count": 0, "posted": 0}, "surrogate_only": {"count": 0, "posted": 0}}
        if era in by_era and group_key in by_era[era]:
            by_era[era][group_key]["count"] += 1
            by_era[era][group_key]["posted"] += 1 if has_results else 0

    for group in [patient_centered, surrogate_only, unclassified]:
        n = group["count"]
        group["posting_rate"] = round(100 * group["posted"] / n, 1) if n else 0

    for era_data in by_era.values():
        for gk in ["patient_centered", "surrogate_only"]:
            if gk in era_data:
                n = era_data[gk]["count"]
                era_data[gk]["posting_rate"] = round(100 * era_data[gk]["posted"] / n, 1) if n else 0

    # Chi-squared: patient-centered vs surrogate posting rates
    a = patient_centered["posted"]
    b = patient_centered["count"] - patient_centered["posted"]
    c = surrogate_only["posted"]
    d = surrogate_only["count"] - surrogate_only["posted"]
    chi2, p = chi_squared_2x2(a, b, c, d)

    return {
        "patient_centered": patient_centered,
        "surrogate_only": surrogate_only,
        "unclassified": unclassified,
        "by_era": by_era,
        "chi2_test": {"chi2": round(chi2, 2), "p": round(p, 4), "cramers_v": round(cramers_v(a, b, c, d), 4)},
    }


def analyze_publication_gap(classified_trials):
    """Angle 12: results posting by patient-centricity level."""
    levels = {"high": {"count": 0, "posted": 0, "enrollments": []},
              "medium": {"count": 0, "posted": 0, "enrollments": []},
              "low": {"count": 0, "posted": 0, "enrollments": []}}

    X_logistic = []
    y_logistic = []

    for t in classified_trials:
        gap = _to_float(t.get("gap_score"), 1.0)
        has_results = _to_bool(t.get("has_results"))
        enrollment = _to_int(t.get("enrollment"))

        if gap < 0.5:
            level = "high"
        elif gap < 0.8:
            level = "medium"
        else:
            level = "low"

        levels[level]["count"] += 1
        levels[level]["posted"] += 1 if has_results else 0
        levels[level]["enrollments"].append(enrollment)

        X_logistic.append([gap])
        y_logistic.append(1 if has_results else 0)

    by_centricity = {}
    for level, data in levels.items():
        n = data["count"]
        by_centricity[level] = {
            "count": n,
            "posted": data["posted"],
            "posting_rate": round(100 * data["posted"] / n, 1) if n else 0,
            "median_enrollment": round(median(data["enrollments"]), 0) if data["enrollments"] else 0,
        }

    # Evidence waste: completed trials with no results, weighted by enrollment
    total_enrolled_no_results = sum(
        _to_int(t.get("enrollment")) for t in classified_trials if not _to_bool(t.get("has_results"))
    )
    total_enrolled = sum(_to_int(t.get("enrollment")) for t in classified_trials)

    # Simple logistic regression: P(results) ~ gap_score
    logistic_result = {}
    if len(X_logistic) > 10:
        try:
            lr = logistic_regression_simple(X_logistic, y_logistic, max_iter=50)
            logistic_result = {
                "gap_score_coefficient": round(lr["coefficients"][0], 4),
                "intercept": round(lr["intercept"], 4),
                "iterations": lr["iterations"],
            }
        except Exception:
            logistic_result = {"error": "convergence failure"}

    return {
        "by_centricity": by_centricity,
        "evidence_waste": {
            "total_no_results_enrollment": total_enrolled_no_results,
            "total_enrollment": total_enrolled,
            "pct_wasted": round(100 * total_enrolled_no_results / total_enrolled, 1) if total_enrolled else 0,
        },
        "logistic_model": logistic_result,
    }


def load_classified_trials(csv_path=None):
    if csv_path is None:
        csv_path = os.path.join(os.path.dirname(__file__), "..", "OutcomeGap", "outputs", "classified_trials.csv")
    with open(csv_path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_fit_results(csv_path=None):
    if csv_path is None:
        csv_path = os.path.join(os.path.dirname(__file__), "..", "TrialFit", "outputs", "trial_fit_results.csv")
    with open(csv_path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save_outputs(sponsor_result, transparency_result, publication_result):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(os.path.join(OUTPUT_DIR, "sponsor_comparison.json"), "w") as f:
        json.dump(sponsor_result, f, indent=2)
    with open(os.path.join(OUTPUT_DIR, "transparency.json"), "w") as f:
        json.dump(transparency_result, f, indent=2)
    with open(os.path.join(OUTPUT_DIR, "publication_gap.json"), "w") as f:
        json.dump(publication_result, f, indent=2)


def main():
    print("Loading data...", file=sys.stderr)
    classified = load_classified_trials()
    fit = load_fit_results()
    print(f"Loaded {len(classified)} classified + {len(fit)} fit results", file=sys.stderr)

    print("Analyzing sponsor comparison (Angle 5)...", file=sys.stderr)
    sponsor_result = analyze_sponsor_comparison(classified, fit)

    print("Analyzing results transparency (Angle 7)...", file=sys.stderr)
    transparency_result = analyze_results_transparency(classified)

    print("Analyzing publication gap (Angle 12)...", file=sys.stderr)
    publication_result = analyze_publication_gap(classified)

    save_outputs(sponsor_result, transparency_result, publication_result)
    print("Done.", file=sys.stderr)


if __name__ == "__main__":
    main()
