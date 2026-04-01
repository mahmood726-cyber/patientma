"""Angle 6: Geographic disparities in CV trial distribution."""
import csv
import json
import os
import sys

csv.field_size_limit(10 * 1024 * 1024)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "shared"))

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")

# WHO region mapping (major trial countries)
WHO_REGIONS = {
    "United States": "Americas", "Canada": "Americas", "Brazil": "Americas", "Mexico": "Americas",
    "Argentina": "Americas", "Colombia": "Americas", "Chile": "Americas", "Peru": "Americas",
    "United Kingdom": "Europe", "Germany": "Europe", "France": "Europe", "Italy": "Europe",
    "Spain": "Europe", "Netherlands": "Europe", "Belgium": "Europe", "Sweden": "Europe",
    "Denmark": "Europe", "Norway": "Europe", "Finland": "Europe", "Switzerland": "Europe",
    "Austria": "Europe", "Poland": "Europe", "Czech Republic": "Europe", "Hungary": "Europe",
    "Greece": "Europe", "Portugal": "Europe", "Ireland": "Europe", "Romania": "Europe",
    "Turkey": "Europe", "Russia": "Europe", "Ukraine": "Europe",
    "China": "Western Pacific", "Japan": "Western Pacific", "South Korea": "Western Pacific",
    "Australia": "Western Pacific", "Taiwan": "Western Pacific", "New Zealand": "Western Pacific",
    "India": "South-East Asia", "Thailand": "South-East Asia", "Indonesia": "South-East Asia",
    "South Africa": "Africa", "Egypt": "Eastern Mediterranean", "Iran": "Eastern Mediterranean",
    "Saudi Arabia": "Eastern Mediterranean", "Israel": "Europe",
    "Pakistan": "Eastern Mediterranean",
}

# Total CV deaths by WHO region (WHO GHE 2019, approximate)
CV_MORTALITY_BY_REGION = {
    "Americas": 1_200_000,
    "Europe": 3_900_000,
    "Western Pacific": 6_100_000,
    "South-East Asia": 4_600_000,
    "Eastern Mediterranean": 1_700_000,
    "Africa": 1_300_000,
}


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


def analyze_geographic_disparities(location_data, classified_data):
    """Angle 6: trial distribution by country and WHO region vs. CV burden."""
    # Build classified lookup
    classified_by_id = {t["nct_id"]: t for t in classified_data}

    by_country = {}
    by_region = {}
    total_with_location = 0

    for row in location_data:
        countries_str = row.get("countries", "")
        if not countries_str:
            continue
        total_with_location += 1
        countries = [c.strip() for c in countries_str.split("|") if c.strip()]

        classified = classified_by_id.get(row["nct_id"], {})
        gap = _to_float(classified.get("gap_score"), 1.0)
        core = _to_int(classified.get("core_count"))

        for country in countries:
            if country not in by_country:
                by_country[country] = {"trial_count": 0, "gap_sum": 0.0, "core_any": 0}
            by_country[country]["trial_count"] += 1
            by_country[country]["gap_sum"] += gap
            by_country[country]["core_any"] += 1 if core > 0 else 0

            region = WHO_REGIONS.get(country, "Other")
            if region not in by_region:
                by_region[region] = {"trial_count": 0, "gap_sum": 0.0, "core_any": 0, "countries": set()}
            by_region[region]["trial_count"] += 1
            by_region[region]["gap_sum"] += gap
            by_region[region]["core_any"] += 1 if core > 0 else 0
            by_region[region]["countries"].add(country)

    # Compute summary stats
    for country, data in by_country.items():
        n = data["trial_count"]
        data["mean_gap_score"] = round(data["gap_sum"] / n, 4) if n else 1.0
        data["pct_with_core"] = round(100 * data["core_any"] / n, 1) if n else 0
        del data["gap_sum"]
        del data["core_any"]

    for region, data in by_region.items():
        n = data["trial_count"]
        data["mean_gap_score"] = round(data["gap_sum"] / n, 4) if n else 1.0
        data["pct_with_core"] = round(100 * data["core_any"] / n, 1) if n else 0
        data["n_countries"] = len(data["countries"])
        data["countries"] = sorted(data["countries"])
        del data["gap_sum"]
        del data["core_any"]

        cv_deaths = CV_MORTALITY_BY_REGION.get(region, 0)
        if cv_deaths > 0:
            data["cv_deaths_total"] = cv_deaths
            data["trials_per_million_cv_deaths"] = round(data["trial_count"] / (cv_deaths / 1_000_000), 1)
        else:
            data["trials_per_million_cv_deaths"] = 0

    # Top 20 countries
    top_countries = sorted(by_country.items(), key=lambda x: -x[1]["trial_count"])[:20]

    return {
        "total_with_location": total_with_location,
        "total_countries": len(by_country),
        "by_country": by_country,
        "by_region": by_region,
        "top_20_countries": [{"country": k, **v} for k, v in top_countries],
    }


def load_locations(path=None):
    if path is None:
        path = os.path.join(os.path.dirname(__file__), "..", "shared", "cv_trial_locations.csv")
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_classified(path=None):
    if path is None:
        path = os.path.join(os.path.dirname(__file__), "..", "OutcomeGap", "outputs", "classified_trials.csv")
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save_output(result):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(os.path.join(OUTPUT_DIR, "geographic.json"), "w") as f:
        json.dump(result, f, indent=2)


def main():
    print("Loading data...", file=sys.stderr)
    locations = load_locations()
    classified = load_classified()
    print(f"Loaded {len(locations)} locations + {len(classified)} classified", file=sys.stderr)

    print("Analyzing geographic disparities (Angle 6)...", file=sys.stderr)
    result = analyze_geographic_disparities(locations, classified)
    print(f"  Countries: {result['total_countries']}", file=sys.stderr)
    print(f"  With location: {result['total_with_location']}", file=sys.stderr)

    save_output(result)
    print("Done.", file=sys.stderr)


if __name__ == "__main__":
    main()
