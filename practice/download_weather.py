# download_weather.py (practice version of ingestion/download_weather.py, ticket T01)
# Purpose: fetch the MET Malaysia 7-day weather forecast and archive the raw response as gzip.
#   A new file is saved only when the content differs from the last saved copy; the hash and
#   path of that copy are kept in manifest.json.
# Output (Malaysia time):
#   practice/output/weather_forecast/date=<YYYY-MM-DD>/fetched_at=<HHMMSS>.json.gz
#   practice/output/weather_forecast/manifest.json
# Usage: python practice/download_weather.py

import requests
from datetime import datetime, timezone, timedelta
from pathlib import Path
import gzip
import json
import hashlib

# Malaysia time (UTC+8). Set explicitly because the collector VM's clock runs in UTC.
MYT = timezone(timedelta(hours=8))

# ==========================================================
# Fetch the forecast

# Timeout = seconds of silence from the server before giving up (not the total download time).
# - Not set: if the server never answers, the script hangs forever, nothing is logged, the code
#   below never runs, and the next scheduled run cannot start.
# - Too small: a slow but working server is treated as a failure, and that forecast version is
#   lost for good.
# - Too big: only a longer wait when the server is really down; nobody waits on this background
#   job, so 60 s is safe as long as it stays far below the run interval (3 h).
response = requests.get('https://api.data.gov.my/weather/forecast/', timeout=60)
response.raise_for_status()     # turn an HTTP error (4xx/5xx) into an exception
records = response.json()       # parse once; also checks that the body is valid JSON
                                # a list of records, one per location per date

# Fetch time: taken after the response has arrived, so it is the moment this version of the
# forecast was actually received. It names the date= folder and the fetched_at= file.
fetched_at = datetime.now(MYT)

# ==========================================================
# Hash the content (not the raw bytes) to detect an unchanged forecast

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

OUT_DIR = Path(__file__).resolve().parent / "output" / "weather_forecast"

# The manifest remembers the last saved copy: {"sha256": ..., "file": ...}.
# On the first run there is no manifest, so use {}; .get() then returns None, which never equals
# a hash, so the content counts as changed and is saved without a separate first-run branch.
# Deleting the manifest makes the script forget the last copy, so the next run saves a duplicate.
# That is the safe direction: a duplicate can be removed later by its hash, a missed version
# can never be recovered.
manifest_path = OUT_DIR / "manifest.json"
last_saved = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}

if last_saved.get("sha256") == content_hash:
    print("unchanged")
else:
    # Folder named "date=<value>" (Hive-style partitioning): Spark turns it into a "date" column and
    # can skip other days' folders when a query filters on date. The records carry no publication
    # time, so this folder (and the file name) is the only place the fetch time is kept.
    # The file name "fetched_at=..." is NOT a partition (only folders are); it is read from the path.
    out_dir = OUT_DIR / f"date={fetched_at:%Y-%m-%d}"
    out_dir.mkdir(parents=True, exist_ok=True)
    gz_path = out_dir / f"fetched_at={fetched_at:%H%M%S}.json.gz"

    # Save the raw response as gzip
    raw = response.content  # the raw bytes from the server, stored as-is (not the parsed data)
    compressed = gzip.compress(raw)

    gz_path.write_bytes(compressed)
    print(f'saved {gz_path} ({len(compressed)/1024:.0f} KB)')

    # Update the manifest only after the .gz file is written. In the opposite order, a crash
    # between the two steps would leave a manifest that points at a file that does not exist; the
    # next run would find the same hash and print "unchanged", so that version would never be saved.
    # The path is stored relative to weather_forecast/ (no home directory in it), so the manifest
    # stays valid when the output folder lives somewhere else, for example on the collector VM.
    gz_relative_path = gz_path.relative_to(OUT_DIR)

    new_manifest = {
        "sha256": content_hash,
        "file": str(gz_relative_path)
    }

    manifest_path.write_text(json.dumps(new_manifest, indent=2))
    print("updated")
