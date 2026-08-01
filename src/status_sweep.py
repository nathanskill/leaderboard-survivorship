#!/usr/bin/env python3
"""
status_sweep.py — the terminal live status sweep required by the frozen
protocol (REF-2026-018).

Protocol reference: locked_protocol_v1.0.md section 4 defines a provider's
death as absence from the archived index roster "confirmed by one polite live
status sweep at analysis time". Until this ran, the realised endpoint was
roster absence alone, and the manuscript declared that as a live deviation
from the frozen definition. This module closes it.

What it measures, and why it is worth more than a compliance tick: it
separates the two things the paper has had to keep apart in prose. A provider
that has left the leaderboard may still have a live public page (it left the
top-N view) or may be gone entirely (the page no longer resolves). Roster
absence alone cannot tell them apart. One request per provider does.

POLITENESS AND SCOPE. robots.txt (fetched 2026-08-01) disallows a set of
sub-paths under /signals/ (deals, positions, reviews, pending-orders, new)
but not the provider page itself, which is the only path requested here. One
request per provider, serialised, with a 2-second pause, a descriptive
user-agent, and no authentication, no form submission and no personal data.
The sample is stratified rather than exhaustive so the total request count
stays modest.

A CONTROL GROUP is checked alongside the departed sample: every provider that
is right-censored (still present on the final archived roster). Without it, a
404 for a departed provider is ambiguous — the platform might simply retire
old pages regardless of who is behind them. The control fixes that: if
still-listed providers resolve while departed ones do not, page removal tracks
departure rather than page age.

Both groups are fetched by this script and both are resumable on signal_id,
so the whole sweep — departed sample and control alike — is reproducible from
the repository. (Provenance note: the control's first pass on 1 August 2026
was issued by an ad-hoc script before this code path existed; the committed
rows carry that run's timestamps, and re-running here appends nothing because
the ids are already present.)

Reads:  artifacts/analysis/survival_intervals.csv (who is coded dead, and who
        is right-censored and therefore the control)
Writes: artifacts/status/live_status.csv
        artifacts/status/control_still_listed.csv
        artifacts/status/status_summary.json
"""
import argparse
import csv
import json
import os
import random
import time
import urllib.error
import urllib.request
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INTERVALS = os.path.join(ROOT, "artifacts", "analysis", "survival_intervals.csv")
OUT = os.path.join(ROOT, "artifacts", "status")

URL = "https://www.mql5.com/en/signals/%s"
UA = ("leaderboard-survivorship-research/1.0 (academic measurement, one "
      "request per provider; contact via "
      "github.com/nathanskill/leaderboard-survivorship)")
PAUSE = 2.0
TIMEOUT = 45
SEED = 20260723           # protocol freeze date, as elsewhere
PER_STRATUM = 20          # providers sampled per last-seen year


def head(url):
    """HEAD the page; fall back to a ranged GET if HEAD is not honoured."""
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return r.status, r.headers.get("Content-Length", ""), ""
    except urllib.error.HTTPError as e:
        if e.code in (403, 405):                 # HEAD refused; try tiny GET
            try:
                g = urllib.request.Request(
                    url, headers={"User-Agent": UA, "Range": "bytes=0-2047"})
                with urllib.request.urlopen(g, timeout=TIMEOUT) as r2:
                    return r2.status, r2.headers.get("Content-Length", ""), ""
            except urllib.error.HTTPError as e2:
                return e2.code, "", ""
            except Exception as exc2:            # noqa: BLE001
                return -1, "", str(exc2)[:80]
        return e.code, "", ""
    except Exception as exc:                     # noqa: BLE001
        return -1, "", str(exc)[:80]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--per-stratum", type=int, default=PER_STRATUM)
    p.add_argument("--dry-run", action="store_true",
                   help="draw and report the sample without any request")
    p.add_argument("--control-only", action="store_true",
                   help="check only the control group, then summarise")
    a = p.parse_args()

    os.makedirs(OUT, exist_ok=True)
    rng = random.Random(SEED)

    # Providers coded dead (an interval, not right-censored), keyed by the
    # year in which they were last seen on a roster.
    by_year = defaultdict(list)
    with open(INTERVALS, newline="") as f:
        for r in csv.DictReader(f):
            if r["type"] != "interval":
                continue
            by_year[r["last_seen_ts"][:4]].append(r["signal_id"])

    sample = []
    for year in sorted(by_year):
        ids = sorted(by_year[year])
        k = min(a.per_stratum, len(ids))
        for sid in rng.sample(ids, k):
            sample.append((year, sid))
    print(f"strata: {len(by_year)} years; sampled {len(sample)} providers "
          f"(<= {a.per_stratum}/year); estimated runtime "
          f"{len(sample) * PAUSE / 60:.0f} min")
    if a.dry_run:
        for y in sorted(by_year):
            print(f"  {y}: {len(by_year[y])} dead, "
                  f"{min(a.per_stratum, len(by_year[y]))} sampled")
        return 0

    # ---- control group: every right-censored provider --------------------
    # Issued by this script so the control is reproducible from the repo.
    # Resumable on signal_id, like the departed sweep.
    ctrl_ids = []
    with open(INTERVALS, newline="") as f:
        for r in csv.DictReader(f):
            if r["type"] == "censored":
                ctrl_ids.append((r["signal_id"], r["entry_ts"]))
    ctrl_ids.sort()
    cpath = os.path.join(OUT, "control_still_listed.csv")
    cdone = set()
    if os.path.exists(cpath):
        with open(cpath, newline="") as f:
            for r in csv.DictReader(f):
                cdone.add(r["signal_id"])
    cnew = not os.path.exists(cpath)
    cstamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    todo_ctrl = [(sid, ets) for sid, ets in ctrl_ids if sid not in cdone]
    CTRL_FIELDS = ["signal_id", "entry_ts", "http_status", "group",
                   "checked_utc"]
    if not cnew:
        # Appending to a file whose header has fewer columns would silently
        # misalign every new row, so refuse rather than corrupt.
        with open(cpath, newline="") as f:
            existing = next(csv.reader(f))
        if existing != CTRL_FIELDS:
            raise SystemExit(
                "control file header %s does not match %s; refusing to "
                "append. Migrate the file first." % (existing, CTRL_FIELDS))
    if todo_ctrl:
        print(f"control group: {len(ctrl_ids)} still-listed providers, "
              f"{len(todo_ctrl)} to check")
        with open(cpath, "a", newline="") as f:
            w = csv.DictWriter(f, fieldnames=CTRL_FIELDS)
            if cnew:
                w.writeheader()
            for sid, ets in todo_ctrl:
                status, _clen, _err = head(URL % sid)
                w.writerow({"signal_id": sid, "entry_ts": ets,
                            "http_status": status,
                            "group": "still-listed-control",
                            "checked_utc": cstamp})
                f.flush()
                time.sleep(PAUSE)
    else:
        print(f"control group: {len(ctrl_ids)} providers already checked")
    if a.control_only:
        print("control-only run; skipping the departed sweep")

    done = {}
    path = os.path.join(OUT, "live_status.csv")
    if os.path.exists(path):
        with open(path, newline="") as f:
            for r in csv.DictReader(f):
                done[r["signal_id"]] = r
    new = not os.path.exists(path)
    stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    with open(path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["signal_id", "last_seen_year",
                                          "http_status", "content_length",
                                          "error", "checked_utc"])
        if new:
            w.writeheader()
        for i, (year, sid) in enumerate(sample, 1):
            if sid in done or a.control_only:
                continue
            status, clen, err = head(URL % sid)
            w.writerow({"signal_id": sid, "last_seen_year": year,
                        "http_status": status, "content_length": clen,
                        "error": err, "checked_utc": stamp})
            f.flush()
            if i % 25 == 0:
                print(f"  [{i}/{len(sample)}] last={status}")
            time.sleep(PAUSE)

    rows = list(csv.DictReader(open(path, newline="")))
    ctrl_path = os.path.join(OUT, "control_still_listed.csv")
    ctrl = list(csv.DictReader(open(ctrl_path, newline=""))) \
        if os.path.exists(ctrl_path) else []
    live = [r for r in rows if r["http_status"] == "200"]
    gone = [r for r in rows if r["http_status"] in ("404", "410")]
    other = [r for r in rows if r not in live and r not in gone]
    per_year = defaultdict(lambda: {"n": 0, "live": 0})
    for r in rows:
        per_year[r["last_seen_year"]]["n"] += 1
        if r["http_status"] == "200":
            per_year[r["last_seen_year"]]["live"] += 1

    ctrl_live = sum(1 for r in ctrl if str(r.get("http_status")) == "200")
    # Matched-recency contrast: departed in the most recent year present in
    # both groups, versus still-listed providers whose first appearance falls
    # in that same year. This is the comparison that separates departure from
    # page age, because both sides are equally recent.
    recent = max((r["last_seen_year"] for r in rows), default="")
    dep_recent = [r for r in rows if r["last_seen_year"] == recent]
    ctl_recent = [r for r in ctrl if r.get("entry_ts", "")[:4] == recent]

    n = len(rows)
    summary = {
        "checked_utc": stamp,
        "n_checked": n,
        "n_live_200": len(live),
        "n_gone_404_410": len(gone),
        "n_other_or_error": len(other),
        "share_still_live": round(len(live) / n, 4) if n else None,
        "by_last_seen_year": {y: {**v,
                                  "share_live": round(v["live"] / v["n"], 4)}
                              for y, v in sorted(per_year.items())},
        "control_still_listed": {
            "n": len(ctrl), "n_live_200": ctrl_live,
            "share_live": round(ctrl_live / len(ctrl), 4) if ctrl else None,
            "definition": ("every right-censored provider, i.e. present on "
                           "the final archived roster"),
        },
        "matched_recency_contrast": {
            "year": recent,
            "departed_n": len(dep_recent),
            "departed_live": sum(1 for r in dep_recent
                                 if r["http_status"] == "200"),
            "still_listed_n": len(ctl_recent),
            "still_listed_live": sum(1 for r in ctl_recent
                                     if str(r.get("http_status")) == "200"),
        },
        "method": ("one HEAD request per sampled provider page "
                   "(/en/signals/<id>), 2 s apart, descriptive user-agent, no "
                   "authentication and no personal data; robots.txt permits "
                   "this path"),
        "interpretation": [
            "A 200 means the provider page still resolves: the provider left "
            "the archived top-N leaderboard view but was not removed from the "
            "platform. A 404/410 means the page no longer resolves.",
            "This confirms the protocol's death definition operationally and, "
            "more usefully, measures how far leaderboard visibility and "
            "platform presence diverge — the distinction the survival results "
            "have had to make in prose.",
            "The sweep is a single point in time (the check date), so a live "
            "page today says nothing about the provider's state at the moment "
            "it left the roster.",
            "Sampling is stratified by last-seen year and capped per stratum, "
            "so shares are within-stratum estimates; the pooled share is not "
            "population-weighted.",
            "The control group contains no provider whose first appearance "
            "predates 2024, because no longer-tenured provider is still on "
            "the final roster. A page-retirement policy operating only on "
            "timescales beyond that range is therefore not excluded by the "
            "control alone; the matched-recency contrast is what separates "
            "departure from page age within the range the data covers.",
        ],
    }
    with open(os.path.join(OUT, "status_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps({k: v for k, v in summary.items()
                      if k not in ("interpretation", "by_last_seen_year")},
                     indent=2))
    print("\nby last-seen year (checked / still live):")
    for y, v in sorted(per_year.items()):
        print(f"  {y}  {v['n']:>3} / {v['live']:>3}  ({v['live']/v['n']:.0%})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
