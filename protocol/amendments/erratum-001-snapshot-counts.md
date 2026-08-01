# Erratum 001 — Snapshot-count discrepancy in frozen protocol §5

Date: 2026-07-31.
Applies to: `protocol/locked_protocol_v1.0.md` §5 ("Data"), the sentence
"Verified independently: 1,322 index snapshots across 100 distinct months",
and the same figures formerly echoed in `README.md`.
The frozen protocol file is not edited; this numbered erratum supersedes the
quoted sentence per the protocol's own amendment rule (amendments may
restrict claims but may not alter endpoints, the cohort rule, or the death
definition — none of which are touched here).

## 1. The discrepancy

The extraction pipeline (`src/extract.py --index`, run 2026-07-25, committed
in 597b65a) retained **141 monthly index snapshots across 141 distinct
calendar months**, spanning 2011-10 → 2026-07 (178 calendar months; 37 months
have no archived capture — see the coverage table in `README.md`).

The frozen text claims **100 distinct months**. This is a direct
contradiction, not a subset relation: the extraction query collapses to one
capture per `YYYYMM`, so 141 returned rows prove the underlying capture set
contains at least 141 distinct months. A capture set with only 100 distinct
months could not produce 141 collapsed rows for the same URL.

The **1,322** figure is not itself contradicted: it is consistent with an
uncollapsed count of raw CDX capture records for the index URL (many months
have multiple captures). The error is the "100 distinct months" clause, and
the frozen sentence's framing of 1,322 as "index snapshots" when the study's
snapshot unit is the retained one-per-month capture.

## 2. Exact CDX query used at extraction (recorded verbatim)

From `src/extract.py::cmd_index` (unchanged since commit 597b65a):

```
GET https://web.archive.org/cdx/search/cdx
    ?url=mql5.com%2Fen%2Fsignals
    &output=json
    &fl=timestamp%2Coriginal%2Cstatuscode%2Cdigest%2Clength
    &filter=statuscode%3A200
    &collapse=timestamp%3A6
```

URL-variant handling: no `matchType` parameter is passed, so the CDX default
(exact match on the canonicalised SURT urlkey) applies. Canonicalisation
folds scheme (`http`/`https`), `www.` and port variants of
`mql5.com/en/signals` into one key — the committed manifest shows originals
such as `http://www.mql5.com:80/en/signals`. `filter=statuscode:200` drops
redirects and errors; `collapse=timestamp:6` keeps the first capture per
`YYYYMM`. The 141 returned rows are committed in
`artifacts/snapshots/index_snapshots.csv`; the fetched raw bytes are hashed
in `artifacts/manifests/index_fetch_manifest.csv`.

## 3. The freeze-time query was not recorded

The "verified independently: 1,322 / 100 distinct months" check predates the
pipeline and its query, filters, and variant handling were not committed
anywhere in this repository. It therefore cannot be reproduced or debugged.
The most likely source of the "100 distinct months" figure is a differently
canonicalised or differently filtered query (e.g. a variant-specific URL, a
status filter admitting fewer captures, or a truncated first page), but this
is conjecture and is labelled as such.

## 4. Which count is authoritative

**The extraction-time count is authoritative: 141 monthly snapshots across
141 distinct months (2011-10 → 2026-07, 178-month span, 37 months without a
capture).** Reasons: (a) the query producing it is committed verbatim in
`src/extract.py` and re-runnable; (b) every retained snapshot's raw bytes
are on disk and SHA-256-hashed in a committed manifest; (c) every downstream
artifact (rosters, turnover, survival) derives from exactly this set.

Rule for all outputs: quote "141 monthly snapshots (one per calendar month
with an archived capture, 2011-10 → 2026-07)". The phrase "1,322 index
snapshots across 100 distinct months" must not be quoted anywhere except in
discussions of this erratum; 1,322 may be described only as "raw CDX capture
records before monthly collapsing".
