# Vanishing Winners: Interval-Censored Survival of Signal-Provider Visibility on a Public Copy-Trading Leaderboard, 2011–2026

**Zhennan (Nathan) Yu** — Independent Researcher, Sydney, Australia

*DRAFT v0.1 — 1 August 2026. Not submitted, not peer reviewed, not a preprint.* All results were produced under the protocol frozen at repository commit `684241f` (annotated tag `v1.0-protocol-freeze`, 25 July 2026), created **before any data extraction began**. The frozen file is never edited; the single post-freeze amendment is `protocol/amendments/erratum-001-snapshot-counts.md`, discussed openly in Section 3.1. Every quantitative claim below names the committed artifact it comes from; the claims→artifacts map is in the repository `README.md`. No individual provider is named anywhere in this study, and no provider or platform is characterised as fraudulent.

---

## Abstract

Retail copy-trading marketplaces present prospective followers with a public leaderboard of signal providers. What a follower sees is, by construction, the set of providers visible today; those who have already gone are not shown, and platform-side datasets cannot recover them. We reconstruct one such leaderboard from a public web archive and estimate how long providers remain visible on it. From **141 monthly archived snapshots** of the MQL5 signal index spanning **2011-10 to 2026-07** we recover **2,090 distinct provider identities**. Membership is unstable: mean turnover between adjacent snapshots is **54.4%** across 140 transitions, and **65.8%** of providers ever observed appear in **exactly one** snapshot. Because disappearance is only ever bracketed between two captures, never observed exactly, we estimate visibility duration with the Turnbull (1976) nonparametric maximum-likelihood estimator for interval-censored data, implemented directly and unit-tested against eight cases with known analytic answers. Estimated survival of leaderboard visibility after first appearance is **S(30 d) = 0.367**, **S(90 d) = 0.214**, **S(180 d) = 0.111** and **S(365 d) = 0.039**, with a **median of 11 days**. The estimate lies inside the naive Kaplan–Meier bound envelope at **all four assessable marks**; the two longer marks are reported as *not assessable* because fewer than 20 subjects remain at risk there. The endpoint is **leaderboard visibility**, not account closure and not performance: a provider may persist off the leaderboard, and disappearance is reported as disappearance, not as failure. Within that boundary, the leaderboard a prospective follower reads is a length-biased snapshot of a population whose modal entrant is seen once and not again, and roughly 96% of entrants are no longer visible one year after first appearing.

---

## 1. Introduction

A retail copy-trading marketplace sells a simple proposition: here are the traders who are doing well, and you may follow them automatically. The interface carrying that proposition is a leaderboard — a ranked or filtered list of signal providers with growth, subscriber counts and track-record lengths displayed inline. For a prospective follower, that list *is* the market. It is also, structurally, a survivor set. A provider who left last month is not on it; one who left last year has left no trace in it at all. The follower chooses among the visible, with no view of the base rate from which the visible were drawn.

This is the classic survivorship problem of the fund-performance literature [4, 5, 6, 7], relocated into a consumer-facing interface where the population turns over far faster than a hedge-fund database and where the reader is a retail investor rather than an analyst. The problem is well known in the copy-trading literature too — well enough that researchers state it as a limitation of their own data. Schneider & Oehler, studying ZuluTrade signal providers, report that their collection leaves a *"substantial survivorship bias"* because accounts no longer findable through the platform's search function are absent from the dataset [1, §3]; their companion paper adds the judgement that the vanished had likely been running underperforming portfolios [2]. The field therefore names the bias, believes it to be adverse, and reports that platform-side data cannot recover the disappeared.

Web archives can. Archived captures of a public leaderboard page preserve the roster as it stood on the capture date, including the providers who are gone by the next capture. Enumerating those captures over a long enough window turns "who is visible now" into "who was ever visible, and for how long" — which is exactly the quantity the platform-side view cannot supply.

**Contribution.** Following the frozen protocol's narrowed claim, this paper provides the first survival-analytic estimate of signal-provider attrition on a retail copy-trading marketplace. Concretely, this draft delivers the estimator and the visibility-duration result: a Turnbull nonparametric maximum-likelihood survival curve for **how long a provider identity remains visible on the public leaderboard**, and a quantification of the resulting selection bias in the tenure dimension of what a prospective follower sees. Prior work has either acknowledged this survivorship bias without measuring it [1, 2] or collected longitudinal leaderboard snapshots for other purposes, reporting listing lifetimes only incidentally [3]. The frozen contribution wording also claims a first quantification of the bias in the platform's *observable performance distribution*; that second half requires performance covariates which this draft does not yet extract, and Section 6 states plainly that it is not delivered here. We claim only what the artifacts support.

Three boundaries are set at the outset, all fixed in the frozen protocol rather than chosen after seeing results.

*The unit of analysis is the provider identity, not the portfolio or listing.* Kawai et al. [3] collect repeated public-API snapshots of two cryptocurrency copy-trading leaderboards and report that portfolios there are typically short-lived (median 2.9 days). A leader who closes a losing portfolio and opens a new one has performed a portfolio event, not a departure; the two are never conflated in our coding. We claim no priority for longitudinal leaderboard snapshotting — that belongs to [3]. What is new here is the estimator and the bias quantification, not the collection.

*"Survivorship" here means leaderboard-provider disappearance, not retail-investor retention.* Tong & Preda [13] use the term for whether individual retail traders keep trading. This study's subjects are pseudonymous commercial vendors selling signals to the public, and the event is their disappearance from a public listing.

*The endpoint is visibility, not viability.* Disappearance from the archived index is not proof of account closure, business failure, or losses. A provider may drop below a display threshold, be delisted, change listing identity, restrict their signal, or simply stop being rendered near the top of a page whose layout the platform has redesigned. We measure how long a name stays on the board a follower reads, and say nothing more than that.

---

## 2. Related work

### 2.1 Survivorship bias in performance measurement

The methodological ancestry of this study is the fund-performance literature's long argument about what a voluntarily self-listed database omits. Brown, Goetzmann, Ibbotson & Ross [4] formalised how survivorship manufactures apparent persistence out of attrition; Brown, Goetzmann & Ibbotson [5] measured attrition directly in offshore hedge funds and showed the premium that conditioning on survival induces in reported returns. Liang's "living and the dead" comparison [6] is this paper's closest structural template: assemble the graveyard, compare it against the visible set, report the gap. Fung & Hsieh [7] separate survivorship from backfill and instant-history bias — a distinction that maps onto leaderboard mechanics, where a displayed track record may predate the provider's first appearance in the top-N view. Bhardwaj, Gorton & Rouwenhorst [8] supply the closest economic analogue in a retail-facing product: managed accounts sold to individual investors, with high attrition and public track records that systematically overstate what an investor received.

What that literature had, and this setting lacks, is a database vendor who retains dead records. Copy-trading platforms are the opposite: the interface is the dataset, and the interface forgets. The archival approach reconstructs a graveyard that was never maintained.

### 2.2 Interval-censored survival methodology

Disappearance from an archived leaderboard is never observed at a point in time: a provider present at capture *t* and absent at *t+1* left somewhere in the half-open interval (*t*, *t+1*]. This is textbook interval censoring, and the correct nonparametric estimator is Turnbull's [9] empirical distribution function for arbitrarily grouped, censored and truncated data, obtained by self-consistency. Dating every departure at the interval's right endpoint (a naive Kaplan–Meier on "first seen absent") biases survival upward; dating it at the left endpoint ("last seen present") biases it downward. Both naive curves are used here — not as estimates, but as a bounding validity check on the NPMLE (Section 3.6).

For covariate effects the natural next step is Finkelstein's [10] proportional-hazards model for interval-censored data, or, where captures fall on a fixed grid, Allison's [11] discrete-time formulation. Neither is fitted here, because no covariates are extracted yet (Section 6). Ma et al. [12] provide a setting template from the adjacent literature: a Cox analysis of 5,164 UK spread-betting traders' exit, finding a non-monotone relationship between success and exit hazard — a reminder that "who leaves" is not a simple ordering on performance, and one reason this paper does not read disappearance as failure.

### 2.3 Copy-trading and social trading

The nearest precedent in collection design is Kawai, Soska, Routledge, Zetlin-Jones & Christin [3], who repeatedly snapshot the public leaderboards of two cryptocurrency copy-trading platforms (TraderWagon, October 2022 – August 2023; Bybit, February – August 2023) via public APIs, and study investor behaviour and incentives. Their paper reports, as a methodological aside, that portfolios on those platforms are typically short-lived — a median of 2.9 days and a mean of 16.1 days — and identifies the mechanism by which a leader can close a losing portfolio and open a new one to reshape their visible history. **This work must be cited and distinguished.** The distinction is threefold. First, unit: their tracked object is a portfolio or listing; ours is the provider identity, and the frozen protocol forbids conflating the two. Second, purpose: attrition is not their research object, and the lifetime figure appears in passing without a survival function, a hazard model, or an entry/exit rate. Third, censoring: an incidental median over observed listing lifetimes is not an estimate of a survival distribution when the observation window truncates lifetimes at both ends. Our contribution sits on top of a snapshot corpus; it is not the corpus.

The most direct motivation comes from the ZuluTrade line of work. Schneider & Oehler [1] study whether FX signal providers employ lottery-like strategies to compete for visibility, and state that their approach leaves a substantial survivorship bias because accounts no longer findable through the platform's search — indicating abandonment or inactivity — are not in the dataset. Oehler & Schneider [2] repeat the admission and add the inference that vanished providers had likely been administering underperforming portfolios. Read together, these are an explicit statement by domain experts that the disappeared exist in large numbers, are probably not a random sample of providers, and cannot be reached by platform-side collection. That is the gap this paper fills — not by asserting a better sampling frame but by using a different one: a third-party archive that captured the page on dates the platform has since overwritten.

Finally, Tong & Preda [13] use "survivorship" in this same market family with a different referent — whether retail investors keep participating. The term is disambiguated here once: this study is about providers leaving a listing, not investors leaving a market.

---

## 3. Data and method

### 3.1 Snapshot enumeration from the Wayback CDX API

The sampling frame is the set of archived captures of the MQL5 public signals index page. Enumeration uses the Internet Archive's CDX API. The query is committed verbatim in `src/extract.py::cmd_index` and has been unchanged since the extraction commit:

```
GET https://web.archive.org/cdx/search/cdx
    ?url=mql5.com%2Fen%2Fsignals
    &output=json
    &fl=timestamp%2Coriginal%2Cstatuscode%2Cdigest%2Clength
    &filter=statuscode%3A200
    &collapse=timestamp%3A6
```

Three parameters carry the study's sampling decisions. No `matchType` is passed, so the CDX default applies — exact match on the canonicalised SURT urlkey, which folds `http`/`https`, `www.` and port variants of `mql5.com/en/signals` into a single key (the committed manifest accordingly contains originals such as `http://www.mql5.com:80/en/signals`). `filter=statuscode:200` drops redirects and error captures. `collapse=timestamp:6` retains the **first capture per `YYYYMM`**, defining the study's snapshot unit as one capture per calendar month.

The query returned **141 rows**, committed in `artifacts/snapshots/index_snapshots.csv`, spanning **2011-10 to 2026-07** — 141 distinct calendar months inside a 178-month span, leaving **37 months with no archived capture**. Per-year counts range from 3 (2011, a partial year from October, and 2022) to 12 (2012–2014, 2016, 2019, 2025). The missing-month table, including the longest outage (2017-11 → 2018-06, eight consecutive months), is in the repository `README.md`.

**A frozen-protocol discrepancy, declared.** The frozen §5 states that the source was "verified independently: 1,322 index snapshots across 100 distinct months". That is not the count the pipeline produced, and it cannot be: because the query collapses to one capture per `YYYYMM`, 141 returned rows prove at least 141 distinct months in the underlying capture set. The pre-freeze check's own query, filters and variant handling were never committed and cannot be reproduced. Under the protocol's amendment rule — amendments may restrict claims but may not alter endpoints, the cohort rule or the death definition — erratum 001 declares the extraction-time count authoritative on three grounds: its query is committed verbatim and re-runnable, every retained capture's raw bytes are hashed in a committed manifest, and every downstream artifact derives from exactly this set. The figure 1,322 is not itself contradicted; it is consistent with an uncollapsed count of raw CDX capture records and is described here only as such. All reported results use the 141-snapshot set.

### 3.2 Raw replay fetch and hash manifest

Each retained capture was fetched through the Wayback `id_` replay endpoint (`https://web.archive.org/web/<timestamp>id_/<original>`), which returns the **unrewritten original bytes** rather than the archive's rewritten presentation copy. Fetching is deliberately slow and serial: one request at a time, a fixed 1.5-second delay, a 90-second timeout, at most three retries with escalating back-off, and a descriptive User-Agent naming the research repository so the archive operator can identify and, if desired, block the traffic.

The result is **141 fetched files, 141 successes, zero failures**, each recorded with its byte length and SHA-256 digest in `artifacts/manifests/index_fetch_manifest.csv` (141 rows, all `status=ok`). Two mechanical details matter for reproducibility: the manifest is rewritten atomically in full on every step, so a retried fetch *replaces* its failed row rather than appending a duplicate; and resumability counts only `status=="ok"` rows as complete, where an earlier version treated any manifest row as done and would have silently dropped a failed snapshot from every subsequent re-collection. Raw HTML is retained locally under `data/` and is not committed (Section 7.2).

### 3.3 Roster parsing and the `dom_order` caveat

Provider identity is the numeric signal id appearing in the archived HTML's links. Ids are matched with an anchored pattern on the locale-prefixed path (`/signals/<1–9 digits>` followed by a path, quote, query, fragment or word boundary), because signal ids have no fixed width — the earliest 2011 listings are three digits and current ones six or seven — and an unanchored numeric match would capture unrelated integers. Within each snapshot, ids are deduplicated in **first-occurrence order**. The output is `artifacts/rosters/index_rosters.csv`: **4,325 roster rows across 141 snapshots**, with per-snapshot roster size minimum 10, median 30 and maximum 53 (direct tabulation of the committed roster file; the same shape report is printed by `src/extract.py --parse-index`).

The roster file carries a column named `dom_order`, and its meaning must be stated precisely because a plausible misreading would invalidate an entire endpoint. **`dom_order` is the first-occurrence order of a signal id across the concatenated page sections of the archived HTML. It is not a leaderboard rank.** In the 2012–2017 layouts, positions 11–20 are the MT4 top-ten appended after the MT5 top-ten, so `dom_order` 11 is a first-placed listing, not an eleventh-placed one. In post-2018 layouts the order runs across sections — Reliability, then Popular, then High rating, then New — so a single integer conflates four orderings. In at least one capture the leading entry is the platform's own demonstration signal inside an alphabetical list. The column is retained because it preserves document structure for later section-aware parsing, and because deleting information is worse than labelling it. It is labelled in the code, in the artifact, and here: **`dom_order` must never be fed to the protocol's secondary "past public rank predicts subsequent performance" endpoint as if it were a rank.** Deriving a true rank requires a (section, within-section position) pair for the eras in which the page is a genuine ranked list; that is future work, and the secondary endpoint is not attempted here.

### 3.4 Cohort construction

The cohort rule is frozen in protocol §6 and implemented in `src/survival.py`.

- **Entry.** A provider enters at the first snapshot in which its id appears on the index roster; time zero is that capture's timestamp. **Follow-up** is all subsequent snapshots in the retained set.
- **Death (interval).** A provider last present at snapshot *t\_k* and absent at *t\_{k+1}* contributes the interval (*L*, *R*], where *L* is days from entry to *t\_k* (last seen present) and *R* is days from entry to *t\_{k+1}* (first seen absent). Where whole-day rounding would give *R ≤ L*, *R* is set to *L + 1* so the interval is never empty.
- **Right censoring.** A provider still present at the final snapshot is right-censored at its last observed duration.
- **Re-listing.** A provider reappearing under a new listing id is coded as a *new* provider and the prior listing as a death, because archives cannot establish identity continuity across a rename. The rule was fixed in advance; its bias is one-sided (Section 5.4).
- **Sparse-year rule.** Any calendar year with fewer than two usable snapshots is reported descriptively only and excluded from the survival model. The threshold was fixed at freeze; the check runs on every execution and writes its result to an artifact rather than being asserted in prose.

### 3.5 Interval-censored estimation

The Turnbull NPMLE [9] is implemented directly in `src/survival.py` with no external dependency, in two stages.

**Support-set construction.** Turnbull intervals are the maximal regions in which the estimator can place mass: pairs (*q*, *p*] where *q* is an observed left endpoint, *p* the smallest right endpoint strictly greater than *q*, and no endpoint of any kind lies strictly inside (*q*, *p*). Two constraints are load-bearing, and both were caught by the unit tests rather than by inspection. The data convention is half-open, so a degenerate candidate (*q*, *q*] is the empty set and must never become a support interval. And the "no endpoint strictly inside" test must examine **all** endpoints, left and right; checking only left endpoints merges genuinely disjoint intervals into one support point and silently corrupts the curve. The first version of the estimator did both wrong, produced a plausible-looking curve, and was caught by the disjoint-intervals test (commit `efa735a`).

**Self-consistency iteration.** Mass is assigned by the standard self-consistency (EM) recursion: each subject's probability is redistributed across the support intervals contained in its own interval, in proportion to current mass, and renormalised; iteration stops when the maximum coordinate change falls below 10⁻⁹, with a 20,000-iteration ceiling. Right-censored subjects are handled by admitting an infinite right endpoint into the candidate set, so mass beyond the last observed event is not forced to zero. The estimated support has **52 intervals** (`artifacts/analysis/survival_turnbull.csv`).

**Unit tests.** Eight tests with known analytic answers guard the estimator (`tests/test_survival.py`, all passing): mass sums to one; two subjects in non-overlapping intervals split mass evenly; seven identical intervals collapse to one support interval carrying all mass; a wide interval containing a narrow one puts all mass on the narrow region; one event plus one later-censored subject leaves survival strictly above zero; an all-censored sample identifies no deaths; survival is monotone non-increasing; and degenerate intervals (*t*, *t+ε*] reduce to the empirical CDF. These are deliberately cases where a wrong implementation fails loudly rather than returning a curve that looks reasonable.

### 3.6 Bounds validity check and the tail non-assessability rule

Any interval-censored NPMLE must lie between two naive Kaplan–Meier curves computed on the same data: one dating every death at its interval's **left** endpoint (deaths as early as possible ⇒ survival lower bound) and one at the **right** endpoint (deaths as late as possible ⇒ survival upper bound). A Turnbull curve outside that envelope is proof of an implementation error, not a finding. `src/bounds_check.py` computes both bounds and compares them against the estimate at each reported mark, writing `artifacts/analysis/bounds_check.csv`.

The check carries an explicit non-assessability rule. In the far tail the risk set becomes small, and with few subjects remaining the two naive curves can *cross*, because moving deaths from *L* to *R* reorders them against the censoring times. A crossed envelope is a numerical artefact, not evidence about the estimator. Marks with fewer than **20** subjects still at risk are therefore reported as **"n/a (tail)"** rather than silently passed or failed. The threshold is a stated convention, not a derived quantity, and is recorded in code and artifact so a reader who disagrees can see exactly which marks it moves.

---

## 4. Results

### 4.1 Corpus

The analysed corpus is 141 monthly snapshots of the public signals index, 2011-10 to 2026-07, yielding 4,325 roster rows and **2,090 distinct provider identities** (`artifacts/analysis/turnover_summary.json`, `artifacts/analysis/survival_summary.json`). Adjacent-snapshot spacing is irregular by construction: the shortest gap between consecutive retained captures is 7 days and the longest 282, with a median of 30 (direct tabulation of `artifacts/snapshots/index_snapshots.csv`). Section 4.4 explains why that spacing distribution, not only the sample size, governs how precisely the short-duration region of the curve is identified.

### 4.2 Turnover (Primary Endpoint 2)

Across the 140 adjacent-snapshot transitions, **mean retention is 45.6% and mean turnover 54.4%** (`artifacts/analysis/turnover_summary.json`). Stratified by the year of the earlier snapshot in each transition (`artifacts/analysis/turnover_by_year.csv`):

| Year | Transitions | Mean retention | Mean turnover |
|---|---|---|---|
| 2011 | 3 | 0.6667 | 0.3333 |
| 2012 | 12 | 0.5375 | 0.4625 |
| 2013 | 12 | 0.3325 | 0.6675 |
| 2014 | 12 | 0.4833 | 0.5167 |
| 2015 | 10 | 0.4900 | 0.5100 |
| 2016 | 12 | 0.5458 | 0.4542 |
| 2017 | 10 | 0.5000 | 0.5000 |
| 2018 | 6 | 0.4667 | 0.5333 |
| 2019 | 12 | 0.4188 | 0.5812 |
| 2020 | 10 | 0.4044 | 0.5956 |
| 2021 | 10 | 0.3913 | 0.6087 |
| 2022 | 3 | 0.2091 | 0.7909 |
| 2023 | 4 | 0.3193 | 0.6807 |
| 2024 | 6 | 0.4011 | 0.5989 |
| 2025 | 12 | 0.4939 | 0.5061 |
| 2026 | 6 | 0.5152 | 0.4848 |

Two arithmetic conventions must not be conflated. The headline **54.4%** is the mean over all 140 transitions. The dashed reference line in Figure 2 (left panel) is the **unweighted mean of the sixteen yearly means, 55.2%**, which weights a three-transition year equally with a twelve-transition year. Both come from the same committed artifacts; neither is a rate per unit time, because the underlying intervals are not of equal length.

Year strata should be read with their transition counts attached. The extremes sit in the thinnest years: the lowest turnover (33.3%) is 2011, a partial year contributing three transitions from an October start, and the highest (79.1%) is 2022, which also contributes three and sits beside the corpus's sparsest archival coverage. The dense years, carrying ten to twelve transitions each, occupy a narrower band of roughly 45–61%. There is a visible upward drift from the mid-2010s into the early 2020s and a partial return toward the corpus mean in 2025–2026, but with irregular spacing and unequal year weights this is described, not modelled; no trend test is performed.

### 4.3 Appearance distribution

Of the 2,090 providers, **1,376 (65.8%) appear in exactly one snapshot** (`artifacts/analysis/appearance_distribution.csv`). A further 284 (13.6%) appear in two, bringing the cumulative share at two or fewer to 79.4%; 93.6% appear in five or fewer. The upper tail is very thin: one provider appears in 30 snapshots, one in 27, one in 22 and two in 21 — five providers out of 2,090 visible in more than twenty of the 141 monthly captures.

This distribution is the descriptive core of the paper's claim about what a follower sees. Roster sizes range from 10 to 53 with a median of 30, so a single capture shows a follower a few dozen names while the corpus as a whole contains two thousand. Those names are drawn overwhelmingly from a population whose members are, modally, present for one capture and absent at the next.

### 4.4 Survival of leaderboard visibility (Primary Endpoint 1)

The Turnbull NPMLE over all 2,090 providers gives (`artifacts/analysis/survival_summary.json`):

| Mark | Estimated S(t) | Interpretation |
|---|---|---|
| 30 days | **0.367** | ~37% of entrants still visible after one month |
| 90 days | **0.2143** | ~21% still visible after three months |
| 180 days | **0.1109** | ~11% still visible after six months |
| 365 days | **0.039** | ~4% still visible after one year |
| 730 days | 0.008 | reported, but the bounds check cannot assess it |
| 1,095 days | 0.0014 | reported, but the bounds check cannot assess it |

The estimated **median visibility duration is 11 days**, and it requires an immediate caveat, stated here rather than under limitations because it bears directly on how the number should be read. Survival falls from 0.584 to 0.426 across the support interval (8, 11] days, so the median is *bracketed* there; the code reports its right endpoint, 11 days — the conservative choice, crediting providers with the longest visibility the data permit. More importantly, the three earliest support intervals — (0, 7], (7, 8] and (8, 11] — jointly carry **57.4%** of the estimated mass (`artifacts/analysis/survival_turnbull.csv`), and their endpoints are exactly the three shortest adjacent-snapshot gaps in the corpus: 7, 8 and 11 days. Under a one-capture-per-month design, sub-fortnight resolution exists only where an end-of-month capture happens to be followed by a start-of-month capture, which occurs in **3 of 140** transitions. The estimator is behaving correctly — the NPMLE concentrates mass in the narrowest identifiable regions, and a provider seen once and then gone contributes the interval (0, gap], which contains all three — but the short-duration region of the curve rests on a handful of accidentally close capture pairs. **The median should be read as "under a fortnight, imprecisely located", not as a point estimate of 11 days.** The 90-, 180- and 365-day marks rest on far more transitions and are correspondingly more robust.

**Censoring accounting.** Of the 2,090 provider records, **2,041 contribute an interval-censored disappearance** and **49 are right-censored** at the final snapshot (`artifacts/analysis/survival_intervals.csv`, `type` column). Of those 49, **16 are providers first observed at the final snapshot itself**, right-censored at zero days. Zero-follow-up records are informationless for the NPMLE — they constrain no support interval, and estimates are numerically identical whether they are included or excluded — so including them is the smaller intervention, and their count is reported explicitly as `n_zero_followup` rather than quietly dropped. Readers preferring exclusion should note that the denominator changes from 2,090 to 2,074 and no estimate moves.

**Sparse-year rule.** The frozen rule was evaluated and produced **no exclusions**: the minimum usable-snapshot count in any calendar year is 3, in 2011 and 2022, above the threshold of 2 (`artifacts/analysis/sparse_year_check.txt`). This is a rule that was applied and did not bind, not a rule that was unnecessary — had either year fallen one snapshot lower, it would have left the survival model automatically and the exclusion would have been reported with counts.

### 4.5 Bounds validity check

`artifacts/analysis/bounds_check.csv`:

| Days | At risk | KM lower bound | Turnbull | KM upper bound | Result |
|---|---|---|---|---|---|
| 30 | 1,417 | 0.2895 | 0.3670 | 0.6854 | **PASS** |
| 90 | 674 | 0.1696 | 0.2143 | 0.3292 | **PASS** |
| 180 | 320 | 0.0971 | 0.1109 | 0.1589 | **PASS** |
| 365 | 88 | 0.0347 | 0.0390 | 0.0451 | **PASS** |
| 730 | 18 | 0.0066 | 0.0080 | 0.0108 | n/a (tail) |
| 1,095 | 2 | 0.0015 | 0.0014 | 0.0013 | n/a (tail) |

All four assessable marks pass. The two longest are not assessable under the pre-stated 20-subject rule; at 1,095 days the "lower" bound (0.0015) exceeds the "upper" bound (0.0013), which is precisely the crossing pathology the rule exists to catch — with two subjects at risk, the envelope is not an envelope. Reporting those marks as not assessable rather than as passes is the difference between a validity check and a decoration.

The envelope width is itself informative. At 30 days the naive bounds span 0.29 to 0.69 — a factor of more than two — a direct measure of how much the monthly capture cadence leaves undetermined at short durations, and independent confirmation of the caveat in Section 4.4. By 365 days the bounds have narrowed to 0.035–0.045.

### 4.6 Figures

**Figure 1 — Survival of leaderboard visibility, 2,090 signal providers, 2011–2026** (`paper/figures/fig1_survival.png`, generated by `src/make_figures.py` from `artifacts/analysis/survival_turnbull.csv` and `artifacts/analysis/survival_intervals.csv`). The solid curve is the Turnbull interval-censored NPMLE of the probability that a provider is still visible on the archived leaderboard index, against days since first appearance, truncated at 730 days for legibility. The shaded band is the naive Kaplan–Meier bound envelope: its lower edge dates every disappearance at the last capture at which the provider was present, its upper edge at the first capture at which the provider was absent. The band is **not** a confidence interval; it is the range of curves consistent with the same data under the two extreme (and both wrong) assumptions about *when* inside each interval the disappearance occurred, and the estimate must lie inside it. Marked points are the four assessable marks: 30 d = 36.7%, 90 d = 21.4%, 180 d = 11.1%, 1 y = 3.9%. The band's width at short durations, and its narrowness beyond one year, are the visual form of the resolution caveat in Section 4.4.

**Figure 2 — Roster turnover by year and appearance-count distribution** (`paper/figures/fig2_turnover.png`, generated by `src/make_figures.py` from `artifacts/analysis/turnover_by_year.csv` and `artifacts/analysis/appearance_distribution.csv`). *Left:* mean adjacent-snapshot turnover for each calendar year, over the transitions whose earlier snapshot falls in that year; the dashed line is the unweighted mean of the sixteen yearly rates (55.2%, printed as 55%), which differs from the transition-weighted headline of 54.4% because years contribute between 3 and 12 transitions each. The 2011 and 2022 bars each rest on three transitions and are not comparable in precision to the twelve-transition years. *Right:* the share of providers appearing in exactly *k* snapshots, truncated at *k* = 10; 65.8% appear exactly once, and the truncated tail (*k* > 10) holds 1.7% of providers.

---

## 5. Discussion

### 5.1 What a 96%-within-a-year attrition figure does and does not mean

With S(365 d) = 0.039, roughly **96% of providers who ever appear on this leaderboard are no longer visible on it one year later**. The temptation is to read that as a failure rate. It is not one, and the protocol's language discipline forbids the reading: disappearance is reported as disappearance, not as failure, absent evidence.

What the figure *does* support is a statement about the information environment. Leaderboard membership is not a durable status a follower can treat as a slowly changing signal. It is closer to a rapidly refreshing display in which the great majority of entries will not be there in a year, and in which the modal entry is present for one monthly capture and absent at the next. Any inference a follower draws from "this provider is on the leaderboard" must be conditioned on that base rate, and the base rate is not shown to them.

What the figure does *not* support: that 96% of these providers lost money; that 96% closed their accounts; that the platform removed them; or that the provider population shrank. Each is a different endpoint with a different measurement, and none is measured here.

### 5.2 The endpoint is visibility

The measured event is **absence from the archived index roster at a later capture, having been present at an earlier one**. At least five distinct real-world processes produce that event, and this study cannot separate them:

1. The provider stopped operating the signal — the reading closest to "failure", and the one the copy-trading literature's authors expect to dominate [1, 2].
2. The provider continued but fell below whatever threshold governs inclusion in the archived view — a ranking, popularity, subscriber-count or editorial cutoff a still-active provider can cross downward.
3. The platform changed the page's layout, section composition or default sort (Section 3.3 documents at least three layout eras in this corpus).
4. The provider re-listed under a new id, which the frozen rule codes as a death plus a new entrant (Section 5.4).
5. The archive's crawler captured a different or partial rendering of the page on the later date.

Processes 2, 3 and 5 have nothing to do with the provider's fortunes. This is why the endpoint is named *leaderboard visibility* throughout, and why the conclusion is framed as a measurement of what a reader of the leaderboard can and cannot infer rather than as a mortality statistic about a business population. It is also why the protocol's terminal live status sweep — a single polite status-code check that would let index absence be cross-checked against page absence — matters, and why its non-execution is declared as an open deviation in Section 6.

### 5.3 The selection bias a prospective follower faces

The gap between the leaderboard view and the entering-cohort distribution has a precise statistical name in the tenure dimension: **length bias**. A single capture samples providers in proportion to how long they are visible, because a long-visible provider is available to be sampled in many captures and a briefly visible one in few. The names a follower reads on any given day therefore over-represent durable providers relative to everyone who ever entered. And yet, even after that over-representation, 65.8% of providers ever observed across 141 captures were observed exactly once.

Put the two facts together and the consequence is sharper than either alone. The leaderboard is a *favourable* sample of the entering cohort in the tenure dimension — biased toward survivors by the very mechanics of being a snapshot — and it still consists overwhelmingly of names whose visible tenure will be short. A follower reasoning "the people on this list are the ones who lasted" is making an inference the sampling process partially supports and the base rate substantially undercuts.

Two boundaries. First, this is a claim about tenure, not returns: with no performance covariates in this draft, the analogous statement about the *displayed performance* distribution — the second half of the frozen contribution claim — is not established here (Section 6). Second, length bias in the sampling of a *snapshot* is not the same quantity as the survival function estimated from the *entering cohort*; the two are reported separately rather than combined into one adjusted number, because combining them would require assumptions about entry rates over time that this corpus does not pin down.

### 5.4 Why the conservative renaming rule can only overstate attrition

The frozen cohort rule codes a provider who reappears under a new listing id as a death of the old identity plus the birth of a new one. Archives cannot establish identity continuity across a rename — the archived page carries a display name and an id, and neither is a stable, verifiable person-level key — so the rule was fixed in advance rather than decided after seeing how much difference it made.

Its bias is one-sided, which is worth stating precisely because one-sided biases are usable. Every misclassified rename does two things: it truncates a genuinely longer visibility spell into a shorter one, and it injects a spurious new entrant whose own spell begins at the rename. Both push the estimated survival curve **down**, and no mechanism in the rule can lengthen an estimated spell. Therefore **the reported survival curve is a lower bound on the true survival of continuous provider identities**, and the true attrition of the persons or businesses behind these listings is at most what is reported here, not more. A reader who believes renaming is common should read every number in Section 4.4 as an underestimate of durability — and note that this direction cuts against the paper's own headline, which is the safe direction for it to cut. The same logic applies to turnover: 54.4% is an upper bound on the churn of continuous identities.

### 5.5 Relation to the reported portfolio lifetimes on crypto copy-trading platforms

Kawai et al. [3] report a median portfolio lifetime of 2.9 days on two cryptocurrency copy-trading platforms; this study estimates a median leaderboard-visibility duration of about a fortnight for provider identities on an FX signal marketplace. The two numbers are not comparable, and presenting them as a replication or a contrast would be a mistake. They differ in unit (portfolio versus provider identity), platform and asset class, observation window (roughly one year of daily API polling versus fifteen years of monthly archival captures), estimator (an observed median versus an interval-censored NPMLE), and — decisively — temporal resolution: a daily-polled corpus can resolve a 2.9-day lifetime and a monthly-captured one structurally cannot (Section 4.4). What the two results share is a direction: on both platform families, the objects displayed on a public copy-trading leaderboard are short-lived relative to any plausible investment horizon.

---

## 6. Limitations

This section is deliberately long. Headline numbers about consumer-facing interfaces travel further than their caveats, so the caveats are stated specifically.

**The time origin is first archived appearance, not platform registration.** A provider first observed in a 2019 capture may have been operating since 2015 and merely absent from the archived top-N view until then. This is delayed entry, and it is not corrected. Its effect is not signable in general: providers already long-lived when first captured contribute short *observed* spells if they leave soon after, biasing the estimate down, while excluding pre-entry survival time biases the population interpretation the other way. The estimand is "time from first archived leaderboard appearance to disappearance", not "provider lifetime", and the two must not be substituted for one another.

**Snapshot spacing is irregular, and the short-duration region rests on very few transitions.** Gaps between consecutive retained captures range from 7 to 282 days, median 30. The interval-censored estimator absorbs this rather than assuming it away, which is why it was chosen — but absorbing irregular spacing is not the same as recovering information that was never captured. As Section 4.4 documents, the three support intervals below 12 days carry 57.4% of the mass and derive from the three shortest capture gaps in 140 transitions. Any use of this curve below roughly one month is indicative only. The eight-month outage of 2017-11 → 2018-06 widens every interval that brackets it, and 2022–2024 is the sparsest stretch in the corpus.

**The archived view is a top-N page, not the provider population.** Roster sizes vary from 10 to 53, and the page's composition changed at least three times (Section 3.3). "Entering the cohort" therefore means "becoming visible in whatever the index page rendered on that date", a definition that drifts with the platform's design decisions. Comparisons across layout eras — including the year-stratified turnover table — inherit that drift, and no attempt is made to normalise it.

**Web-archive capture is not random sampling.** Pages are crawled for reasons unrelated to this study: inbound links, prior crawl history, user submissions, partner crawls. Capture dates and completeness are consequently non-random with respect to the page's own content and traffic; a period of high platform attention may be more densely captured than a quiet one. This study has no instrument for that selection and does not model it. The 37 uncaptured months are the visible part of the problem; the non-random timing of the 141 captured ones is the invisible part.

**No performance covariates, so the frozen contribution's second half is not delivered.** The frozen wording claims a first quantification of the bias in the platform's *observable performance distribution*. This draft extracts identity and document order only; growth, subscriber, reliability, trade-count and track-record-length fields are present in the archived static DOM but are not parsed here. The performance half of the contribution is therefore **not established in this draft**, and the abstract and introduction claim only the visibility-duration result. Fitting Finkelstein [10] or Allison [11] hazard models with covariates is deferred for the same reason.

**The protocol's terminal live status sweep has not been run.** Protocol §4 defines death as index absence "confirmed by one polite live status sweep at analysis time", and §5 provides for a single status-code-only sweep. No such sweep has been executed and no artifact for one exists in the repository. The endpoint as implemented is **index-roster absence alone**. This is a live deviation from the frozen protocol, declared here rather than glossed: it alters no reported number, but the death definition realised in the analysis is weaker than the one frozen, and "disappearance" should be read as an archival-visibility event that has not been cross-checked against the provider page's current HTTP status.

**The secondary endpoint is untouched, by design.** Because `dom_order` is document order and not rank (Section 3.3), the protocol's demoted secondary endpoint — whether past public rank predicts subsequently observable performance — is not attempted. This is a deliberate refusal, not an omission: feeding `dom_order` into a rank-based analysis would produce results that look like findings and are not.

**Single platform, single interface locale.** All data come from one marketplace's English-language (`/en/`) index page. Nothing here establishes that the attrition regime generalises to other copy-trading platforms, and the archived non-English locales of the same platform are not analysed, so even generalisation across the localised interfaces a follower might actually read is untested.

**Conservative renaming, restated as a limitation.** The rule of Section 5.4 is a modelling choice made under an identification constraint, not a measurement. Its bias direction is known (attrition overstated), its magnitude is not, and the corpus contains no instrument for estimating it.

**Thin year strata.** The sparse-year rule did not bind, but five of the sixteen years contribute six or fewer transitions (2011: 3; 2022: 3; 2023: 4; 2018: 6; 2024: 6), and two of those hold the extreme values of the turnover table. The threshold of two was fixed at freeze and is not re-litigated here, but readers should weight the yearly table by its transition counts.

**No causal or comparative claim.** Nothing here identifies why providers disappear, compares platforms, evaluates any provider, or supports an allegation against any named party. The study is a distributional measurement of one public information environment over fifteen years.

---

## 7. Reproducibility, data availability, and disclosures

### 7.1 Reproducibility statement

All protocol documents, amendments, code, unit tests, derived artifacts and figures are public at `github.com/nathanskill/leaderboard-survivorship`. The protocol was frozen at commit `684241f` (annotated tag `v1.0-protocol-freeze`, 25 July 2026) **before any data extraction**, fixing the endpoints, cohort rule, interval-censored death definition, sparse-year threshold, conservative renaming rule and contribution wording. The frozen file is never edited; the only post-freeze amendment is `protocol/amendments/erratum-001-snapshot-counts.md` (Section 3.1), which restricts a factual claim and touches no endpoint, cohort rule or death definition.

The pipeline runs `src/extract.py` in three stages (`--index`, `--fetch-index`, `--parse-index`), then `src/turnover.py`, `src/survival.py` and `src/bounds_check.py`, then `src/make_figures.py`. The analysis scripts use only the Python standard library; only figure generation requires matplotlib. Unit tests run with `python3 -m unittest discover -s tests` (8 tests). Two determinism properties are deliberate: artifact rows are sorted on stable keys before writing, because an earlier version's set-iteration order made the committed CSVs non-byte-reproducible under hash randomisation; and the figure script consumes only committed artifacts, so figures regenerate without re-fetching anything.

Each results subsection above names the artifact file it draws on, and the repository `README.md` carries the claims→artifacts map in tabular form.

### 7.2 Data availability

**Public and committed:** the CDX enumeration output (`artifacts/snapshots/index_snapshots.csv`, 141 rows); the fetch manifest with per-file byte lengths and SHA-256 digests (`artifacts/manifests/index_fetch_manifest.csv`, 141 rows, all `ok`); the parsed per-snapshot rosters (`artifacts/rosters/index_rosters.csv`, 4,325 rows); and all analysis artifacts under `artifacts/analysis/`. Figures are committed under `paper/figures/`.

**Regenerable, not redistributed:** the raw archived HTML (141 files under a gitignored `data/` directory) is not re-uploaded. It is third-party archived content, and re-hosting it is neither necessary nor appropriate when the original is publicly addressable. A reproducer obtains it by re-running `src/extract.py --index --fetch-index` and verifying each file against the committed SHA-256 manifest; byte-identical replay is what the `id_` endpoint is for. One ordinary risk of archive-based work applies: a capture withdrawn or made unavailable upstream cannot be re-fetched, and the manifest then documents what was analysed without permitting its recovery.

**Ethics and collection conduct.** All source material is lawfully public. Providers are pseudonymous commercial vendors selling signals to the public; reporting is aggregate only and no individual provider is named in any output, figure or artifact discussion. Signal ids are retained solely as within-study join keys. No private messages, user data, personal identifiers or account contents were collected. Fetching was serial and rate-limited to one request per 1.5 seconds with a descriptive User-Agent identifying the research repository. No platform account was created and no authenticated surface was accessed.

### 7.3 Conflict-of-interest disclosure

Reproduced verbatim from the frozen protocol (§8):

> The author is employed full-time at a retail FX/CFD brokerage in Sydney and operates independent Chinese-language trading-education web properties. The employer does not distribute MQL5-integrated copy-trading products (confirmed 25 July 2026), so no employer commercial interest attaches to the studied platform. No employer data, systems, or client information is used. Research data does not enter the author's commercial content channels before publication; after publication, only the published paper is cited.

### 7.4 AI-assistance disclosure

Large-language-model assistants (Anthropic Claude) were used under the author's direction for code drafting, literature search, data processing, and manuscript drafting and editing. All protocol decisions, frozen specifications, claim boundaries and interpretive judgements are the author's; all reported numbers were verified against the committed artifact files named in each section, and no committed number was altered in the course of drafting. `[Adapt to venue disclosure format at submission.]`

---

## References

1. J. Schneider, A. Oehler. *Competition for visibility: When do (FX) signal providers employ lotteries?* International Review of Financial Analysis 78:101892, 2021. DOI 10.1016/j.irfa.2021.101892.
2. A. Oehler, J. Schneider. *Social trading: do signal providers trigger gambling?* Review of Managerial Science 17(4):1269–1331, 2022. DOI 10.1007/s11846-022-00560-6. (Open access.)
3. D. Kawai, K. Soska, B. Routledge, A. Zetlin-Jones, N. Christin. *Stranger Danger? Investor Behavior and Incentives on Cryptocurrency Copy-Trading Platforms.* CHI '24, 1–20, 2024. DOI 10.1145/3613904.3642715.
4. S. J. Brown, W. N. Goetzmann, R. G. Ibbotson, S. A. Ross. *Survivorship Bias in Performance Studies.* Review of Financial Studies 5(4):553–580, 1992. DOI 10.1093/rfs/5.4.553.
5. S. J. Brown, W. N. Goetzmann, R. G. Ibbotson. *Offshore Hedge Funds: Survival and Performance, 1989–95.* Journal of Business 72(1):91–117, 1999. DOI 10.1086/209603.
6. B. Liang. *Hedge Funds: The Living and the Dead.* Journal of Financial and Quantitative Analysis 35(3):309–326, 2000. DOI 10.2307/2676206.
7. W. Fung, D. A. Hsieh. *Performance Characteristics of Hedge Funds and Commodity Funds: Natural vs. Spurious Biases.* Journal of Financial and Quantitative Analysis 35(3):291–307, 2000. DOI 10.2307/2676205.
8. G. Bhardwaj, G. B. Gorton, K. G. Rouwenhorst. *Fooling Some of the People All of the Time: The Inefficient Performance and Persistence of Commodity Trading Advisors.* Review of Financial Studies 27(11):3099–3132, 2014. DOI 10.1093/rfs/hhu040.
9. B. W. Turnbull. *The Empirical Distribution Function with Arbitrarily Grouped, Censored and Truncated Data.* Journal of the Royal Statistical Society, Series B 38(3):290–295, 1976. DOI 10.1111/j.2517-6161.1976.tb01597.x.
10. D. M. Finkelstein. *A Proportional Hazards Model for Interval-Censored Failure Time Data.* Biometrics 42(4):845–854, 1986. DOI 10.2307/2530698.
11. P. D. Allison. *Discrete-Time Methods for the Analysis of Event Histories.* Sociological Methodology 13:61–98, 1982. DOI 10.2307/270718.
12. T. Ma, P. Fraser-Mackenzie, M.-C. Sung, A. P. Kansara, J. E. V. Johnson. *Are the least successful traders those most likely to exit the market?* European Journal of Operational Research 299(1):330–345, 2022. DOI 10.1016/j.ejor.2021.08.050.
13. X. Tong, A. Preda. *Does social communication make investors stay in the market?* Socio-Economic Review 22(4):1865–1890, 2023. DOI 10.1093/ser/mwad065.

*All DOIs in this list were resolved against Crossref during the protocol's pre-freeze citation verification (25 July 2026). No citation in this draft is included without that verification.*
