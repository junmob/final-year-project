# check_realtime.py
# Purpose: one-off probe. Downloads both GTFS Realtime feeds and checks whether trip_id /
#          route_id match the latest archived GTFS Static (data-source summary §4.4).
#          Output goes to docs/evidence/realtime_probe/ as evidence; this is not the
#          long-running collector (see ingestion/collect_gtfs_rt.py).
import gzip
import io
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests
from google.protobuf.json_format import MessageToDict
from google.transit import gtfs_realtime_pb2

ROOT = Path(__file__).resolve().parent.parent
STATIC_DIR = ROOT / "data" / "raw" / "gtfs_static"
RT_DIR = ROOT / "docs" / "evidence" / "realtime_probe"
FEEDS = ["rapid-bus-kl", "rapid-bus-mrtfeeder"]
# The trailing slash avoids a 301 redirect (which would cost a second request).
BASE = "https://api.data.gov.my/gtfs-realtime/vehicle-position/prasarana/?category="


def latest_static_file(category: str, name: str) -> tuple[pd.DataFrame, str] | None:
    """Read one file of the latest successful Static snapshot (see download_gtfs_static.py)."""
    snapshots = STATIC_DIR / category / "snapshots.jsonl"
    if not snapshots.exists():
        return None
    last = None
    for line in snapshots.read_text(encoding="utf-8").splitlines():
        if line.strip() and (record := json.loads(line)).get("status") == "ok":
            last = record
    if last is None or name not in last["files"]:
        return None
    digest = last["files"][name]
    data = gzip.decompress((STATIC_DIR / category / "blobs" / digest[:2] / f"{digest}.gz").read_bytes())
    return pd.read_csv(io.BytesIO(data), dtype=str), last["checked_at_myt"]


def main() -> None:
    RT_DIR.mkdir(parents=True, exist_ok=True)
    for i, category in enumerate(FEEDS):
        if i:
            time.sleep(20)  # stay well inside the 4 requests/minute limit
        print("=" * 60)
        print(f"Feed: {category}")

        resp = requests.get(BASE + category, timeout=30)
        print(f"HTTP status: {resp.status_code}, size: {len(resp.content) / 1024:.1f} KB")
        if resp.status_code != 200:
            continue

        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")  # UTC avoids time-zone mix-ups
        (RT_DIR / f"raw_{category}_{stamp}.pb").write_bytes(resp.content)

        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(resp.content)
        df = pd.json_normalize([MessageToDict(e.vehicle) for e in feed.entity])
        print(f"Vehicles online: {len(df)}")
        if df.empty:
            continue

        print(f"Fields: {list(df.columns)}")
        print(df.head(5).to_string())
        df.to_csv(RT_DIR / f"rt_{category}_{stamp}.csv", index=False)

        if "timestamp" in df.columns:
            ts = pd.to_numeric(df["timestamp"])
            newest = datetime.fromtimestamp(ts.max(), tz=timezone.utc)
            oldest = datetime.fromtimestamp(ts.min(), tz=timezone.utc)
            print(f"Newest GPS time: {newest}, oldest: {oldest}")

        static = latest_static_file(category, "trips.txt")
        if static is None:
            print(f"No Static snapshot for {category}; run scripts/download_gtfs_static.py first")
            continue
        trips, checked_at = static
        print(f"Static snapshot used: {checked_at}")
        for rt_col, st_col in [("trip.tripId", "trip_id"), ("trip.routeId", "route_id")]:
            if rt_col not in df.columns:
                print(f"Field {rt_col} not present in the Realtime feed")
                continue
            rt_ids = df[rt_col].dropna().astype(str)
            matched = rt_ids.isin(set(trips[st_col]))
            print(f"{rt_col} match rate: {matched.mean():.1%} "
                  f"({matched.sum()}/{len(rt_ids)}, missing {df[rt_col].isna().sum()})")
            print(f"   unmatched examples: {rt_ids[~matched].head(5).tolist()}")


if __name__ == "__main__":
    main()
