#!/usr/bin/env python3
"""
turnover.py — descriptive turnover statistics for REF-2026-018.

Implements Primary Endpoint 2 of protocol/locked_protocol_v1.0.md
(leaderboard membership turnover between adjacent archived snapshots,
stratified by year) plus the appearance-count distribution that motivates
the survival analysis.

This script is DESCRIPTIVE ONLY. The survival estimator (Turnbull NPMLE for
interval-censored disappearance, Primary Endpoint 1) is a separate stage and
is not run here. Nothing here conditions on outcome; no provider is named.

Reads:  artifacts/rosters/index_rosters.csv
Writes: artifacts/analysis/turnover_by_year.csv
        artifacts/analysis/appearance_distribution.csv
        artifacts/analysis/turnover_summary.json
"""
import csv
import json
import os
from collections import OrderedDict, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ART = os.path.join(ROOT, "artifacts")
ROSTERS = os.path.join(ART, "rosters", "index_rosters.csv")
OUT = os.path.join(ART, "analysis")


def load_snapshots():
    snap = OrderedDict()
    with open(ROSTERS, newline="") as f:
        for r in csv.DictReader(f):
            snap.setdefault(r["timestamp"], []).append(r["signal_id"])
    return OrderedDict((k, snap[k]) for k in sorted(snap))


def main():
    os.makedirs(OUT, exist_ok=True)
    snap = load_snapshots()
    ts = list(snap)

    # --- Endpoint 2: adjacent-snapshot retention / turnover -----------------
    transitions = []
    for a, b in zip(ts, ts[1:]):
        A, B = set(snap[a]), set(snap[b])
        if not A:
            continue
        retained = len(A & B)
        transitions.append({
            "from_ts": a, "to_ts": b,
            "n_from": len(A), "n_to": len(B),
            "retained": retained,
            "retention_rate": retained / len(A),
            "turnover_rate": 1 - retained / len(A),
            "gap_days": None,   # snapshot spacing is irregular; see caveat
        })

    by_year = defaultdict(list)
    for t in transitions:
        by_year[t["from_ts"][:4]].append(t["retention_rate"])

    with open(os.path.join(OUT, "turnover_by_year.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["year", "n_transitions", "mean_retention",
                    "mean_turnover"])
        for y in sorted(by_year):
            v = by_year[y]
            m = sum(v) / len(v)
            w.writerow([y, len(v), round(m, 4), round(1 - m, 4)])

    # --- appearance-count distribution -------------------------------------
    appearances = defaultdict(int)
    for members in snap.values():
        for p in set(members):
            appearances[p] += 1
    dist = defaultdict(int)
    for c in appearances.values():
        dist[c] += 1
    total = len(appearances)

    with open(os.path.join(OUT, "appearance_distribution.csv"), "w",
              newline="") as f:
        w = csv.writer(f)
        w.writerow(["n_snapshots_present", "n_providers", "share",
                    "cumulative_share"])
        cum = 0
        for c in sorted(dist):
            cum += dist[c]
            w.writerow([c, dist[c], round(dist[c] / total, 4),
                        round(cum / total, 4)])

    overall = sum(t["retention_rate"] for t in transitions) / len(transitions)
    summary = {
        "n_snapshots": len(ts),
        "first_snapshot": ts[0],
        "last_snapshot": ts[-1],
        "n_distinct_providers": total,
        "n_transitions": len(transitions),
        "mean_retention_rate": round(overall, 4),
        "mean_turnover_rate": round(1 - overall, 4),
        "share_seen_once": round(dist.get(1, 0) / total, 4),
        "caveats": [
            "Snapshot spacing is irregular (Wayback capture dates), so "
            "adjacent-snapshot turnover is not a constant-interval rate; "
            "year strata mitigate but do not remove this.",
            "Rosters reflect what the archived index page rendered, which "
            "is a top-N view, not the full provider population.",
            "A provider re-listing under a new id is coded as a new "
            "provider (conservative rule, protocol section 6); this can "
            "only overstate turnover, never understate it.",
            "Descriptive only: no survival estimate, no causal claim.",
        ],
    }
    with open(os.path.join(OUT, "turnover_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
