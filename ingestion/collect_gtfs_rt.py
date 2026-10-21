# collect_gtfs_rt.py
# Purpose: long-running collector for GTFS Realtime vehicle positions. Each response is
#          written unchanged to Bronze as a raw .pb file (design doc v0.4 §8.3.3).
#
# Rules (data-source summary §2.3, §4, §7; design doc §8.3.2):
#   - Each of the two feeds is polled every 30 s, offset by 15 s, which uses the full
#     4 requests/minute GTFS Realtime quota.
#   - No retries: a failed slot (including HTTP 429) is skipped and logged.
#   - Raw bytes are stored as received. The only parsing is a light Protobuf check that
#     classifies the slot (ok / ok_empty / parse_error).
#
# Bronze layout (date and hour are Malaysia time, file name is the UTC slot):
#   <BRONZE_DIR>/gtfs_rt/feed=<feed>/date=<YYYY-MM-DD>/hour=<HH>/<YYYYMMDD>T<HHMMSS>Z.pb
#   <BRONZE_DIR>/gtfs_rt/_invalid/feed=<feed>/date=<YYYY-MM-DD>/<...>Z.pb   unparseable bodies
#   <BRONZE_DIR>/_health/feed_health_<YYYY-MM-DD>.jsonl                     one line per slot
import hashlib
import json
import os
import signal
import socket
import threading
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
from google.protobuf.message import DecodeError
from google.transit import gtfs_realtime_pb2

ROOT = Path(__file__).resolve().parent.parent
BRONZE_DIR = Path(os.environ.get("BRONZE_DIR", ROOT / "data" / "bronze"))
RT_DIR = BRONZE_DIR / "gtfs_rt"
HEALTH_DIR = BRONZE_DIR / "_health"
# The trailing slash matters: without it the API answers 301 and every poll costs two requests.
BASE = "https://api.data.gov.my/gtfs-realtime/vehicle-position/prasarana/?category="
FEEDS = ["rapid-bus-kl", "rapid-bus-mrtfeeder"]
SLOT_SECONDS = 15  # the two feeds take turns, so each feed is polled every 30 s
REQUEST_TIMEOUT = (5, 10)  # (connect, read); must stay below one slot
INSTANCE = os.environ.get("COLLECTOR_INSTANCE", socket.gethostname())
MYT = timezone(timedelta(hours=8))

stop = threading.Event()
session = requests.Session()
session.headers["User-Agent"] = "fyp-gtfs-rt-collector/1.0"


def write_atomic(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_bytes(data)
    tmp.replace(path)  # never leave a half-written file under the final name


def classify(body: bytes) -> tuple[str, int | None, int | None, str | None]:
    """Return (status, entity_count, header_timestamp, error) for a 200 response body."""
    feed = gtfs_realtime_pb2.FeedMessage()
    try:
        feed.ParseFromString(body)
    except DecodeError as e:
        return "parse_error", None, None, f"DecodeError: {e}"
    if not feed.HasField("header"):
        return "parse_error", None, None, "missing FeedHeader"
    entities = len(feed.entity)
    return ("ok" if entities else "ok_empty"), entities, feed.header.timestamp or None, None


def fetch_slot(feed: str, slot_ts: int) -> dict:
    slot_utc = datetime.fromtimestamp(slot_ts, tz=timezone.utc)
    myt = slot_utc.astimezone(MYT)
    name = f"{slot_utc:%Y%m%dT%H%M%SZ}.pb"
    record = {
        "slot_utc": slot_utc.isoformat(),
        "feed": feed,
        "instance": INSTANCE,
        "requested_at_utc": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
        "status": None,
        "http_status": None,
        "latency_ms": None,
        "bytes": None,
        "sha256": None,
        "entities": None,
        "header_ts": None,
        "file": None,
        "error": None,
    }
    started = time.monotonic()
    try:
        resp = session.get(BASE + feed, timeout=REQUEST_TIMEOUT, allow_redirects=False)
        record["latency_ms"] = round((time.monotonic() - started) * 1000)
        record["http_status"] = resp.status_code
        if resp.status_code == 429:
            record["status"], record["error"] = "rate_limited", "HTTP 429"
        elif resp.status_code != 200:
            record["status"], record["error"] = "http_error", f"HTTP {resp.status_code}"
        elif not resp.content:
            record["status"], record["error"] = "http_error", "empty body"
        else:
            body = resp.content
            status, entities, header_ts, error = classify(body)
            if status == "parse_error":
                path = RT_DIR / "_invalid" / f"feed={feed}" / f"date={myt:%Y-%m-%d}" / name
            else:
                path = RT_DIR / f"feed={feed}" / f"date={myt:%Y-%m-%d}" / f"hour={myt:%H}" / name
            write_atomic(path, body)
            record.update(status=status, entities=entities, header_ts=header_ts, error=error,
                          bytes=len(body), sha256=hashlib.sha256(body).hexdigest(),
                          file=str(path.relative_to(BRONZE_DIR)))
    except requests.Timeout as e:
        record["status"], record["error"] = "timeout", f"{type(e).__name__}: {e}"
    except requests.RequestException as e:
        record["status"], record["error"] = "network_error", f"{type(e).__name__}: {e}"
    except OSError as e:
        record["status"], record["error"] = "write_error", f"{type(e).__name__}: {e}"

    if record["latency_ms"] is None:
        record["latency_ms"] = round((time.monotonic() - started) * 1000)
    write_health(record, myt)
    return record


def write_health(record: dict, myt: datetime) -> None:
    try:
        HEALTH_DIR.mkdir(parents=True, exist_ok=True)
        path = HEALTH_DIR / f"feed_health_{myt:%Y-%m-%d}.jsonl"
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
    except OSError as e:
        print(f"health log write failed: {e}", flush=True)


def main() -> None:
    signal.signal(signal.SIGTERM, lambda *_: stop.set())
    signal.signal(signal.SIGINT, lambda *_: stop.set())
    print(f"collector {INSTANCE} started: feeds={FEEDS} bronze={BRONZE_DIR}", flush=True)

    while not stop.is_set():
        # Next 15 s boundary. If a slow request overran a slot, that slot is not re-sent;
        # it has no health record and is later counted as no_record against the slot grid.
        slot_ts = (int(time.time()) // SLOT_SECONDS + 1) * SLOT_SECONDS
        if stop.wait(max(0, slot_ts - time.time())):
            break
        feed = FEEDS[(slot_ts // SLOT_SECONDS) % len(FEEDS)]
        r = fetch_slot(feed, slot_ts)
        detail = f"entities={r['entities']}" if r["error"] is None else r["error"]
        print(f"{r['slot_utc']} {feed}: {r['status']} ({detail}, {r['latency_ms']} ms)", flush=True)

    print("collector stopped", flush=True)


if __name__ == "__main__":
    main()
