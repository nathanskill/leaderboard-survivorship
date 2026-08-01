# Leaderboard Survivorship (REF-2026-018)

Status: `PROTOCOL FROZEN / EXTRACTION COMPLETE / PRIMARY ENDPOINTS 1-2 ANALYSED`

What happens to signal providers *after* they reach the public leaderboard of a retail copy-trading marketplace? This study reconstructs the MQL5 signal leaderboard from a decade of web archives and estimates provider disappearance, leaderboard turnover, and the gap between the **leaderboard view** a prospective subscriber sees and the **entering-cohort distribution** of everyone who ever appeared.

The field already names this gap and declines to measure it. Schneider & Oehler (2021, IRFA 78:101892) report that their platform-side data *"leads to a substantial survivorship bias as accounts which can no longer be found … are not included in the dataset"*, and their companion paper judges the vanished to have been the underperformers. Web archives can recover them.

- **Protocol**: [`protocol/locked_protocol_v1.0.md`](protocol/locked_protocol_v1.0.md) — frozen before extraction (tag `v1.0-protocol-freeze`). Endpoints, cohort rule, death definition and the conservative renaming rule are fixed there. Post-freeze corrections are numbered errata under [`protocol/amendments/`](protocol/amendments/); the frozen file is never edited.
- **Method**: interval-censored survival (Turnbull NPMLE) — disappearance is only ever bracketed between two archive snapshots, never observed exactly.
- **Data**: Wayback Machine CDX + archived HTML of the `mql5.com/en/signals` index. The CDX API reports 1,322 raw captures of the index URL; the pipeline retains **one capture per calendar month, 141 monthly snapshots spanning 178 months (2011-10 → 2026-07)**, each fetched as unrewritten original bytes and SHA-256-hashed (`artifacts/manifests/`). 37 of the 178 months have no archived capture (table below). The frozen protocol's "1,322 index snapshots across 100 distinct months" is reconciled in [`protocol/amendments/erratum-001-snapshot-counts.md`](protocol/amendments/erratum-001-snapshot-counts.md). Aggregate reporting only; no provider is named.
- **Results** (committed under [`artifacts/analysis/`](artifacts/analysis/)): 2,090 distinct providers; mean adjacent-snapshot turnover 54.4%; 65.8% of providers appear in exactly one snapshot; Turnbull survival of leaderboard visibility S(30d)=0.367, S(90d)=0.2143, S(180d)=0.1109, S(365d)=0.039; all assessable marks lie inside the naive Kaplan-Meier bound envelope (`bounds_check.csv`). The frozen sparse-year rule (protocol §6) was evaluated: no year falls below the threshold (`sparse_year_check.txt`).

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

## Figures

Paper figures live in `paper/figures/` and regenerate deterministically from the committed artifacts via `src/make_figures.py`, which runs under any Python with matplotlib (the analysis scripts in `src/` remain stdlib-only).

Related repositories by the same author: [pump-and-dump-replication-audit](https://github.com/nathanskill/pump-and-dump-replication-audit) · [alert-burden-audit](https://github.com/nathanskill/alert-burden-audit) · [evidence-separated-trading-screening](https://github.com/nathanskill/evidence-separated-trading-screening)

License: MIT.
