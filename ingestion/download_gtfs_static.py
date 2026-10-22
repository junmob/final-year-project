# download_gtfs_static.py
# Purpose: daily check of the 3 core GTFS Static feeds with per-file, content-addressed
#          deduplication (design doc v0.4 §8.3.3; data-source summary §3.7).
#
# Why per-file instead of per-ZIP:
#   - rapid-bus-mrtfeeder re-exports calendar.txt every day with a rolling start_date,
#     so the ZIP changes daily even when the timetable does not ("pseudo versions").
#   - rapid-rail-kl ZIPs contain macOS packaging artefacts (__MACOSX/) that change on
#     every repack.
#   - Storing a full ZIP per change would add hundreds of MB per year to the repository.
#
# Layout (per category; <BRONZE_DIR> defaults to data/raw for the GitHub Actions backup and is
# set to the Bronze directory on the collector VM):
#   <BRONZE_DIR>/gtfs_static/<category>/blobs/<sha256[:2]>/<sha256>.gz   file contents, stored once
#   <BRONZE_DIR>/gtfs_static/<category>/snapshots.jsonl                  one line per daily check
# Each snapshot records the hash of every file in the ZIP, so the exact contents of any
# day's feed can be reconstructed. The ZIP container itself (timestamps, compression) is
# not kept byte-for-byte; only file contents are.
import gzip
import hashlib
import io
import json
import os
import sys
import time
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = Path(os.environ.get("BRONZE_DIR", ROOT / "data" / "raw")) / "gtfs_static"
URL = "https://api.data.gov.my/gtfs-static/prasarana/?category="  # trailing slash avoids a 301
CATEGORIES = ["rapid-bus-kl", "rapid-bus-mrtfeeder", "rapid-rail-kl"]
REQUEST_GAP_SECONDS = 20  # data-source summary §7.1: at least 20 s between requests
RETRIES, RETRY_WAIT_SECONDS = 3, 60  # Static has its own rate-limit quota, so retrying is safe
JUNK_PREFIXES = ("__MACOSX/",)
MYT = timezone(timedelta(hours=8))


def is_junk(name: str) -> bool:
    base = name.rsplit("/", 1)[-1]
    return name.startswith(JUNK_PREFIXES) or base.startswith("._") or base == ".DS_Store"


def store_blob(category_dir: Path, data: bytes) -> str:
    digest = hashlib.sha256(data).hexdigest()
    path = category_dir / "blobs" / digest[:2] / f"{digest}.gz"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".gz.tmp")
        tmp.write_bytes(gzip.compress(data, mtime=0))
        tmp.replace(path)
    return digest


def last_snapshot(snapshots_path: Path) -> dict | None:
    if not snapshots_path.exists():
        return None
    last = None
    with open(snapshots_path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                record = json.loads(line)
                if record.get("status") == "ok":
                    last = record
    return last


def ingest_zip(category: str, zip_bytes: bytes, checked_at: datetime, source: str) -> dict:
    category_dir = OUT_DIR / category
    snapshots_path = category_dir / "snapshots.jsonl"
    previous = last_snapshot(snapshots_path)

    files, junk = {}, {}
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
        for name in sorted(n for n in z.namelist() if not n.endswith("/")):
            digest = store_blob(category_dir, z.read(name))
            (junk if is_junk(name) else files)[name] = digest

    prev_files = previous["files"] if previous else {}
    changed = sorted(n for n in set(files) | set(prev_files) if files.get(n) != prev_files.get(n))
    record = {
        "checked_at_myt": checked_at.isoformat(timespec="seconds"),
        "source": source,
        "status": "ok",
        "zip_sha256": hashlib.sha256(zip_bytes).hexdigest(),
        "zip_bytes": len(zip_bytes),
        "files": files,
        "junk_files": junk,
        "changed_files": changed if previous else sorted(files),
        "is_first_snapshot": previous is None,
    }
    category_dir.mkdir(parents=True, exist_ok=True)
    with open(snapshots_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record


def get_with_retry(url: str) -> requests.Response:
    for attempt in range(1, RETRIES + 1):
        try:
            resp = requests.get(url, timeout=60)
            resp.raise_for_status()
            zipfile.ZipFile(io.BytesIO(resp.content)).testzip()  # reject truncated downloads
            return resp
        except (requests.RequestException, zipfile.BadZipFile) as e:
            if attempt == RETRIES:
                raise
            print(f"[retry] {url}: {e}; waiting {RETRY_WAIT_SECONDS} s", flush=True)
            time.sleep(RETRY_WAIT_SECONDS)
    raise AssertionError("unreachable")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    failed = False

    for i, category in enumerate(CATEGORIES):
        if i:
            time.sleep(REQUEST_GAP_SECONDS)
        checked_at = datetime.now(MYT)
        try:
            resp = get_with_retry(URL + category)
            record = ingest_zip(category, resp.content, checked_at, source="api")
        except (requests.RequestException, zipfile.BadZipFile) as e:
            print(f"[failed] {category}: {e}")
            failed = True
            snapshots_path = OUT_DIR / category / "snapshots.jsonl"
            snapshots_path.parent.mkdir(parents=True, exist_ok=True)
            with open(snapshots_path, "a", encoding="utf-8") as f:
                f.write(json.dumps({"checked_at_myt": checked_at.isoformat(timespec="seconds"),
                                    "source": "api", "status": "failed", "error": str(e)}) + "\n")
            continue

        if record["changed_files"]:
            print(f"[changed] {category}: {record['changed_files']}")
        else:
            print(f"[unchanged] {category}: no data file changed")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
