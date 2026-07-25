# Locked Protocol v1.0 — Signal-Provider Survivorship on a Public Copy-Trading Leaderboard

Status: **FROZEN at the commit that introduces this file.** Changes require a numbered amendment; amendments may restrict claims but may not alter endpoints, the cohort rule, or the death definition after extraction begins.

Author: Zhennan (Nathan) Yu, independent researcher, Sydney.

## 1. Research question

In the public MQL5 signal marketplace, what happens to signal providers *after* they appear on the public top-N leaderboard — their disappearance hazard, the leaderboard's membership turnover, and the gap between the **leaderboard view** (what a prospective subscriber sees) and the **entering-cohort distribution** (what happened to everyone who ever appeared)?

## 2. Motivation: a limitation the field states and declines to measure

Schneider & Oehler (2021, *International Review of Financial Analysis* 78:101892, §3) write of their ZuluTrade data: *"This approach leads to a substantial survivorship bias as accounts which can no longer be found by using the platform's search function – indicating abandonment or inactivity – are not included in the dataset."* Their companion open-access paper (Oehler & Schneider 2022, *Review of Managerial Science* 17(4):1269–1331, p. 1276) states the same and adds that vanished providers *"had likely been administering underperforming"* portfolios. The field therefore names this bias, judges the disappeared to be disproportionately poor performers, and reports that platform-side data cannot recover them.

Web archives can. This study recovers the disappeared from archived leaderboard snapshots and estimates what platform-side data structurally cannot.

## 3. Contribution claim (frozen wording)

> We provide the **first survival-analytic estimate** of signal-provider attrition on a retail copy-trading marketplace, and the **first quantification of the resulting bias in the platform's observable performance distribution**. Prior work has either acknowledged this survivorship bias without measuring it (Oehler & Schneider 2022; Schneider & Oehler 2021) or collected longitudinal leaderboard snapshots for other purposes, reporting listing lifetimes only incidentally (Kawai et al. 2024).

**Drafting rules (frozen, non-negotiable):**
1. **Never claim first longitudinal leaderboard snapshotting.** Kawai et al. (CHI 2024) collected repeated public-API snapshots of two crypto copy-trading leaderboards (TraderWagon, Bybit) and report a median listing lifetime of 2.9 days. What is new here is the estimator and the bias quantification, not the collection.
2. **State the unit of analysis in the opening.** This study's unit is the **provider identity**; Kawai et al. track portfolios/listings. A leader closing a losing portfolio and opening a new one is a different event from a provider leaving, and the two are never conflated in coding.
3. **Define "survivorship" against prior usage.** Tong & Preda (2023, *Socio-Economic Review* 22(4):1865–1890) use it for *retail investor* retention. Here it means *leaderboard provider* disappearance. One sentence in the introduction distinguishes the two.

## 4. Endpoints (order fixed)

- **Primary 1 — disappearance hazard.** Survival curve for providers after first appearance in the top-N, estimated by the Turnbull (1976) NPMLE for interval-censored data: disappearance is only bracketed between two archive snapshots, never observed exactly. Death = provider page absent (HTTP 404 / removed from index) at a later snapshot, confirmed by one polite live status sweep at analysis time.
- **Primary 2 — leaderboard turnover.** Retention/replacement rate of top-N membership between adjacent snapshots, stratified by year.
- **Secondary (explicitly demoted, censoring reported in full).** Whether past public rank predicts subsequently observable performance. Heavily right-censored; reported with a complete censoring table; excluded from abstract claims.

## 5. Data (all lawful and public; no IRB surface)

- **Primary:** Wayback Machine CDX + raw archived HTML of `mql5.com/en/signals` (index) and `/en/signals/<id>` (provider pages). Verified independently: 1,322 index snapshots across 100 distinct months; ~33k archived provider pages (12,432 exact-id pages); pages are **server-rendered**, with Growth / Subscribers / Reliability / Trades / Started / Weeks / Leverage present in static DOM (no JS execution needed); ~15–20% of provider pages return 404, the death signal.
- **Secondary:** one polite live status-code sweep at analysis time (robots.txt respected, human-rate limited, status codes only — no content scraping).
- Providers are pseudonymous commercial vendors selling signals to the public. **Reporting is aggregate only; no individual provider is named in any output.** No private messages, no user data, no personal identifiers.

## 6. Cohort design (frozen; parameters written into the freeze commit)

- **Entry:** a provider first observed in the top-N of an index snapshot. N and the snapshot set are fixed at freeze.
- **Follow-up:** all subsequent available snapshots plus the terminal live sweep.
- **Sparse-year rule (mechanical):** any year with fewer than 2 usable snapshots is reported descriptively only and excluded from the survival model. Threshold fixed at freeze; exclusions reported with counts.
- **Renaming/re-listing:** a provider re-appearing under a new listing id is, by default, coded as a *new listing* and the prior listing as a death, because archives cannot establish identity continuity. This conservative rule is stated in the paper and its direction of bias is discussed (it can only overstate attrition, never understate it).

## 7. Analysis

Turnbull NPMLE survival curves with interval-censored intervals defined by snapshot pairs; Finkelstein (1986) interval-censored proportional hazards (or Allison (1982) discrete-time hazard where snapshots fall on a fixed grid) for covariate effects; year-stratified turnover tables; and the headline comparison — the performance distribution *as displayed on the leaderboard* versus *as realised across the entering cohort*.

## 8. Conflict-of-interest disclosure (in all outputs)

The author is employed full-time at a retail FX/CFD brokerage in Sydney and operates independent Chinese-language trading-education web properties. The employer does not distribute MQL5-integrated copy-trading products (confirmed 25 July 2026), so no employer commercial interest attaches to the studied platform. No employer data, systems, or client information is used. Research data does not enter the author's commercial content channels before publication; after publication, only the published paper is cited.

## 9. Language discipline

No individual provider is characterised as a scam or fraud. Findings are distributional statements about an information environment. Disappearance is reported as disappearance, not as failure, absent evidence.

## 10. Venue

WEIS 2027 (primary) or ConPro '27; arXiv q-fin.TR + cs.CY preprint on completion.
