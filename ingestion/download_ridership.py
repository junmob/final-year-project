# download_ridership.py
# Purpose: archive the Rapid Rail (Klang Valley) daily origin-destination ridership file
#          (data-source summary §6.4). The file holds the whole year and is overwritten in place
#          (new days appended, older days sometimes revised; the 2025 file was still updated in
#          April 2026), so every distinct version is kept to preserve the revision history.
#   - A cheap HEAD request compares the ETag with the last stored version; the file (about 5 MB)
#     is downloaded only when the ETag changes, and stored only when its sha256 is new.
#   - Both the current and the previous year's file are checked, because older files are still
#     revised and the current-year file only appears after 1 January.
#   - These files are on storage.data.gov.my (file storage), not the rate-limited OpenAPI.
#
# Layout (Malaysia time; <BRONZE_DIR> defaults to data/raw):
#   <BRONZE_DIR>/ridership_rapidrail/year=<YYYY>/downloaded=<YYYY-MM-DD>/fetched_at=<HHMMSS>.parquet
#   <BRONZE_DIR>/ridership_rapidrail/year=<YYYY>/versions.jsonl   one line per check
import hashlib
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = Path(os.environ.get("BRONZE_DIR", ROOT / "data" / "raw")) / "ridership_rapidrail"
URL = "https://storage.data.gov.my/transportation/rail/rapidrail_{year}_daily.parquet"
MYT = timezone(timedelta(hours=8))


def last_ok(versions_path: Path) -> dict:
    last = {}
    if versions_path.exists():
        for line in versions_path.read_text(encoding="utf-8").splitlines():
            if line.strip() and (record := json.loads(line)).get("status") in ("changed", "same_content"):
                last = record
    return last


def check_year(year: int) -> bool:
    now = datetime.now(MYT)
    year_dir = OUT_DIR / f"year={year}"
    versions_path = year_dir / "versions.jsonl"
    previous = last_ok(versions_path)
    entry = {"checked_at_myt": now.isoformat(timespec="seconds"), "status": None, "etag": None,
             "last_modified": None, "bytes": None, "sha256": None, "file": None, "error": None}

    def log(**fields) -> None:
        entry.update(fields)
        year_dir.mkdir(parents=True, exist_ok=True)
        with open(versions_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    url = URL.format(year=year)
    try:
        head = requests.head(url, timeout=30)
        if head.status_code == 404:
            print(f"[absent] {year}: no file published yet", flush=True)
            return True  # expected for the new year in early January; not logged
        head.raise_for_status()
        etag, modified = head.headers.get("ETag"), head.headers.get("Last-Modified")
        if previous and etag and etag == previous.get("etag"):
            print(f"[unchanged] {year}: ETag {etag}", flush=True)
            return True  # unchanged checks are not logged, to keep versions.jsonl small

        resp = requests.get(url, timeout=120)
        resp.raise_for_status()
        body = resp.content
        if not body.startswith(b"PAR1") or not body.endswith(b"PAR1"):
            raise ValueError("response is not a complete Parquet file")
    except (requests.RequestException, ValueError) as e:
        log(status="failed", error=f"{type(e).__name__}: {e}")
        print(f"[failed] {year}: {e}", flush=True)
        return False

    digest = hashlib.sha256(body).hexdigest()
    etag, modified = resp.headers.get("ETag", etag), resp.headers.get("Last-Modified", modified)
    if digest == previous.get("sha256"):
        log(status="same_content", etag=etag, last_modified=modified, bytes=len(body), sha256=digest)
        print(f"[same content] {year}: new ETag but identical bytes", flush=True)
        return True

    path = year_dir / f"downloaded={now:%Y-%m-%d}" / f"fetched_at={now:%H%M%S}.parquet"
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_bytes(body)
    tmp.replace(path)
    rel = str(path.relative_to(OUT_DIR))
    log(status="changed", etag=etag, last_modified=modified, bytes=len(body), sha256=digest, file=rel)
    print(f"[changed] {year}: saved {rel} ({len(body) / 1e6:.1f} MB, Last-Modified {modified})", flush=True)
    return True


def main() -> int:
    year = datetime.now(MYT).year
    ok = True
    for y in (year - 1, year):
        ok = check_year(y) and ok
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
