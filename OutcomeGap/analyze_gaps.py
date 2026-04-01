"""CardioOutcomeGap: analyze patient-relevance gap in CV trial outcomes."""
import csv
import json
import os
import sys

csv.field_size_limit(2**30)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "shared"))

from outcome_classifier import classify_trial, _detect_condition

SHARED_DIR = os.path.join(os.path.dirname(__file__), "..", "shared")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")


def load_trials(csv_path=None):
    """Load trials from the shared CSV."""
    if csv_path is None:
        csv_path = os.path.join(SHARED_DIR, "cv_trials.csv")
    with open(csv_path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def compute_era(start_date):
    """Map a start date (YYYY-MM or YYYY-MM-DD) to a 5-year era bin."""
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
    """Classify all trials and return enriched row dicts."""
    results = []
    for trial in trials:
        conditions_text = trial.get("conditions", "")
        detected = _detect_condition(conditions_text)

        ct_result = classify_trial(
            primary_outcomes=trial.get("primary_outcomes", ""),
            secondary_outcomes=trial.get("secondary_outcomes", ""),
            condition=detected if detected else conditions_text,
        )

        results.append({
            "nct_id": trial["nct_id"],
            "title": trial.get("title", ""),
            "conditions": conditions_text,
            "detected_condition": detected if detected else "other",
            "phase": trial.get("phase", "").split("|")[0] if trial.get("phase") else "",
            "enrollment": int(trial.get("enrollment", 0) or 0),
            "sponsor_name": trial.get("sponsor_name", ""),
            "sponsor_class": trial.get("sponsor_class", ""),
            "era": compute_era(trial.get("start_date", "")),
            "has_results": trial.get("has_results", "").lower() in ("true", "1", "yes") if isinstance(trial.get("has_results"), str) else bool(trial.get("has_results")),
            "core_count": ct_result["core_count"],
            "surrogate_count": ct_result["surrogate_count"],
            "unclassified_count": ct_result["unclassified_count"],
            "has_PRO": ct_result["has_PRO"],
            "gap_score": ct_result["gap_score"],
            "core_names": "|".join(ct_result["core_names"]),
            "surrogate_names": "|".join(ct_result["surrogate_names"]),
        })
    return results


def aggregate_by_field(results, field):
    """Group results by a field and compute aggregate stats."""
    groups = {}
    for r in results:
        key = r.get(field, "Unknown")
        if key not in groups:
            groups[key] = {"count": 0, "core_sum": 0, "pro_sum": 0, "gap_sum": 0.0}
        g = groups[key]
        g["count"] += 1
        g["core_sum"] += 1 if r["core_count"] > 0 else 0
        g["pro_sum"] += 1 if r["has_PRO"] else 0
        g["gap_sum"] += r["gap_score"]

    for key, g in groups.items():
        n = g["count"]
        g["pct_with_core"] = round(100 * g["core_sum"] / n, 1) if n > 0 else 0
        g["pct_with_PRO"] = round(100 * g["pro_sum"] / n, 1) if n > 0 else 0
        g["mean_gap_score"] = round(g["gap_sum"] / n, 4) if n > 0 else 1.0

    return groups


def build_summary(results):
    """Build a full summary dict for dashboard embedding."""
    n = len(results)
    core_any = sum(1 for r in results if r["core_count"] > 0)
    pro_any = sum(1 for r in results if r["has_PRO"])
    gap_total = sum(r["gap_score"] for r in results)

    return {
        "total_trials": n,
        "pct_with_core": round(100 * core_any / n, 1) if n > 0 else 0,
        "pct_with_PRO": round(100 * pro_any / n, 1) if n > 0 else 0,
        "mean_gap_score": round(gap_total / n, 4) if n > 0 else 1.0,
        "by_condition": aggregate_by_field(results, "detected_condition"),
        "by_phase": aggregate_by_field(results, "phase"),
        "by_era": aggregate_by_field(results, "era"),
        "by_sponsor_class": aggregate_by_field(results, "sponsor_class"),
    }


def save_outputs(results, summary):
    """Save classified trials CSV and summary JSON."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    csv_path = os.path.join(OUTPUT_DIR, "classified_trials.csv")
    if results:
        fieldnames = list(results[0].keys())
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

    json_path = os.path.join(OUTPUT_DIR, "summary.json")
    with open(json_path, "w") as f:
        json.dump(summary, f, indent=2)

    outcome_counts = {}
    for r in results:
        for name in r["core_names"].split("|"):
            if name:
                outcome_counts[name] = outcome_counts.get(name, 0) + 1
        for name in r["surrogate_names"].split("|"):
            if name:
                outcome_counts[name] = outcome_counts.get(name, 0) + 1
    top_outcomes = sorted(outcome_counts.items(), key=lambda x: -x[1])[:20]
    top_path = os.path.join(OUTPUT_DIR, "top_outcomes.json")
    with open(top_path, "w") as f:
        json.dump(top_outcomes, f, indent=2)

    return csv_path, json_path


def main():
    """Run the full gap analysis pipeline."""
    print("Loading CV trials...", file=sys.stderr)
    trials = load_trials()
    print(f"Loaded {len(trials)} trials", file=sys.stderr)

    print("Classifying outcomes...", file=sys.stderr)
    results = classify_all_trials(trials)

    print("Building summary...", file=sys.stderr)
    summary = build_summary(results)

    print("Saving outputs...", file=sys.stderr)
    csv_path, json_path = save_outputs(results, summary)

    print(f"\nResults:", file=sys.stderr)
    print(f"  Total trials: {summary['total_trials']}", file=sys.stderr)
    print(f"  % with core outcome: {summary['pct_with_core']}%", file=sys.stderr)
    print(f"  % with PRO: {summary['pct_with_PRO']}%", file=sys.stderr)
    print(f"  Mean gap score: {summary['mean_gap_score']}", file=sys.stderr)
    print(f"  Output: {csv_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
