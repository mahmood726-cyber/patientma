# Evolution of Patient-Centricity in Cardiovascular Trials and a Live Evidence-Matching Tool: A 36-Year Registry Analysis

**Target journal:** BMJ Evidence-Based Medicine (Original Research)

**Authors:** [AUTHOR], [CO-AUTHORS]

**Affiliations:** [AFFILIATIONS]

**Corresponding author:** [AUTHOR], [EMAIL]

---

## Abstract

**Objective:** To track the temporal evolution of patient-centricity in cardiovascular trials over 36 years and to present a live patient-trial matching tool (CardioEvidence) built on these data.

**Design:** Longitudinal registry analysis with change-point detection.

**Data source:** All 65,383 cardiovascular trials on ClinicalTrials.gov (1990–2026), with yearly metrics for outcome gap score, core outcome adoption, PRO inclusion, generalizability index, and age exclusion rates.

**Main outcome measures:** Annual outcome gap score (0=fully patient-centered, 1=no core outcomes) with 5-year moving average; structural breakpoints detected by segmented regression; policy event overlay.

**Results:** The gap score improved from 0.99 in 1990 to a nadir of 0.93 in 2005, then reversed, reaching 0.95 by 2026. Change-point analysis identified two structural breakpoints: 1998 (end of rapid improvement phase; slope −0.0028/year 1990–1998 flattened to −0.0004/year) and 2011 (onset of deterioration; slope reversed to +0.0008/year). The 1998 breakpoint coincided with the emergence of large cardiovascular outcome trials (HOPE, CAPRICORN, RALES); the 2011 breakpoint aligned with the founding of the COMET Initiative — paradoxically, the start of worsening.

Core outcome adoption rose from 2.0% (1990) to 15.9% (2005), then plateaued at 13–15%. PRO inclusion increased modestly from 0% (1990) to 9.3% (2026 year-to-date). The generalizability index declined from 84.8 (1990) to 80.5 (2026), driven by increasing age exclusions (4.0% in 1990 to 40.1% in 2026).

Six major policy interventions (FDA PRO Guidance 2006/2009, COMET Initiative 2010, SPIRIT-PRO 2015, FDA PFDD 2017, ICH E8(R1) 2021) left no detectable imprint on the gap score trajectory.

We also present CardioEvidence, a live browser-based tool (2,123 lines) that matches individual patients to relevant cardiovascular trials based on condition, age, comorbidities, and outcome preferences, returning patient-centricity scores for each match.

**Conclusions:** After initial improvement (1990–2005), patient-centricity in cardiovascular trials has stagnated or worsened, with no detectable impact from major policy initiatives. Structural incentives beyond guidelines are needed. CardioEvidence provides a proof-of-concept for translating registry-level findings into individual-level trial matching.

---

## Introduction

The patient-centricity of clinical trials — the degree to which they measure outcomes that matter to patients, include populations that reflect real-world practice, and report results transparently — is a growing concern in evidence-based medicine.[1] Our companion analyses (Papers 1–3) demonstrated that only 13.8% of cardiovascular trials measure COMET core outcomes, 38.5% exclude elderly adults, and 96.1% of enrollment occurs in trials without posted results. These cross-sectional findings raise a critical question: is the situation improving, stable, or worsening?

We addressed this by constructing a 36-year time series (1990–2026) of patient-centricity metrics across all 65,383 cardiovascular trials registered on ClinicalTrials.gov, applying change-point analysis to identify structural shifts, and overlaying major policy events to assess their impact.

Additionally, we present CardioEvidence — a live, browser-based tool that translates these registry-level findings into individual-level utility by matching patients to relevant cardiovascular trials based on their clinical profile and outcome preferences.

## Methods

### Yearly time series construction

For each year from 1990 to 2026, we computed: (1) mean outcome gap score, (2) proportion with at least one core outcome, (3) proportion with PRO, (4) mean generalizability index, (5) proportion excluding adults ≥75, and (6) proportion sex-restricted. We also computed a 5-year centered moving average for the gap score to smooth year-to-year variation.

### Change-point detection

We applied segmented regression (piecewise linear regression) to the gap score time series, testing models with 0, 1, 2, and 3 breakpoints and selecting the optimal model by Bayesian Information Criterion (BIC). The segmented regression was implemented as discontinuous piecewise linear regression, fitting independent segments between breakpoints. For single-point segments, sum of squared errors was set to zero.

### Policy event overlay

We identified six major policy events relevant to patient-centered trial design: FDA PRO Guidance (draft 2006, final 2009), COMET Initiative founding (2010), SPIRIT-PRO extension (2015), FDA Patient-Focused Drug Development guidance series (2017), and ICH E8(R1) revision (2021). These were overlaid on the time series to assess temporal association with changes in trajectory.

### CardioEvidence tool

We developed a browser-based patient-trial matching tool (CardioEvidence) that queries the ClinicalTrials.gov API in real time, allowing users to enter a patient profile (age, sex, condition, comorbidities, outcome preferences) and receive a ranked list of matching active trials with patient-centricity scores. The tool is implemented as a single HTML file (2,123 lines) using vanilla JavaScript with no server dependencies.

## Results

### Three-phase evolution

The gap score time series revealed three distinct phases (Figure 1):

**Phase 1: Rapid improvement (1990–1998).** The gap score declined from 0.99 to 0.96 (slope −0.0028/year, P<0.001). Core outcome adoption increased from 2.0% to 9.8%. This phase corresponded to the emergence of landmark cardiovascular outcome trials (HOPE, RALES, 4S) that established clinical events as primary endpoints.

**Phase 2: Plateau (1998–2011).** The gap score was essentially flat (slope −0.0004/year), fluctuating between 0.93 and 0.95. Core outcome adoption stabilized at 13–16%. Trial volume increased dramatically (from 194 in 1998 to 2,261 in 2011), but the proportion measuring patient-relevant outcomes did not keep pace.

**Phase 3: Deterioration (2011–2026).** The gap score reversed direction (slope +0.0008/year), rising from 0.94 to 0.95. While core adoption held at 13–14%, the increasing volume of trials with no core outcomes diluted overall patient-centricity. PRO inclusion continued to improve modestly (5.4% in 2010 to 9.3% in 2026 YTD), but this was insufficient to offset the gap score increase.

**Table 1. Key metrics at breakpoint years and endpoints**

| Year | N trials | Gap score | % Core | % PRO | Mean GI | % Age <75 |
|------|----------|-----------|--------|-------|---------|-----------|
| 1990 | 50 | 0.990 | 2.0 | 0.0 | 84.8 | 4.0 |
| 1998 | 194 | 0.962 | 9.8 | 4.6 | 80.5 | 36.1 |
| 2005 | 1,216 | 0.938 | 15.9 | 8.3 | 80.1 | 38.1 |
| 2011 | 2,261 | 0.942 | 15.6 | 7.4 | 79.7 | 41.1 |
| 2019 | 3,388 | 0.958 | 13.2 | 5.9 | 80.6 | 37.9 |
| 2025 | 3,900 | 0.958 | 13.7 | 7.2 | 80.5 | 38.7 |

### Policy events had no detectable impact

None of the six policy events produced a visible deflection in the gap score trajectory. The FDA PRO Guidance (2009) was followed by stable PRO rates. The COMET Initiative founding (2010) preceded the onset of the deterioration phase. SPIRIT-PRO (2015) and FDA PFDD (2017) left no imprint. ICH E8(R1) (2021) is too recent to assess definitively, but no early signal is visible.

### Generalizability declined as trial volume increased

The mean generalizability index declined from 84.8 (1990) to 80.5 (2026). The proportion of trials excluding adults ≥75 increased dramatically: from 4.0% (1990) to 40.1% (2026 YTD). This suggests that as the cardiovascular trial enterprise scaled, it became more restrictive in its participant selection.

### CardioEvidence: from registry audit to patient tool

To demonstrate the translational potential of this registry analysis, we developed CardioEvidence — a live browser-based tool that matches individual patients to relevant cardiovascular trials. Users enter:
- **Condition:** heart failure, ACS, AF, hypertension, or general CV
- **Demographics:** age, sex
- **Comorbidities:** CKD, diabetes, COPD, etc.
- **Preferences:** importance of core outcomes, PROs, proximity

The tool queries the ClinicalTrials.gov API in real time and returns a ranked list of active, recruiting trials that (1) accept the patient's profile, (2) are geographically accessible, and (3) measure patient-relevant outcomes. Each trial receives a patient-centricity score derived from our gap score methodology. The tool is freely available at [URL] and requires no installation.

## Discussion

### The paradox of improvement without impact

The central finding is paradoxical: despite two decades of policy attention to patient-centered trial design, the gap score has stagnated since 2005 and worsened since 2011. The COMET Initiative, SPIRIT-PRO, and FDA PFDD guidance have not translated into measurable improvement in the proportion of cardiovascular trials measuring core outcomes.

This is not necessarily a failure of these initiatives — the counterfactual (what would have happened without them) is unknowable. But it demonstrates that voluntary guidelines are insufficient to redirect the trial enterprise toward patient-relevant measurement. The contrast between the pre-1998 improvement (driven by paradigm-shifting outcome trials) and the post-2011 stagnation (despite extensive guidance) suggests that field-wide shifts require either landmark empirical evidence or structural incentives (e.g., regulatory requirements), not guidelines alone.

### The volume dilution effect

The transition from Phase 1 to Phase 3 coincided with a 20-fold increase in annual trial registrations (194 in 1998 to 3,900 in 2025). Much of this growth was in early-phase, mechanistic, and surrogate-focused trials that are inherently unlikely to measure core outcomes. The *absolute* number of patient-centered trials increased, but the *proportion* declined as the denominator grew faster.

### Generalizability erosion

The parallel decline in generalizability (rising age exclusion rates from 4% to 40%) adds a second dimension to the problem. Not only are fewer trials measuring what matters, but those that do are increasingly conducted in populations that do not reflect the patients who need the evidence most.

### CardioEvidence: closing the loop

CardioEvidence represents a proof-of-concept for translating registry-level audits into patient-facing tools. By computing patient-centricity scores for active trials, it enables patients and clinicians to preferentially enroll in trials that measure outcomes they care about — creating a demand-side incentive for patient-centered trial design.

### Limitations

(1) ClinicalTrials.gov underrepresents early trials (pre-2005 registration was not mandatory). (2) Segmented regression assumes linear segments; the true trajectory may be nonlinear. (3) Policy impact may operate with a lag longer than our observation period. (4) CardioEvidence depends on real-time API availability and may not capture all active trials.

## Conclusions

After initial improvement (1990–2005), patient-centricity in cardiovascular trials has stagnated, with no detectable impact from six major policy interventions. The gap score has worsened since 2011 despite the founding of the COMET Initiative. Structural incentives — regulatory requirements, funder mandates, ethics committee gatekeeping — are needed to redirect the trial enterprise toward outcomes that matter to patients. CardioEvidence demonstrates that registry-level findings can be translated into patient-facing tools to support informed trial enrollment.

---

## References

1. Williamson PR, Altman DG, Bagley H, et al. The COMET Handbook: version 1.0. Trials. 2017;18(Suppl 3):280.
2. Chalmers I, Glasziou P. Avoidable waste in the production and reporting of research evidence. Lancet. 2009;374:86-89.
3. Calvert M, Kyte D, Mercieca-Bebber R, et al. Guidelines for inclusion of patient-reported outcomes in clinical trial protocols: the SPIRIT-PRO extension. JAMA. 2018;319:483-494.
4. US Food and Drug Administration. Patient-focused drug development: methods to identify what is important to patients. Guidance for industry. 2022.
5. International Council for Harmonisation. ICH E8(R1) General considerations for clinical studies. 2021.

---

## Data availability statement

Analysis code, yearly time series, and CardioEvidence tool available at [REPOSITORY_URL].

## Funding

[FUNDING STATEMENT]

## Competing interests

[COMPETING INTERESTS]

## Word count

Main text: ~3,000 words
