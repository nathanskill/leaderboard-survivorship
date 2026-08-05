# Leaderboard Survivorship (REF-2026-018)

Working title: *Vanishing Winners: Interval-Censored Survival of Signal-Provider Visibility on a Public Copy-Trading Leaderboard, 2011–2026*

Status: protocol frozen before extraction · both primary endpoints analysed · displayed-performance bias quantified · terminal status sweep run · manuscript at draft v0.2. Not submitted, not peer reviewed, not a preprint.

## The question

What happens to signal providers *after* they reach the public leaderboard of a retail copy-trading marketplace? This study reconstructs the MQL5 signals leaderboard from fifteen years of Wayback Machine captures and estimates three things: how long a provider stays visible after first appearing, how fast the board's membership turns over, and how far the performance distribution a visitor sees diverges from that of everyone who ever appeared.

The field names this gap and declines to measure it. Schneider & Oehler (2021, IRFA 78:101892) write that their platform-side approach "leads to a substantial survivorship bias", because accounts that can no longer be found on the platform drop out of the dataset; their companion paper (Oehler & Schneider 2022) adds that the vanished were likely the underperformers. Platform-side data structurally cannot recover the disappeared. Web archives can.

## What has been done

**Corpus.** 141 monthly snapshots of the archived signals index, one per calendar month with a capture, October 2011 to July 2026, each fetched as unrewritten original bytes and SHA-256-hashed (`artifacts/manifests/index_fetch_manifest.csv`: 141 rows, every fetch `ok`). Parsing yields 4,325 roster rows and 2,090 distinct provider identities (`artifacts/rosters/index_rosters.csv`). 37 of the 178 months in the span have no archived capture; every gap is tabulated below. Aggregate reporting only — no provider is named anywhere in this repository.

**Survival of visibility (Primary Endpoint 1).** A disappearance is only ever bracketed between two snapshots, never observed exactly, so the estimator is the Turnbull NPMLE for interval-censored data, implemented from scratch in standard-library Python (`src/survival.py`) and covered by 8 analytic unit tests (`tests/test_survival.py`) — one of which caught a support-set bug before any number was reported. Median visibility is 11 days, and the manuscript insists this be read as "under a fortnight, imprecisely located": 57.4% of the estimated mass sits in three support intervals whose endpoints are the three shortest capture gaps in the corpus. The marks are S(30d)=0.367, S(90d)=0.2143, S(180d)=0.1109 and S(365d)=0.039; 96% of provider identities are gone from the board within a year of first appearing. All four assessable marks lie inside a naive Kaplan–Meier bound envelope, and the 2- and 3-year marks are declared not assessable (fewer than 20 at risk) rather than passed (`artifacts/analysis/bounds_check.csv`).

**Turnover (Primary Endpoint 2).** Mean adjacent-snapshot turnover is 54.4% across 140 transitions. 65.8% of providers appear in exactly one snapshot; 93.6% appear in five or fewer (`artifacts/analysis/turnover_summary.json`, `appearance_distribution.csv`).

**Displayed-performance bias.** From August 2017 the archived cards carry their own performance figures, extracted from the same bytes with no further fetching: 4,325 rows, 2,569 with a displayed growth percentage (`artifacts/performance/`). The distribution a visitor encounters is shifted upward against the entering cohort: median displayed growth 154.0% versus 104.5%. At each provider's first observed card, those later seen again already display 155.5% against 90.5% for those never seen again — a gap of +65.0 points whose provider-clustered bootstrap interval [30.5, 93.0] excludes zero. The survivor median exceeds the roster median in 68 of 71 snapshot transitions. The obvious confound, that displayed growth is cumulative and survivors could simply be older, is real (median displayed track record 1 year versus 0) and was tested: the gap persists in every displayed-track-record band (+40, +64, +93, +71 points at 0–3 years), with an interval excluding zero in the two well-populated bands and covering zero in the two thin ones (`artifacts/analysis/survivorship_bias_summary.json`). Every figure here is displayed performance, not audited performance.

**Terminal live status sweep.** The frozen protocol defines death as roster absence confirmed by one polite live sweep at analysis time. The sweep ran on 1 August 2026, closing a deviation the manuscript had until then declared openly. 309 departed providers (at most 20 per last-seen year, seed 20260723) received one HEAD request each, 2 seconds apart, alongside a control of all 49 providers still on the final archived roster. 18 of 309 departed pages resolve (5.8%) against 49 of 49 controls; at matched recency, 14 of 20 against 37 of 37; and no departed provider last seen before 2025 resolves at all — 0 of 269 across 2011–2024, then 4 of 20 in 2025 and 14 of 20 in 2026 (`artifacts/status/status_summary.json`). Leaving the board is followed by removal of the provider's page on a lag of roughly one to two years, not simultaneously. The sweep reads one date only. It dates no removal, and no coded death was re-classified on it.

The current draft is [`paper/manuscript_draft_v0.2.md`](paper/manuscript_draft_v0.2.md); v0.1 is retained unedited for the record, and [`paper/README.md`](paper/README.md) logs exactly what changed between them and when. Three figures regenerate deterministically from the committed artifacts.

## The discipline

The protocol was frozen before any extraction (annotated tag `v1.0-protocol-freeze`, 25 July 2026) and fixes the endpoints, the cohort rule, the interval-censored death definition and the contribution wording ([`protocol/locked_protocol_v1.0.md`](protocol/locked_protocol_v1.0.md)). The frozen file is never edited. Corrections become numbered amendments under [`protocol/amendments/`](protocol/amendments/).

There has been one. The frozen text claimed "1,322 index snapshots across 100 distinct months"; extraction produced 141 monthly snapshots across 141 distinct months, a direct contradiction. [Erratum-001](protocol/amendments/erratum-001-snapshot-counts.md) records the extraction-time CDX query verbatim, rules that count authoritative, and states plainly that the freeze-time figure cannot be reproduced because its query was never written down. The 1,322 survives only as what it was: raw CDX capture records before monthly collapsing, from a check that predates the pipeline.

Two later self-corrections are preserved rather than tidied away. An early version of the bias script threaded one random generator through every bootstrap block, so adding the stratified comparison shifted intervals that had already been reported (point estimates unchanged). Seeding is now per block, `Random("<master seed>:<block>")`, so any comparison reproduces its interval in isolation, and the stale endpoints quoted in commit `a9a8db0` are left standing in the history as the argument for the practice. The committed `survivorship_bias_summary.json` is authoritative.

Second, the standing claim that no individual is named was audited rather than trusted (2 August 2026). None of the 13 committed CSVs or 5 JSON artifacts carries a provider name, account handle, avatar URL or free-text field, and none of the 1,193 account handles or 640 display names present in the gitignored raw HTML appears in any commit on any ref. Every path that has ever existed in the history is still tracked: 41 at audit time, 42 now — the 42nd being the audit commit's own addition of `src/pseudonymise.py`.

That script is the open decision. Raw signal ids remain in 5 artifacts across 11,098 rows as join keys. They are a re-identification vector, since each id resolves to a provider page, and they are also what makes the corpus reproducible against the archive. [`src/pseudonymise.py`](src/pseudonymise.py) implements the alternative in a mapped and an irreversible mode and is committed unrun; its docstring explains why pseudonymising would not anonymise the corpus — `(timestamp, dom_order)` is unique on all 4,325 roster rows, so re-derivation restores the mapping. No artifact has been pseudonymised. The reasoning, with its costs, is in manuscript §7.2.

## Reproducing

```
python3 src/extract.py --index          # enumerate monthly captures via the CDX API
python3 src/extract.py --fetch-index    # fetch raw bytes into data/; verify against the SHA-256 manifest
python3 src/extract.py --parse-index    # parse per-snapshot rosters
python3 src/turnover.py
python3 src/survival.py
python3 src/bounds_check.py
python3 src/extract_performance.py      # offline: re-reads the already-fetched files
python3 src/survivorship_bias.py
python3 src/make_figures.py             # the one script that needs matplotlib
python3 -m unittest discover -s tests   # 8 tests covering the Turnbull estimator
```

The three extraction stages are mutually exclusive flags; run them one at a time, in that order. Everything except figure generation uses only the Python standard library. The raw HTML (gitignored `data/`) is regenerable rather than redistributed: it is third-party archived content, publicly addressable, so a reproducer re-fetches it and checks each file against `artifacts/manifests/index_fetch_manifest.csv`. The status sweep (`src/status_sweep.py`) is the single exception to offline reproducibility, and the exception is inherent: its sample is fully deterministic, but a live status code is a property of the network on the day it was read. The committed `artifacts/status/` files are the record of 1 August 2026, not a target a re-run should match.

## What is not claimed

Nothing here is a statement about realised or audited performance. The extracted figures are what the card displayed; no returns data exists in this corpus for survivors or for the disappeared, and no claim is made that survivors subsequently performed better or that the disappeared lost money. No causal claim is made about why providers disappear or why survivors' displayed figures are higher. No rank-based result is reported: `dom_order` is document order across page sections, not a rank, and the performance covariates do not lift that caveat. No covariate hazard model has been fitted (Finkelstein and Allison remain unfitted), so no hazard ratio appears anywhere. Nothing is claimed about a provider's state at the moment it left the board: the sweep observes one date, so a page that resolves, or does not, on 2026-08-01 says nothing about that provider when it departed.

Four scope limits sit alongside these. The bias analysis covers 2017-08 to 2026-07, not the full span. The 2- and 3-year track-record strata are thin and establish nothing on their own. The sweep's pooled 5.8% is a within-stratum sample description, not a population-weighted rate. And the sweep's control contains no provider first appearing before 2024, so a page-retirement policy operating only on longer timescales is not excluded by the control alone.

Priority is not claimed for longitudinal leaderboard collection either. Kawai et al. (2024) collected repeated API snapshots of two crypto copy-trading leaderboards; what is new here is the estimator and the bias quantification (frozen wording, protocol §3).

Manuscript §5.6 places the measurement beside two regulatory observations — IOSCO's 2025 reports on imitative trading and finfluencers, and the FCA's December 2024 CFD portfolio letter — as adjacent observations only. This study found no evidence of market manipulation and has no instrument capable of finding any: the corpus holds no order book, trade record, timing or account-level data.

## Snapshot coverage: missing months

The 178-month span 2011-10 → 2026-07 has 37 months with no archived capture of the index page. Per protocol §6 these are reported as exclusions; the interval-censored estimator absorbs irregular spacing rather than assuming it away, but the Nov 2017 – Jun 2018 gap (8 consecutive months) widens every disappearance interval that brackets it.

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

Every quantitative claim in the manuscript is traceable to a committed artifact. Section numbers refer to [`paper/manuscript_draft_v0.2.md`](paper/manuscript_draft_v0.2.md); §§3.7, 3.8 and 4.6 were new in v0.2, and §§3.9 and 4.7 (the terminal sweep) were added by the in-place revision of 2 August 2026, which renumbered the Figures subsection to §4.8.

| Manuscript claim | Artifact |
|---|---|
| §3.1 CDX query, 141 monthly snapshots, 2011-10 → 2026-07, 37 uncaptured months | `artifacts/snapshots/index_snapshots.csv`; query verbatim in `src/extract.py::cmd_index` and `protocol/amendments/erratum-001-snapshot-counts.md` |
| §3.2 raw `id_` replay fetch, 141/141 successes, SHA-256 per file | `artifacts/manifests/index_fetch_manifest.csv` (141 rows, all `status=ok`) |
| §3.3 rosters: 4,325 rows / 141 snapshots; roster size min 10, median 30, max 53; `dom_order` is DOM order, not a rank | `artifacts/rosters/index_rosters.csv`; caveat in `src/extract.py::cmd_parse_index` |
| §3.5 Turnbull NPMLE, 52 support intervals; 8 unit tests | `artifacts/analysis/survival_turnbull.csv`; `tests/test_survival.py` |
| §4.1 corpus: 2,090 distinct providers; snapshot gaps 7–282 days, median 30 | `artifacts/analysis/turnover_summary.json`, `survival_summary.json`, `artifacts/snapshots/index_snapshots.csv` |
| §4.2 turnover: mean 54.4% over 140 transitions; per-year table; unweighted yearly mean 55.2% (Figure 2 line) | `artifacts/analysis/turnover_summary.json`, `turnover_by_year.csv` |
| §4.3 appearance distribution: 1,376 (65.8%) seen once; 79.4% ≤2; 93.6% ≤5 | `artifacts/analysis/appearance_distribution.csv` |
| §4.4 survival S(30d)=0.367, S(90d)=0.2143, S(180d)=0.1109, S(365d)=0.039; median 11 d; 57.4% of mass in the three support intervals ≤11 d | `artifacts/analysis/survival_summary.json`, `survival_turnbull.csv` |
| §4.4 censoring: 2,041 interval, 49 right-censored, 16 of them at 0 days | `artifacts/analysis/survival_intervals.csv` (`type` column), `survival_summary.json` |
| §4.4 sparse-year rule evaluated, no exclusions (min 3 snapshots, 2011 and 2022) | `artifacts/analysis/sparse_year_check.txt` |
| §4.5 bounds check: PASS at 30/90/180/365 d; 730/1095 d not assessable (n<20 at risk) | `artifacts/analysis/bounds_check.csv` |
| §3.7 performance extraction: 4,325 rows / 141 snapshots (identical to the roster count); 2,569 with growth, 2,270 with subscribers, 432 with a rating, 956 with a weekly series; a card lacking a field yields empty, never a neighbour's value | `artifacts/performance/provider_performance.csv`, `extraction_summary.json`; rule in `src/extract_performance.py::parse_snapshot` |
| §3.7 era-dependence: growth absent 2011–2016 (0 of 1,092 rows), first present in the 2017-08-28 capture, 73 of 141 captures carry it | `artifacts/performance/extraction_coverage.csv` (141 rows), `extraction_summary.json` (`coverage_by_year`) |
| §3.8 clustered bootstrap (2,000 resamples, percentile, provider as cluster) with per-block seeding, and direct intervals for the difference of medians; ≥8-per-side stratum rule; ≥5 roster / ≥3 survivor transition rule | `artifacts/analysis/survivorship_bias_summary.json` (`bootstrap`, `inference_note`), `src/survivorship_bias.py::block_rng`, `::boot_gap_ci` |
| §4.6 comparison 1: visibility-weighted median 154.0 [137.97, 173.0] vs entry-cohort 104.5 [96.0, 113.5], gap +49.5 pp (no interval, by choice — the gap is partly definitional) | `artifacts/analysis/survivorship_bias_summary.json` (`comparison_1_…`) |
| §4.6 comparison 2: at first appearance, seen again 155.5 [119.5, 184.01] (n=390) vs seen once 90.5 [83.5, 101.0] (n=1,014); difference +65.0 pp [30.5, 93.0], excludes zero | `artifacts/analysis/survivorship_bias_summary.json` (`comparison_2_…`, `median_gap_ci95`) |
| §4.6 comparison 3: 71 of 72 adjacent growth-bearing transitions eligible; median delta +64.0 pp; positive in 68 (95.8%) | `artifacts/analysis/survivorship_bias.csv` (71 rows), `survivorship_bias_summary.json` (`comparison_3_…`) |
| §4.6 comparison 4: confound real (median displayed track record 1 y vs 0 y); gaps +40 [7.0, 65.01], +64 [29.0, 95.0], +93 [−16.51, 269.01], +71 [−199.0, 205.0] pp at 0/1/2/3 years; difference interval excludes zero at 0 and 1 year | `artifacts/analysis/survivorship_bias_summary.json` (`comparison_4_stratified_by_track_record`) |
| §3.9 sweep design: 309 departed sampled ≤20 per last-seen year from the 2,041 coded dead (seed 20260723, 15.1% of the frame); control = all 49 right-censored providers; one HEAD per `/en/signals/<id>` 2 s apart, 358 requests total, status codes only; `robots.txt` (fetched 2026-08-01) permits that path | `src/status_sweep.py` (module docstring, `head`, `main`), `artifacts/status/status_summary.json` (`method`) |
| §4.7 live status on 2026-08-01: 18/309 departed pages resolve (5.8%) vs 49/49 controls; matched recency 14/20 vs 37/37; 0/269 for last-seen years 2011–2024, 4/20 in 2025, 14/20 in 2026; control tenure limited to first appearances in 2024–2026 | `artifacts/status/status_summary.json`, `live_status.csv` (309 rows), `control_still_listed.csv` (49 rows) |
| §4.8 Figures 1, 2 and 3 | `paper/figures/fig1_survival.png`, `fig2_turnover.png`, `fig3_survivorship_bias.png` (regenerated by `src/make_figures.py`) |

## Figures

Paper figures live in `paper/figures/` and regenerate from the committed artifacts via `src/make_figures.py`; no re-fetching is involved.

One caveat worth stating here as well as in the paper. Figure 3's error bars are the intervals for each group's own median, drawn separately. The paper's inference rests on the direct bootstrap interval for the *difference* of medians, which lives in the summary artifact and is not drawable on a chart of levels. In the 0-year band the two disagree — the drawn bars touch at 69.0 while the difference interval [7.0, 65.01] excludes zero — and the difference interval is the reported result.

---

Related repositories by the same author: [pump-and-dump-replication-audit](https://github.com/nathanskill/pump-and-dump-replication-audit) · [alert-burden-audit](https://github.com/nathanskill/alert-burden-audit) · [evidence-separated-trading-screening](https://github.com/nathanskill/evidence-separated-trading-screening)

MIT licence (`LICENSE`).
