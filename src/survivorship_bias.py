#!/usr/bin/env python3
"""
survivorship_bias.py — the second half of the frozen contribution claim:
how much the leaderboard's visible performance distribution differs from the
distribution of everyone who ever entered it.

Protocol reference: locked_protocol_v1.0.md. Half (i) — how long providers
stay visible — is delivered by survival.py. This module delivers half (ii).

Three comparisons, all on the displayed growth figure (what a prospective
follower could actually read off the card at capture time; not audited
performance):

  1. VISIBILITY-WEIGHTED vs ENTRY-COHORT. The distribution a browsing visitor
     encounters counts a provider once per snapshot in which it appears, so a
     provider visible for 40 snapshots contributes 40 observations while a
     provider visible once contributes one. The entry cohort counts every
     provider exactly once, at first appearance. The gap between the two is
     the survivorship bias in what the leaderboard displays.

  2. SURVIVORS vs SINGLE-APPEARANCE, at first appearance only. Holding the
     observation point fixed (each provider's own first card), does the
     displayed growth of providers who go on to appear again differ from that
     of providers never seen again? This isolates selection from exposure.

  3. WITHIN-SNAPSHOT. For each snapshot, the median displayed growth of that
     snapshot's roster versus the median of the subset that is still present
     at the following snapshot. This is what the bias looks like at the
     moment of browsing.

Uncertainty: provider-clustered bootstrap (resampling whole providers), n=2000,
fixed seed, percentile intervals — the same discipline as the survival stage.

Reads:  artifacts/performance/provider_performance.csv
        artifacts/rosters/index_rosters.csv
Writes: artifacts/analysis/survivorship_bias.csv
        artifacts/analysis/survivorship_bias_summary.json
"""
import csv
import json
import os
import random
from collections import OrderedDict, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PERF = os.path.join(ROOT, "artifacts", "performance", "provider_performance.csv")
OUT = os.path.join(ROOT, "artifacts", "analysis")

N_BOOT = 2000
SEED = 20260723          # protocol freeze date, as in the survival stage


def median(xs):
    if not xs:
        return None
    s = sorted(xs)
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2


def quantile(xs, q):
    if not xs:
        return None
    s = sorted(xs)
    i = q * (len(s) - 1)
    lo, hi = int(i), min(int(i) + 1, len(s) - 1)
    return s[lo] + (s[hi] - s[lo]) * (i - lo)


def boot_median_ci(groups, rng):
    """Provider-clustered bootstrap CI for a median.

    `groups` is a list of per-provider lists of values; resampling is over
    providers, so a provider seen many times moves in and out as a unit.
    """
    if not groups:
        return (None, None)
    n = len(groups)
    meds = []
    for _ in range(N_BOOT):
        vals = []
        for _ in range(n):
            vals.extend(groups[rng.randrange(n)])
        m = median(vals)
        if m is not None:
            meds.append(m)
    if not meds:
        return (None, None)
    return (round(quantile(meds, 0.025), 2), round(quantile(meds, 0.975), 2))


def load():
    perf = []
    with open(PERF, newline="") as f:
        for r in csv.DictReader(f):
            if r["growth_pct"] == "":
                continue
            perf.append({"ts": r["timestamp"], "sid": r["signal_id"],
                         "growth": float(r["growth_pct"])})
    return perf


def main():
    os.makedirs(OUT, exist_ok=True)
    rng = random.Random(SEED)
    perf = load()

    # snapshot -> set of ids with a growth figure; provider -> observations
    snaps = OrderedDict()
    by_prov = defaultdict(list)
    for r in perf:
        snaps.setdefault(r["ts"], {})[r["sid"]] = r["growth"]
        by_prov[r["sid"]].append((r["ts"], r["growth"]))
    ts_sorted = sorted(snaps)
    for sid in by_prov:
        by_prov[sid].sort()

    # ---- comparison 1: visibility-weighted vs entry cohort ---------------
    visible_groups = [[g for _, g in obs] for obs in by_prov.values()]
    visible_vals = [g for grp in visible_groups for g in grp]
    entry_groups = [[obs[0][1]] for obs in by_prov.values()]
    entry_vals = [g for grp in entry_groups for g in grp]

    # ---- comparison 2: survivors vs single-appearance, at first appearance
    surv_groups, once_groups = [], []
    for sid, obs in by_prov.items():
        (surv_groups if len(obs) > 1 else once_groups).append([obs[0][1]])
    surv_vals = [g for grp in surv_groups for g in grp]
    once_vals = [g for grp in once_groups for g in grp]

    # ---- comparison 3: within-snapshot roster vs its survivors -----------
    per_snap = []
    for a, b in zip(ts_sorted, ts_sorted[1:]):
        roster = snaps[a]
        nxt = set(snaps[b])
        allv = list(roster.values())
        survv = [v for k, v in roster.items() if k in nxt]
        if len(allv) < 5 or len(survv) < 3:
            continue
        per_snap.append({
            "from_ts": a, "to_ts": b, "n_roster": len(allv),
            "n_survived": len(survv),
            "median_roster": round(median(allv), 2),
            "median_survivors": round(median(survv), 2),
            "delta": round(median(survv) - median(allv), 2),
        })

    with open(os.path.join(OUT, "survivorship_bias.csv"), "w",
              newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(per_snap[0].keys()))
        w.writeheader()
        w.writerows(per_snap)

    deltas = [p["delta"] for p in per_snap]
    pos = sum(1 for d in deltas if d > 0)

    def block(name, vals, groups):
        lo, hi = boot_median_ci(groups, rng)
        return {
            "n_observations": len(vals), "n_providers": len(groups),
            "median": round(median(vals), 2),
            "median_ci95": [lo, hi],
            "p25": round(quantile(vals, 0.25), 2),
            "p75": round(quantile(vals, 0.75), 2),
            "share_negative": round(sum(1 for v in vals if v < 0) / len(vals), 4),
        }

    summary = {
        "growth_field": ("displayed cumulative growth percentage as shown on "
                         "the archived card; window varies by card and its "
                         "label is retained in the extraction artifact"),
        "snapshots_with_growth": len(ts_sorted),
        "providers_with_growth": len(by_prov),
        "comparison_1_visibility_weighted_vs_entry_cohort": {
            "visibility_weighted": block("visible", visible_vals, visible_groups),
            "entry_cohort": block("entry", entry_vals, entry_groups),
            "median_gap": round(median(visible_vals) - median(entry_vals), 2),
        },
        "comparison_2_first_appearance_survivors_vs_single": {
            "survivors": block("surv", surv_vals, surv_groups),
            "single_appearance": block("once", once_vals, once_groups),
            "median_gap": round(median(surv_vals) - median(once_vals), 2),
        },
        "comparison_3_within_snapshot": {
            "n_transitions": len(per_snap),
            "median_delta": round(median(deltas), 2),
            "transitions_with_positive_delta": pos,
            "share_positive": round(pos / len(per_snap), 4),
        },
        "bootstrap": {"n": N_BOOT, "seed": SEED,
                      "unit": "provider (clustered)", "method": "percentile"},
        "caveats": [
            "The growth figure is what the page displayed, not audited "
            "performance; cards differ in the window the figure covers, so "
            "levels are comparable only in the loose sense in which a "
            "browsing visitor compares them.",
            "Growth is present only from 2017 onward; earlier layouts carry "
            "no growth field, so this analysis covers a shorter span than the "
            "survival analysis.",
            "A difference between survivors and single-appearance providers "
            "is a selection statement about what remains visible; it is not "
            "evidence about the providers' subsequent returns, which are not "
            "observed here.",
            "Comparison 1 is definitional as well as empirical: the "
            "visibility-weighted distribution counts long-lived providers "
            "many times by construction. That is precisely what a visitor "
            "encounters, which is why it is reported.",
        ],
    }
    with open(os.path.join(OUT, "survivorship_bias_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2)[:2600])


if __name__ == "__main__":
    main()
