"""Build the unified 12-angle MegaDashboard by embedding all analysis outputs."""
import json
import os
import sys

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")


def load_json(path):
    """Load a JSON file, return empty dict if not found."""
    full_path = os.path.join(BASE_DIR, path)
    if not os.path.exists(full_path):
        print(f"  WARNING: {path} not found, using empty data", file=sys.stderr)
        return {}
    with open(full_path, "r", encoding="utf-8") as f:
        return json.load(f)


def build():
    """Load all outputs and embed into dashboard HTML."""
    data = {
        "outcomegap_summary": load_json("OutcomeGap/outputs/summary.json"),
        "outcomegap_top_outcomes": load_json("OutcomeGap/outputs/top_outcomes.json"),
        "intervention_landscape": load_json("OutcomeGap/outputs/intervention_landscape.json"),
        "composite_analysis": load_json("OutcomeGap/outputs/composite_analysis.json"),
        "trialfit_summary": load_json("TrialFit/outputs/summary.json"),
        "sex_gap": load_json("TrialFit/outputs/sex_gap.json"),
        "elderly_exclusion": load_json("TrialFit/outputs/elderly_exclusion.json"),
        "sponsor_comparison": load_json("Transparency/outputs/sponsor_comparison.json"),
        "transparency": load_json("Transparency/outputs/transparency.json"),
        "geographic": load_json("Transparency/outputs/geographic.json"),
        "publication_gap": load_json("Transparency/outputs/publication_gap.json"),
        "yearly_trends": load_json("Evolution/outputs/yearly_trends.json"),
        "changepoints": load_json("Evolution/outputs/changepoints.json"),
    }

    data_json = json.dumps(data)

    dashboard_path = os.path.join(os.path.dirname(__file__), "dashboard.html")
    with open(dashboard_path, "r", encoding="utf-8") as f:
        html = f.read()

    html = html.replace("const DATA = {};", f"const DATA = {data_json};")

    with open(dashboard_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Dashboard built with {len(data)} data sections", file=sys.stderr)
    return dashboard_path


if __name__ == "__main__":
    build()
