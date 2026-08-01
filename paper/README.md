# Paper — REF-2026-018

Status: `SECOND DRAFT / NOT SUBMITTED / NOT PEER REVIEWED / NOT A PREPRINT`

## Manuscript

- [`manuscript_draft_v0.2.md`](manuscript_draft_v0.2.md) — **current draft**, 1 August 2026. *Vanishing Winners: Interval-Censored Survival of Signal-Provider Visibility on a Public Copy-Trading Leaderboard, 2011–2026*. Zhennan (Nathan) Yu, independent researcher, Sydney. ~12,300 words in Sections 1–7.
- [`manuscript_draft_v0.1.md`](manuscript_draft_v0.1.md) — first full draft, retained unedited for the record.

**What changed in v0.2.** v0.1 stated that the second half of the frozen contribution claim — a first quantification of the bias in the platform's *observable performance distribution* — was not deliverable, because no performance covariates had been extracted. That statement is withdrawn. The covariates have been extracted from the same archived bytes (manuscript §3.7) and the bias has been quantified in four comparisons, one of them a robustness check against the displayed-track-record confound (§3.8, §4.6, §5.3, Figure 3). No number reported in v0.1 has changed: no survival, turnover, appearance-distribution or bounds artifact was regenerated, and the additions are strictly additive to the corpus.

All quantitative results were produced under the protocol frozen at commit `684241f` (annotated tag `v1.0-protocol-freeze`, 25 July 2026), created **before any data extraction**. The frozen protocol file is never edited; the only post-freeze amendment is [`../protocol/amendments/erratum-001-snapshot-counts.md`](../protocol/amendments/erratum-001-snapshot-counts.md), discussed in manuscript Section 3.1.

Every quantitative claim in the draft names the committed artifact it comes from. The claims→artifacts map is in the [repository README](../README.md#claims--artifacts-map).

## Figures

All three figures regenerate deterministically from the committed artifacts via [`../src/make_figures.py`](../src/make_figures.py); no re-fetching is required.

| File | Content | Source artifacts |
|---|---|---|
| [`figures/fig1_survival.png`](figures/fig1_survival.png) | Turnbull interval-censored survival of leaderboard visibility, with the naive-KM bound envelope and the four assessable marks (30 d / 90 d / 180 d / 1 y) | `artifacts/analysis/survival_turnbull.csv`, `artifacts/analysis/survival_intervals.csv` |
| [`figures/fig2_turnover.png`](figures/fig2_turnover.png) | Left: adjacent-snapshot turnover by year. Right: appearance-count distribution, truncated at 10 | `artifacts/analysis/turnover_by_year.csv`, `artifacts/analysis/appearance_distribution.csv` |
| [`figures/fig3_survivorship_bias.png`](figures/fig3_survivorship_bias.png) | (a) displayed growth at first appearance, providers seen again vs seen once, with clustered-bootstrap intervals; (b) the same comparison within displayed-track-record bands (0–3 years); (c) per-transition survivor-minus-roster median deltas | `artifacts/analysis/survivorship_bias_summary.json`, `artifacts/analysis/survivorship_bias.csv` |

Full captions — including the distinction between the transition-weighted headline turnover (54.4%) and the unweighted mean of yearly rates plotted in Figure 2 (55.2%), and the note that Figure 3's bar labels are rounded while the text carries the unrounded medians — are in manuscript Section 4.7.

## Headline numbers

**Visibility (2011-10 → 2026-07, 141 captures).** 2,090 distinct providers · mean adjacent-snapshot turnover 54.4% · 65.8% seen in exactly one snapshot · S(30 d)=0.367, S(90 d)=0.2143, S(180 d)=0.1109, S(365 d)=0.039 · median 11 days (hedged: "under a fortnight, imprecisely located") · bounds check PASS at all four assessable marks.

**Displayed-performance bias (2017-08 → 2026-07, 73 growth-bearing captures, 1,404 providers, 2,569 growth figures).** Visibility-weighted median displayed growth 154.0% vs entry-cohort 104.5% (+49.5 pp) · at first appearance, providers later seen again 155.5% [123.99, 184.0] vs never seen again 90.5% [83.0, 101.0], intervals non-overlapping · survivor median exceeds roster median in 68 of 71 transitions, median delta +64.0 pp · within displayed-track-record bands the gap is +40, +64, +93 and +71 pp at 0, 1, 2 and 3 years, with intervals separating at 0 and 1 year only.

Every performance figure is what the archived card **displayed**; none is audited performance and none is a return realised by any follower.

## What is established, and what is not

Both halves of the frozen contribution claim are now delivered: the survival-analytic estimate of provider attrition, and the quantification of the bias in the leaderboard's *displayed* performance distribution. Scoped precisely:

**Established.** How long provider identities stay visible on the archived index; how fast the roster turns over; how the displayed growth distribution a visitor encounters differs from the entering cohort's (exposure); and that providers who go on to remain visible were already displaying higher figures on their first observed card (selection at entry), a gap that survives stratification on displayed track-record length in the two well-populated bands.

**Not established.** Realised or audited performance of any provider — no returns data exists in this corpus, for survivors or for the disappeared. Any statement that survivors subsequently performed better, or that the disappeared lost money. Any causal claim about why providers disappear or why survivors' displayed figures are higher. Any rank-based result. Any covariate hazard model (Finkelstein / Allison remain unfitted).

## Open items carried into the next draft

Declared in the manuscript, not hidden here:

1. **The protocol's terminal live status sweep has not been run** (manuscript Section 6). The realised endpoint is index-roster absence alone, which is weaker than the frozen death definition. This is a live deviation from the protocol.
2. **Short-duration resolution is thin**: 57.4% of the estimated mass sits in three support intervals whose endpoints are the three shortest capture gaps in 140 transitions, so the 11-day median is hedged in the text as "under a fortnight, imprecisely located".
3. **The secondary endpoint is deliberately not attempted**, because `dom_order` is document order and not a rank (manuscript Section 3.3). Extracting performance covariates does not change this.
4. **Two of the four track-record strata are thin** (2 years: 27 vs 58 providers; 3 years: 11 vs 11) and their bootstrap intervals overlap; the stratified result rests on the 0-year and 1-year bands.
5. **The growth field starts in 2017**, so the bias analysis covers 73 of 141 captures and roughly nine years against the survival analysis's fifteen.
6. **The performance comparisons are post-hoc in design** — the frozen protocol names the headline comparison but specifies no estimator, uncertainty method or stratification; those were implementation-time choices, recorded in code and artifact rather than claimed as pre-registered.
