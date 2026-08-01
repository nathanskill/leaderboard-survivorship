#!/usr/bin/env python3
"""
survival.py — Primary Endpoint 1 of protocol/locked_protocol_v1.0.md:
interval-censored survival of signal providers after first leaderboard entry.

Why interval censoring (protocol section 4): disappearance is never observed
directly. A provider present at snapshot t_k and absent at t_{k+1} disappeared
somewhere in the open interval (t_k, t_{k+1}]. Treating the right endpoint as
an exact death time (naive Kaplan-Meier) biases survival downward; treating
the left endpoint biases it upward. The Turnbull (1976) NPMLE is the correct
estimator for arbitrarily grouped censored data and is implemented here
directly (self-consistency / EM iteration), with no external dependency.

Cohort (frozen, protocol section 6):
  entry  = first snapshot in which the provider appears on the index roster
  death  = first snapshot at which the provider is absent, having been present
           at the immediately preceding snapshot => interval (L, R]
  right-censored = still present at the final snapshot
  re-listing under a new id is a NEW provider (conservative; can only
           overstate attrition -- protocol section 6)

Robustness: providers whose observation begins at the last snapshot are
INCLUDED as right-censored at 0 days. Such observations are informationless
for the NPMLE (they constrain nothing), so estimates are identical to
excluding them; inclusion is the smaller intervention and their count is
reported explicitly as n_zero_followup.

Sparse-year rule (frozen, protocol section 6): any calendar year with fewer
than 2 usable snapshots is reported descriptively only and excluded from the
survival model. The check is evaluated on every run and its result written to
artifacts/analysis/sparse_year_check.txt.

Reads:  artifacts/rosters/index_rosters.csv
Writes: artifacts/analysis/survival_intervals.csv
        artifacts/analysis/survival_turnbull.csv
        artifacts/analysis/survival_summary.json
        artifacts/analysis/sparse_year_check.txt
"""
import csv
import json
import os
from collections import OrderedDict
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ART = os.path.join(ROOT, "artifacts")
ROSTERS = os.path.join(ART, "rosters", "index_rosters.csv")
OUT = os.path.join(ART, "analysis")

TOL = 1e-9
MAX_ITER = 20000


def parse_ts(ts):
    return datetime.strptime(ts[:14], "%Y%m%d%H%M%S")


def load_snapshots():
    snap = OrderedDict()
    with open(ROSTERS, newline="") as f:
        for r in csv.DictReader(f):
            snap.setdefault(r["timestamp"], set()).add(r["signal_id"])
    return OrderedDict((k, snap[k]) for k in sorted(snap))


def build_intervals(snap):
    """Return (intervals, stats). Each interval is (L, R) in days since entry;
    R = None means right-censored at last observation."""
    ts = list(snap)
    times = [parse_ts(t) for t in ts]
    first_idx, last_idx = {}, {}
    for i, t in enumerate(ts):
        for p in snap[t]:
            first_idx.setdefault(p, i)
            last_idx[p] = i

    items = []
    n_censored = n_zero_followup = 0
    for p, i0 in first_idx.items():
        i_last = last_idx[p]
        entry = times[i0]
        if i_last == len(ts) - 1:
            # Still present at the final snapshot: right-censored. This
            # includes providers first observed AT the final snapshot, which
            # are right-censored at 0 days -- informationless for the NPMLE
            # (estimates identical to excluding them) but counted explicitly.
            dur = (times[i_last] - entry).days
            n_censored += 1
            if i0 == len(ts) - 1:
                n_zero_followup += 1
            items.append(((float(dur), None),
                          (p, ts[i0], ts[i_last], dur, "", "censored")))
            continue
        L = (times[i_last] - entry).days          # last seen alive
        R = (times[i_last + 1] - entry).days      # first seen absent
        if R <= L:
            R = L + 1
        items.append(((float(L), float(R)),
                      (p, ts[i0], ts[i_last], L, R, "interval")))

    # Deterministic output order: set iteration above is subject to hash
    # randomization, which made the committed CSV non-byte-reproducible
    # (identical as a multiset, different row order per run). Sort by
    # (entry_ts, signal_id) so artifact bytes are stable across runs.
    items.sort(key=lambda it: (it[1][1], it[1][0]))
    intervals = [iv for iv, _ in items]
    rows = [row for _, row in items]

    stats = {"n_providers": len(first_idx), "n_intervals": len(intervals),
             "n_right_censored": n_censored,
             "n_zero_followup": n_zero_followup}
    return intervals, rows, stats


SPARSE_YEAR_MIN = 2   # frozen at protocol section 6: "fewer than 2 usable
                      # snapshots" => descriptive reporting only, excluded
                      # from the survival model


def sparse_year_check(snap):
    """Frozen sparse-year rule (protocol section 6, mechanical): any calendar
    year with fewer than SPARSE_YEAR_MIN usable snapshots is excluded from
    the survival model and reported descriptively only. Returns (snap_kept,
    result_line); writes the one-line result artifact."""
    per_year = {}
    for t in snap:
        per_year[t[:4]] = per_year.get(t[:4], 0) + 1
    sparse = sorted(y for y, c in per_year.items() if c < SPARSE_YEAR_MIN)
    mn = min(per_year.values())
    at_min = sorted(y for y, c in per_year.items() if c == mn)
    if sparse:
        kept = OrderedDict((t, s) for t, s in snap.items()
                           if t[:4] not in sparse)
        line = ("sparse-year rule evaluated (protocol section 6, threshold "
                "< %d usable snapshots/year): years %s below threshold, "
                "excluded from the survival model and reported descriptively "
                "only (%d snapshots dropped)."
                % (SPARSE_YEAR_MIN, ", ".join(sparse),
                   len(snap) - len(kept)))
    else:
        kept = snap
        line = ("sparse-year rule evaluated (protocol section 6, threshold "
                "< %d usable snapshots/year): no year below threshold "
                "(min = %d usable snapshots, in %s); no exclusions."
                % (SPARSE_YEAR_MIN, mn, " and ".join(at_min)))
    with open(os.path.join(OUT, "sparse_year_check.txt"), "w") as f:
        f.write(line + "\n")
    print(line)
    return kept, line


def turnbull(intervals):
    """Turnbull NPMLE via self-consistency (EM). intervals: list of (L, R)
    with R=None for right censoring. Returns list of (left, right, prob)
    support intervals with positive mass."""
    # Candidate support: Turnbull intervals are [q_i, p_i] where q is a left
    # endpoint and p the next right endpoint with no other endpoint between.
    lefts = sorted({L for L, _ in intervals})
    rights = sorted({R for _, R in intervals if R is not None})
    INF = float("inf")
    if any(R is None for _, R in intervals):
        rights = rights + [INF]

    # Turnbull support: intervals (q, p] with q a left endpoint, p a right
    # endpoint, p strictly greater than q (the data convention is half-open
    # (L, R], so a degenerate (q, q] is the empty set and must never be a
    # support interval), and no endpoint of ANY kind strictly inside (q, p).
    # Checking only left endpoints, or admitting p == q, merges genuinely
    # disjoint intervals into one support point and corrupts the estimate.
    endpoints = sorted(set(lefts) | set(rights))
    cand = []
    for q in lefts:
        nxt = [r for r in rights if r > q]
        if not nxt:
            continue
        p = min(nxt)
        if not any(q < e < p for e in endpoints):
            cand.append((q, p))
    cand = sorted(set(cand))
    m = len(cand)
    if m == 0:
        return []

    # alpha[i][j] = 1 if support interval j is inside subject i's interval
    alpha = []
    for L, R in intervals:
        hi = INF if R is None else R
        alpha.append([1.0 if (q >= L and p <= hi) else 0.0 for q, p in cand])

    prob = [1.0 / m] * m
    for _ in range(MAX_ITER):
        new = [0.0] * m
        for a in alpha:
            denom = sum(a[j] * prob[j] for j in range(m))
            if denom <= 0:
                continue
            for j in range(m):
                if a[j]:
                    new[j] += a[j] * prob[j] / denom
        n = len(intervals)
        new = [x / n for x in new]
        if max(abs(new[j] - prob[j]) for j in range(m)) < TOL:
            prob = new
            break
        prob = new
    return [(cand[j][0], cand[j][1], prob[j]) for j in range(m)
            if prob[j] > 1e-8]


def main():
    os.makedirs(OUT, exist_ok=True)
    snap = load_snapshots()
    snap, sparse_line = sparse_year_check(snap)
    intervals, rows, stats = build_intervals(snap)

    with open(os.path.join(OUT, "survival_intervals.csv"), "w",
              newline="") as f:
        w = csv.writer(f)
        w.writerow(["signal_id", "entry_ts", "last_seen_ts",
                    "L_days", "R_days", "type"])
        w.writerows(rows)

    support = turnbull(intervals)

    # Survival function: S(t) = 1 - cumulative mass at or before t
    surv, cum = [], 0.0
    for q, p, pr in support:
        cum += pr
        surv.append((q, p, pr, 1 - cum))

    with open(os.path.join(OUT, "survival_turnbull.csv"), "w",
              newline="") as f:
        w = csv.writer(f)
        w.writerow(["support_left_days", "support_right_days",
                    "mass", "survival_after"])
        for q, p, pr, s in surv:
            w.writerow([q, "inf" if p == float("inf") else p,
                        round(pr, 6), round(s, 6)])

    def s_at(days):
        c = sum(pr for q, p, pr, _ in surv if p != float("inf") and p <= days)
        return round(1 - c, 4)

    marks = {f"S_{d}d": s_at(d) for d in (30, 90, 180, 365, 730, 1095)}
    # median: first t where S(t) <= 0.5
    median = None
    for q, p, pr, s in surv:
        if s <= 0.5:
            median = p if p != float("inf") else None
            break

    summary = {
        **stats,
        "sparse_year_rule": sparse_line,
        "estimator": "Turnbull (1976) NPMLE, self-consistency/EM",
        "n_support_intervals": len(support),
        "survival": marks,
        "median_survival_days": median,
        "caveats": [
            "Time origin is first observed appearance on the archived index, "
            "not platform registration; providers may predate their first "
            "capture.",
            "Snapshot spacing is irregular, so interval widths vary; this is "
            "handled by the interval-censored estimator rather than assumed "
            "away.",
            "Disappearance from the archived top-N roster is not proof of "
            "account closure: a provider may persist off the leaderboard. "
            "The endpoint is leaderboard visibility, and is reported as such.",
            "Re-listing under a new id counts as a new provider "
            "(conservative; can only overstate attrition).",
        ],
    }
    with open(os.path.join(OUT, "survival_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
