#!/usr/bin/env python3
"""
extract.py — archive extraction for the leaderboard survivorship study
(REF-2026-018), implementing protocol/locked_protocol_v1.0.md.

Stage 1 (--index): enumerate archived snapshots of the leaderboard index via
    the Wayback CDX API, collapse to one snapshot per month, and record them.
Stage 2 (--fetch-index): download the raw archived HTML of each retained index
    snapshot (id_ replay = unrewritten original bytes) and hash it.
Stage 3 (--parse-index): extract the provider ids and inline fields present in
    each snapshot's static DOM, producing the per-snapshot leaderboard rosters
    from which cohorts and turnover are computed.

Politeness: serial requests with a fixed delay, descriptive User-Agent, and
bounded retries. Raw HTML lives under data/ (gitignored); rosters, manifests
and hashes are written to artifacts/ (public record). No provider is named in
any aggregate output; ids are retained only as within-study join keys.
"""
import argparse
import csv
import gzip
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import OrderedDict, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
ART = os.path.join(ROOT, "artifacts")
RAW_INDEX = os.path.join(DATA, "raw", "index")

CDX = "https://web.archive.org/cdx/search/cdx"
REPLAY = "https://web.archive.org/web/{ts}id_/{url}"
TARGET_INDEX = "mql5.com/en/signals"

UA = ("leaderboard-survivorship-research/1.0 "
      "(+https://github.com/nathanskill/leaderboard-survivorship)")
DELAY = 1.5          # seconds between requests (polite, serial)
TIMEOUT = 90
RETRIES = 3


def ensure(*dirs):
    for d in dirs:
        os.makedirs(d, exist_ok=True)


def get(url, tries=RETRIES):
    last = None
    for attempt in range(1, tries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                raw = r.read()
            if raw[:2] == b"\x1f\x8b":
                raw = gzip.decompress(raw)
            return raw
        except urllib.error.HTTPError as e:
            if e.code in (404, 403):
                return None
            last = e
        except Exception as e:            # noqa: BLE001 - network is messy
            last = e
        time.sleep(5 * attempt)
    print("  ! giving up on %s (%s)" % (url, last), file=sys.stderr)
    return None


def sha256(b):
    return hashlib.sha256(b).hexdigest()


# ---------------------------------------------------------------- stage 1
def cmd_index():
    """Enumerate archived index snapshots, one per month (earliest in month)."""
    ensure(DATA, ART, os.path.join(ART, "snapshots"))
    q = {
        "url": TARGET_INDEX,
        "output": "json",
        "fl": "timestamp,original,statuscode,digest,length",
        "filter": "statuscode:200",
        "collapse": "timestamp:6",     # one capture per YYYYMM
    }
    url = CDX + "?" + urllib.parse.urlencode(q)
    print("querying CDX:", url)
    raw = get(url)
    if not raw:
        print("CDX query failed", file=sys.stderr)
        return 1
    rows = json.loads(raw.decode("utf-8", "replace"))
    header, data = rows[0], rows[1:]
    out = os.path.join(ART, "snapshots", "index_snapshots.csv")
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header + ["year", "month"])
        for r in data:
            ts = r[0]
            w.writerow(r + [ts[:4], ts[4:6]])
    per_year = defaultdict(int)
    for r in data:
        per_year[r[0][:4]] += 1
    print("retained %d monthly index snapshots" % len(data))
    print("per-year density:", dict(sorted(per_year.items())))
    print("written:", out)
    return 0


# ---------------------------------------------------------------- stage 2
def cmd_fetch_index(limit=None):
    """Download raw (unrewritten) archived HTML for each retained snapshot."""
    ensure(RAW_INDEX, os.path.join(ART, "manifests"))
    src = os.path.join(ART, "snapshots", "index_snapshots.csv")
    if not os.path.exists(src):
        print("run --index first", file=sys.stderr)
        return 2
    with open(src, newline="") as f:
        snaps = list(csv.DictReader(f))
    if limit:
        snaps = snaps[:limit]
    man = os.path.join(DATA, "index_fetch_manifest.csv")
    fields = ["timestamp", "original", "bytes", "sha256", "status"]
    # Resumability: only rows with status=="ok" count as done. Building the
    # done-set from ALL rows (the previous behaviour) treated failed fetches
    # as complete and silently dropped those snapshots on any re-collection.
    manifest = OrderedDict()
    if os.path.exists(man):
        with open(man, newline="") as f:
            for r in csv.DictReader(f):
                manifest[r["timestamp"]] = r

    def write_manifest():
        # Full atomic rewrite: a retried fetch REPLACES its failed row in
        # place rather than appending a duplicate, and an interrupted run
        # still leaves a valid, duplicate-free manifest on disk.
        tmp = man + ".tmp"
        with open(tmp, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            for r in manifest.values():
                w.writerow(r)
        os.replace(tmp, man)

    ok = skipped = failed = 0
    for i, s in enumerate(snaps, 1):
        ts = s["timestamp"]
        prev = manifest.get(ts)
        if prev is not None and prev["status"] == "ok":
            skipped += 1
            continue
        path = os.path.join(RAW_INDEX, "%s.html" % ts)
        body = get(REPLAY.format(ts=ts, url=s["original"]))
        if body is None:
            manifest[ts] = {"timestamp": ts, "original": s["original"],
                            "bytes": 0, "sha256": "", "status": "failed"}
            failed += 1
        else:
            with open(path, "wb") as f:
                f.write(body)
            manifest[ts] = {"timestamp": ts, "original": s["original"],
                            "bytes": len(body), "sha256": sha256(body),
                            "status": "ok"}
            ok += 1
        write_manifest()
        if i % 20 == 0:
            print("  %d/%d (ok=%d skip=%d fail=%d)" % (i, len(snaps), ok,
                                                       skipped, failed))
        time.sleep(DELAY)
    write_manifest()
    import shutil
    shutil.copy2(man, os.path.join(ART, "manifests",
                                   "index_fetch_manifest.csv"))
    print("fetch complete: ok=%d skipped=%d failed=%d" % (ok, skipped, failed))
    return 0


# ---------------------------------------------------------------- stage 3
# Signal ids are plain integers with no fixed width: the earliest 2011
# listings are 3 digits (e.g. /en/signals/134) and current ones are 6-7.
# Anchoring on the locale-prefixed path avoids matching unrelated numbers.
ID_RE = re.compile(r"/signals/(\d{1,9})(?:[/\"'?#]|\b)")
# Inline numeric fields appear in the static DOM; captured leniently and
# validated downstream rather than assumed.
GROWTH_RE = re.compile(r"([+-]?\d[\d\s,]*\.?\d*)\s*%")


def cmd_parse_index():
    """Extract per-snapshot provider rosters from the archived index HTML."""
    ensure(os.path.join(ART, "rosters"))
    files = sorted(f for f in os.listdir(RAW_INDEX) if f.endswith(".html")) \
        if os.path.isdir(RAW_INDEX) else []
    if not files:
        print("no fetched snapshots; run --fetch-index first", file=sys.stderr)
        return 2
    out = os.path.join(ART, "rosters", "index_rosters.csv")
    rows = 0
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        # dom_order is FIRST-OCCURRENCE ORDER of a signal id across the
        # concatenated page sections of the archived index HTML -- it is NOT
        # a leaderboard rank. In 2012-2017 layouts positions 11-20 are the
        # MT4 top-10 appended after the MT5 top-10; post-2018 the order runs
        # across Reliability -> Popular -> High rating -> New sections; and
        # in snapshot 20120805222021 "position 1" is the MetaQuotes demo
        # signal in an alphabetical list. This column MUST NEVER feed the
        # protocol's secondary "past public rank predicts performance"
        # endpoint as-is; deriving a true rank requires (section,
        # within-section position) for eras where the page is a genuine
        # ranked list.
        w.writerow(["timestamp", "dom_order", "signal_id"])
        for name in files:
            ts = name[:-5]
            with open(os.path.join(RAW_INDEX, name), "rb") as fh:
                html = fh.read().decode("utf-8", "replace")
            seen, ordered = set(), []
            for m in ID_RE.finditer(html):
                sid = m.group(1)
                if sid not in seen:
                    seen.add(sid)
                    ordered.append(sid)
            for pos, sid in enumerate(ordered, 1):
                w.writerow([ts, pos, sid])
                rows += 1
    print("parsed %d snapshots -> %d roster rows" % (len(files), rows))
    print("written:", out)
    # quick shape report
    per_snap = defaultdict(int)
    with open(out, newline="") as f:
        for r in csv.DictReader(f):
            per_snap[r["timestamp"]] += 1
    vals = sorted(per_snap.values())
    if vals:
        print("providers per snapshot: min=%d median=%d max=%d"
              % (vals[0], vals[len(vals) // 2], vals[-1]))
    return 0


def main():
    p = argparse.ArgumentParser(
        description="Archive extraction for REF-2026-018 "
                    "(protocol/locked_protocol_v1.0.md)")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--index", action="store_true",
                   help="enumerate monthly index snapshots via CDX")
    g.add_argument("--fetch-index", action="store_true",
                   help="download raw archived HTML for each snapshot")
    g.add_argument("--parse-index", action="store_true",
                   help="extract per-snapshot provider rosters")
    p.add_argument("--limit", type=int, default=None,
                   help="with --fetch-index: process only the first N")
    a = p.parse_args()
    if a.index:
        return cmd_index()
    if a.fetch_index:
        return cmd_fetch_index(a.limit)
    return cmd_parse_index()


if __name__ == "__main__":
    sys.exit(main())
