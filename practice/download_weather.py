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
import hashlib

MYT = timezone(timedelta(hours=8))
now = datetime.now(MYT)

res = requests.get('https://api.data.gov.my/weather/forecast/', timeout=60)
res.raise_for_status()  # turn an HTTP error (4xx/5xx) into an exception

data = res.json()  # parse once; also checks that the body is valid JSON
data_bytes = json.dumps(data, sort_keys=True, ensure_ascii=False).encode()
data_hash = hashlib.sha256(data_bytes).hexdigest()

OUT_DIR = Path(__file__).resolve().parent / "output" / "weather_forecast"
manifest_file = OUT_DIR / "manifest.json"

info = json.loads(manifest_file.read_text()) if manifest_file.exists() else {}

if info.get("sha256") == data_hash:
    print("unchanged")
else:
    raw = res.content  # the raw bytes from the server, stored as-is (not the parsed data)
    compressed = gzip.compress(raw)

    out_dir = OUT_DIR / f"date={now:%Y-%m-%d}"
    out_dir.mkdir(parents=True, exist_ok=True)
    full_file_path = out_dir / f"fetched_at={now:%H%M%S}.json.gz"

    full_file_path.write_bytes(compressed)
    print(f'saved {full_file_path} ({len(compressed)/1024:.0f} KB)')

    relative_file_path = full_file_path.relative_to(OUT_DIR)

    manifest_file.write_text(json.dumps({"sha256": data_hash, "file": str(relative_file_path)}, indent=2))
    print("updated")



