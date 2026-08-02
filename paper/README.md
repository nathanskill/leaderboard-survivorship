# Paper — REF-2026-018

Status: `SECOND DRAFT / NOT SUBMITTED / NOT PEER REVIEWED / NOT A PREPRINT`

## Manuscript

- [`manuscript_draft_v0.2.md`](manuscript_draft_v0.2.md) — **current draft**, 1 August 2026, revised in place 2 August 2026 (there is no v0.3). *Vanishing Winners: Interval-Censored Survival of Signal-Provider Visibility on a Public Copy-Trading Leaderboard, 2011–2026*. Zhennan (Nathan) Yu, independent researcher, Sydney. ~15,700 words in Sections 1–7.
- [`manuscript_draft_v0.1.md`](manuscript_draft_v0.1.md) — first full draft, retained unedited for the record.

**What changed in v0.2.** v0.1 stated that the second half of the frozen contribution claim — a first quantification of the bias in the platform's *observable performance distribution* — was not deliverable, because no performance covariates had been extracted. That statement is withdrawn. The covariates have been extracted from the same archived bytes (manuscript §3.7) and the bias has been quantified in four comparisons, one of them a robustness check against the displayed-track-record confound (§3.8, §4.6, §5.3, Figure 3). No number reported in v0.1 has changed: no survival, turnover, appearance-distribution or bounds artifact was regenerated, and the additions are strictly additive to the corpus.

**What changed in the in-place revision of 2 August 2026.** v0.2 declared the frozen protocol's **terminal live status sweep** unexecuted and recorded that as a live deviation from the frozen death definition. **The sweep has now been run** (`../src/status_sweep.py`, executed 1 August 2026; artifacts under [`../artifacts/status/`](../artifacts/status/)) and the declaration is replaced by its result: manuscript §3.9 (methods) and §4.7 (results) are new, the Figures subsection is renumbered §4.8, and the abstract, §1, §5.2, §6 and §§7.1–7.2 are revised where they described the sweep as pending. No previously reported number changed, and the survival analysis was deliberately not re-coded on live status — the endpoint remains leaderboard visibility. What the sweep adds is a measurement of how far leaderboard visibility and platform presence diverge, which the previous draft could only assert as a possibility.

**What changed in the in-place revision of 2 August 2026 (second pass).** Two additions, neither touching a result. A **re-identification audit** of every committed artifact and manuscript file was run: no provider name, author name, avatar URL, account handle or free-text field appears in any committed CSV or JSON; no raw HTML fragment appears in any commit on any ref; no provider is named in any manuscript, README, figure or code comment. The draft's standing claim that no individual provider is named anywhere in this study is therefore verified, not assumed. Raw signal ids remain in the artifacts as join keys — a considered position, stated with its costs in manuscript §7.2; [`../src/pseudonymise.py`](../src/pseudonymise.py) implements the alternative and is committed **unrun**. Separately, manuscript **§5.6** is new: this study's investor-protection measurement placed beside two independently sourced regulatory observations (IOSCO FR/06/2025 and FR/08/2025; FCA CFD portfolio letter, 13 December 2024), each verified against the issuing regulator's primary document on 2 August 2026. No number changed and the endpoint is unchanged.

All quantitative results were produced under the protocol frozen at commit `684241f` (annotated tag `v1.0-protocol-freeze`, 25 July 2026), created **before any data extraction**. The frozen protocol file is never edited; the only post-freeze amendment is [`../protocol/amendments/erratum-001-snapshot-counts.md`](../protocol/amendments/erratum-001-snapshot-counts.md), discussed in manuscript Section 3.1.

Every quantitative claim in the draft names the committed artifact it comes from. The claims→artifacts map is in the [repository README](../README.md#claims--artifacts-map).

## Figures

All three figures regenerate deterministically from the committed artifacts via [`../src/make_figures.py`](../src/make_figures.py); no re-fetching is required.

| File | Content | Source artifacts |
|---|---|---|
| [`figures/fig1_survival.png`](figures/fig1_survival.png) | Turnbull interval-censored survival of leaderboard visibility, with the naive-KM bound envelope and the four assessable marks (30 d / 90 d / 180 d / 1 y) | `artifacts/analysis/survival_turnbull.csv`, `artifacts/analysis/survival_intervals.csv` |
| [`figures/fig2_turnover.png`](figures/fig2_turnover.png) | Left: adjacent-snapshot turnover by year. Right: appearance-count distribution, truncated at 10 | `artifacts/analysis/turnover_by_year.csv`, `artifacts/analysis/appearance_distribution.csv` |
| [`figures/fig3_survivorship_bias.png`](figures/fig3_survivorship_bias.png) | (a) displayed growth at first appearance, providers seen again vs seen once, with clustered-bootstrap intervals; (b) the same comparison within displayed-track-record bands (0–3 years); (c) per-transition survivor-minus-roster median deltas | `artifacts/analysis/survivorship_bias_summary.json`, `artifacts/analysis/survivorship_bias.csv` |

Full captions — including the distinction between the transition-weighted headline turnover (54.4%) and the unweighted mean of yearly rates plotted in Figure 2 (55.2%), and the note that Figure 3's bar labels are rounded while the text carries the unrounded medians — are in manuscript Section 4.8. The terminal status sweep of Sections 3.9 and 4.7 has no figure; it is reported as two tables.

## Headline numbers

**Visibility (2011-10 → 2026-07, 141 captures).** 2,090 distinct providers · mean adjacent-snapshot turnover 54.4% · 65.8% seen in exactly one snapshot · S(30 d)=0.367, S(90 d)=0.2143, S(180 d)=0.1109, S(365 d)=0.039 · median 11 days (hedged: "under a fortnight, imprecisely located") · bounds check PASS at all four assessable marks.

**Displayed-performance bias (2017-08 → 2026-07, 73 growth-bearing captures, 1,404 providers, 2,569 growth figures).** Visibility-weighted median displayed growth 154.0% vs entry-cohort 104.5% (+49.5 pp) · at first appearance, providers later seen again 155.5% vs never seen again 90.5%, a difference of +65.0 pp whose direct bootstrap interval [30.5, 93.0] excludes zero · survivor median exceeds roster median in 68 of 71 transitions, median delta +64.0 pp · within displayed-track-record bands the gap is +40 [7.0, 65.01], +64 [29.0, 95.0], +93 [−16.51, 269.01] and +71 [−199.0, 205.0] pp at 0, 1, 2 and 3 years — excluding zero in the two well-populated bands, covering it in the two thin ones.

**Terminal live status sweep (checked 1 August 2026).** 309 departed providers sampled ≤20 per last-seen year (seed 20260723) · one HEAD per provider page 2 s apart · control = all 49 providers still on the final archived roster · **18/309 departed pages resolve (5.8%) against 49/49 controls (100%)** · matched recency **14/20 against 37/37** · **0/269 resolve for last-seen years 2011–2024**, 4/20 in 2025, 14/20 in 2026 · i.e. departure is followed by page removal on a lag of roughly one to two years. Single timepoint; the endpoint is not redefined by it.

Every performance figure is what the archived card **displayed**; none is audited performance and none is a return realised by any follower.

## What is established, and what is not

Both halves of the frozen contribution claim are now delivered: the survival-analytic estimate of provider attrition, and the quantification of the bias in the leaderboard's *displayed* performance distribution. Scoped precisely:

**Established.** How long provider identities stay visible on the archived index; how fast the roster turns over; how the displayed growth distribution a visitor encounters differs from the entering cohort's (exposure); that providers who go on to remain visible were already displaying higher figures on their first observed card (selection at entry), a gap that survives stratification on displayed track-record length in the two well-populated bands; and how far leaderboard visibility and platform presence stood apart on 1 August 2026 — departed pages resolve at 5.8% against a still-listed control at 100%, with a departure-to-removal lag of roughly one to two years.

**Not established.** Realised or audited performance of any provider — no returns data exists in this corpus, for survivors or for the disappeared. Any statement that survivors subsequently performed better, or that the disappeared lost money. Any causal claim about why providers disappear or why survivors' displayed figures are higher. Any rank-based result. Any covariate hazard model (Finkelstein / Allison remain unfitted). Any statement about a provider's state at the moment it left the board: the status sweep reads one date, so a resolving page on 2026-08-01 is not evidence about that provider's condition on the day it disappeared from the roster, and no coded death was reclassified on it.

## Open items carried into the next draft

Declared in the manuscript, not hidden here:

1. **The protocol's terminal live status sweep has been run and the deviation is closed** (manuscript Sections 3.9, 4.7, 5.2, 6). What remains open is what the sweep cannot reach: it is a single timepoint, so it dates no removal and says nothing about a provider's state when it left; its sample is stratified and capped, so the pooled 5.8% is not a population rate; and the still-listed control contains no provider first appearing before 2024, so a page-retirement policy operating only on longer timescales is not excluded by the control alone. A repeat sweep at a later date would turn the inferred lag into an observed one.
2. **Short-duration resolution is thin**: 57.4% of the estimated mass sits in three support intervals whose endpoints are the three shortest capture gaps in 140 transitions, so the 11-day median is hedged in the text as "under a fortnight, imprecisely located".
3. **The secondary endpoint is deliberately not attempted**, because `dom_order` is document order and not a rank (manuscript Section 3.3). Extracting performance covariates does not change this.
4. **Two of the four track-record strata are thin** (2 years: 27 vs 58 providers; 3 years: 11 vs 11) and their difference intervals cover zero; the stratified result rests on the 0-year and 1-year bands. In the 0-year band the direct difference interval excludes zero while the two separately-computed intervals touch at 69.0 — the conservative overlap heuristic and the direct test disagree there, and the manuscript reports the direct interval and states the weaker reading (§3.8, §4.6, §6).
5. **The growth field starts in 2017**, so the bias analysis covers 73 of 141 captures and roughly nine years against the survival analysis's fifteen.
6. **The performance comparisons are post-hoc in design** — the frozen protocol names the headline comparison but specifies no estimator, uncertainty method or stratification; those were implementation-time choices, recorded in code and artifact rather than claimed as pre-registered.
