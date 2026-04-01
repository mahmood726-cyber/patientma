"""Angle 4: Temporal evolution of patient-centricity with change-point detection."""
import csv
import json
import os
import sys

csv.field_size_limit(2**30)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "shared"))
from stats_utils import segmented_regression

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")

POLICY_EVENTS = [
    {"year": 2006, "label": "FDA PRO Guidance draft"},
    {"year": 2009, "label": "FDA PRO Guidance final"},
    {"year": 2010, "label": "COMET Initiative founded"},
    {"year": 2015, "label": "SPIRIT-PRO extension"},
    {"year": 2017, "label": "FDA PFDD guidance series"},
    {"year": 2021, "label": "ICH E8(R1) revision"},
]


def _to_float(val, default=None):
    if val is None or val == "" or val == "None":
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def _to_int(val, default=None):
    if val is None or val == "" or val == "None":
        return default
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return default


def _to_bool_str(val):
    return str(val).lower() in ("true", "1", "yes")


def compute_yearly_trends(trials):
    """Compute year-level time series of patient-centricity metrics."""
    yearly = {}

    for t in trials:
        start = t.get("start_date", "")
        if not start or len(start) < 4:
            continue
        try:
            year = int(start[:4])
        except ValueError:
            continue
        if year < 1990 or year > 2026:
            continue

        if year not in yearly:
            yearly[year] = {
                "count": 0, "gap_sum": 0.0, "core_any": 0, "pro_any": 0,
                "gi_values": [], "age_cutoff_below_75": 0, "sex_restricted": 0,
            }
        y = yearly[year]
        y["count"] += 1

        gap = _to_float(t.get("gap_score"), 1.0)
        y["gap_sum"] += gap

        core = _to_int(t.get("core_count"), 0)
        y["core_any"] += 1 if core > 0 else 0

        has_pro = _to_bool_str(t.get("has_PRO", "False"))
        y["pro_any"] += 1 if has_pro else 0

        gi = _to_int(t.get("generalizability_index"))
        if gi is not None:
            y["gi_values"].append(gi)

        max_age = _to_int(t.get("max_age"))
        if max_age is not None and max_age < 75:
            y["age_cutoff_below_75"] += 1

        sex = t.get("sex", "both")
        if sex in ("male", "female"):
            y["sex_restricted"] += 1

    # Build sorted year list
    years_sorted = sorted(yearly.keys())
    result_years = []
    for yr in years_sorted:
        y = yearly[yr]
        n = y["count"]
        result_years.append({
            "year": yr,
            "count": n,
            "mean_gap_score": round(y["gap_sum"] / n, 4) if n else 1.0,
            "pct_with_core": round(100 * y["core_any"] / n, 1) if n else 0,
            "pct_with_PRO": round(100 * y["pro_any"] / n, 1) if n else 0,
            "mean_gi": round(sum(y["gi_values"]) / len(y["gi_values"]), 1) if y["gi_values"] else None,
            "pct_age_cutoff_below_75": round(100 * y["age_cutoff_below_75"] / n, 1) if n else 0,
            "pct_sex_restricted": round(100 * y["sex_restricted"] / n, 1) if n else 0,
            "ma5_gap_score": None,  # Filled below
        })

    # 5-year moving average for gap score
    gap_values = [yr["mean_gap_score"] for yr in result_years]
    for i in range(len(result_years)):
        start_idx = max(0, i - 2)
        end_idx = min(len(gap_values), i + 3)
        window = gap_values[start_idx:end_idx]
        result_years[i]["ma5_gap_score"] = round(sum(window) / len(window), 4) if window else None

    return {"years": result_years, "policy_events": POLICY_EVENTS}


def detect_changepoints(years, values, max_breakpoints=2):
    """Apply segmented regression to detect change points in a time series."""
    if len(years) < 5:
        return {"n_breakpoints": 0, "breakpoints": [], "segments": []}
    # Constant series has no meaningful breakpoints (SSE~0 makes BIC degenerate)
    if len(set(values)) <= 1:
        return {"n_breakpoints": 0, "breakpoints": [], "segments": []}
    return segmented_regression(years, values, max_breakpoints=max_breakpoints)


def load_merged_data():
    """Load and merge OutcomeGap classified + TrialFit results + shared CSV for full metrics."""
    og_path = os.path.join(os.path.dirname(__file__), "..", "OutcomeGap", "outputs", "classified_trials.csv")
    tf_path = os.path.join(os.path.dirname(__file__), "..", "TrialFit", "outputs", "trial_fit_results.csv")
    cv_path = os.path.join(os.path.dirname(__file__), "..", "shared", "cv_trials.csv")

    with open(og_path, "r", encoding="utf-8") as f:
        og_data = {r["nct_id"]: r for r in csv.DictReader(f)}
    with open(tf_path, "r", encoding="utf-8") as f:
        tf_data = {r["nct_id"]: r for r in csv.DictReader(f)}
    # Load start_date from shared CV trials CSV
    cv_dates = {}
    with open(cv_path, "r", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            cv_dates[r["nct_id"]] = r.get("start_date", "")

    merged = []
    for nct_id, og in og_data.items():
        tf = tf_data.get(nct_id, {})
        row = {**og}
        row["generalizability_index"] = tf.get("generalizability_index", "")
        row["max_age"] = tf.get("max_age", "")
        row["sex"] = tf.get("sex", "both")
        row["start_date"] = cv_dates.get(nct_id, "")
        merged.append(row)
    return merged


def save_outputs(trends, changepoints):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(os.path.join(OUTPUT_DIR, "yearly_trends.json"), "w") as f:
        json.dump(trends, f, indent=2)
    with open(os.path.join(OUTPUT_DIR, "changepoints.json"), "w") as f:
        json.dump(changepoints, f, indent=2)


def main():
    print("Loading merged data...", file=sys.stderr)
    data = load_merged_data()
    print(f"Loaded {len(data)} merged trial records", file=sys.stderr)

    print("Computing yearly trends (Angle 4)...", file=sys.stderr)
    trends = compute_yearly_trends(data)
    print(f"  Years covered: {trends['years'][0]['year']} - {trends['years'][-1]['year']}", file=sys.stderr)

    # Change-point detection on gap score
    years = [yr["year"] for yr in trends["years"] if yr["count"] >= 50]
    gap_scores = [yr["mean_gap_score"] for yr in trends["years"] if yr["count"] >= 50]
    print("Detecting change points...", file=sys.stderr)
    cp_gap = detect_changepoints(years, gap_scores)
    print(f"  Gap score breakpoints: {cp_gap.get('breakpoints', [])}", file=sys.stderr)

    core_pcts = [yr["pct_with_core"] for yr in trends["years"] if yr["count"] >= 50]
    cp_core = detect_changepoints(years, core_pcts)

    changepoints = {
        "gap_score": cp_gap,
        "pct_with_core": cp_core,
    }

    save_outputs(trends, changepoints)
    print("Done.", file=sys.stderr)


if __name__ == "__main__":
    main()
