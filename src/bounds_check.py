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


def main():
    rows = list(csv.DictReader(open(os.path.join(ART, "survival_intervals.csv"))))
    iv = [(float(r["L_days"]), float(r["R_days"])) for r in rows
          if r["type"] == "interval"]
    cen = [float(r["L_days"]) for r in rows if r["type"] == "censored"]
    tb = json.load(open(os.path.join(ART, "survival_summary.json")))["survival"]

    lower = km([L for L, _ in iv], cen)   # deaths at L  -> survival lower bound
    upper = km([R for _, R in iv], cen)   # deaths at R  -> survival upper bound

    out, ok_all = [], True
    for key, val in tb.items():
        day = int(key.split("_")[1].rstrip("d"))
        lo, hi = at(lower, day), at(upper, day)
        ok = lo - 1e-4 <= val <= hi + 1e-4
        ok_all &= ok
        out.append([day, round(lo, 4), val, round(hi, 4), "PASS" if ok else "FAIL"])

    with open(os.path.join(ART, "bounds_check.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["days", "km_lower_bound", "turnbull", "km_upper_bound", "result"])
        w.writerows(out)
    for r in out:
        print(r)
    print("ALL PASS" if ok_all else "BOUNDS VIOLATED")
    return 0 if ok_all else 1


if __name__ == "__main__":
    raise SystemExit(main())
