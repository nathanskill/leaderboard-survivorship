#!/usr/bin/env python3
"""
make_figures.py — deterministic figures for REF-2026-018 from frozen artifacts.

Figure 1: Turnbull interval-censored survival of leaderboard visibility after
first appearance, with the naive-KM bound envelope from bounds_check logic.
Figure 2: adjacent-snapshot turnover by year + appearance-count distribution.

Reads only committed artifacts; writes PNG files. No randomness.
"""
import csv
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = os.environ.get("REPO_018", os.path.expanduser("~/research/leaderboard-survivorship"))
ART = os.path.join(REPO, "artifacts", "analysis")
OUT = os.environ.get("FIG_OUT", os.path.join(REPO, "paper", "figures"))

GREY = "#4a4a4a"
BLUE = "#1f77b4"
BAND = "#9ecae1"


def load_turnbull():
    rows = list(csv.DictReader(open(os.path.join(ART, "survival_turnbull.csv"))))
    steps = []  # (time, survival_after)
    for r in rows:
        right = r["support_right_days"]
        if right == "inf":
            continue
        steps.append((float(right), float(r["survival_after"])))
    return steps


def km(deaths, censors):
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


def load_bounds():
    rows = list(csv.DictReader(open(os.path.join(ART, "survival_intervals.csv"))))
    iv = [(float(r["L_days"]), float(r["R_days"])) for r in rows
          if r["type"] == "interval"]
    cen = [float(r["L_days"]) for r in rows if r["type"] == "censored"]
    return km([L for L, _ in iv], cen), km([R for _, R in iv], cen), rows


def step_xy(steps, xmax):
    xs, ys = [0.0], [1.0]
    for t, s in steps:
        if t > xmax:
            break
        xs += [t, t]
        ys += [ys[-1], s]
    xs.append(xmax)
    ys.append(ys[-1])
    return xs, ys


def fig1():
    steps = load_turnbull()
    lower, upper, rows = load_bounds()
    XMAX = 730.0

    fig, ax = plt.subplots(figsize=(7.0, 4.4))
    lx, ly = step_xy(lower, XMAX)
    ux, uy = step_xy(upper, XMAX)
    ax.fill(lx + ux[::-1], ly + uy[::-1], color=BAND, alpha=0.45, lw=0,
            label="naive-KM bound envelope (deaths at L vs at R)")
    tx, ty = step_xy(steps, XMAX)
    ax.plot(tx, ty, color=BLUE, lw=2.0,
            label="Turnbull NPMLE (interval-censored)")

    for d, lab in [(30, "30 d"), (90, "90 d"), (180, "180 d"), (365, "1 y")]:
        s = next((y for x, y in zip(tx, ty) if x >= d), None)
        sv = [y for x, y in zip(tx, ty) if x <= d]
        s = sv[-1] if sv else 1.0
        ax.plot([d], [s], "o", color=GREY, ms=4)
        ax.annotate(f"{lab}: {s:.1%}", (d, s), textcoords="offset points",
                    xytext=(8, 8), fontsize=8.5, color=GREY)

    ax.set_xlim(0, XMAX)
    ax.set_ylim(0, 1.0)
    ax.set_xlabel("days since first appearance on the archived leaderboard index")
    ax.set_ylabel("probability still visible on the leaderboard")
    ax.set_title("Survival of leaderboard visibility, 2,090 signal providers, 2011–2026",
                 fontsize=11)
    ax.legend(fontsize=8.5, loc="upper right", frameon=False)
    ax.grid(alpha=0.25, lw=0.5)
    fig.tight_layout()
    path = os.path.join(OUT, "fig1_survival.png")
    fig.savefig(path, dpi=200)
    print("written:", path)


def fig2():
    by_year = list(csv.DictReader(open(os.path.join(ART, "turnover_by_year.csv"))))
    dist = list(csv.DictReader(open(os.path.join(ART, "appearance_distribution.csv"))))

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.6, 3.8))

    years = [r["year"] for r in by_year]
    tv = [float(r["mean_turnover"]) for r in by_year]
    a1.bar(years, tv, color=BLUE, alpha=0.85)
    a1.axhline(sum(tv) / len(tv), color=GREY, ls="--", lw=1,
               label=f"unweighted mean of yearly rates {sum(tv)/len(tv):.0%}")
    a1.set_ylabel("mean adjacent-snapshot turnover")
    a1.set_title("Roster turnover by year", fontsize=10)
    a1.tick_params(axis="x", rotation=60, labelsize=7.5)
    a1.legend(fontsize=8, frameon=False)
    a1.grid(axis="y", alpha=0.25, lw=0.5)

    ks = [int(r["n_snapshots_present"]) for r in dist][:10]
    share = [float(r["share"]) for r in dist][:10]
    a2.bar([str(k) for k in ks], share, color=BLUE, alpha=0.85)
    a2.set_xlabel("snapshots in which a provider appears")
    a2.set_ylabel("share of providers")
    a2.set_title("Appearance-count distribution (truncated at 10)", fontsize=10)
    a2.annotate(f"{share[0]:.0%} appear exactly once", (0, share[0]),
                textcoords="offset points", xytext=(10, -2), fontsize=9,
                color=GREY)
    a2.grid(axis="y", alpha=0.25, lw=0.5)

    fig.tight_layout()
    path = os.path.join(OUT, "fig2_turnover.png")
    fig.savefig(path, dpi=200)
    print("written:", path)


def fig3():
    """Survivorship bias in the displayed performance distribution."""
    import json
    d = json.load(open(os.path.join(ART, "survivorship_bias_summary.json")))
    c2 = d["comparison_2_first_appearance_survivors_vs_single"]
    c4 = d["comparison_4_stratified_by_track_record"]
    per = list(csv.DictReader(open(os.path.join(ART, "survivorship_bias.csv"))))

    fig, (a1, a2, a3) = plt.subplots(1, 3, figsize=(11.6, 4.2))

    # (a) survivors vs single-appearance at first appearance, with CIs
    labels = ["seen again", "seen once"]
    meds = [c2["survivors"]["median"], c2["single_appearance"]["median"]]
    cis = [c2["survivors"]["median_ci95"], c2["single_appearance"]["median_ci95"]]
    ns = [c2["survivors"]["n_providers"], c2["single_appearance"]["n_providers"]]
    err = [[m - c[0] for m, c in zip(meds, cis)],
           [c[1] - m for m, c in zip(meds, cis)]]
    a1.bar(labels, meds, color=[BLUE, "#9e9e9e"], alpha=0.9, width=0.55)
    a1.errorbar(labels, meds, yerr=err, fmt="none", ecolor=GREY,
                capsize=5, lw=1.2)
    for i, (m, n) in enumerate(zip(meds, ns)):
        a1.annotate(f"{m:.0f}%\nn={n}", (i, cis[i][1]), ha="center",
                    textcoords="offset points", xytext=(0, 8), fontsize=9,
                    color=GREY)
    a1.set_ylabel("median displayed growth at first\nappearance (%)", fontsize=9)
    a1.set_title("(a) Selection at entry", fontsize=10)
    a1.set_ylim(0, max(c[1] for c in cis) * 1.35)
    a1.grid(axis="y", alpha=0.25, lw=0.5)

    # (b) stratified by displayed track record
    st = c4["strata"]
    x = [s["track_record_years"] for s in st]
    xs = [i - 0.18 for i in range(len(x))]
    xo = [i + 0.18 for i in range(len(x))]
    a2.bar(xs, [s["median_survivors"] for s in st], width=0.34, color=BLUE,
           alpha=0.9, label="seen again")
    a2.bar(xo, [s["median_single"] for s in st], width=0.34, color="#9e9e9e",
           alpha=0.9, label="seen once")
    a2.errorbar(xs, [s["median_survivors"] for s in st],
                yerr=[[s["median_survivors"] - s["ci95_survivors"][0] for s in st],
                      [s["ci95_survivors"][1] - s["median_survivors"] for s in st]],
                fmt="none", ecolor=GREY, capsize=3, lw=1)
    a2.errorbar(xo, [s["median_single"] for s in st],
                yerr=[[s["median_single"] - s["ci95_single"][0] for s in st],
                      [s["ci95_single"][1] - s["median_single"] for s in st]],
                fmt="none", ecolor=GREY, capsize=3, lw=1)
    a2.set_xticks(range(len(x)))
    a2.set_xticklabels([str(v) for v in x])
    a2.set_xlabel("displayed track record at first appearance (years)")
    a2.set_ylabel("median displayed growth (%)", fontsize=9)
    a2.set_title("(b) Within track-record bands", fontsize=10)
    a2.legend(fontsize=8, frameon=False)
    a2.grid(axis="y", alpha=0.25, lw=0.5)

    # (c) within-snapshot deltas
    deltas = [float(r["delta"]) for r in per]
    a3.hist(deltas, bins=18, color=BLUE, alpha=0.85)
    a3.axvline(0, color=GREY, lw=1)
    pos = sum(1 for v in deltas if v > 0)
    a3.set_xlabel("survivor median $-$ roster median\n(percentage points)", fontsize=9)
    a3.set_ylabel("snapshot transitions")
    a3.set_title(f"(c) Positive in {pos} of {len(deltas)} transitions",
                 fontsize=10)
    a3.grid(axis="y", alpha=0.25, lw=0.5)

    fig.tight_layout()
    path = os.path.join(OUT, "fig3_survivorship_bias.png")
    fig.savefig(path, dpi=200)
    print("written:", path)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    fig1()
    fig2()
    fig3()
