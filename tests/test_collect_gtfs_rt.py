from pathlib import Path

import collect_gtfs_rt

PB_REL = Path("gtfs_rt/feed=rapid-bus-mrtfeeder/date=2026-10-23/hour=00/20261022T160015Z.pb")


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
