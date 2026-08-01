# Leaderboard Survivorship (REF-2026-018)

Status: `PROTOCOL FROZEN / EXTRACTION COMPLETE / PRIMARY ENDPOINTS 1-2 ANALYSED / PERFORMANCE COVARIATES EXTRACTED / SURVIVORSHIP BIAS QUANTIFIED / TERMINAL LIVE STATUS SWEEP RUN / SECOND MANUSCRIPT DRAFT (REVISED IN PLACE) / NOT SUBMITTED`

Working title:

> Vanishing Winners: Interval-Censored Survival of Signal-Provider Visibility on a Public Copy-Trading Leaderboard, 2011–2026

Current draft: [`paper/manuscript_draft_v0.2.md`](paper/manuscript_draft_v0.2.md); the first full draft is retained unedited at [`paper/manuscript_draft_v0.1.md`](paper/manuscript_draft_v0.1.md) (see [`paper/README.md`](paper/README.md)). Not submitted, not peer reviewed, not a preprint.

What happens to signal providers *after* they reach the public leaderboard of a retail copy-trading marketplace? This study reconstructs the MQL5 signal leaderboard from a decade of web archives and estimates provider disappearance, leaderboard turnover, and the gap between the **leaderboard view** a prospective subscriber sees and the **entering-cohort distribution** of everyone who ever appeared.

The field already names this gap and declines to measure it. Schneider & Oehler (2021, IRFA 78:101892) report that their platform-side data *"leads to a substantial survivorship bias as accounts which can no longer be found … are not included in the dataset"*, and their companion paper judges the vanished to have been the underperformers. Web archives can recover them.

- **Protocol**: [`protocol/locked_protocol_v1.0.md`](protocol/locked_protocol_v1.0.md) — frozen before extraction (tag `v1.0-protocol-freeze`). Endpoints, cohort rule, death definition and the conservative renaming rule are fixed there. Post-freeze corrections are numbered errata under [`protocol/amendments/`](protocol/amendments/); the frozen file is never edited.
- **Method**: interval-censored survival (Turnbull NPMLE) — disappearance is only ever bracketed between two archive snapshots, never observed exactly.
- **Data**: Wayback Machine CDX + archived HTML of the `mql5.com/en/signals` index. The CDX API reports 1,322 raw captures of the index URL; the pipeline retains **one capture per calendar month, 141 monthly snapshots spanning 178 months (2011-10 → 2026-07)**, each fetched as unrewritten original bytes and SHA-256-hashed (`artifacts/manifests/`). 37 of the 178 months have no archived capture (table below). The frozen protocol's "1,322 index snapshots across 100 distinct months" is reconciled in [`protocol/amendments/erratum-001-snapshot-counts.md`](protocol/amendments/erratum-001-snapshot-counts.md). Aggregate reporting only; no provider is named.
- **Results — visibility** (committed under [`artifacts/analysis/`](artifacts/analysis/)): 2,090 distinct providers; mean adjacent-snapshot turnover 54.4%; 65.8% of providers appear in exactly one snapshot; Turnbull survival of leaderboard visibility S(30d)=0.367, S(90d)=0.2143, S(180d)=0.1109, S(365d)=0.039; all assessable marks lie inside the naive Kaplan-Meier bound envelope (`bounds_check.csv`). The frozen sparse-year rule (protocol §6) was evaluated: no year falls below the threshold (`sparse_year_check.txt`).
- **Results — displayed-performance bias** (committed under [`artifacts/performance/`](artifacts/performance/) and [`artifacts/analysis/`](artifacts/analysis/)): the performance figures the archived cards themselves carried were extracted from the same bytes with no further fetching — 4,325 provider rows (identical to the roster count), 2,569 with a displayed growth percentage, present only from 2017-08 onward. The distribution a visitor encounters is shifted upward relative to the entering cohort (median displayed growth 154.0% vs 104.5%), and at each provider's own first card those later seen again already display 155.5% against 90.5% for those never seen again — a difference of +65.0 pp whose provider-clustered bootstrap interval [30.5, 93.0] excludes zero. The survivor median exceeds the roster median in 68 of 71 transitions (median delta +64.0 pp). The obvious confound — cumulative growth since a stated inception year, so survivors may simply be older — is real (median displayed track record 1 year vs 0) and was tested: the gap persists within every reported band (+40, +64, +93, +71 pp at 0–3 years) and its interval excludes zero in the two well-populated bands and covers zero in the two thin ones. Every figure is **displayed**, not audited, performance.
- **Results — terminal live status sweep** (committed under [`artifacts/status/`](artifacts/status/)): the frozen protocol (§4) defines death as index absence "confirmed by one polite live status sweep at analysis time". That sweep ran on **1 August 2026** (`src/status_sweep.py`), closing the deviation the previous draft had declared. 309 departed providers were sampled stratified by last-seen year (≤20/year, seed 20260723) and checked with one HEAD request per provider page 2 s apart, alongside a **control group of all 49 right-censored providers** (those present on the final archived roster). **18 of 309 departed pages still resolve (5.8%) against 49 of 49 controls (100%)**; at matched recency the contrast is **14 of 20 against 37 of 37**; and **no departed provider last seen before 2025 resolves at all — 0 of 269 across 2011–2024**, 4 of 20 in 2025, 14 of 20 in 2026. Leaving the leaderboard is followed by removal of the provider's page on a lag of roughly **one to two years**, not simultaneously with it. The control is what makes this readable — without it a 404 could reflect a page-retirement policy indifferent to who is behind the page — and its own limit is recorded in the artifact: no control provider first appears before 2024, so a retirement policy operating only on longer timescales is not excluded by the control alone. The sweep is a **single point in time**: a live page today says nothing about that provider's state when it left the roster. The endpoint is unchanged — it remains leaderboard visibility, no result was re-coded on live status, and no reported number moved.

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

Every quantitative claim in the manuscript is traceable to a committed artifact. Manuscript sections refer to [`paper/manuscript_draft_v0.2.md`](paper/manuscript_draft_v0.2.md); §§3.7, 3.8, 4.6 and Figure 3 were new in v0.2, and §§3.9 and 4.7 (the terminal status sweep) were added by the in-place revision of 2 August 2026, which renumbered the Figures subsection from §4.7 to §4.8.

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
| §3.8 clustered bootstrap (2,000 resamples, percentile, provider as cluster) with **per-block seeding** `Random("<master seed 20260723>:<block>")`, and direct intervals for the difference of medians; ≥8-per-side stratum rule; ≥5 roster / ≥3 survivor transition rule | `artifacts/analysis/survivorship_bias_summary.json` (`bootstrap`, `…inference_note`), `src/survivorship_bias.py::block_rng`, `::boot_gap_ci` |
| §4.6 comparison 1: visibility-weighted median 154.0 [137.97, 173.0] vs entry-cohort 104.5 [96.0, 113.5], gap +49.5 pp (no interval, by choice — the gap is partly definitional) | `artifacts/analysis/survivorship_bias_summary.json` (`comparison_1_…`) |
| §4.6 comparison 2: at first appearance, seen again 155.5 [119.5, 184.01] (n=390) vs seen once 90.5 [83.5, 101.0] (n=1,014); difference +65.0 pp [30.5, 93.0], excludes zero | `artifacts/analysis/survivorship_bias_summary.json` (`comparison_2_…`, `median_gap_ci95`) |
| §4.6 comparison 3: 71 of 72 adjacent growth-bearing transitions; median delta +64.0 pp; positive in 68 (95.8%) | `artifacts/analysis/survivorship_bias.csv` (71 rows), `artifacts/analysis/survivorship_bias_summary.json` (`comparison_3_…`) |
| §4.6 comparison 4: confound real (median displayed track record 1 y vs 0 y); gaps +40 [7.0, 65.01], +64 [29.0, 95.0], +93 [−16.51, 269.01], +71 [−199.0, 205.0] pp at 0/1/2/3 years; difference interval excludes zero at 0 and 1 year | `artifacts/analysis/survivorship_bias_summary.json` (`comparison_4_stratified_by_track_record`, `strata_whose_gap_interval_excludes_zero`) |
| §3.9 status sweep design: 309 departed providers sampled ≤20 per last-seen year from the 2,041 coded dead (seed 20260723, 15.1% of the frame); control = all 49 right-censored providers; one HEAD per `/en/signals/<id>` 2 s apart, 358 requests total, status codes only; `robots.txt` fetched 2026-08-01 permits that path and disallows the `deals` / `positions` / `reviews` / `pending-orders` / `new` sub-paths. Provenance note in §3.9: the script writes `live_status.csv` but *reads* `control_still_listed.csv`, so the control's codes are documented by the committed artifact rather than re-issued by the script | `src/status_sweep.py` (module docstring, `head`, `main`), `artifacts/status/status_summary.json` (`method`) |
| §4.7 live status on 2026-08-01: 18/309 departed pages resolve (5.8%) vs 49/49 controls; matched recency 14/20 vs 37/37; 0/269 resolve for last-seen years 2011–2024, 4/20 in 2025, 14/20 in 2026; control tenure limited to first appearances in 2024–2026 | `artifacts/status/status_summary.json`, `artifacts/status/live_status.csv` (309 rows), `artifacts/status/control_still_listed.csv` (49 rows) |
| §4.8 Figures 1, 2 and 3 | `paper/figures/fig1_survival.png`, `paper/figures/fig2_turnover.png`, `paper/figures/fig3_survivorship_bias.png` (regenerated by `src/make_figures.py`) |

Claims the artifacts **do** support, stated at their exact scope: how long provider identities remain visible; how fast the roster turns over; how the *displayed* growth distribution a visitor encounters differs from the entering cohort's (exposure); that providers who go on to remain visible were already displaying higher figures on their first observed card (selection at entry), a gap that survives stratification on displayed track-record length in the two well-populated bands; and, from the terminal sweep, how far leaderboard visibility and platform presence had diverged **on 1 August 2026** — a lag of roughly one to two years between leaving the board and the provider page ceasing to resolve, measured against a still-listed control.

Claims the artifacts do **not** support, and which the manuscript therefore does not make: any statement about **realised or audited performance** — the extracted figures are what the card displayed, no returns data exists in this corpus for survivors or for the disappeared, and no claim is made that survivors subsequently performed better or that the disappeared lost money; any **causal** claim about why providers disappear or why survivors' displayed figures are higher; any **rank-based** result (see the `dom_order` caveat, which the performance covariates do not lift); any **covariate hazard model** (Finkelstein / Allison remain unfitted, so no hazard ratio appears anywhere); and any **statement about a provider's state at the moment it left the board** — the status sweep observes one date, so a page that resolves (or does not) on 2026-08-01 says nothing about that provider when it departed, no coded death was re-classified on it, and the endpoint remains leaderboard visibility. Three further scope limits: the bias analysis covers 2017-08 → 2026-07, not the full 2011–2026 span; the 2-year and 3-year track-record strata have overlapping intervals and establish nothing on their own; and the sweep's pooled 5.8% is a within-stratum sample description, not a population-weighted rate.

## Figures

Paper figures live in `paper/figures/` and regenerate deterministically from the committed artifacts via `src/make_figures.py`, which runs under any Python with matplotlib (the analysis scripts in `src/` remain stdlib-only). Figure 3 (`fig3_survivorship_bias.png`) plots the displayed-performance bias: selection at entry, the same comparison within displayed-track-record bands, and the per-transition distribution of survivor-minus-roster medians.

Figure 3's error bars are the intervals for each group's **own** median, drawn separately. The paper's inference rests on the direct bootstrap interval for the **difference** of medians, which is in the summary artifact and the manuscript tables and is not drawable on a chart of levels; in the 0-year band the two disagree (drawn bars touch at 69.0, difference interval [7.0, 65.01] excludes zero) and the difference interval is the reported result.

One reproducibility note for `src/survivorship_bias.py`: bootstrap seeding is **per block** (`Random("<master seed>:<block name>")`), so blocks are independent — any comparison can be re-run in isolation and reproduce its published interval, and adding or reordering an analysis cannot shift another's. An earlier revision threaded a single generator through every block; adding the stratified comparison then moved the intervals of comparisons 1–3 with point estimates unchanged, which is why the commit message at `a9a8db0` quotes endpoints that no longer match. The committed `artifacts/analysis/survivorship_bias_summary.json` is authoritative and is what the manuscript quotes.

Related repositories by the same author: [pump-and-dump-replication-audit](https://github.com/nathanskill/pump-and-dump-replication-audit) · [alert-burden-audit](https://github.com/nathanskill/alert-burden-audit) · [evidence-separated-trading-screening](https://github.com/nathanskill/evidence-separated-trading-screening)

License: MIT.
