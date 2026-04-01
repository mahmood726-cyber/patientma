"""Angles 8 (Intervention Landscape) + 11 (Composite Endpoints) for OutcomeGap."""
import csv
import json
import os
import sys

csv.field_size_limit(2**30)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "shared"))

from outcome_classifier import classify_trial, _detect_condition
from intervention_classifier import classify_intervention
from composite_detector import detect_composite, decompose_composite

SHARED_DIR = os.path.join(os.path.dirname(__file__), "..", "shared")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")


def analyze_intervention_landscape(trials):
    """Angle 8: classify interventions and cross-reference with outcome gap."""
    type_stats = {}

    for trial in trials:
        itypes = classify_intervention(trial.get("interventions", ""))
        detected_cond = _detect_condition(trial.get("conditions", ""))
        ct_result = classify_trial(
            primary_outcomes=trial.get("primary_outcomes", ""),
            secondary_outcomes=trial.get("secondary_outcomes", ""),
            condition=detected_cond if detected_cond else trial.get("conditions", ""),
        )

        for itype in itypes:
            if itype not in type_stats:
                type_stats[itype] = {
                    "count": 0, "gap_sum": 0.0, "core_any": 0,
                    "pro_any": 0, "by_condition": {},
                }
            s = type_stats[itype]
            s["count"] += 1
            s["gap_sum"] += ct_result["gap_score"]
            s["core_any"] += 1 if ct_result["core_count"] > 0 else 0
            s["pro_any"] += 1 if ct_result["has_PRO"] else 0

            cond_key = detected_cond if detected_cond else "other"
            if cond_key not in s["by_condition"]:
                s["by_condition"][cond_key] = {"count": 0, "gap_sum": 0.0}
            s["by_condition"][cond_key]["count"] += 1
            s["by_condition"][cond_key]["gap_sum"] += ct_result["gap_score"]

    by_type = {}
    for itype, s in type_stats.items():
        n = s["count"]
        by_type[itype] = {
            "count": n,
            "mean_gap_score": round(s["gap_sum"] / n, 4) if n else 1.0,
            "pct_with_core": round(100 * s["core_any"] / n, 1) if n else 0,
            "pct_with_PRO": round(100 * s["pro_any"] / n, 1) if n else 0,
            "by_condition": {
                k: {"count": v["count"], "mean_gap_score": round(v["gap_sum"] / v["count"], 4)}
                for k, v in s["by_condition"].items()
            },
        }

    return {"by_type": by_type, "total_trials": len(trials)}


def analyze_composites(trials):
    """Angle 11: detect composite endpoints and classify components."""
    total_composite = 0
    total_mixed = 0
    total_pure_core = 0
    total_pure_surrogate = 0
    composite_texts = []

    for trial in trials:
        primary = trial.get("primary_outcomes", "")
        if not primary:
            continue

        for measure in primary.split("|"):
            measure = measure.strip()
            if not measure:
                continue

            det = detect_composite(measure)
            if det["is_composite"]:
                total_composite += 1
                composite_texts.append(measure)

                detected_cond = _detect_condition(trial.get("conditions", ""))
                if detected_cond:
                    decomp = decompose_composite(measure, detected_cond)
                    if decomp["mixed_relevance"]:
                        total_mixed += 1
                    else:
                        classifications = set(c["classification"] for c in decomp["components"] if c["classification"] != "unclassified")
                        if classifications == {"core"}:
                            total_pure_core += 1
                        elif classifications == {"surrogate"}:
                            total_pure_surrogate += 1

    n = len(trials)
    # Count unique composite text patterns
    from collections import Counter
    common = Counter(composite_texts).most_common(20)

    return {
        "total_trials": n,
        "total_with_composite": total_composite,
        "pct_composite": round(100 * total_composite / n, 1) if n else 0,
        "total_mixed": total_mixed,
        "pct_mixed": round(100 * total_mixed / max(total_composite, 1), 1),
        "total_pure_core": total_pure_core,
        "total_pure_surrogate": total_pure_surrogate,
        "common_composites": [{"text": t, "count": c} for t, c in common],
    }


def load_trials(csv_path=None):
    if csv_path is None:
        csv_path = os.path.join(SHARED_DIR, "cv_trials.csv")
    with open(csv_path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save_outputs(intervention_result, composite_result):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(os.path.join(OUTPUT_DIR, "intervention_landscape.json"), "w") as f:
        json.dump(intervention_result, f, indent=2)
    with open(os.path.join(OUTPUT_DIR, "composite_analysis.json"), "w") as f:
        json.dump(composite_result, f, indent=2)


def main():
    print("Loading CV trials...", file=sys.stderr)
    trials = load_trials()
    print(f"Loaded {len(trials)} trials", file=sys.stderr)

    print("Analyzing intervention landscape (Angle 8)...", file=sys.stderr)
    intervention_result = analyze_intervention_landscape(trials)
    for itype, stats in sorted(intervention_result["by_type"].items(), key=lambda x: -x[1]["count"]):
        print(f"  {itype}: {stats['count']} trials, gap={stats['mean_gap_score']}, core={stats['pct_with_core']}%", file=sys.stderr)

    print("Analyzing composite endpoints (Angle 11)...", file=sys.stderr)
    composite_result = analyze_composites(trials)
    print(f"  Composites: {composite_result['total_with_composite']} ({composite_result['pct_composite']}%)", file=sys.stderr)
    print(f"  Mixed relevance: {composite_result['total_mixed']} ({composite_result['pct_mixed']}%)", file=sys.stderr)

    save_outputs(intervention_result, composite_result)
    print("Done.", file=sys.stderr)


if __name__ == "__main__":
    main()
