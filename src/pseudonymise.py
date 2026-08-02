#!/usr/bin/env python3
"""
pseudonymise.py — replace raw platform signal ids with study-local pseudonyms
across every committed artifact that carries one (REF-2026-018).

STATUS: PREPARED, NOT RUN. No committed artifact in this repository has been
pseudonymised. This module exists so that the decision recorded in the
re-identification audit can be executed in one command if the author decides
to take it. Running it changes the published corpus; that is the author's call,
not the script's, which is why --apply is mandatory and the default is a dry
run that writes nothing.

WHY THE QUESTION ARISES. Signal ids are platform-assigned integers. They are
already public on a public leaderboard, and they are the join key that makes
every result in this study reproducible against the archive. They are also a
re-identification vector: /en/signals/<id> resolves to a provider page, and
behind these pseudonymous commercial listings are, in some proportion, natural
persons. Under Australian defamation law a natural person who is reasonably
identifiable can sue; a corporation with 10+ employees generally cannot.

WHAT THIS SCRIPT CANNOT DO, STATED UP FRONT. Pseudonymising the id column does
NOT make a provider unidentifiable, because the corpus is reproducible by
design and re-derivation restores the mapping:

  1. artifacts/rosters/index_rosters.csv and
     artifacts/performance/provider_performance.csv keep (timestamp,
     dom_order), which is unique on all 4,325 rows in each file. Anyone who
     re-runs `src/extract.py --index --fetch-index --parse-index` — which the
     reproducibility statement instructs them to do — recovers the exact id
     for every pseudonym by positional join. Removing dom_order to block that
     join would destroy the roster artifact's document-order provenance and
     the extraction consistency check of manuscript section 3.7.
  2. The archived pages themselves are public and permanent. The names are in
     the Wayback Machine whether or not this repository carries the ids.

So the honest description of what pseudonymisation buys is: it removes the
one-step lookup (paste an id into a URL) and makes re-identification require
deliberate re-derivation. It does not make the study anonymous, and any claim
that it does would be false. The corresponding cost is stated per mode below.

MODES
  --mode mapped        Write the id->pseudonym mapping to a file under the
                       gitignored data/ directory. Reproducibility is fully
                       preserved for the author and for anyone the author
                       chooses to give the mapping to; a third party can still
                       re-derive it from the archive as above. This is the
                       "pseudonymise with a published mapping held locally"
                       option.
  --mode irreversible  Derive pseudonyms from a random salt that is never
                       written anywhere, then discard it. The author loses the
                       mapping too. Note that this does NOT achieve
                       irreversibility in fact, for the reasons above; it only
                       destroys the author's own copy. Offered for
                       completeness, and recommended against in the audit
                       precisely because it pays a real reproducibility cost
                       for a privacy gain the corpus's own design denies it.

PSEUDONYM ORDERING. Labels are assigned in salted-hash order, never in
ascending id order. Ascending order would leak id ordering, and MQL5 ids are
issued roughly monotonically over time, so the pseudonym sequence would
disclose each provider's registration vintage — a partial re-identification
vector reintroduced by a careless implementation of the fix.

USAGE
  python3 src/pseudonymise.py                      # dry run, reports scope
  python3 src/pseudonymise.py --mode mapped --apply
  python3 src/pseudonymise.py --mode irreversible --apply
  python3 src/pseudonymise.py --verify             # check a completed run

Reads and rewrites in place (only with --apply):
  artifacts/rosters/index_rosters.csv          (4,325 rows)
  artifacts/performance/provider_performance.csv (4,325 rows)
  artifacts/analysis/survival_intervals.csv     (2,090 rows)
  artifacts/status/live_status.csv              (309 rows)
  artifacts/status/control_still_listed.csv     (49 rows)
"""
import argparse
import csv
import hashlib
import hmac
import json
import os
import secrets
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Every committed artifact carrying a raw platform id, with its id column.
TARGETS = [
    (os.path.join("artifacts", "rosters", "index_rosters.csv"), "signal_id"),
    (os.path.join("artifacts", "performance", "provider_performance.csv"), "signal_id"),
    (os.path.join("artifacts", "analysis", "survival_intervals.csv"), "signal_id"),
    (os.path.join("artifacts", "status", "live_status.csv"), "signal_id"),
    (os.path.join("artifacts", "status", "control_still_listed.csv"), "signal_id"),
]

# The mapping lives under the gitignored data/ tree, never under artifacts/.
MAPPING = os.path.join(ROOT, "data", "pseudonym_mapping.csv")

PREFIX = "P"
WIDTH = 5  # P00001 .. P02090 for the 2,090 providers in this corpus


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as fh:
        r = csv.DictReader(fh)
        return r.fieldnames, list(r)


def write_csv(path, fieldnames, rows):
    """Atomic rewrite, matching the discipline used elsewhere in the pipeline."""
    tmp = path + ".tmp"
    with open(tmp, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    os.replace(tmp, path)


def collect_ids():
    """Union of raw ids across all target artifacts, with per-file counts."""
    ids, per_file = set(), []
    for rel, col in TARGETS:
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            sys.exit("missing artifact: %s" % rel)
        fields, rows = read_csv(path)
        if col not in (fields or []):
            sys.exit("artifact %s has no column %s (already pseudonymised?)" % (rel, col))
        here = {r[col] for r in rows if r[col] != ""}
        per_file.append((rel, len(rows), len(here)))
        ids |= here
    return ids, per_file


def build_mapping(ids, salt):
    """id -> pseudonym, assigned in salted-hash order so labels leak no ordering."""
    ordered = sorted(
        ids,
        key=lambda i: hmac.new(salt, str(i).encode(), hashlib.sha256).digest(),
    )
    return {i: "%s%0*d" % (PREFIX, WIDTH, n) for n, i in enumerate(ordered, start=1)}


def apply_mapping(mapping):
    touched = []
    for rel, col in TARGETS:
        path = os.path.join(ROOT, rel)
        fields, rows = read_csv(path)
        n = 0
        for r in rows:
            if r[col] != "":
                r[col] = mapping[r[col]]
                n += 1
        write_csv(path, fields, rows)
        touched.append((rel, n))
    return touched


def verify():
    """Confirm no raw numeric id survives in any target artifact."""
    bad = 0
    for rel, col in TARGETS:
        path = os.path.join(ROOT, rel)
        fields, rows = read_csv(path)
        raw = [r[col] for r in rows if r[col] and not r[col].startswith(PREFIX)]
        status = "OK" if not raw else "RAW IDS PRESENT: %d" % len(raw)
        bad += len(raw)
        print("  %-52s %s" % (rel, status))
    print("\n%s" % ("all target artifacts carry pseudonyms only"
                    if bad == 0 else "%d raw ids remain" % bad))
    return 0 if bad == 0 else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--mode", choices=("mapped", "irreversible"), default="mapped")
    ap.add_argument("--apply", action="store_true",
                    help="actually rewrite the artifacts (default is a dry run)")
    ap.add_argument("--verify", action="store_true",
                    help="check a completed run and exit")
    args = ap.parse_args()

    if args.verify:
        sys.exit(verify())

    ids, per_file = collect_ids()
    print("scope of the change")
    for rel, nrows, nids in per_file:
        print("  %-52s %5d rows, %4d distinct raw ids" % (rel, nrows, nids))
    print("  %-52s %5s        %4d distinct providers overall"
          % ("(union)", "", len(ids)))

    if not args.apply:
        print("\nDRY RUN — nothing written. Re-run with --mode {mapped|irreversible} --apply.")
        print("Read the audit's reproducibility costs before applying; they are not")
        print("recoverable from this repository once the mapping is discarded.")
        return

    if os.path.exists(MAPPING):
        sys.exit("refusing to overwrite an existing mapping at %s" % MAPPING)

    salt = secrets.token_bytes(32)
    mapping = build_mapping(ids, salt)
    touched = apply_mapping(mapping)

    if args.mode == "mapped":
        os.makedirs(os.path.dirname(MAPPING), exist_ok=True)
        with open(MAPPING, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["signal_id", "pseudonym"])
            for i in sorted(mapping, key=lambda x: mapping[x]):
                w.writerow([i, mapping[i]])
        os.chmod(MAPPING, 0o600)
        note = "mapping written to %s (gitignored, mode 0600)" % os.path.relpath(MAPPING, ROOT)
    else:
        note = ("no mapping written; the salt was never persisted and is now gone. "
                "Re-derivation from the archive remains possible for any third party "
                "(see this module's docstring), so this is not anonymisation.")

    del salt
    print("\napplied (%s):" % args.mode)
    for rel, n in touched:
        print("  %-52s %5d ids replaced" % (rel, n))
    print("\n%s" % note)
    print(json.dumps({
        "applied_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "mode": args.mode,
        "n_providers": len(mapping),
        "n_rows_rewritten": sum(n for _, n in touched),
        "files": [rel for rel, _ in touched],
    }, indent=2))
    print("\nNOT DONE BY THIS SCRIPT, and required before committing the result:")
    print("  - update every manuscript and README passage that describes signal ids")
    print("    as retained join keys (manuscript sections 3.3, 7.2; README data notes)")
    print("  - record the change as a numbered amendment under protocol/amendments/")
    print("  - re-run the pipeline's consumers or confirm none read raw ids")


if __name__ == "__main__":
    main()
