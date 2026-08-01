# Paper — REF-2026-018

Status: `FIRST FULL DRAFT / NOT SUBMITTED / NOT PEER REVIEWED / NOT A PREPRINT`

## Manuscript

- [`manuscript_draft_v0.1.md`](manuscript_draft_v0.1.md) — *Vanishing Winners: Interval-Censored Survival of Signal-Provider Visibility on a Public Copy-Trading Leaderboard, 2011–2026*. Zhennan (Nathan) Yu, independent researcher, Sydney. First full draft, 1 August 2026; ~6,900 words in Sections 1–7.

All quantitative results were produced under the protocol frozen at commit `684241f` (annotated tag `v1.0-protocol-freeze`, 25 July 2026), created **before any data extraction**. The frozen protocol file is never edited; the only post-freeze amendment is [`../protocol/amendments/erratum-001-snapshot-counts.md`](../protocol/amendments/erratum-001-snapshot-counts.md), discussed in manuscript Section 3.1.

Every quantitative claim in the draft names the committed artifact it comes from. The claims→artifacts map is in the [repository README](../README.md#claims--artifacts-map).

## Figures

Both figures regenerate deterministically from the committed artifacts via [`../src/make_figures.py`](../src/make_figures.py); no re-fetching is required.

| File | Content | Source artifacts |
|---|---|---|
| [`figures/fig1_survival.png`](figures/fig1_survival.png) | Turnbull interval-censored survival of leaderboard visibility, with the naive-KM bound envelope and the four assessable marks (30 d / 90 d / 180 d / 1 y) | `artifacts/analysis/survival_turnbull.csv`, `artifacts/analysis/survival_intervals.csv` |
| [`figures/fig2_turnover.png`](figures/fig2_turnover.png) | Left: adjacent-snapshot turnover by year. Right: appearance-count distribution, truncated at 10 | `artifacts/analysis/turnover_by_year.csv`, `artifacts/analysis/appearance_distribution.csv` |

Full captions, including the distinction between the transition-weighted headline turnover (54.4%) and the unweighted mean of yearly rates plotted in Figure 2 (55.2%), are in manuscript Section 4.6.

## Headline numbers

141 monthly archived snapshots (2011-10 → 2026-07) · 2,090 distinct providers · mean adjacent-snapshot turnover 54.4% · 65.8% seen in exactly one snapshot · S(30 d)=0.367, S(90 d)=0.2143, S(180 d)=0.1109, S(365 d)=0.039 · median 11 days · bounds check PASS at all four assessable marks.

## Open items carried into the next draft

Declared in the manuscript, not hidden here:

1. **The protocol's terminal live status sweep has not been run** (manuscript Section 6). The realised endpoint is index-roster absence alone, which is weaker than the frozen death definition.
2. **No performance covariates are extracted**, so the second half of the frozen contribution claim — first quantification of the bias in the platform's *observable performance distribution* — is **not** delivered in this draft, and the abstract and introduction claim only the visibility-duration result.
3. **The secondary endpoint is deliberately not attempted**, because `dom_order` is document order and not a rank (manuscript Section 3.3).
4. **Short-duration resolution is thin**: 57.4% of the estimated mass sits in three support intervals whose endpoints are the three shortest capture gaps in 140 transitions, so the 11-day median is hedged in the text as "under a fortnight, imprecisely located".
