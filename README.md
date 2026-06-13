# PatientMA

Patient-centred meta-analysis tooling for cardiovascular trials. A suite of
small, dependency-free Python analyses plus offline single-file HTML dashboards
that measure how well trials and meta-analyses address outcomes that matter to
patients.

## Pilots

- **OutcomeGap** — classifies trial outcome measures against a COMET-derived
  core-outcome taxonomy and computes a patient-relevance gap score
  (`1 - core/total`).
- **TrialFit** — parses eligibility criteria (age, sex, comorbidity exclusions,
  functional status) and computes a 0–100 generalizability index.
- **Transparency** — results-posting rates and geographic representation.
- **Evolution** — yearly trends and segmented-regression changepoints.
- **Evidence** — eligibility parsing and a query-builder dashboard.

## Shared library

`shared/` holds the reusable pieces:

- `stats_utils.py` — pure-Python statistics (normal/chi-squared CDF, Acklam
  inverse-normal, 2×2 chi-squared with Yates correction, Cramér's V,
  Mann-Whitney U with tie correction, segmented regression, simple logistic
  regression). No numpy/scipy dependency.
- `outcome_classifier.py` — COMET taxonomy classification.
- `intervention_classifier.py`, `composite_detector.py` — intervention typing
  and composite-endpoint decomposition.

## Tests

```
python run_tests.py
```

Runs the pytest suite across all pilots (167 tests at last sync).

## Layout

Each pilot directory contains its `analyze_*.py` engine, a `test_*.py` suite,
and an offline `dashboard.html` / `index.html`. The HTML dashboards are fully
self-contained (no external CDN).
