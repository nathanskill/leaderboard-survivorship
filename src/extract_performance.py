#!/usr/bin/env python3
"""
extract_performance.py — performance covariates from the archived leaderboard
index pages (REF-2026-018).

Protocol reference: locked_protocol_v1.0.md. The frozen contribution claim has
two halves: (i) a survival-analytic estimate of leaderboard-visibility
duration, and (ii) a quantification of the resulting bias in the platform's
observable performance distribution. Half (i) is delivered by survival.py.
This module supplies the covariates half (ii) needs.

What the archived cards carry (era-dependent):
  * growth percentage and its label ("growth since YYYY" / "growth for N
    months"), i.e. a cumulative return figure as the platform displayed it;
  * subscriber count;
  * star rating and the number of ratings;
  * reliability and algo-trading bar levels;
  * a weekly growth time series in a hidden input.

Everything extracted here is what the PAGE DISPLAYED at capture time. It is
not audited performance and is never treated as such: the endpoint of this
study is what a prospective follower could see, so the displayed figure is
exactly the right object.

Reads:  data/raw/index/*.html (already fetched; no network access)
Writes: artifacts/performance/provider_performance.csv
        artifacts/performance/extraction_coverage.csv
        artifacts/performance/extraction_summary.json
"""
import csv
import json
import os
import re
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw", "index")
OUT = os.path.join(ROOT, "artifacts", "performance")

# One card per provider on the modern layout. Older eras use table rows; both
# are handled by splitting on the id anchor and reading a bounded window.
ID_RE = re.compile(r"/signals/(?:show/)?(\d{1,9})(?:[/\"'?#]|\b)")

GROWTH_RE = re.compile(
    r"signal-card__growth-value[^>]*>\s*([+-]?[\d,]+(?:\.\d+)?)\s*%|"
    r"growth[^<>%]{0,40}?([+-]?[\d,]+(?:\.\d+)?)\s*%", re.I)
GROWTH_LABEL_RE = re.compile(
    r"signal-card__growth-label[^>]*>\s*([^<]{3,40})", re.I)
SUBS_RE = re.compile(
    r"subscribers[^>]*>.{0,200}?>\s*([\d,]+)\s*<|"
    r"title=\"Subscribers\"[^>]*>\s*([\d,]+)", re.I | re.S)
RATING_RE = re.compile(r"g-rating__info[^>]*>\s*([\d.]+)\s*\((\d+)\)", re.I)
RELIABILITY_RE = re.compile(r"risk-bars-rel(\d)", re.I)
ALGO_RE = re.compile(r"risk-bars-algo\s+val(\d)[^>]*>[^<]*(?:</span>)?\s*"
                     r"(?:&nbsp;)?\s*(\d{1,3})\s*%", re.I)
SERIES_RE = re.compile(r"s-avatar-chart[^>]*>\s*<input value=\"\[([^\]]{10,4000})\]",
                       re.I)

# Window after an id anchor within which that provider's fields must appear.
# Cards are ~2.5 kB on the modern layout; older table rows are shorter.
WINDOW = 3000

FIELDS = ["timestamp", "signal_id", "dom_order", "growth_pct", "growth_label",
          "subscribers", "rating", "n_ratings", "reliability_level",
          "algo_pct", "series_points", "series_last"]


def num(s):
    if not s:
        return ""
    s = s.replace(",", "").replace(" ", "")
    try:
        return float(s)
    except ValueError:
        return ""


def parse_snapshot(html):
    """Yield one dict per provider occurrence, in DOM order."""
    hits = list(ID_RE.finditer(html))
    seen = set()
    order = 0
    for i, m in enumerate(hits):
        sid = m.group(1)
        if sid in seen:
            continue
        seen.add(sid)
        order += 1
        end = hits[i + 1].start() if i + 1 < len(hits) else len(html)
        # Cap the window so a sparse page cannot borrow a distant card's data.
        seg = html[m.end():min(end, m.end() + WINDOW)]

        g = GROWTH_RE.search(seg)
        growth = num(g.group(1) or g.group(2)) if g else ""
        gl = GROWTH_LABEL_RE.search(seg)
        s = SUBS_RE.search(seg)
        subs = num((s.group(1) or s.group(2))) if s else ""
        r = RATING_RE.search(seg)
        rel = RELIABILITY_RE.search(seg)
        al = ALGO_RE.search(seg)
        ser = SERIES_RE.search(seg)
        pts = last = ""
        if ser:
            vals = [v.strip() for v in ser.group(1).split(",")]
            # series is [t0,v0,t1,v1,...]; values are the odd positions
            vs = [num(v) for v in vals[1::2]]
            vs = [v for v in vs if v != ""]
            if vs:
                pts, last = len(vs), vs[-1]

        yield {
            "signal_id": sid, "dom_order": order,
            "growth_pct": growth,
            "growth_label": re.sub(r"\s+", " ", gl.group(1)).strip() if gl else "",
            "subscribers": subs,
            "rating": num(r.group(1)) if r else "",
            "n_ratings": num(r.group(2)) if r else "",
            "reliability_level": r.group(1) if False else (rel.group(1) if rel else ""),
            "algo_pct": num(al.group(2)) if al else "",
            "series_points": pts, "series_last": last,
        }


def main():
    os.makedirs(OUT, exist_ok=True)
    files = sorted(f for f in os.listdir(RAW) if f.endswith(".html"))
    rows = []
    coverage = []
    for fn in files:
        ts = fn[:-len(".html")]
        with open(os.path.join(RAW, fn), encoding="utf-8", errors="ignore") as f:
            html = f.read()
        recs = list(parse_snapshot(html))
        for rec in recs:
            rec["timestamp"] = ts
            rows.append(rec)
        have = lambda k: sum(1 for r in recs if r[k] != "")   # noqa: E731
        coverage.append({
            "timestamp": ts, "n_providers": len(recs),
            "with_growth": have("growth_pct"),
            "with_subscribers": have("subscribers"),
            "with_rating": have("rating"),
            "with_series": have("series_points"),
            "bytes": len(html),
        })

    with open(os.path.join(OUT, "provider_performance.csv"), "w",
              newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows({k: r.get(k, "") for k in FIELDS} for r in rows)

    with open(os.path.join(OUT, "extraction_coverage.csv"), "w",
              newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(coverage[0].keys()))
        w.writeheader()
        w.writerows(coverage)

    by_year = defaultdict(lambda: {"snap": 0, "rows": 0, "growth": 0})
    for c in coverage:
        y = c["timestamp"][:4]
        by_year[y]["snap"] += 1
        by_year[y]["rows"] += c["n_providers"]
        by_year[y]["growth"] += c["with_growth"]

    n = len(rows)
    summary = {
        "snapshots": len(files),
        "provider_rows": n,
        "with_growth": sum(1 for r in rows if r["growth_pct"] != ""),
        "with_subscribers": sum(1 for r in rows if r["subscribers"] != ""),
        "with_rating": sum(1 for r in rows if r["rating"] != ""),
        "with_series": sum(1 for r in rows if r["series_points"] != ""),
        "coverage_by_year": {y: v for y, v in sorted(by_year.items())},
        "caveats": [
            "Every field is what the archived page DISPLAYED at capture time; "
            "it is not audited performance, and the growth figure's window "
            "varies by card (its label is retained verbatim).",
            "Field availability is era-dependent: early layouts carry fewer "
            "fields, so coverage must be reported per snapshot before any "
            "cross-era comparison.",
            "Extraction is windowed after each provider id anchor; a card "
            "lacking a field yields empty rather than borrowing a neighbour's.",
        ],
    }
    with open(os.path.join(OUT, "extraction_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps({k: v for k, v in summary.items()
                      if k not in ("coverage_by_year", "caveats")}, indent=2))
    print("\ncoverage by year (snapshots / rows / rows-with-growth):")
    for y, v in sorted(by_year.items()):
        print(f"  {y}  {v['snap']:>3} / {v['rows']:>5} / {v['growth']:>5}")


if __name__ == "__main__":
    main()
