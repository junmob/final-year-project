# download_weather.py
# Purpose: archive the MET Malaysia weather forecast and weather warnings (design doc v0.4
#          §8.3.3; data-source summary §6.1, §6.2, §7.1). A response is stored only when its
#          content differs from the last stored one.
#   - The forecast endpoint returns the whole country's 7-day forecast in one response
#     (3080 rows, about 0.9 MB on 2026-10-20), so no paging is needed.
#   - There is no history API: a forecast revision that is not fetched is lost for good.
#   - Records carry no publication time, so the fetch time stands in for it (E35).
#
# Layout (Malaysia time; <BRONZE_DIR> defaults to data/raw for the GitHub Actions archive):
#   <BRONZE_DIR>/<name>/date=<YYYY-MM-DD>/fetched_at=<HHMMSS>.json.gz   stored responses
#   <BRONZE_DIR>/<name>/manifest.json                                   hash of the last stored response
#   <BRONZE_DIR>/<name>/fetch_log.jsonl                                 one line per attempt
# Usage: python download_weather.py [--only weather_forecast|weather_warning]
import argparse
import gzip
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = Path(os.environ.get("BRONZE_DIR", ROOT / "data" / "raw"))
# The trailing slash matters: without it the API answers 301.
ENDPOINTS = {
    "weather_forecast": "https://api.data.gov.my/weather/forecast/",
    "weather_warning": "https://api.data.gov.my/weather/warning/",
}
REQUEST_GAP_SECONDS = 20  # data-source summary §6.1.4: at least 20 s between requests
MYT = timezone(timedelta(hours=8))


def append_log(name: str, entry: dict) -> None:
    path = OUT_DIR / name / "fetch_log.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def fetch(name: str, url: str) -> bool:
    now = datetime.now(MYT)
    entry = {"fetched_at_myt": now.isoformat(timespec="seconds"), "status": None,
             "sha256": None, "records": None, "file": None, "error": None}
    try:
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        data = resp.json()  # make sure the body is valid JSON
    except (requests.RequestException, ValueError) as e:
        entry.update(status="failed", error=f"{type(e).__name__}: {e}")
        append_log(name, entry)
        print(f"[failed] {name}: {e}", flush=True)
        return False

    # Hash the canonical JSON so that whitespace or key order alone does not count as new content.
    canonical = json.dumps(data, ensure_ascii=False, sort_keys=True).encode()
    digest = hashlib.sha256(canonical).hexdigest()
    entry.update(sha256=digest, records=len(data) if isinstance(data, list) else None)
    manifest_path = OUT_DIR / name / "manifest.json"
    previous = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    if digest == previous.get("sha256"):
        entry["status"] = "unchanged"
        append_log(name, entry)
        print(f"[unchanged] {name}: same content as {previous['file']}", flush=True)
        return True

    out_dir = OUT_DIR / name / f"date={now:%Y-%m-%d}"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"fetched_at={now:%H%M%S}.json.gz"
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_bytes(gzip.compress(resp.content, mtime=0))  # raw body; mtime=0 keeps bytes stable
    tmp.replace(path)
    rel = str(path.relative_to(OUT_DIR / name))
    manifest_path.write_text(json.dumps({"sha256": digest, "file": rel, "records": entry["records"]},
                                        indent=2, ensure_ascii=False))
    entry.update(status="changed", file=rel)
    append_log(name, entry)
    print(f"[changed] {name}: saved {rel} ({len(resp.content) / 1024:.0f} KB raw)", flush=True)
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Archive weather forecast and warnings.")
    parser.add_argument("--only", choices=sorted(ENDPOINTS), help="fetch a single endpoint")
    args = parser.parse_args()
    names = [args.only] if args.only else list(ENDPOINTS)

    ok = True
    for i, name in enumerate(names):
        if i:
            time.sleep(REQUEST_GAP_SECONDS)
        ok = fetch(name, ENDPOINTS[name]) and ok
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
