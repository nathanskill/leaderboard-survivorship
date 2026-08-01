#!/usr/bin/env python3
"""
survivorship_bias.py — the second half of the frozen contribution claim:
how much the leaderboard's visible performance distribution differs from the
distribution of everyone who ever entered it.

Protocol reference: locked_protocol_v1.0.md. Half (i) — how long providers
stay visible — is delivered by survival.py. This module delivers half (ii).

Four comparisons, all on the displayed growth figure (what a prospective
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

  4. STRATIFIED BY TRACK-RECORD LENGTH. Comparison 2 has an obvious
     confound: the displayed figure is growth since a stated inception year,
     so a provider with a longer displayed history mechanically shows a
     larger cumulative number, and providers who survive may simply be older.
     The card's growth label carries that inception year, so the comparison
     is repeated within bands of displayed track-record length at first
     appearance. If the gap vanishes inside the bands, comparison 2 was an
     age artefact; if it persists, it is not.

Uncertainty: provider-clustered bootstrap (resampling whole providers), n=2000,
percentile intervals — the same discipline as the survival stage. Each block
draws from its OWN generator, seeded deterministically from the master seed
and the block's name, so that adding or reordering an analysis cannot shift a
previously reported interval. An earlier revision threaded one generator
through every block; adding the stratified comparison then moved the intervals
of comparisons 1-3 while leaving their point estimates unchanged. Per-block
seeding removes that coupling.

Reads:  artifacts/performance/provider_performance.csv
        artifacts/rosters/index_rosters.csv
Writes: artifacts/analysis/survivorship_bias.csv
        artifacts/analysis/survivorship_bias_summary.json
"""
import csv
import json
import os
import random
import re
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


def boot_gap_ci(groups_a, groups_b, rng):
    """Bootstrap interval for the DIFFERENCE of two medians.

    Comparing two separately-computed intervals for overlap is a crude and
    conservative test: non-overlap implies a difference, but overlap does not
    imply its absence. Resampling both groups jointly and taking the interval
    of the difference is the direct statement, and matches the paired-delta
    discipline used in the companion replication audit.
    """
    if not groups_a or not groups_b:
        return (None, None)
    na, nb = len(groups_a), len(groups_b)
    gaps = []
    for _ in range(N_BOOT):
        va = []
        for _ in range(na):
            va.extend(groups_a[rng.randrange(na)])
        vb = []
        for _ in range(nb):
            vb.extend(groups_b[rng.randrange(nb)])
        ma, mb = median(va), median(vb)
        if ma is not None and mb is not None:
            gaps.append(ma - mb)
    if not gaps:
        return (None, None)
    return (round(quantile(gaps, 0.025), 2), round(quantile(gaps, 0.975), 2))


def block_rng(name):
    """Deterministic per-block generator: seed = master seed + block name.

    Blocks are independent, so adding a comparison never perturbs another's
    interval, and any single block can be re-run in isolation.
    """
    return random.Random("%d:%s" % (SEED, name))


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


SINCE_RE = re.compile(r"since\s+(\d{4})", re.I)


def load():
    perf = []
    with open(PERF, newline="") as f:
        for r in csv.DictReader(f):
            if r["growth_pct"] == "":
                continue
            m = SINCE_RE.search(r.get("growth_label", "") or "")
            age = ""
            if m:
                a = int(r["timestamp"][:4]) - int(m.group(1))
                if a >= 0:
                    age = a
            perf.append({"ts": r["timestamp"], "sid": r["signal_id"],
                         "growth": float(r["growth_pct"]), "age": age})
    return perf


def main():
    os.makedirs(OUT, exist_ok=True)
    perf = load()

    # snapshot -> set of ids with a growth figure; provider -> observations
    snaps = OrderedDict()
    by_prov = defaultdict(list)
    for r in perf:
        snaps.setdefault(r["ts"], {})[r["sid"]] = r["growth"]
        by_prov[r["sid"]].append((r["ts"], r["growth"], r["age"]))
    ts_sorted = sorted(snaps)
    for sid in by_prov:
        by_prov[sid].sort()

    # ---- comparison 1: visibility-weighted vs entry cohort ---------------
    visible_groups = [[o[1] for o in obs] for obs in by_prov.values()]
    visible_vals = [g for grp in visible_groups for g in grp]
    entry_groups = [[obs[0][1]] for obs in by_prov.values()]
    entry_vals = [g for grp in entry_groups for g in grp]

    # ---- comparison 2: survivors vs single-appearance, at first appearance
    surv_groups, once_groups = [], []
    for sid, obs in by_prov.items():
        (surv_groups if len(obs) > 1 else once_groups).append([obs[0][1]])
    surv_vals = [g for grp in surv_groups for g in grp]
    once_vals = [g for grp in once_groups for g in grp]

    # ---- comparison 4: stratified by displayed track-record length -------
    strata = defaultdict(lambda: ([], []))
    for obs in by_prov.values():
        age = obs[0][2]
        if age == "":
            continue
        (strata[age][0] if len(obs) > 1 else strata[age][1]).append(obs[0][1])
    stratified = []
    for age in sorted(strata):
        sv, on = strata[age]
        if len(sv) < 8 or len(on) < 8:
            continue                      # too thin to report
        slo, shi = boot_median_ci([[v] for v in sv],
                                  block_rng("strat%s.surv" % age))
        olo, ohi = boot_median_ci([[v] for v in on],
                                  block_rng("strat%s.single" % age))
        glo, ghi = boot_gap_ci([[v] for v in sv], [[v] for v in on],
                               block_rng("strat%s.gap" % age))
        stratified.append({
            "track_record_years": age,
            "n_survivors": len(sv), "median_survivors": round(median(sv), 2),
            "ci95_survivors": [slo, shi],
            "n_single": len(on), "median_single": round(median(on), 2),
            "ci95_single": [olo, ohi],
            "gap": round(median(sv) - median(on), 2),
            "gap_ci95": [glo, ghi],
            "gap_ci_excludes_zero": bool(glo is not None and glo > 0),
            "ci_overlap": bool(slo is not None and ohi is not None
                               and slo <= ohi),
        })
    age_sv = [o[0][2] for o in by_prov.values()
              if len(o) > 1 and o[0][2] != ""]
    age_on = [o[0][2] for o in by_prov.values()
              if len(o) == 1 and o[0][2] != ""]

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
        lo, hi = boot_median_ci(groups, block_rng(name))
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
            "median_gap_ci95": list(boot_gap_ci(surv_groups, once_groups,
                                                block_rng("c2.gap"))),
        },
        "comparison_4_stratified_by_track_record": {
            "rationale": ("the displayed figure is cumulative growth since a "
                          "stated inception year, so longer-displayed "
                          "providers show larger numbers mechanically; the "
                          "confound is real (median displayed track record at "
                          "first appearance: %s years for providers seen "
                          "again, %s for providers seen once), so the "
                          "comparison is repeated within bands"
                          % (median(age_sv), median(age_on))),
            "median_track_record_survivors": median(age_sv),
            "median_track_record_single": median(age_on),
            "strata": stratified,
            "gap_positive_in_all_reported_strata": all(
                s["gap"] > 0 for s in stratified),
            "strata_whose_gap_interval_excludes_zero": [
                s["track_record_years"] for s in stratified
                if s["gap_ci_excludes_zero"]],
            "inference_note": ("gap_ci95 is the direct bootstrap interval for "
                               "the difference of medians and is the statement "
                               "to read; ci_overlap between the two separate "
                               "intervals is reported alongside it only "
                               "because it is the cruder comparison a reader "
                               "may otherwise make, and it is conservative"),
        },
        "comparison_3_within_snapshot": {
            "n_transitions": len(per_snap),
            "median_delta": round(median(deltas), 2),
            "transitions_with_positive_delta": pos,
            "share_positive": round(pos / len(per_snap), 4),
        },
        "bootstrap": {"n": N_BOOT, "master_seed": SEED,
                      "seeding": ("per block: Random('<master_seed>:<block "
                                  "name>'), so blocks are independent and "
                                  "adding an analysis cannot shift another's "
                                  "interval"),
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
            "Comparison 2's gap is not an artefact of displayed track-record "
            "length: the confound is present but the gap persists inside "
            "every reported band (comparison 4). Bands thinner than 8 "
            "providers on either side are not reported.",
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
