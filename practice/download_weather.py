# download_weather.py (practice version of ingestion/download_weather.py, ticket T01)
# Purpose: fetch the MET Malaysia weather endpoints (7-day forecast and warnings) and archive each
#   raw response as gzip. A new file is saved only when the content differs from the last saved
#   copy; the hash and path of that copy are kept in manifest.json. Every endpoint fetched appends
#   one line to its own fetch_log.jsonl.
# Output (Malaysia time), one folder per endpoint (<name> = weather_forecast or weather_warning):
#   practice/output/<name>/date=<YYYY-MM-DD>/fetched_at=<HHMMSS>.json.gz
#   practice/output/<name>/manifest.json
#   practice/output/<name>/fetch_log.jsonl
# Exit code: 0 if every selected endpoint succeeded (changed or unchanged), 1 if any failed.
# Usage:
#   python practice/download_weather.py                          # both endpoints, 20 s apart
#   python practice/download_weather.py --only weather_warning   # one endpoint only

import requests
from datetime import datetime, timezone, timedelta
from pathlib import Path
import gzip
import json
import hashlib
import sys
import time
import argparse

# name -> URL. The name is also the endpoint's output folder and a valid value for --only.
# Adding an endpoint with the same steps (fetch JSON, hash, save if changed, log) is one more line.
ENDPOINTS = {
    "weather_forecast": "https://api.data.gov.my/weather/forecast/",
    "weather_warning": "https://api.data.gov.my/weather/warning/"
}

# Each endpoint writes under OUT_DIR / <name>, with its own files, manifest and log.
OUT_DIR = Path(__file__).resolve().parent / "output"

# Malaysia time (UTC+8). Set explicitly because the collector VM's clock runs in UTC.
MYT = timezone(timedelta(hours=8))

# Fetch one endpoint once.
# Returns the response, the parsed records, the log line started for this run, and the fetch time.
def fetch(url:str, MYT:timezone):
    response = None
    records = None

    # All six log fields exist from the start (None is written as null), in the order of the
    # ticket's table, so every log line has the same keys in the same order.
    KEYS = ["fetched_at_myt", "status", "sha256", "records", "file", "error"]
    log_data = dict.fromkeys(KEYS)

    try:
        # Timeout = seconds of silence from the server before giving up (not the total download
        # time).
        # - Not set: if the server never answers, the script hangs forever, nothing is logged, the
        #   code below never runs, and the next scheduled run cannot start.
        # - Too small: a slow but working server is treated as a failure, and that forecast
        #   version is lost for good.
        # - Too big: only a longer wait when the server is really down; nobody waits on this
        #   background job, so 60 s is safe as long as it stays far below the run interval (3 h).
        response = requests.get(url, timeout=60)
        response.raise_for_status()     # turn an HTTP error (4xx/5xx) into an exception
        records = response.json()       # parse once; also checks that the body is valid JSON
                                        # a list of records, one per location per date
        log_data["records"] = len(records)

    # Only requests' own exceptions are caught. RequestException is the parent of all of them:
    # ConnectionError, Timeout, HTTPError (from raise_for_status) and JSONDecodeError (from
    # .json(), e.g. an HTML page sent with status 200). Anything else is a bug in this script and
    # should crash with a traceback, not be logged as if the server had failed.
    # The error keeps the exception type ("HTTPError: 404 ...") so failures can be grouped by cause.
    except requests.RequestException as e:
        error_msg = f"{type(e).__name__}: {e}"
        print(f"FAILED:\n{error_msg}")
        log_data["error"] = error_msg
        log_data["status"] = "failed"
    finally:
        # Fetch time: taken once the request has finished. finally runs after try whether it
        # succeeded or failed, so the time exists on both paths and is set in one place only.
        # On success it is the moment this version of the forecast was actually received.
        # It names the date= folder and the fetched_at= file.
        fetched_at = datetime.now(MYT)
        log_data["fetched_at_myt"] = fetched_at.isoformat(timespec="seconds")

    return response, records, log_data, fetched_at


# Hash the content (not the raw bytes) to detect an unchanged forecast.
def compute_content_hash (records):
    # Two responses with the same content can still differ byte for byte (spacing, key order, how
    # non-ASCII characters are escaped). Parsing drops the spacing and escaping; dumping again with
    # fixed options gives one canonical string for the same content:
    # - sort_keys=True: keys in a JSON object have no meaning in their order, so put them in one
    #   fixed order. Lists keep their order, because in a list the order is part of the content.
    # - ensure_ascii=False: keep non-ASCII characters as they are instead of \uXXXX escapes. Either
    #   setting gives a stable hash; it only has to stay the same between runs, otherwise every
    #   hash changes once and one duplicate is saved.
    # hexdigest() returns the hash as a 64-character hex string, which JSON can store and which can
    # be compared as text (digest() returns raw bytes, which JSON cannot hold).
    canonical_bytes = json.dumps(records, sort_keys=True, ensure_ascii=False).encode()
    content_hash = hashlib.sha256(canonical_bytes).hexdigest()
    return content_hash


# Save the raw response and update the manifest, but only if the content has changed since the
# last saved copy. Fills in status, sha256 and file in the log line.
def save_if_changed(response, out_dir, content_hash, manifest_path, fetched_at, log_data):
    # The manifest remembers only the last saved copy: {"sha256": ..., "file": ...}.
    # Comparing with the last copy (not with every older one) keeps the archive a time series of
    # versions: if the forecast goes A -> B -> A, the second A is saved, because at that moment the
    # forecast really did change back to A.
    # On the first run there is no manifest, so use {}; .get() then returns None, which never
    # equals a hash, so the content counts as changed and is saved without a separate first-run
    # branch. Deleting the manifest makes the script forget the last copy, so the next run saves a
    # duplicate.
    # That is the safe direction: a duplicate can be removed later by its hash, a missed version
    # can never be recovered.
    last_saved = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}

    if last_saved.get("sha256") == content_hash:
        print("unchanged")
        log_data["status"] = "unchanged"
        log_data["sha256"] = content_hash

    else:
        # Folder named "date=<value>" (Hive-style partitioning): Spark turns it into a "date"
        # column and can skip other days' folders when a query filters on date. The records carry
        # no publication time, so this folder (and the file name) is the only place the fetch time
        # is kept. The file name "fetched_at=..." is NOT a partition (only folders are); it is read
        # from the path.
        # The double extension ".json.gz" names both layers: gzip on the outside, JSON on the
        # inside. gzip-aware tools strip only the last one (gunzip gives "....json", Spark and
        # pandas pick the codec from ".gz" and still see JSON), so nobody has to open the file to
        # know what it holds.
        partition_dir = out_dir / f"date={fetched_at:%Y-%m-%d}"
        partition_dir.mkdir(parents=True, exist_ok=True)
        gz_path = partition_dir / f"fetched_at={fetched_at:%H%M%S}.json.gz"

        # Atomic write: write everything to "<name>.tmp" first, then rename it to the real name.
        # Writing straight to gz_path gives the file its real name as soon as writing starts. A
        # crash halfway (power cut, VM restart, killed process) would leave a truncated .gz that
        # looks like a normal file: gzip readers fail on it ("unexpected end of file"), and nothing
        # ever repairs it, because the manifest was not updated and the next run saves a new file
        # under a new name. With the .tmp step a half-written file keeps the ".tmp" ending, so
        # anything that looks for "*.json.gz" never sees it.
        # with_name(name + ".tmp") keeps the full target name in front ("....json.gz.tmp");
        # with_suffix(".tmp") would replace ".gz" and give "....json.tmp".
        # The .tmp file is in the same folder on purpose: a rename is a single step only within one
        # filesystem (across filesystems it fails).
        tmp = gz_path.with_name(gz_path.name + ".tmp")

        # Save the raw response as gzip
        # - Raw, not parsed: Bronze keeps exactly what the server sent, so it can be parsed again if
        #   the parsing logic changes later. Turning it into a table (e.g. Parquet) is Silver's job.
        # - Compressed: the JSON repeats the same keys in every record, so it shrinks about 47x
        #   (about 910 KB -> 19 KB on 2026-10-28). At up to 8 saves a day that is about 55 MB a year
        #   instead of about 2.6 GB.
        # - gzip, not bz2/xz/zstd: it is in the standard library, and every tool in this project
        #   reads it without extra setup (zcat, pandas, Spark, DuckDB). bz2 is smaller here (about
        #   12 KB) but slower to read; at 19 KB per file the difference does not matter.
        raw = response.content  # the raw bytes from the server, stored as-is (not the parsed data)
        # mtime=0: gzip writes a timestamp into bytes 5-8 of its header, by default the time of
        # compression, so the same response compressed twice gives different bytes. With 0 there,
        # the same input always gives the same file, and two copies can be compared with a plain
        # file hash (sha256sum) without decompressing them or knowing the JSON format. The fetch
        # time is not lost: it is in the folder and file name.
        compressed = gzip.compress(raw, mtime=0)

        tmp.write_bytes(compressed)
        # Path.replace renames in one step (and would overwrite gz_path if it existed), so a reader
        # sees either no file or the complete file, never a partial one.
        tmp.replace(gz_path)

        print(f'saved {gz_path} ({len(compressed)/1024:.0f} KB)')

        # Update the manifest only after the .gz file is written. In the opposite order, a crash
        # between the two steps would leave a manifest that points at a file that does not exist;
        # the next run would find the same hash and print "unchanged", so that version would never
        # be saved.
        # The path is stored relative to the endpoint's own folder (out_dir), with no home
        # directory and no endpoint name in it, so out_dir / file always finds the file, also when
        # the output folder lives somewhere else, e.g. on the VM. It must be out_dir, not the
        # global OUT_DIR: that one is the parent of all endpoints and would add "<name>/" in front.
        gz_relative_path = gz_path.relative_to(out_dir)

        new_manifest = {
            "sha256": content_hash,
            "file": str(gz_relative_path)
        }

        log_data["sha256"] = content_hash
        log_data["file"] = str(gz_relative_path)

        # The manifest is overwritten on purpose: it answers "which copy is the latest?", so only
        # one entry is needed. The history of every run is in fetch_log.jsonl instead.
        manifest_path.write_text(json.dumps(new_manifest, indent=2))
        print("changed")
        log_data["status"] = "changed"

    return log_data


# Append this run's log line to fetch_log.jsonl (JSON Lines: one JSON object per line).
# Adding a run only writes one new line at the end ("a" mode); earlier lines are never touched.
# A JSON array would have to be read, extended and rewritten in full on every run, and a crash
# during that rewrite could leave the whole file unreadable. Here a crash can damage at most the
# last line, and every other line still parses on its own.
def append_log(log_data:dict, log_path:Path):
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_data) + "\n")    # no indent: one record must stay on one line


# All the steps for one endpoint: fetch -> hash -> save if changed -> log. Returns its exit code
# (0 = changed or unchanged, 1 = failed).
# Every endpoint goes through the same steps and only the name and URL differ, so the steps live
# in one function instead of one copy per endpoint. With copies, a later fix (e.g. step 7's atomic
# write) would have to be made in every copy, and a copy that is missed still runs without any
# error, just with the old behaviour.
def ingest_endpoint(name:str, url:str):
    out_dir = OUT_DIR / name
    # Created here, not only when a file is saved: a failed first fetch still needs the folder
    # for its log line.
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = out_dir / "manifest.json"
    log_path = out_dir / "fetch_log.jsonl"

    response, records, log_data, fetched_at = fetch(url, MYT)

    # A failed fetch must stop here, before hashing. records is None, so the hash would be the
    # hash of "null": the first failure would save the error page (an HTML 404 page) as a
    # forecast and point the manifest at it, and every later failure would match that hash and be
    # logged as "unchanged", so an outage would look like a forecast that simply did not change.
    # The failed line is still logged: without it "no new file" cannot be told apart from
    # "unchanged", and availability (successful runs / all runs) would always look like 100%.
    if log_data["status"] == "failed":
        append_log(log_data, log_path)
        return 1

    content_hash = compute_content_hash(records)

    log_data = save_if_changed(response, out_dir, content_hash, manifest_path, fetched_at, log_data)

    append_log(log_data, log_path)

    return 0


def main():
    # --only exists because the VM runs the endpoints on separate timers: the forecast every 3 h
    # and the warnings every hour, each calling this script with --only <name>. Without it, the
    # hourly warning run would also fetch the forecast every hour.
    # choices: argparse itself rejects any other name (error message, exit code 2).
    parser = argparse.ArgumentParser(description="Ingest weather feeds into the Bronze layer.")
    parser.add_argument(
        "--only",
        choices=list(ENDPOINTS),
        help="process only this feed (default: all feeds)"
    )
    args = parser.parse_args()

    if args.only:
        selected = {args.only: ENDPOINTS[args.only]}
    else:
        selected = ENDPOINTS

    # Both endpoints share the Weather API limit of 4 requests per minute. The limit is a ceiling,
    # not a target: one request per endpoint per run is all that is needed. 20 s between requests
    # means at most 3 a minute, which leaves room for timing jitter and for other runs (e.g. the
    # VM's timers) using the same limit; 15 s would sit exactly on the limit.
    # The sleep is only between requests (i > 0): none before the first or after the last.
    # A failed endpoint does not stop the loop: the other endpoint is still fetched and logged.
    exit_codes = []
    for i, (name, url) in enumerate(selected.items()):
        if i > 0:
            time.sleep(20)
        exit_codes.append(ingest_endpoint(name, url))

    return 1 if any(exit_codes) else 0     # 1 if at least one endpoint returned 1


# Run main() only when this file is run directly (python practice/download_weather.py).
# main() returns 0 (every endpoint succeeded) or 1 (at least one failed); sys.exit() hands that
# number to the operating system as the exit code. A plain main() call would drop it and always
# exit with 0. The VM's systemd timer (and Airflow later) reads the exit code, not the printed text,
# to decide whether a run failed.
if __name__ == "__main__":
    sys.exit(main())
