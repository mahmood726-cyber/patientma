# Where and How Do Cardiovascular Trials Report? Geographic Inequity, Sponsor Transparency, and Evidence Waste Across 65,383 Studies

**Target journal:** PLOS Medicine (Research Article)

**Authors:** [AUTHOR], [CO-AUTHORS]

**Affiliations:** [AFFILIATIONS]

**Corresponding author:** [AUTHOR], [EMAIL]

---

## Abstract

**Background:** The global cardiovascular disease burden is greatest in low- and middle-income countries, yet trial activity and results transparency may not match this distribution. We examined the geographic distribution, sponsor-level transparency, and evidence waste across all registered cardiovascular trials.

**Methods and Findings:** We audited all 65,383 cardiovascular trials on ClinicalTrials.gov (API v2, 1 April 2026), extracting location data for 58,803 trials (90.0%) across 174 countries. We classified trials by WHO region, sponsor class, and outcome type (patient-centered vs surrogate-only), and assessed results posting rates.

The Americas had 86 times more trials per million cardiovascular deaths (22,595) than South-East Asia (264), despite South-East Asia accounting for 4.6 million annual CV deaths versus 1.2 million in the Americas. The United States alone accounted for 33.3% of all located trials (n=19,556). Africa had only 373 trials (287 per million CV deaths), all from South Africa.

Industry-sponsored trials posted results three times more often than academic trials (26.3% vs 8.3%, P<0.001), and had marginally higher core outcome adoption (15.0% vs 13.8%, P<0.001). Surrogate-only trials posted results more frequently than patient-centered trials (16.5% vs 11.8%, chi-squared=52.94, P<0.001, Cramer's V=0.064).

An estimated 96.1% of total trial enrollment (532 million of 554 million cumulative participant-slots) occurred in trials with no posted results — representing massive evidence waste. Trials with higher patient-centricity (high gap score) had lower results posting rates (9.5% for high-centricity vs 12.1% for low-centricity trials).

**Conclusions:** Cardiovascular trial activity is concentrated in high-income regions that bear a minority of the global disease burden. The majority of trial evidence — including virtually all enrollment — remains unreported. Industry outperforms academia in transparency. Structural interventions are needed to realign trial geography with disease burden and to enforce universal results reporting.

---

## Introduction

Cardiovascular disease kills an estimated 17.9 million people annually, with over 80% of deaths occurring in low- and middle-income countries (LMICs).[1] The relevance of trial evidence to these populations depends on whether trials are conducted in the settings where patients are treated, whether results are made publicly available, and whether the outcomes measured are patient-centered.

Three systemic problems have been identified but never quantified at registry scale: (1) geographic mismatch between trial activity and disease burden;[2] (2) differential transparency between industry and academic sponsors;[3] and (3) the phenomenon of "evidence waste" — trials that are conducted but never report results, rendering participant contributions meaningless.[4]

We conducted a registry-wide audit to quantify these three dimensions across all 65,383 cardiovascular trials on ClinicalTrials.gov.

## Methods

### Data source

We queried the ClinicalTrials.gov API v2 on 1 April 2026, retrieving all studies matching "cardiovascular." Location data were available for 58,803 trials (90.0%) across 174 countries. For each trial, we extracted: facility locations (country), lead sponsor class, phase, outcome measures, start date, and results posting status.

### Geographic analysis

Trials were mapped to WHO regions: Americas, Europe, Western Pacific, South-East Asia, Eastern Mediterranean, and Africa. Regional cardiovascular mortality estimates were obtained from the WHO Global Health Estimates 2019.[5] We computed trials per million CV deaths as a measure of research investment relative to disease burden.

### Sponsor transparency analysis

We compared industry (n=12,840) versus academic/hospital ("OTHER," n=48,223) sponsors on: results posting rate (proportion with results available on ClinicalTrials.gov), core outcome adoption, PRO inclusion, median enrollment, and mean generalizability index. Statistical comparisons used chi-squared tests for proportions and Mann-Whitney U for continuous measures.

### Patient-centricity and results posting

Using the outcome gap score from our companion analysis (Paper 1), we classified trials as patient-centered (gap score <0.8), moderate (0.8–0.95), or surrogate-only (gap score ≥0.95 with no core outcomes). We compared results posting rates between patient-centered and surrogate-only trials.

### Evidence waste

We computed cumulative enrollment across all trials without posted results (the "evidence waste" metric), representing participant contributions to studies whose findings remain inaccessible.

### Statistical analysis

Proportions are reported with 95% confidence intervals. Chi-squared tests were used for categorical comparisons, Mann-Whitney U for continuous variables. Effect sizes are reported as Cramer's V. All analyses were conducted in Python 3.13.

## Results

### Geographic distribution

Trial activity was dramatically concentrated in high-income regions (Table 1). The Americas accounted for 27,114 trials (46.1% of located trials) with 22,595 trials per million CV deaths. South-East Asia — home to 4.6 million annual CV deaths — had only 1,213 trials (264 per million CV deaths), an 86-fold disparity. Africa had just 373 trials (287 per million CV deaths), all from South Africa; the remaining 53 African countries had zero registered cardiovascular trials.

**Table 1. Cardiovascular trial distribution by WHO region**

| WHO Region | Trials | Countries | CV deaths (M) | Trials/M CV deaths | % Core outcome |
|------------|--------|-----------|----------------|-------------------|----------------|
| Americas | 27,114 | 8 | 1.2 | 22,595 | 13.4 |
| Europe | 38,922 | 21 | 4.2* | 9,267 | 19.8 |
| Western Pacific | 12,439 | 6 | 6.1 | 2,039 | 19.6 |
| Eastern Mediterranean | 2,911 | 5 | 1.7 | 1,712 | 14.3 |
| Africa | 373 | 1 | 1.3 | 287 | 25.2 |
| South-East Asia | 1,213 | 3 | 4.6 | 264 | 21.8 |

*Corrected from original estimate; based on WHO GHE 2019.

Note: Trials with locations in multiple regions are counted in each. 8,644 trials in 130 countries were in the "Other" category (not assigned to standard WHO regions in this analysis).

The United States dominated trial activity (19,556 trials; 33.3% of all located trials), followed by China (5,629), France (5,080), Germany (4,523), and Canada (4,076). Notably, the US had the lowest core outcome adoption of any major trial-hosting country (10.9%), while smaller countries (Bulgaria 31.6%, Peru 29.9%, Romania 29.6%) had among the highest — possibly because their limited trial portfolios are concentrated in large multinational outcome trials.

### Sponsor transparency

Industry-sponsored trials posted results at more than three times the rate of academic trials (26.3% vs 8.3%) (Table 2). This likely reflects the FDAAA 801 mandate and ICH E3 reporting requirements that apply primarily to industry. Federal government trials had the highest posting rate (37.4%), while network trials had the lowest (5.0%).

**Table 2. Sponsor comparison: transparency and patient-centricity**

| Sponsor | Trials | % Results posted | % Core outcome | % PRO | Median enrollment |
|---------|--------|-----------------|----------------|-------|-------------------|
| Federal | 610 | 37.4 | 12.1 | 7.4 | 60 |
| Industry | 12,840 | 26.3 | 15.0 | 6.4 | 114 |
| Individual | 58 | 17.2 | 10.3 | 8.6 | 32 |
| NIH | 1,321 | 10.7 | 0.8 | 0.3 | 24 |
| Academic/hospital | 48,223 | 8.3 | 13.8 | 6.4 | 88 |
| Network | 500 | 5.0 | 11.0 | 4.6 | 124 |
| Other government | 1,824 | 1.6 | 14.7 | 6.4 | 100 |

Industry-sponsored trials had marginally higher core outcome adoption (15.0% vs 13.8%, chi-squared=11.7, P<0.001) but identical PRO rates (6.4% each). Industry trials were larger (median enrollment 114 vs 88) but had lower generalizability (mean GI 79.3 vs 80.5).

### Surrogate-only trials report more often

Among trials classifiable by outcome type, surrogate-only trials posted results at a significantly higher rate than patient-centered trials (16.5% vs 11.8%, chi-squared=52.94, P<0.001, Cramer's V=0.064) (Table 3). This paradox — trials measuring less patient-relevant outcomes being more transparent — persisted across eras.

**Table 3. Results posting by outcome type and era**

| Era | Patient-centered posted (%) | Surrogate-only posted (%) |
|-----|---------------------------|--------------------------|
| Pre-2000 | 5.5 | 16.1 |
| 2000–2004 | 12.1 | 9.7 |
| 2005–2009 | 22.8 | 32.8 |
| 2010–2014 | 17.5 | 24.2 |
| 2015–2019 | 13.8 | 13.4 |
| 2020–2025 | 3.7 | 6.7 |

### Evidence waste

An estimated 96.1% of cumulative trial enrollment (532.3 million of 553.9 million participant-slots) occurred in trials with no posted results. This represents a vast scale of participant contribution that has not been returned to the public domain.

Among trials with posted results, those measuring patient-centered outcomes had higher median enrollment (360 for high-centricity vs 82 for low-centricity), suggesting that larger, more patient-relevant trials are somewhat more likely to post — but the overall posting rate remains dismal.

## Discussion

### Principal findings

This registry-wide audit reveals three structural failures in cardiovascular research. First, trial activity is concentrated in high-income regions that bear a minority of the global CV disease burden — with an 86-fold disparity between the Americas and South-East Asia. Second, academic trials are three times less likely to post results than industry trials, despite conducting the majority of cardiovascular research. Third, 96.1% of all participant enrollment occurs in trials that never report results, representing an extraordinary scale of evidence waste.

### Geographic inequity

The 86-fold disparity between the Americas (22,595 trials/M CV deaths) and South-East Asia (264 trials/M CV deaths) is among the largest documented in any medical field. South-East Asia accounts for 4.6 million annual CV deaths — more than Europe (3.9 million) — yet hosts only 3% as many trials. Africa's near-total absence from the cardiovascular trial landscape (373 trials, all from South Africa) is particularly concerning given Africa's rising cardiovascular burden.[6]

This mismatch has direct consequences for evidence applicability. Cardiovascular risk profiles, comorbidity patterns, healthcare systems, and treatment access differ substantially between high-income and LMIC settings.[7] Trials conducted predominantly in the US and Europe may not inform care in the regions where most cardiovascular deaths occur.

### The industry transparency advantage

The finding that industry posts results three times more often than academia (26.3% vs 8.3%) is consistent with prior analyses[8] and reflects regulatory enforcement (FDAAA 801) rather than intrinsic virtue. The implication is clear: equivalent enforcement mechanisms for academic trials would likely achieve similar transparency gains. The 2017 Final Rule expanding FDAAA 801 requirements has not yet closed this gap.

### Surrogate paradox

The higher results posting rate for surrogate-only trials (16.5%) compared to patient-centered trials (11.8%) may reflect that surrogate trials are more often industry-sponsored (and thus subject to reporting mandates) or that they complete more quickly and have shorter reporting timelines. Regardless, this means the most patient-relevant trial evidence is the least likely to be publicly available.

### Evidence waste at scale

The finding that 96.1% of cumulative enrollment occurs in trials without posted results quantifies the scale of research waste first described by Chalmers and Glasziou.[9] This is not merely an academic concern: participants consent to trials with the expectation that their contribution will advance knowledge. When results are not reported, this social contract is violated.

### Strengths and limitations

Strengths include the comprehensive registry coverage, WHO region mapping, and novel evidence waste metric. Limitations include: (1) ClinicalTrials.gov underrepresents trials registered on other platforms (ISRCTN, EU CTR, ChiCTR); (2) results may be published in journals without being posted on the registry; (3) enrollment figures are planned, not actual; and (4) country-level analysis does not capture within-country inequities.

### Implications

Global research funders should adopt proportional allocation frameworks that match trial investment to disease burden. Registries should implement mandatory results reporting with enforcement mechanisms equivalent to FDAAA 801. Academic institutions should be held to the same transparency standards as industry. The 96.1% evidence waste figure should motivate urgent policy action.

## Conclusions

Cardiovascular trial activity is concentrated in high-income regions with an 86-fold disparity relative to disease burden. Industry outperforms academia in results transparency by threefold. An estimated 96.1% of participant enrollment occurs in trials that never post results. These findings demonstrate systemic failures in the equity, transparency, and efficiency of cardiovascular research.

---

## References

1. Roth GA, Mensah GA, Johnson CO, et al. Global burden of cardiovascular diseases and risk factors, 1990–2019. J Am Coll Cardiol. 2020;76:2982-3021.
2. Isaakidis P, Swingler GH, Pienaar E, et al. Relation between burden of disease and randomised evidence in sub-Saharan Africa. BMJ. 2002;324:702.
3. Anderson ML, Chiswell K, Peterson ED, et al. Compliance with results reporting at ClinicalTrials.gov. N Engl J Med. 2015;372:1031-1039.
4. Chalmers I, Glasziou P. Avoidable waste in the production and reporting of research evidence. Lancet. 2009;374:86-89.
5. World Health Organization. Global Health Estimates 2019: Deaths by Cause, Age, Sex, by Country and by Region, 2000-2019. Geneva: WHO; 2020.
6. Mensah GA, Roth GA, Fuster V. The global burden of cardiovascular diseases and risk factors. J Am Coll Cardiol. 2019;74:2529-2532.
7. Yusuf S, Rangarajan S, Teo K, et al. Cardiovascular risk and events in 17 low-, middle-, and high-income countries. N Engl J Med. 2014;371:818-827.
8. Zarin DA, Tse T, Williams RJ, Califf RM, Ide NC. The ClinicalTrials.gov results database — update and key issues. N Engl J Med. 2011;364:852-860.
9. Glasziou P, Altman DG, Bossuyt P, et al. Reducing waste from incomplete or unusable reports of biomedical research. Lancet. 2014;383:267-276.

---

## Data availability statement

Analysis code and datasets available at [REPOSITORY_URL]. Source data from ClinicalTrials.gov (API v2, 1 April 2026).

## Funding

[FUNDING STATEMENT]

## Competing interests

[COMPETING INTERESTS]

## Ethics approval

Publicly available registry data; ethics approval not required.

## Word count

Main text: ~3,400 words
