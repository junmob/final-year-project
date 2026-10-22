# bronze_sync.py
# Purpose: pull the Bronze archive from the collector VM to the local machine and verify it
#          (design doc v0.4 §8.3.2, §8.3.4 tier B). Run on the local machine whenever it is on;
#          later it becomes the first task of the Airflow pipeline.
#
# Pull-based: the local machine connects to the VM over SSH (the VM never connects back,
# because the local machine is behind NAT and often switched off).
#
# Steps:
#   1. rsync everything except today's loose RT files (those are not packed yet) and *.tmp.
#      Nothing is ever deleted locally, and nothing is deleted on the VM.
#   2. Verify what arrived:
#      - RT packs: pack sha256 against its manifest, then every member against the file list;
#        packs that passed once are remembered and not re-read on later runs.
#      - GTFS Static: every blob decompresses to content whose sha256 equals its file name, and
#        every blob referenced by snapshots.jsonl exists.
#      - Weather: every stored response listed in fetch_log.jsonl exists and hashes as logged.
#      - Ridership: every stored version listed in versions.jsonl exists and hashes as logged.
#   3. Append one summary line to <LOCAL_DATA_DIR>/_sync/sync_log.jsonl.
# The local copy keeps the VM's layout, so later jobs (MinIO upload, Spark) see the same paths.
#
# Usage: python ingestion/bronze_sync.py [--verify-only]
import argparse
import gzip
import hashlib
import json
import os
import subprocess
import sys
import tarfile
from datetime import datetime, timezone
from pathlib import Path

import zstandard

REMOTE = os.environ.get("BRONZE_REMOTE", "fyp-collector:fyp-data/bronze/")
LOCAL_DATA_DIR = Path(os.environ.get("LOCAL_DATA_DIR", Path.home() / "fyp-data"))
LOCAL_BRONZE = LOCAL_DATA_DIR / "bronze"
SYNC_DIR = LOCAL_DATA_DIR / "_sync"
VERIFIED_PACKS = SYNC_DIR / "verified_packs.jsonl"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def pull() -> None:
    LOCAL_BRONZE.mkdir(parents=True, exist_ok=True)
    cmd = [
        "rsync", "-az", "--partial-dir=.rsync-partial", "--itemize-changes",
        "--exclude=/gtfs_rt/feed=*",  # today's loose RT files: still being written, not packed yet
        "--exclude=*.tmp",            # half-written files on the VM
        REMOTE, f"{LOCAL_BRONZE}/",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"rsync failed ({result.returncode}): {result.stderr.strip()}")
    changed = [line for line in result.stdout.splitlines() if line.startswith(">f")]
    print(f"[pull] {len(changed)} files transferred or updated")


def verify_packs(problems: list[str]) -> dict:
    done = {r["pack_sha256"] for r in read_jsonl(VERIFIED_PACKS)}
    checked = skipped = 0
    for manifest_path in sorted((LOCAL_BRONZE / "gtfs_rt" / "_packs").glob("feed=*/date=*/manifest.json")):
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        pack_path = manifest_path.with_name(manifest["pack_file"])
        where = f"{manifest['feed']} {manifest['date_myt']}"
        if manifest["pack_sha256"] in done:
            skipped += 1
            continue
        if not pack_path.exists() or sha256_file(pack_path) != manifest["pack_sha256"]:
            problems.append(f"RT pack {where}: missing or sha256 mismatch")
            continue
        expected = {f["name"]: f["sha256"] for f in manifest["files"]}
        actual = {}
        with open(pack_path, "rb") as raw, zstandard.ZstdDecompressor().stream_reader(raw) as stream:
            with tarfile.open(fileobj=stream, mode="r|") as tar:
                for member in tar:
                    if member.isfile():
                        actual[member.name] = sha256_bytes(tar.extractfile(member).read())
        if actual != expected or len(actual) != manifest["file_count"]:
            problems.append(f"RT pack {where}: members do not match the manifest")
            continue
        SYNC_DIR.mkdir(parents=True, exist_ok=True)
        with open(VERIFIED_PACKS, "a", encoding="utf-8") as f:
            f.write(json.dumps({"feed": manifest["feed"], "date_myt": manifest["date_myt"],
                                "pack_sha256": manifest["pack_sha256"], "file_count": len(actual),
                                "verified_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds")}) + "\n")
        checked += 1
    return {"packs_verified": checked, "packs_already_verified": skipped}


def verify_static(problems: list[str]) -> dict:
    blobs = 0
    for category_dir in sorted((LOCAL_BRONZE / "gtfs_static").glob("*/")):
        present = set()
        for blob in category_dir.glob("blobs/*/*.gz"):
            digest = blob.name.removesuffix(".gz")
            if sha256_bytes(gzip.decompress(blob.read_bytes())) != digest:
                problems.append(f"Static blob {category_dir.name}/{blob.name}: content does not match its name")
            present.add(digest)
            blobs += 1
        for snap in read_jsonl(category_dir / "snapshots.jsonl"):
            for name, digest in {**snap.get("files", {}), **snap.get("junk_files", {})}.items():
                if digest not in present:
                    problems.append(f"Static {category_dir.name} {snap['checked_at_myt']}: blob for {name} missing")
    return {"static_blobs_verified": blobs}


def verify_weather(problems: list[str]) -> dict:
    files = 0
    for name in ("weather_forecast", "weather_warning"):
        base = LOCAL_BRONZE / name
        for entry in read_jsonl(base / "fetch_log.jsonl"):
            if entry.get("status") != "changed":
                continue
            path = base / entry["file"]
            if not path.exists():
                problems.append(f"{name} {entry['file']}: missing")
                continue
            data = json.loads(gzip.decompress(path.read_bytes()))
            canonical = json.dumps(data, ensure_ascii=False, sort_keys=True).encode()
            if sha256_bytes(canonical) != entry["sha256"]:
                problems.append(f"{name} {entry['file']}: content does not match fetch_log")
            files += 1
    return {"weather_files_verified": files}


def verify_ridership(problems: list[str]) -> dict:
    files = 0
    base = LOCAL_BRONZE / "ridership_rapidrail"
    for versions in sorted(base.glob("year=*/versions.jsonl")):
        for entry in read_jsonl(versions):
            if entry.get("status") != "changed":
                continue
            path = base / entry["file"]
            if not path.exists() or sha256_file(path) != entry["sha256"]:
                problems.append(f"ridership {entry['file']}: missing or sha256 mismatch")
            files += 1
    return {"ridership_files_verified": files}


def main() -> int:
    parser = argparse.ArgumentParser(description="Pull and verify the Bronze archive from the VM.")
    parser.add_argument("--verify-only", action="store_true", help="skip rsync, only verify the local copy")
    args = parser.parse_args()

    started = datetime.now(timezone.utc)
    if not args.verify_only:
        pull()
    problems: list[str] = []
    summary = {}
    for step in (verify_packs, verify_static, verify_weather, verify_ridership):
        summary.update(step(problems))

    record = {"started_at_utc": started.isoformat(timespec="seconds"),
              "finished_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
              "pulled": not args.verify_only, **summary, "problems": problems}
    SYNC_DIR.mkdir(parents=True, exist_ok=True)
    with open(SYNC_DIR / "sync_log.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")

    for key, value in summary.items():
        print(f"[verify] {key}: {value}")
    for p in problems:
        print(f"[PROBLEM] {p}")
    print("[ok] local copy verified" if not problems else f"[failed] {len(problems)} problem(s)")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
