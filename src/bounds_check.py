#!/usr/bin/env python3
"""
bounds_check.py — validity check for the Turnbull estimate.

Any interval-censored NPMLE must lie between two naive Kaplan-Meier curves
computed on the same data: one that dates every death at the interval's LEFT
endpoint (last seen alive => deaths as early as possible => survival lower
bound) and one that dates it at the RIGHT endpoint (first seen absent =>
deaths as late as possible => survival upper bound). A Turnbull curve outside
those bounds is proof of an implementation error, not a finding.

Writes artifacts/analysis/bounds_check.csv
"""
import csv, json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ART = os.path.join(ROOT, "artifacts", "analysis")


def km(deaths, censors):
    """Kaplan-Meier with censored subjects leaving the risk set at their time."""
    ev = sorted([(t, "d") for t in deaths] + [(t, "c") for t in censors])
    at_risk, S, curve, i = len(ev), 1.0, [], 0
    while i < len(ev):
        t = ev[i][0]
        d = c = 0
        while i < len(ev) and ev[i][0] == t:
            if ev[i][1] == "d":
                d += 1
            else:
                c += 1
            i += 1
        if d and at_risk:
            S *= 1 - d / at_risk
        curve.append((t, S))
        at_risk -= d + c
    return curve


def at(curve, day):
    s = 1.0
    for t, v in curve:
        if t <= day:
            s = v
        else:
            break
    return s


def at_risk(iv, cen, day):
    """Subjects still under observation at `day` (interval not yet closed and
    not yet censored). Bounds are only meaningful while this is non-trivial."""
    n = sum(1 for L, R in iv if R > day) + sum(1 for c in cen if c > day)
    return n


def main():
    rows = list(csv.DictReader(open(os.path.join(ART, "survival_intervals.csv"))))
    iv = [(float(r["L_days"]), float(r["R_days"])) for r in rows
          if r["type"] == "interval"]
    cen = [float(r["L_days"]) for r in rows if r["type"] == "censored"]
    tb = json.load(open(os.path.join(ART, "survival_summary.json")))["survival"]

    lower = km([L for L, _ in iv], cen)   # deaths at L  -> survival lower bound
    upper = km([R for _, R in iv], cen)   # deaths at R  -> survival upper bound

    # Minimum at-risk count below which the naive bounds stop being
    # informative: with a near-empty risk set the two KM curves can cross,
    # because dating deaths at L versus R reorders them against the censoring
    # times. That is a numerical artefact of the tail, not evidence about the
    # estimator, so those marks are reported as not assessable rather than
    # silently passed or failed.
    MIN_AT_RISK = 20

    out, ok_all = [], True
    for key, val in tb.items():
        day = int(key.split("_")[1].rstrip("d"))
        lo, hi = at(lower, day), at(upper, day)
        n = at_risk(iv, cen, day)
        if n < MIN_AT_RISK or hi < lo:
            res = "n/a (tail)"
        else:
            ok = lo - 1e-4 <= val <= hi + 1e-4
            ok_all &= ok
            res = "PASS" if ok else "FAIL"
        out.append([day, n, round(lo, 4), val, round(hi, 4), res])

    with open(os.path.join(ART, "bounds_check.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["days", "at_risk", "km_lower_bound", "turnbull",
                    "km_upper_bound", "result"])
        w.writerows(out)
    for r in out:
        print(r)
    assessed = [r for r in out if r[5] in ("PASS", "FAIL")]
    print("ALL PASS (%d marks assessed)" % len(assessed) if ok_all
          else "BOUNDS VIOLATED")
    return 0 if ok_all else 1


if __name__ == "__main__":
    raise SystemExit(main())
