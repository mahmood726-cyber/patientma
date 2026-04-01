# Multi-Persona Review: PatientMA 12-Angle Suite
### Date: 2026-04-01
### Summary: 5 P0, 19 P1, 14 P2

---

## P0 — Critical (Must Fix)

- **SEC-P0-1** [Security]: XSS in MegaDashboard — no `escapeHtml` function exists. DATA-derived strings rendered via innerHTML in tables (line ~2462) and tooltips (lines ~1664, 1745, 1931) without escaping.
  - Fix: Add `escapeHtml()` function and apply to all DATA-derived strings in innerHTML/tooltip callbacks.

- **SEC-P0-2** [Security]: XSS in MegaDashboard tooltip innerHTML — hit-test callbacks embed `r.label`, `r.name` directly into HTML strings.
  - Fix: Same as SEC-P0-1 — covered by adding `escapeHtml()`.

- **DOM-P0-1** [Domain]: AF elderly prevalence 60% is ~50% too high — registries show 35-45% >75, not 60%. (`analyze_tf_angles.py:22`)
  - Fix: Change AF to 0.42, HF to 0.45. Rerun analysis.

- **DOM-P0-2** [Domain]: Israel misclassified as Eastern Mediterranean in WHO region mapping — should be WHO Europe. (`analyze_geographic.py:28`)
  - Fix: Move Israel to "Europe" in WHO_REGIONS dict.

- **DOM-P0-3** [Domain]: CV_MORTALITY_BY_REGION Europe figure 4.2M is ~8% inflated vs WHO GHE 2019 (should be ~3.9M). Comment says "per million population" but values are absolute totals. (`analyze_geographic.py:32-38`)
  - Fix: Correct Europe to 3,900,000. Fix comment to "total CV deaths by WHO region".

## P1 — Important (Should Fix)

- **ENG-P0-1** [Engineering]: `chi_squared_2x2` ZeroDivisionError when any row/column marginal is zero. (`stats_utils.py:81`)
  - Fix: Add zero-marginal guard before division.

- **STAT-P1-1** [Stats]: Segmented regression fits independent segments without continuity — non-standard for change-point analysis; BIC undercounts by 1 parameter. (`stats_utils.py:328-338`)
  - Fix: Document as "discontinuous piecewise regression" or enforce continuity.

- **STAT-P1-2** [Stats]: Segmented regression fallback uses entire dataset OLS for failed small segment, inflating SSE. (`stats_utils.py:328-331`)
  - Fix: Set SSE=0 for single-point segments.

- **STAT-P1-3** [Stats]: Mann-Whitney U missing continuity correction. (`stats_utils.py:171`)
  - Fix: Use `z = (abs(u_stat - mu) - 0.5) / sigma`.

- **STAT-P1-4** [Stats]: Logistic regression has fixed lr=0.1, only 50 iterations, no convergence check. (`stats_utils.py:361-404`)
  - Fix: Increase max_iter, add convergence check, document feature scaling requirement.

- **STAT-P1-5** [Stats]: Gap score denominator mixes unique core/surrogate counts with raw unclassified count. (`outcome_classifier.py:116-119`)
  - Fix: Document the counting methodology explicitly; consider all-raw or all-unique.

- **STAT-P1-8** [Stats]: "older than" / "greater than" regex incorrectly sets max_age instead of min_age. (`analyze_fit.py:52-59`)
  - Fix: Remove these patterns from max_age section or add context-aware parsing.

- **STAT-P1-10** [Stats]: `if gi:` drops valid GI=0 values — known anti-pattern. (`analyze_transparency.py:67-69`)
  - Fix: Change to `if gi is not None:` with `_to_int(default=None)`.

- **SEC-P1-1** [Security]: CSV formula injection missing in MegaDashboard export — `csvEsc()` has no guard. (`dashboard.html:1961-1968`)
  - Fix: Add formula guard matching OutcomeGap pattern.

- **SEC-P1-2** [Security]: CSV formula injection missing + no field escaping in TrialFit export. (`TrialFit/dashboard.html:1320-1375`)
  - Fix: Implement proper CSV escaping + formula guard.

- **SEC-P1-3** [Security]: No rate limiting on Evidence app CT.gov API calls. (`Evidence/index.html:2014`)
  - Fix: Add 3-second cooldown between searches.

- **SEC-P1-4** [Security]: No HTTP timeout in Python fetch scripts — can hang indefinitely. (`fetch_cv_trials.py:103`, `fetch_locations.py:27`)
  - Fix: Add `timeout=30` to `urlopen()`.

- **DOM-P1-1** [Domain]: ACS COMET missing stent thrombosis + bleeding as core safety outcomes. (`comet_outcomes.json`)
  - Fix: Add stent thrombosis and BARC/TIMI bleeding keywords to ACS core.

- **DOM-P1-4** [Domain]: Drug classifier suffixes "mab", "nib" match common English substrings (ambulatory, inhibitor). (`intervention_classifier.py`)
  - Fix: Use word-boundary matching or longer suffixes.

- **ENG-P1-5** [Engineering]: `compute_era` duplicated in 3 files. (`analyze_gaps.py:25`, `analyze_fit.py:206`, `analyze_tf_angles.py:35`)
  - Fix: Consolidate into shared module.

- **ENG-P1-6** [Engineering]: `_to_int`/`_to_float` helpers duplicated in 3 files with inconsistent defaults. (`analyze_transparency.py`, `analyze_geographic.py`, `analyze_evolution.py`)
  - Fix: Consolidate into shared module.

- **UX-P0-1** [UX]: Canvas elements missing `role="img"` in Evidence app. (`index.html:1145`)
  - Fix: Add `role="img"`.

- **UX-P0-2** [UX]: No `<h1>` in OutcomeGap + TrialFit dashboards. (`OutcomeGap/dashboard.html:498`, `TrialFit/dashboard.html:440`)
  - Fix: Change title `<div>` to `<h1>`.

## P2 — Minor (Nice to Fix)

- **STAT-P2-1** [Stats]: Wilson-Hilferty poor for df=1; exact formula available. (`stats_utils.py:41-56`)
- **STAT-P2-3** [Stats]: Keyword substring matching can produce false positives. (`outcome_classifier.py:35`)
- **STAT-P2-4** [Stats]: "defined as" composite pattern high false-positive rate. (`composite_detector.py:12`)
- **STAT-P2-5** [Stats]: Component splitting breaks on parenthetical lists. (`composite_detector.py:28`)
- **STAT-P1-7** [Stats]: Representation score hardcoded to 10/15. (`analyze_fit.py:241`)
- **SEC-P2-1** [Security]: No localStorage schema validation in Evidence app. (`index.html:1312`)
- **SEC-P2-2** [Security]: Missing BOM prefix in MegaDashboard + TrialFit CSV exports.
- **SEC-P2-3** [Security]: `csv.field_size_limit(2**30)` excessively large — use 10MB.
- **UX-P1-1** [UX]: Modals lack Tab focus trap in Evidence + MegaDashboard.
- **UX-P1-2** [UX]: Dark mode `--text-muted` fails WCAG AA in OutcomeGap + TrialFit.
- **UX-P1-3** [UX]: OutcomeGap badge text fails WCAG AA contrast.
- **UX-P2-1** [UX]: Light mode card labels slightly below AA contrast.
- **DOM-P2-1** [Domain]: HF missing "worsening HF event" keyword. (`comet_outcomes.json`)
- **DOM-P2-2** [Domain]: Composite detector misses "first occurrence of" pattern. (`composite_detector.py`)

## False Positive Watch
- Gap score counting unique COMET items is BY DESIGN (not a bug)
- `_detect_condition()` first-match priority is intentional
- Yates correction in chi-squared is intentional for 2x2
- Representation score = 10 is a known placeholder (flagged as P2)
