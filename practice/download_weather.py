# download_weather.py (practice version of ingestion/download_weather.py, ticket T01)
# Purpose: fetch the MET Malaysia 7-day weather forecast and archive the raw response as gzip.
# Output (Malaysia time):
#   practice/output/weather_forecast/date=<YYYY-MM-DD>/fetched_at=<HHMMSS>.json.gz
# Usage: python practice/download_weather.py
import requests
from datetime import datetime, timezone, timedelta
from pathlib import Path
import gzip
import json

# Malaysia time (UTC+8). Set explicitly because the collector VM's clock runs in UTC.
MYT = timezone(timedelta(hours=8))

# ==========================================================
# Step 1: fetch the forecast

# Timeout = seconds of silence from the server before giving up (not the total download time).
# - Not set: if the server never answers, the script hangs forever, nothing is logged, the code
#   below never runs, and the next scheduled run cannot start.
# - Too small: a slow but working server is treated as a failure, and that forecast version is
#   lost for good.
# - Too big: only a longer wait when the server is really down; nobody waits on this background
#   job, so 60 s is safe as long as it stays far below the run interval (3 h).

res = requests.get('https://api.data.gov.my/weather/forecast/', timeout=60)
res.raise_for_status()  # turn an HTTP error (4xx/5xx) into an exception

data = res.json()  # parse once; also checks that the body is valid JSON

# ==========================================================
# Step 2: save the raw response as gzip

now = datetime.now(MYT)

# Folder named "date=<value>" (Hive-style partitioning): Spark turns it into a "date" column and
# can skip other days' folders when a query filters on date. The records carry no publication
# time, so this folder (and the file name) is the only place the fetch time is kept.
# The file name "fetched_at=..." is NOT a partition (only folders are); it is read from the path.
OUT_DIR = Path(__file__).resolve().parent / "output"
out_dir = OUT_DIR / "weather_forecast" / f"date={now:%Y-%m-%d}"
out_dir.mkdir(parents=True, exist_ok=True)

raw = res.content  # the raw bytes from the server, stored as-is (not the parsed data)
compressed = gzip.compress(raw)

file_path = out_dir / f"fetched_at={now:%H%M%S}.json.gz"
file_path.write_bytes(compressed)

print(f'saved {file_path} ({len(compressed)/1024:.0f} KB)')

# ==========================================================

