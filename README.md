# Leaderboard Survivorship (REF-2026-018)

Status: `PROTOCOL FROZEN / EXTRACTION NOT STARTED / NO RESULTS YET`

What happens to signal providers *after* they reach the public leaderboard of a retail copy-trading marketplace? This study reconstructs the MQL5 signal leaderboard from a decade of web archives and estimates provider disappearance, leaderboard turnover, and the gap between the **leaderboard view** a prospective subscriber sees and the **entering-cohort distribution** of everyone who ever appeared.

The field already names this gap and declines to measure it. Schneider & Oehler (2021, IRFA 78:101892) report that their platform-side data *"leads to a substantial survivorship bias as accounts which can no longer be found … are not included in the dataset"*, and their companion paper judges the vanished to have been the underperformers. Web archives can recover them.

- **Protocol**: [`protocol/locked_protocol_v1.0.md`](protocol/locked_protocol_v1.0.md) — frozen before extraction (tag `v1.0-protocol-freeze`). Endpoints, cohort rule, death definition and the conservative renaming rule are fixed there.
- **Method**: interval-censored survival (Turnbull NPMLE) — disappearance is only ever bracketed between two archive snapshots, never observed exactly.
- **Data**: Wayback Machine CDX + archived HTML, verified independently: 1,322 index snapshots across 100 months, ~33k archived provider pages, server-rendered fields in static DOM. Aggregate reporting only; no provider is named.
- **No results have been produced yet.** Weak or null results will be reported in full when they exist.

Related repositories by the same author: [pump-and-dump-replication-audit](https://github.com/nathanskill/pump-and-dump-replication-audit) · [alert-burden-audit](https://github.com/nathanskill/alert-burden-audit) · [evidence-separated-trading-screening](https://github.com/nathanskill/evidence-separated-trading-screening)

License: MIT.
