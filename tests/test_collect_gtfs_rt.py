import json
from datetime import datetime
from pathlib import Path

import collect_gtfs_rt
from google.transit import gtfs_realtime_pb2

PB_REL = Path("gtfs_rt/feed=rapid-bus-mrtfeeder/date=2026-10-23/hour=00/20261022T160015Z.pb")
SLOT_TS = 1792684815


def make_feed_body(n_vehicles: int, timestamp: int | None = SLOT_TS) -> bytes:
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.header.gtfs_realtime_version = "2.0"
    if timestamp is not None:
        feed.header.timestamp = timestamp
    for i in range(n_vehicles):
        entity = feed.entity.add()
        entity.id = str(i)
        entity.vehicle.vehicle.id = f"TEST{i}"
        entity.vehicle.position.latitude = 3.1595798059854743
        entity.vehicle.position.longitude = 101.71330495332896
    return feed.SerializeToString()


# ===== write_atomic ==========================================================


def test_write_atomic_creates_dirs_and_writes_bytes(tmp_path):
    target = tmp_path / PB_REL
    data = b"\x00\xff\x10new"

    assert not target.parent.exists()

    collect_gtfs_rt.write_atomic(target, data)

    assert target.exists()
    assert target.read_bytes() == data


def test_write_atomic_leaves_no_tmp_file(tmp_path):
    target = tmp_path / PB_REL
    data = b"\x00\xff\x10new"

    collect_gtfs_rt.write_atomic(target, data)

    assert list(tmp_path.rglob("*.tmp")) == []


def test_write_atomic_replaces_existing_file(tmp_path):
    target = tmp_path / PB_REL
    data = b"\x00\xff\x10new"

    target.parent.mkdir(parents=True, exist_ok=True)
    old_data = b"\x00\xff\x10old"
    target.write_bytes(old_data)
    assert target.read_bytes() == old_data

    collect_gtfs_rt.write_atomic(target, data)

    assert target.read_bytes() == data


# ===== classify ==========================================================


def test_classify_feed_with_vehicles_is_ok():
    body = make_feed_body(3)
    assert collect_gtfs_rt.classify(body) == ("ok", 3, SLOT_TS, None)


def test_classify_header_without_vehicles_is_ok_empty():
    body = make_feed_body(0)
    assert collect_gtfs_rt.classify(body) == ("ok_empty", 0, SLOT_TS, None)


# protobuf returns 0 for an unset timestamp, and 0 as a Unix time means
# 1970-01-01T00:00:00Z. classify() turns it into None with `or None`, so a
# missing header timestamp is recorded as null instead of a fake 1970 time.
def test_classify_header_without_timestamp_gives_none():
    body = make_feed_body(1, timestamp=None)
    assert collect_gtfs_rt.classify(body) == ("ok", 1, None, None)


def test_classify_invalid_bytes_is_parse_error():
    body = b"not a protobuf"
    status, entities, header_ts, error = collect_gtfs_rt.classify(body)
    assert status == "parse_error"
    assert entities is None
    assert header_ts is None
    assert error.startswith("DecodeError:")


def test_classify_empty_bytes_is_missing_header():
    body = b""
    assert collect_gtfs_rt.classify(body) == ("parse_error", None, None, "missing FeedHeader")


# ===== write_health ==========================================================


def test_write_health_appends_json_lines(tmp_path, monkeypatch):
    monkeypatch.setattr(collect_gtfs_rt, "HEALTH_DIR", tmp_path / "_health")
    myt = datetime.fromtimestamp(SLOT_TS, tz=collect_gtfs_rt.MYT)
    path = tmp_path / "_health" / "feed_health_2026-10-23.jsonl"

    record_1 = {"status": "ok", "feed": "rapid-bus-kl", "latency_ms": 300, "error": None}
    record_2 = {
        "status": "parse_error",
        "feed": "rapid-bus-mrtfeeder",
        "latency_ms": 400,
        "error": "missing FeedHeader",
    }

    collect_gtfs_rt.write_health(record_1, myt)
    collect_gtfs_rt.write_health(record_2, myt)  # test append mode works

    assert path.exists()

    lines = path.read_text(encoding="utf-8").splitlines()

    assert len(lines) == 2
    assert json.loads(lines[0]) == record_1
    assert json.loads(lines[1]) == record_2
