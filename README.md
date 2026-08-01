# Leaderboard Survivorship (REF-2026-018)

Status: `PROTOCOL FROZEN / EXTRACTION COMPLETE / PRIMARY ENDPOINTS 1-2 ANALYSED / PERFORMANCE COVARIATES EXTRACTED / SURVIVORSHIP BIAS QUANTIFIED / SECOND MANUSCRIPT DRAFT / NOT SUBMITTED`

Working title:

> Vanishing Winners: Interval-Censored Survival of Signal-Provider Visibility on a Public Copy-Trading Leaderboard, 2011–2026

Current draft: [`paper/manuscript_draft_v0.2.md`](paper/manuscript_draft_v0.2.md); the first full draft is retained unedited at [`paper/manuscript_draft_v0.1.md`](paper/manuscript_draft_v0.1.md) (see [`paper/README.md`](paper/README.md)). Not submitted, not peer reviewed, not a preprint.

What happens to signal providers *after* they reach the public leaderboard of a retail copy-trading marketplace? This study reconstructs the MQL5 signal leaderboard from a decade of web archives and estimates provider disappearance, leaderboard turnover, and the gap between the **leaderboard view** a prospective subscriber sees and the **entering-cohort distribution** of everyone who ever appeared.

The field already names this gap and declines to measure it. Schneider & Oehler (2021, IRFA 78:101892) report that their platform-side data *"leads to a substantial survivorship bias as accounts which can no longer be found … are not included in the dataset"*, and their companion paper judges the vanished to have been the underperformers. Web archives can recover them.

- **Protocol**: [`protocol/locked_protocol_v1.0.md`](protocol/locked_protocol_v1.0.md) — frozen before extraction (tag `v1.0-protocol-freeze`). Endpoints, cohort rule, death definition and the conservative renaming rule are fixed there. Post-freeze corrections are numbered errata under [`protocol/amendments/`](protocol/amendments/); the frozen file is never edited.
- **Method**: interval-censored survival (Turnbull NPMLE) — disappearance is only ever bracketed between two archive snapshots, never observed exactly.
- **Data**: Wayback Machine CDX + archived HTML of the `mql5.com/en/signals` index. The CDX API reports 1,322 raw captures of the index URL; the pipeline retains **one capture per calendar month, 141 monthly snapshots spanning 178 months (2011-10 → 2026-07)**, each fetched as unrewritten original bytes and SHA-256-hashed (`artifacts/manifests/`). 37 of the 178 months have no archived capture (table below). The frozen protocol's "1,322 index snapshots across 100 distinct months" is reconciled in [`protocol/amendments/erratum-001-snapshot-counts.md`](protocol/amendments/erratum-001-snapshot-counts.md). Aggregate reporting only; no provider is named.
- **Results — visibility** (committed under [`artifacts/analysis/`](artifacts/analysis/)): 2,090 distinct providers; mean adjacent-snapshot turnover 54.4%; 65.8% of providers appear in exactly one snapshot; Turnbull survival of leaderboard visibility S(30d)=0.367, S(90d)=0.2143, S(180d)=0.1109, S(365d)=0.039; all assessable marks lie inside the naive Kaplan-Meier bound envelope (`bounds_check.csv`). The frozen sparse-year rule (protocol §6) was evaluated: no year falls below the threshold (`sparse_year_check.txt`).
- **Results — displayed-performance bias** (committed under [`artifacts/performance/`](artifacts/performance/) and [`artifacts/analysis/`](artifacts/analysis/)): the performance figures the archived cards themselves carried were extracted from the same bytes with no further fetching — 4,325 provider rows (identical to the roster count), 2,569 with a displayed growth percentage, present only from 2017-08 onward. The distribution a visitor encounters is shifted upward relative to the entering cohort (median displayed growth 154.0% vs 104.5%), and at each provider's own first card those later seen again already display 155.5% [123.99, 184.0] against 90.5% [83.0, 101.0] for those never seen again (provider-clustered bootstrap, non-overlapping). The survivor median exceeds the roster median in 68 of 71 transitions (median delta +64.0 pp). The obvious confound — cumulative growth since a stated inception year, so survivors may simply be older — is real (median displayed track record 1 year vs 0) and was tested: the gap persists within every reported band (+40, +64, +93, +71 pp at 0–3 years), with intervals separating in the two well-populated bands and overlapping in the two thin ones. Every figure is **displayed**, not audited, performance.

## Snapshot coverage: missing months

The 178-month span 2011-10 → 2026-07 has 37 months with no archived capture of the index page. Per protocol §6 these are reported as exclusions; the interval-censored estimator absorbs irregular spacing rather than assuming it away, but the Nov 2017 – Jun 2018 gap (8 consecutive months) widens the disappearance intervals that bracket it.

| Gap (inclusive) | Months missing |
|---|---|
| 2015-02 | 1 |
| 2015-09 | 1 |
| 2017-11 → 2018-06 | 8 |
| 2020-07 → 2020-08 | 2 |
| 2021-11 → 2021-12 | 2 |
| 2022-02 → 2022-07 | 6 |
| 2022-09 → 2022-11 | 3 |
| 2023-01 | 1 |
| 2023-04 → 2023-08 | 5 |
| 2023-10 → 2023-11 | 2 |
| 2024-01 | 1 |
| 2024-03 | 1 |
| 2024-06 → 2024-08 | 3 |
| 2024-10 | 1 |
| **Total** | **37** |

## Claims → artifacts map

Every quantitative claim in the manuscript is traceable to a committed artifact. Manuscript sections refer to [`paper/manuscript_draft_v0.2.md`](paper/manuscript_draft_v0.2.md); §§3.7, 3.8, 4.6 and 4.7's Figure 3 are new in v0.2, and the §4.6/§4.7 numbering shifted by one section relative to v0.1.

| Manuscript claim | Artifact |
|---|---|
| §3.1 CDX query, 141 monthly snapshots, 2011-10 → 2026-07, 37 uncaptured months | `artifacts/snapshots/index_snapshots.csv`; query verbatim in `src/extract.py::cmd_index` and `protocol/amendments/erratum-001-snapshot-counts.md` |
| §3.2 raw `id_` replay fetch, 141/141 successes, zero failures, SHA-256 per file | `artifacts/manifests/index_fetch_manifest.csv` (141 rows, all `status=ok`) |
| §3.3 rosters: 4,325 rows / 141 snapshots; roster size min 10, median 30, max 53; `dom_order` is DOM order, not a rank | `artifacts/rosters/index_rosters.csv`; caveat in `src/extract.py::cmd_parse_index` |
| §3.5 Turnbull NPMLE, 52 support intervals; 8 unit tests | `artifacts/analysis/survival_turnbull.csv`; `tests/test_survival.py` |
| §4.1 corpus: 2,090 distinct providers; snapshot gaps 7–282 days, median 30 | `artifacts/analysis/turnover_summary.json`, `artifacts/analysis/survival_summary.json`, `artifacts/snapshots/index_snapshots.csv` |
| §4.2 turnover: mean 54.4% over 140 transitions; per-year table; unweighted yearly mean 55.2% (Figure 2 line) | `artifacts/analysis/turnover_summary.json`, `artifacts/analysis/turnover_by_year.csv` |
| §4.3 appearance distribution: 1,376 (65.8%) seen once; 79.4% ≤2; 93.6% ≤5 | `artifacts/analysis/appearance_distribution.csv` |
| §4.4 survival S(30d)=0.367, S(90d)=0.2143, S(180d)=0.1109, S(365d)=0.039; median 11 d; 57.4% of mass in the three support intervals ≤11 d | `artifacts/analysis/survival_summary.json`, `artifacts/analysis/survival_turnbull.csv` |
| §4.4 censoring: 2,041 interval, 49 right-censored, 16 of them at 0 days | `artifacts/analysis/survival_intervals.csv` (`type` column), `artifacts/analysis/survival_summary.json` |
| §4.4 sparse-year rule evaluated, no exclusions (min 3 snapshots, 2011 and 2022) | `artifacts/analysis/sparse_year_check.txt` |
| §4.5 bounds check: PASS at 30/90/180/365 d; 730/1095 d not assessable (n<20 at risk) | `artifacts/analysis/bounds_check.csv` |
| §3.7 performance extraction: 4,325 rows / 141 snapshots (identical to the roster count); 2,569 with growth, 2,270 with subscribers, 432 with a rating, 956 with a weekly series; windowed extraction (a card lacking a field yields empty, never a neighbour's value) | `artifacts/performance/provider_performance.csv`, `artifacts/performance/extraction_summary.json`; rule in `src/extract_performance.py::parse_snapshot` |
| §3.7 era-dependence: growth field absent 2011–2016 (0 of 1,092 rows), first present in the 2017-08-28 capture, 73 of 141 captures carry it; coverage by year | `artifacts/performance/extraction_coverage.csv` (141 rows), `artifacts/performance/extraction_summary.json` (`coverage_by_year`) |
| §3.8 clustered bootstrap (2,000 resamples, seed 20260723, percentile, provider as cluster); ≥8-per-side stratum rule; ≥5 roster / ≥3 survivor transition rule | `artifacts/analysis/survivorship_bias_summary.json` (`bootstrap`), `src/survivorship_bias.py` |
| §4.6 comparison 1: visibility-weighted median 154.0 [137.0, 173.0] vs entry-cohort 104.5 [96.0, 114.0], gap +49.5 pp | `artifacts/analysis/survivorship_bias_summary.json` (`comparison_1_…`) |
| §4.6 comparison 2: at first appearance, seen again 155.5 [123.99, 184.0] (n=390) vs seen once 90.5 [83.0, 101.0] (n=1,014), gap +65.0 pp, intervals non-overlapping | `artifacts/analysis/survivorship_bias_summary.json` (`comparison_2_…`) |
| §4.6 comparison 3: 71 of 72 adjacent growth-bearing transitions; median delta +64.0 pp; positive in 68 (95.8%) | `artifacts/analysis/survivorship_bias.csv` (71 rows), `artifacts/analysis/survivorship_bias_summary.json` (`comparison_3_…`) |
| §4.6 comparison 4: confound real (median displayed track record 1 y vs 0 y); gaps +40/+64/+93/+71 pp at 0/1/2/3 years; intervals separate at 0 and 1 year only | `artifacts/analysis/survivorship_bias_summary.json` (`comparison_4_stratified_by_track_record`) |
| §4.7 Figures 1, 2 and 3 | `paper/figures/fig1_survival.png`, `paper/figures/fig2_turnover.png`, `paper/figures/fig3_survivorship_bias.png` (regenerated by `src/make_figures.py`) |

Claims the artifacts **do** support, stated at their exact scope: how long provider identities remain visible; how fast the roster turns over; how the *displayed* growth distribution a visitor encounters differs from the entering cohort's (exposure); and that providers who go on to remain visible were already displaying higher figures on their first observed card (selection at entry), a gap that survives stratification on displayed track-record length in the two well-populated bands.

Claims the artifacts do **not** support, and which the manuscript therefore does not make: any statement about **realised or audited performance** — the extracted figures are what the card displayed, no returns data exists in this corpus for survivors or for the disappeared, and no claim is made that survivors subsequently performed better or that the disappeared lost money; any **causal** claim about why providers disappear or why survivors' displayed figures are higher; any **rank-based** result (see the `dom_order` caveat, which the performance covariates do not lift); any **covariate hazard model** (Finkelstein / Allison remain unfitted, so no hazard ratio appears anywhere); and any **death confirmation beyond index-roster absence** (the protocol's terminal live status sweep has not been run — declared in manuscript §6). Two further scope limits: the bias analysis covers 2017-08 → 2026-07, not the full 2011–2026 span, and the 2-year and 3-year track-record strata have overlapping intervals and establish nothing on their own.

## Figures

Paper figures live in `paper/figures/` and regenerate deterministically from the committed artifacts via `src/make_figures.py`, which runs under any Python with matplotlib (the analysis scripts in `src/` remain stdlib-only). Figure 3 (`fig3_survivorship_bias.png`) plots the displayed-performance bias: selection at entry, the same comparison within displayed-track-record bands, and the per-transition distribution of survivor-minus-roster medians.

One reproducibility note for `src/survivorship_bias.py`: a single seeded generator is threaded through all bootstrap blocks, so running a subset of the comparisons changes the draws consumed by the later ones. Point estimates are unaffected; interval endpoints shift slightly. The committed `artifacts/analysis/survivorship_bias_summary.json` is authoritative and is what the manuscript quotes.

Related repositories by the same author: [pump-and-dump-replication-audit](https://github.com/nathanskill/pump-and-dump-replication-audit) · [alert-burden-audit](https://github.com/nathanskill/alert-burden-audit) · [evidence-separated-trading-screening](https://github.com/nathanskill/evidence-separated-trading-screening)

License: MIT.
