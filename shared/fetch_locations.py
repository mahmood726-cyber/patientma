"""Fetch location/country data for CV trials from CT.gov API v2."""
import csv
import json
import os
import sys
import time
import urllib.request
import urllib.parse

csv.field_size_limit(2**30)

BASE_URL = "https://clinicaltrials.gov/api/v2/studies"
SHARED_DIR = os.path.dirname(os.path.abspath(__file__))
LOCATIONS_PATH = os.path.join(SHARED_DIR, "cv_trial_locations.csv")


def fetch_locations_for_ids(nct_ids):
    """Fetch location countries for a batch of NCT IDs. Returns dict of nct_id -> countries list."""
    id_str = ",".join(nct_ids)
    params = {
        "filter.ids": id_str,
        "fields": "protocolSection.identificationModule.nctId,protocolSection.contactsLocationsModule.locations",
        "pageSize": "1000",
        "format": "json",
    }
    url = BASE_URL + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    results = {}
    for study in data.get("studies", []):
        nct_id = study.get("protocolSection", {}).get("identificationModule", {}).get("nctId", "")
        locations = study.get("protocolSection", {}).get("contactsLocationsModule", {}).get("locations", [])
        countries = list(set(loc.get("country", "") for loc in locations if loc.get("country")))
        results[nct_id] = countries
    return results


def fetch_all_locations(csv_path=None, batch_size=100):
    """Fetch locations for all trials in cv_trials.csv."""
    if csv_path is None:
        csv_path = os.path.join(SHARED_DIR, "cv_trials.csv")

    with open(csv_path, "r", encoding="utf-8") as f:
        nct_ids = [row["nct_id"] for row in csv.DictReader(f)]

    print(f"Fetching locations for {len(nct_ids)} trials in batches of {batch_size}...", file=sys.stderr)
    all_locations = {}

    for i in range(0, len(nct_ids), batch_size):
        batch = nct_ids[i:i + batch_size]
        try:
            batch_result = fetch_locations_for_ids(batch)
            all_locations.update(batch_result)
        except Exception as e:
            print(f"  Error at batch {i//batch_size}: {e}", file=sys.stderr)

        page = i // batch_size + 1
        total_pages = (len(nct_ids) + batch_size - 1) // batch_size
        if page % 50 == 0 or page == total_pages:
            print(f"  Page {page}/{total_pages}: {len(all_locations)} locations fetched", file=sys.stderr)
        time.sleep(0.2)

    return all_locations


def save_locations_csv(all_locations, path=LOCATIONS_PATH):
    """Save locations to CSV: nct_id, countries (pipe-delimited)."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["nct_id", "countries"])
        for nct_id, countries in sorted(all_locations.items()):
            writer.writerow([nct_id, "|".join(countries)])


def load_locations_csv(path=LOCATIONS_PATH):
    """Load locations CSV. Returns list of dicts."""
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()

    if os.path.exists(LOCATIONS_PATH) and not args.refresh:
        print(f"Locations CSV exists at {LOCATIONS_PATH}. Use --refresh.", file=sys.stderr)
        return

    all_locations = fetch_all_locations()
    save_locations_csv(all_locations)
    print(f"Saved {len(all_locations)} trial locations to {LOCATIONS_PATH}", file=sys.stderr)


if __name__ == "__main__":
    main()
