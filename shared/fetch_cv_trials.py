"""Fetch all cardiovascular trials from ClinicalTrials.gov API v2 into a CSV."""
import csv
import json
import os
import sys
import time
import urllib.request
import urllib.parse
from datetime import datetime

BASE_URL = "https://clinicaltrials.gov/api/v2/studies"

FIELDS = [
    "nct_id", "title", "status", "conditions", "phase", "enrollment",
    "sponsor_name", "sponsor_class", "primary_outcomes", "secondary_outcomes",
    "eligibility_criteria", "start_date", "completion_date", "has_results",
    "interventions",
]

CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cv_trials.csv")
META_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cv_trials_meta.json")


def build_query_url(page_token=None):
    """Build the CT.gov API v2 query URL for cardiovascular studies."""
    params = {
        "query.cond": "cardiovascular",
        "pageSize": "1000",
        "countTotal": "true",
        "format": "json",
    }
    if page_token:
        params["pageToken"] = page_token
    return BASE_URL + "?" + urllib.parse.urlencode(params)


def safe_get(d, *keys, default=""):
    """Safely navigate nested dicts, returning default if any key is missing."""
    current = d
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key, None)
        if current is None:
            return default
    return current


def parse_study_row(study):
    """Extract a flat row dict from a CT.gov API v2 study object."""
    proto = study.get("protocolSection", {})
    ident = proto.get("identificationModule", {})
    status_mod = proto.get("statusModule", {})
    cond_mod = proto.get("conditionsModule", {})
    design = proto.get("designModule", {})
    sponsor_mod = proto.get("sponsorCollaboratorsModule", {})
    outcomes_mod = proto.get("outcomesModule", {})
    elig_mod = proto.get("eligibilityModule", {})
    arms_mod = proto.get("armsInterventionsModule", {})

    conditions = cond_mod.get("conditions", [])
    phases = design.get("phases", [])
    enrollment = safe_get(design, "enrollmentInfo", "count", default=0)
    sponsor_name = safe_get(sponsor_mod, "leadSponsor", "name", default="")
    sponsor_class = safe_get(sponsor_mod, "leadSponsor", "class", default="")

    primary = outcomes_mod.get("primaryOutcomes", [])
    secondary = outcomes_mod.get("secondaryOutcomes", [])
    primary_measures = [o.get("measure", "") for o in primary if o.get("measure")]
    secondary_measures = [o.get("measure", "") for o in secondary if o.get("measure")]

    interventions_list = arms_mod.get("interventions", [])
    intervention_names = [i.get("name", "") for i in interventions_list if i.get("name")]

    return {
        "nct_id": ident.get("nctId", ""),
        "title": ident.get("briefTitle", ""),
        "status": status_mod.get("overallStatus", ""),
        "conditions": "|".join(conditions),
        "phase": "|".join(phases),
        "enrollment": enrollment if isinstance(enrollment, int) else 0,
        "sponsor_name": sponsor_name,
        "sponsor_class": sponsor_class,
        "primary_outcomes": "|".join(primary_measures),
        "secondary_outcomes": "|".join(secondary_measures),
        "eligibility_criteria": elig_mod.get("eligibilityCriteria", ""),
        "start_date": safe_get(status_mod, "startDateStruct", "date", default=""),
        "completion_date": safe_get(status_mod, "completionDateStruct", "date", default=""),
        "has_results": study.get("hasResults", False),
        "interventions": "|".join(intervention_names),
    }


def fetch_all_cv_trials(progress=True):
    """Fetch all CV trials from CT.gov API v2 with pagination. Returns list of row dicts."""
    rows = []
    page_token = None
    total = None
    page = 0

    while True:
        url = build_query_url(page_token=page_token)
        with urllib.request.urlopen(url) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        if total is None:
            total = data.get("totalCount", "?")

        studies = data.get("studies", [])
        for study in studies:
            rows.append(parse_study_row(study))

        page += 1
        if progress:
            print(f"  Page {page}: {len(rows)} / {total} studies fetched", file=sys.stderr)

        page_token = data.get("nextPageToken")
        if not page_token:
            break
        time.sleep(0.3)

    return rows, total


def save_csv(rows, path=CSV_PATH):
    """Write rows to CSV."""
    if not rows:
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def save_meta(total, row_count, path=META_PATH):
    """Write fetch metadata JSON."""
    meta = {
        "fetch_date": datetime.now().isoformat(),
        "api_total_count": total,
        "rows_saved": row_count,
        "query": "cardiovascular",
        "source": "ClinicalTrials.gov API v2",
    }
    with open(path, "w") as f:
        json.dump(meta, f, indent=2)


def main():
    """CLI entry point: fetch CV trials and save to CSV."""
    import argparse
    parser = argparse.ArgumentParser(description="Fetch CV trials from ClinicalTrials.gov")
    parser.add_argument("--refresh", action="store_true", help="Force re-download even if CSV exists")
    args = parser.parse_args()

    if os.path.exists(CSV_PATH) and not args.refresh:
        print(f"CSV already exists at {CSV_PATH}. Use --refresh to re-download.", file=sys.stderr)
        return

    print("Fetching all cardiovascular trials from ClinicalTrials.gov...", file=sys.stderr)
    rows, total = fetch_all_cv_trials()
    save_csv(rows)
    save_meta(total, len(rows))
    print(f"Done: {len(rows)} trials saved to {CSV_PATH}", file=sys.stderr)


if __name__ == "__main__":
    main()
