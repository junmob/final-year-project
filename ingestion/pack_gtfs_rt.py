# pack_gtfs_rt.py
# Purpose: daily packing of GTFS Realtime Bronze files (design doc v0.4 §8.3.3).
#   For every feed and every completed Malaysia-time day that still has loose .pb files:
#     1. write all of that day's .pb files into <BRONZE_DIR>/gtfs_rt/_packs/feed=/date=/rt.tar.zst
#     2. re-read the pack and check every member against the sha256 of the loose file
#     3. write manifest.json (file list, sha256, slot counts from the health log)
#     4. only then delete the loose files
#   Safe to re-run: a day that already has a manifest is only re-verified and cleaned up.
#   Loose files that are not in an existing manifest are left in place and reported.
#
# Run by gtfs-rt-pack.timer at 00:30 MYT. Usage: python pack_gtfs_rt.py [--dry-run]
import argparse
import hashlib
import io
import json
import os
import sys
import tarfile
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

import zstandard

ROOT = Path(__file__).resolve().parent.parent
BRONZE_DIR = Path(os.environ.get("BRONZE_DIR", ROOT / "data" / "bronze"))
RT_DIR = BRONZE_DIR / "gtfs_rt"
PACK_DIR = RT_DIR / "_packs"
HEALTH_DIR = BRONZE_DIR / "_health"
SLOTS_PER_DAY = 2880  # one request every 30 s per feed
ZSTD_LEVEL = 10
MYT = timezone(timedelta(hours=8))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def health_summary(feed: str, day: str) -> dict:
    path = HEALTH_DIR / f"feed_health_{day}.jsonl"
    counts: Counter = Counter()
    if path.exists():
        with open(path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    record = json.loads(line)
                    if record.get("feed") == feed:
                        counts[record.get("status") or "unknown"] += 1
    recorded = sum(counts.values())
    return {
        "expected_slots": SLOTS_PER_DAY,
        "recorded_slots": recorded,
        "no_record_slots": max(0, SLOTS_PER_DAY - recorded),
        "status_counts": dict(sorted(counts.items())),
    }


def read_pack(pack_path: Path) -> dict[str, str]:
    """Return {member name: sha256} for every file in a .tar.zst pack."""
    members = {}
    with open(pack_path, "rb") as raw:
        with zstandard.ZstdDecompressor().stream_reader(raw) as stream:
            with tarfile.open(fileobj=stream, mode="r|") as tar:
                for member in tar:
                    if member.isfile():
                        members[member.name] = sha256_bytes(tar.extractfile(member).read())
    return members


def write_pack(pack_path: Path, day_dir: Path, files: list[Path]) -> None:
    pack_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = pack_path.with_name(pack_path.name + ".tmp")
    with open(tmp, "wb") as raw:
        cctx = zstandard.ZstdCompressor(level=ZSTD_LEVEL)
        with cctx.stream_writer(raw, closefd=False) as stream:
            with tarfile.open(fileobj=stream, mode="w|", format=tarfile.PAX_FORMAT) as tar:
                for path in files:
                    data = path.read_bytes()
                    info = tarfile.TarInfo(str(path.relative_to(day_dir)))
                    info.size = len(data)
                    info.mtime = int(path.stat().st_mtime)
                    tar.addfile(info, io.BytesIO(data))
    tmp.replace(pack_path)


def delete_loose(day_dir: Path, expected: dict[str, str]) -> tuple[int, list[str]]:
    deleted, kept = 0, []
    for path in sorted(day_dir.rglob("*.pb")):
        name = str(path.relative_to(day_dir))
        if expected.get(name) == sha256_file(path):
            path.unlink()
            deleted += 1
        else:
            kept.append(name)
    for sub in sorted(day_dir.rglob("*"), reverse=True):
        if sub.is_dir() and not any(sub.iterdir()):
            sub.rmdir()
    if day_dir.exists() and not any(day_dir.iterdir()):
        day_dir.rmdir()
    return deleted, kept


def pack_day(feed: str, day_dir: Path, dry_run: bool) -> bool:
    day = day_dir.name.removeprefix("date=")
    out_dir = PACK_DIR / f"feed={feed}" / f"date={day}"
    pack_path, manifest_path = out_dir / "rt.tar.zst", out_dir / "manifest.json"
    files = sorted(day_dir.rglob("*.pb"))
    if not files:
        return True
    if dry_run:
        print(f"[dry-run] {feed} {day}: {len(files)} loose files")
        return True

    if manifest_path.exists():
        # Earlier run packed this day but was interrupted before (or during) cleanup.
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        expected = {f["name"]: f["sha256"] for f in manifest["files"]}
        if read_pack(pack_path) != expected:
            print(f"[error] {feed} {day}: pack does not match its manifest; nothing deleted")
            return False
    else:
        loose = {str(p.relative_to(day_dir)): sha256_file(p) for p in files}
        write_pack(pack_path, day_dir, files)
        if read_pack(pack_path) != loose:
            pack_path.unlink()
            print(f"[error] {feed} {day}: pack verification failed; pack removed, files kept")
            return False
        expected = loose
        manifest = {
            "feed": feed,
            "date_myt": day,
            "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "pack_file": pack_path.name,
            "pack_sha256": sha256_file(pack_path),
            "pack_bytes": pack_path.stat().st_size,
            "raw_bytes": sum(p.stat().st_size for p in files),
            "file_count": len(files),
            "first_file": min(loose),
            "last_file": max(loose),
            **health_summary(feed, day),
            "files": [{"name": n, "sha256": s} for n, s in sorted(loose.items())],
        }
        tmp = manifest_path.with_name(manifest_path.name + ".tmp")
        tmp.write_text(json.dumps(manifest, indent=1) + "\n", encoding="utf-8")
        tmp.replace(manifest_path)

    deleted, kept = delete_loose(day_dir, expected)
    ratio = manifest["raw_bytes"] / max(1, manifest["pack_bytes"])
    print(f"[packed] {feed} {day}: {manifest['file_count']} files, "
          f"{manifest['pack_bytes'] / 1e6:.1f} MB ({ratio:.1f}x), deleted {deleted} loose files")
    if kept:
        print(f"[warn] {feed} {day}: {len(kept)} loose files not in manifest were kept: {kept[:5]}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="list what would be packed")
    args = parser.parse_args()

    today = datetime.now(MYT).strftime("%Y-%m-%d")
    ok = True
    for feed_dir in sorted(RT_DIR.glob("feed=*")):
        feed = feed_dir.name.removeprefix("feed=")
        for day_dir in sorted(feed_dir.glob("date=*")):
            if day_dir.name.removeprefix("date=") < today:  # never pack the day still being written
                ok = pack_day(feed, day_dir, args.dry_run) and ok
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
