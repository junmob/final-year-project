# download_weather.py (practice version of ingestion/download_weather.py, ticket T01)
# Purpose: fetch the MET Malaysia 7-day weather forecast and archive the raw response as gzip.
#   A new file is saved only when the content differs from the last saved copy; the hash and
#   path of that copy are kept in manifest.json. Every run appends one line to fetch_log.jsonl.
# Output (Malaysia time):
#   practice/output/weather_forecast/date=<YYYY-MM-DD>/fetched_at=<HHMMSS>.json.gz
#   practice/output/weather_forecast/manifest.json
#   practice/output/weather_forecast/fetch_log.jsonl
# Usage: python practice/download_weather.py

import requests
from datetime import datetime, timezone, timedelta
from pathlib import Path
import gzip
import json
import hashlib

# Malaysia time (UTC+8). Set explicitly because the collector VM's clock runs in UTC.
MYT = timezone(timedelta(hours=8))

OUT_DIR = Path(__file__).resolve().parent / "output" / "weather_forecast"


# Fetch the forecast once.
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
        log_data["error"] = None

    except requests.RequestException as e:
        log_data["error"] = str(e)
        log_data["sha256"] = None
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
def save_if_changed(response, OUT_DIR, content_hash, manifest_path, fetched_at, log_data):
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
        log_data["file"] = None

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
        out_dir = OUT_DIR / f"date={fetched_at:%Y-%m-%d}"
        out_dir.mkdir(parents=True, exist_ok=True)
        gz_path = out_dir / f"fetched_at={fetched_at:%H%M%S}.json.gz"

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
        compressed = gzip.compress(raw)

        gz_path.write_bytes(compressed)
        print(f'saved {gz_path} ({len(compressed)/1024:.0f} KB)')

        # Update the manifest only after the .gz file is written. In the opposite order, a crash
        # between the two steps would leave a manifest that points at a file that does not exist;
        # the next run would find the same hash and print "unchanged", so that version would never
        # be saved.
        # The path is stored relative to weather_forecast/ (no home directory in it), so the
        # manifest stays valid when the output folder lives somewhere else, e.g. on the VM.
        gz_relative_path = gz_path.relative_to(OUT_DIR)

        new_manifest = {
            "sha256": content_hash,
            "file": str(gz_relative_path)
        }

        log_data["sha256"] = content_hash
        log_data["file"] = str(gz_relative_path)

        # The manifest is overwritten on purpose: it answers "which copy is the latest?", so only
        # one entry is needed. The history of every run is in fetch_log.jsonl instead.
        manifest_path.write_text(json.dumps(new_manifest, indent=2))
        print("updated")
        log_data["status"] = "changed"

    return log_data


# Append this run's log line to fetch_log.jsonl (JSON Lines: one JSON object per line).
# Adding a run only writes one new line at the end ("a" mode); earlier lines are never touched.
# A JSON array would have to be read, extended and rewritten in full on every run, and a crash
# during that rewrite could leave the whole file unreadable. Here a crash can damage at most the
# last line, and every other line still parses on its own.
def append_jsonl(log_data:dict, log_path:Path):
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_data) + "\n")    # no indent: one record must stay on one line


def main():
    # Settings and paths
    url = 'https://api.data.gov.my/weather/forecast/'

    manifest_path = OUT_DIR / "manifest.json"
    log_path = OUT_DIR / "fetch_log.jsonl"

    # One run: fetch -> hash -> save if changed -> log
    response, records, log_data, fetched_at = fetch(url, MYT)

    content_hash = compute_content_hash(records)

    log_data = save_if_changed(response, OUT_DIR, content_hash, manifest_path, fetched_at, log_data)

    append_jsonl(log_data, log_path)


# Run main() only when this file is run directly (python practice/download_weather.py).
if __name__ == "__main__":
    main()
