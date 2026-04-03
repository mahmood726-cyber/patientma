# Who Do Cardiovascular Trials Include? Generalizability, Age Exclusions, and Sex Representation Across 65,383 Registered Studies

**Target journal:** JAMA Internal Medicine (Original Investigation)

**Authors:** [AUTHOR], [CO-AUTHORS]

**Affiliations:** [AFFILIATIONS]

**Corresponding author:** [AUTHOR], [EMAIL]

---

## Abstract

**Importance:** Cardiovascular disease disproportionately affects older adults and those with comorbidities, yet trial eligibility criteria may systematically exclude these populations, limiting generalizability.

**Objective:** To quantify the generalizability of cardiovascular trials by examining age exclusions, comorbidity restrictions, and sex-specific design features across the entire ClinicalTrials.gov registry.

**Design, Setting, and Participants:** Cross-sectional audit of all 65,383 cardiovascular trials registered on ClinicalTrials.gov (API v2, queried 1 April 2026). We extracted eligibility criteria, age limits, and study design features.

**Main Outcomes and Measures:** Generalizability Index (GI; 0–100, composite of age, sex, comorbidity, functional, and representation dimensions); proportion excluding adults aged 75 and older; proportion excluding common comorbidities; proportion with sex-restricted enrollment or sex-stratified analysis.

**Results:** The median Generalizability Index was 82/100 (mean 80.3), indicating moderate representativeness. Among all trials, 38.5% excluded adults aged 75 and older — rising to 41.3% in heart failure trials, where 50% of real-world patients are elderly. CKD was excluded in 19.6% of trials, cancer in 19.5%, and diabetes in 11.8% — all common cardiovascular comorbidities. The CKD exclusion had the highest estimated real-world impact (impact score 1.57). Only 16 trials (0.02%) were sex-restricted, and only 773 (1.2%) mentioned sex-stratified analysis in their design. Industry-sponsored trials had stricter eligibility (43.0% excluding age >75) than academic trials (37.7%). No meaningful improvement in generalizability was observed over time: the proportion excluding elderly adults remained between 37.6% and 40.4% across all eras.

**Conclusions and Relevance:** More than one-third of cardiovascular trials exclude the elderly populations who bear the greatest disease burden. Only 1.2% plan sex-stratified analyses despite well-documented sex differences in cardiovascular pathophysiology and treatment response. These systematic exclusions compromise the applicability of trial evidence to the patients who need it most.

---

## Introduction

The value of clinical trial evidence depends not only on what is measured but on whom it is measured in. Cardiovascular disease is the leading cause of death in adults aged 75 and older, and cardiovascular patients typically present with multiple comorbidities — chronic kidney disease, diabetes, COPD, cognitive impairment, and frailty.[1,2] Yet trials frequently exclude these populations through eligibility criteria that prioritize internal validity over external generalizability.[3]

Previous studies have documented age exclusions in specific cardiovascular conditions,[4] but no comprehensive registry-wide analysis has been conducted. Similarly, while the underrepresentation of women in cardiovascular trials is well documented,[5] the extent to which trials plan sex-stratified analyses — necessary to detect sex-specific treatment effects — has not been systematically assessed.

We conducted a comprehensive audit of all 65,383 cardiovascular trials on ClinicalTrials.gov to quantify three dimensions of trial generalizability: (1) age-based exclusions and their real-world impact, (2) comorbidity restrictions and their prevalence, and (3) sex-specific trial design features.

## Methods

### Data source

We queried the ClinicalTrials.gov API v2 on 1 April 2026, retrieving all 65,383 studies matching the condition term "cardiovascular." For each trial, we extracted eligibility criteria text, minimum and maximum age limits, sex restrictions, study phase, lead sponsor class, condition, and start date.

### Generalizability Index

We computed a Generalizability Index (GI) for each trial, scored 0–100 across five equally weighted dimensions (each 0–20):

- **Age (0–20):** Based on the breadth of the age range relative to the full adult lifespan. Trials with no upper age limit scored 20; trials excluding adults >65 scored 0.
- **Sex (0–20):** Trials open to both sexes scored 20; sex-restricted trials scored 0.
- **Comorbidity (0–20):** Deductions for each commonly excluded comorbidity (CKD, diabetes, cancer, cognitive impairment, liver disease, COPD, bleeding disorders, frailty, anemia, obesity). Each exclusion reduced the score proportionally based on its real-world prevalence in cardiovascular populations.
- **Functional (0–20):** Deductions for performance status requirements, exercise capacity thresholds, and other functional restrictions.
- **Representation (0–20):** Based on whether the trial mentions recruitment strategies for underrepresented groups.

### Age exclusion analysis

We extracted maximum age limits from the structured eligibility fields. Trials were classified by age cutoff: no limit, 85+, 80–84, 75–79, 70–74, 65–69, or <65. We computed the proportion of trials excluding adults ≥75 (cutoff <75) by condition, era, and sponsor class.

To estimate the real-world impact of age exclusions, we combined trial exclusion rates with published estimates of the proportion of real-world patients aged ≥75 for each condition: atrial fibrillation (42%), heart failure (45%), hypertension (40%), and acute coronary syndrome (35%).[6]

### Sex representation analysis

We identified sex-restricted trials from the structured eligibility sex field. To assess sex-stratified analysis, we searched the study design, outcome measures, and eligibility criteria text for mentions of sex-stratified, gender-stratified, sex-specific, or subgroup-by-sex analysis.

### Comorbidity exclusion analysis

We searched eligibility criteria text for 11 common comorbidities using keyword matching: CKD/renal impairment, diabetes, cancer/malignancy, cognitive impairment/dementia, pregnancy, bleeding disorders, liver disease, COPD, frailty, anemia, and obesity. Each exclusion was assigned a real-world weight (1–8) reflecting the comorbidity's prevalence in cardiovascular populations, and an impact score was computed as: (exclusion rate × real-world weight) / 100.

### Statistical analysis

We report proportions with 95% confidence intervals. Temporal trends were assessed by era. Comparisons used chi-squared tests. Analyses were conducted in Python 3.13.

## Results

### Generalizability Index

The median GI across all 65,383 trials was 82/100 (mean 80.3), indicating moderate generalizability. The dimension scores varied substantially: sex scored highest (mean 10.0/20), reflecting that most trials accept both sexes, while comorbidity scored lowest (mean 36.2/100 within its dimension), reflecting pervasive comorbidity exclusions.

Heart failure trials had the lowest mean GI (79.3), driven by both age and comorbidity restrictions. Atrial fibrillation had the highest (81.6). Phase 2 trials were least generalizable (mean GI 76.2) and observational/unphased studies most generalizable (83.1).

### Age exclusions

Of 65,383 trials, 25,190 (38.5%) excluded adults aged 75 or older through explicit maximum age limits. The exclusion was most severe in heart failure (41.3%), despite half of real-world HF patients being ≥75 (estimated exclusion impact: 20.6%). Atrial fibrillation showed a similar mismatch: 36.6% of trials excluded elderly adults, yet 42% of real-world AF patients are ≥75 (impact: 21.9%).

**Table 1. Elderly exclusion by cardiovascular condition**

| Condition | Trials | % Excluding ≥75 | Real-world elderly % | Impact score |
|-----------|--------|------------------|---------------------|--------------|
| Heart failure | 6,086 | 41.3 | 50.0 | 20.6 |
| Acute coronary syndrome | 7,752 | 39.5 | 35.0 | 13.8 |
| Atrial fibrillation | 3,231 | 36.6 | 42.0* | 21.9 |
| Hypertension | 6,392 | 31.6 | 40.0 | 12.6 |
| Other | 41,922 | 39.2 | 30.0 | 11.7 |

*Corrected from original registry estimate based on population-based AF registries.

Industry-sponsored trials were more restrictive (43.0% excluding ≥75) than academic/hospital-sponsored trials (37.7%) and NIH-funded trials (28.0%).

No temporal improvement was observed: elderly exclusion ranged from 37.6% (2000–2004) to 40.4% (2010–2014), with 38.1% in 2020–2025.

### Comorbidity exclusions

The most commonly excluded comorbidities were pregnancy (38.7%), CKD (19.6%), and cancer (19.5%) (Table 2). When weighted by real-world prevalence in cardiovascular populations, CKD had the highest impact score (1.57), followed by diabetes (0.83) and cancer (0.78).

**Table 2. Comorbidity exclusions ranked by real-world impact**

| Comorbidity | Trials excluding (%) | Real-world weight | Impact score |
|-------------|---------------------|-------------------|--------------|
| CKD | 12,791 (19.6%) | 8 | 1.57 |
| Diabetes | 7,715 (11.8%) | 7 | 0.83 |
| Cancer | 12,746 (19.5%) | 4 | 0.78 |
| Cognitive impairment | 5,831 (8.9%) | 5 | 0.45 |
| Pregnancy | 25,299 (38.7%) | 1 | 0.39 |
| Bleeding disorders | 5,939 (9.1%) | 4 | 0.36 |
| Liver disease | 5,463 (8.4%) | 3 | 0.25 |
| COPD | 3,553 (5.4%) | 4 | 0.22 |
| Frailty | 1,458 (2.2%) | 6 | 0.13 |
| Anemia | 1,962 (3.0%) | 3 | 0.09 |
| Obesity | 981 (1.5%) | 5 | 0.08 |

### Sex representation

Only 16 trials (0.02%) restricted enrollment by sex. While this indicates broad sex-based eligibility, only 773 trials (1.2%) mentioned sex-stratified analysis in their design or outcome specification. This rate was consistent across eras (0.4% pre-2000 to 1.6% in 2005–2009) and conditions (0.7% in AF to 2.0% in ACS). Industry and academic sponsors had identical rates (1.2%).

**Table 3. Sex-stratified analysis by condition**

| Condition | Trials | Sex-restricted | % Sex-stratified |
|-----------|--------|---------------|-----------------|
| Acute coronary syndrome | 7,752 | 3 | 2.0 |
| Hypertension | 6,392 | 3 | 1.8 |
| Heart failure | 6,086 | 2 | 1.2 |
| Atrial fibrillation | 3,231 | 0 | 0.7 |
| Other | 41,922 | 8 | 1.0 |

## Discussion

### Principal findings

This comprehensive audit reveals systematic generalizability gaps in cardiovascular trials. More than one-third (38.5%) exclude adults aged 75+ — the population with the highest cardiovascular mortality. CKD, present in approximately 40% of heart failure patients, is excluded in nearly one-fifth of all trials. And despite decades of advocacy for sex-specific cardiovascular research, only 1.2% of trials mention sex-stratified analysis.

### Age exclusion: a persistent problem

The finding that 41.3% of heart failure trials exclude elderly adults, while 50% of real-world HF patients are ≥75, represents a fundamental evidence-practice mismatch. The PARADIGM-HF trial, which led to sacubitril/valsartan approval, enrolled patients with a mean age of 63.8 years — nearly two decades younger than the typical HF patient in clinical practice.[7] Our data suggest this is not an isolated example but a systemic pattern.

The lack of temporal improvement is striking. Despite repeated calls for more inclusive trials,[8] the proportion excluding elderly adults was 38.1% in 2020–2025 — unchanged from earlier eras. Regulatory incentives (e.g., the FDA's 2020 guidance on inclusion of older adults) have not yet translated into practice.

### The comorbidity burden

CKD emerged as the most impactful exclusion. Chronic kidney disease is present in 40–60% of heart failure patients and substantially modifies both treatment response and prognosis.[9] Excluding CKD patients from 19.6% of cardiovascular trials means that the evidence base systematically omits a population for whom treatment decisions are most uncertain.

### Sex-stratified analysis: a missed opportunity

While sex-restricted enrollment is rare (0.02%), the near-absence of sex-stratified analysis (1.2%) is a different problem. Simply enrolling women is insufficient; without pre-specified sex-stratified analyses, sex-specific treatment effects remain hidden. This is particularly relevant in cardiovascular disease, where sex differences in pathophysiology (heart failure with preserved ejection fraction, spontaneous coronary artery dissection, takotsubo cardiomyopathy) and pharmacokinetics are well established.[10]

### Strengths and limitations

Strengths include comprehensive coverage, systematic classification, and the real-world impact weighting. Limitations include: reliance on registered eligibility criteria text, which may not capture all exclusions applied in practice; keyword-based comorbidity detection, which may undercount implicit exclusions; and the GI weighting scheme, which requires subjective choices about dimension importance.

### Implications

Funders and ethics committees should require explicit justification for excluding adults ≥75 in conditions where elderly patients represent a substantial proportion of the affected population. Regulatory agencies should mandate sex-stratified analysis plans in phase 3 trials for conditions with known sex differences. Registries could flag trials with narrow eligibility criteria relative to the disease epidemiology.

## Conclusions

Among 65,383 cardiovascular trials, 38.5% exclude adults ≥75, 19.6% exclude CKD, and only 1.2% plan sex-stratified analyses. These systematic exclusions limit the applicability of cardiovascular evidence to the populations who bear the greatest disease burden. Structural reforms in trial design requirements are needed.

---

## References

1. Forman DE, Rich MW, Alexander KP, et al. Cardiac care for older adults. J Am Coll Cardiol. 2011;57:1801-1810.
2. Braunwald E. The war against heart failure: the Lancet lecture. Lancet. 2015;385:812-824.
3. Van Spall HGC, Toren A, Kiss A, Fowler RA. Eligibility criteria of randomized controlled trials published in high-impact general medical journals. JAMA. 2007;297:1233-1240.
4. Cherubini A, Oristrell J, Pla X, et al. The persistent exclusion of older patients from ongoing clinical trials regarding heart failure. Arch Intern Med. 2011;171:550-556.
5. Melloni C, Berger JS, Wang TY, et al. Representation of women in randomized clinical trials of cardiovascular disease prevention. Circ Cardiovasc Qual Outcomes. 2010;3:135-142.
6. Go AS, Mozaffarian D, Roger VL, et al. Heart disease and stroke statistics — 2014 update. Circulation. 2014;129:e28-e292.
7. McMurray JJV, Packer M, Desai AS, et al. Angiotensin-neprilysin inhibition versus enalapril in heart failure. N Engl J Med. 2014;371:993-1004.
8. Rich MW, Chyun DA, Skolnick AH, et al. Knowledge gaps in cardiovascular care of the older adult population. Circulation. 2016;133:2103-2122.
9. House AA, Wanner C, Sarnak MJ, et al. Heart failure in chronic kidney disease: conclusions from a Kidney Disease: Improving Global Outcomes (KDIGO) Controversies Conference. Kidney Int. 2019;95:1304-1317.
10. Vogel B, Acevedo M, Appelman Y, et al. The Lancet women and cardiovascular disease Commission. Lancet. 2021;397:2385-2438.

---

## Data availability statement

Analysis code and classified datasets are available at [REPOSITORY_URL]. Source data are from ClinicalTrials.gov (API v2, 1 April 2026, N=65,383).

## Funding

[FUNDING STATEMENT]

## Competing interests

[COMPETING INTERESTS]

## Ethics approval

Publicly available registry data; ethics approval not required.

## Word count

Main text: ~3,100 words
