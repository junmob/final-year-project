# collect_gtfs_rt.py
# 作用：长期采集 GTFS Realtime（vehicle position），把原始 .pb 原样写入 Bronze 目录。
#
# 设计依据：docs/data-source/data-source-summary.md 第 2.3、4、7 节
#   - 两个 feed 各每 30 秒一次，错开 15 秒；合计 4 次/分钟，正好是限流上限
#   - 不立即重试：失败（含 429）就跳过本轮，等下一个时间槽，并记录到健康日志
#   - 只保存完整原始 .pb，不在采集端解析
#
# Bronze 路径：<DATA_DIR>/feed=<feed>/date=<YYYY-MM-DD>/hour=<HH>/<YYYYMMDD>T<HHMMSS>Z.pb
#   date / hour 为马来西亚时间（UTC+8），文件名为 UTC 时间槽，与设计书 v0.4 §8.3.3 一致
# 健康日志：<DATA_DIR>/_health/feed_health_<YYYY-MM-DD>.jsonl（每次请求一行）
import hashlib
import json
import os
import signal
import threading
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ.get("GTFS_RT_DATA_DIR", ROOT / "data" / "raw" / "gtfs_realtime"))
BASE = "https://api.data.gov.my/gtfs-realtime/vehicle-position/prasarana?category="
FEEDS = ["rapid-bus-kl", "rapid-bus-mrtfeeder"]
SLOT_SECONDS = 15  # 两个 feed 轮流占用时间槽，每个 feed 的周期 = 30 秒
REQUEST_TIMEOUT = 10  # 必须小于时间槽，避免一次慢请求占用下一个槽
MYT = timezone(timedelta(hours=8))

stop = threading.Event()


def fetch_slot(feed: str, slot_ts: int) -> None:
    slot_utc = datetime.fromtimestamp(slot_ts, tz=timezone.utc)
    record = {
        "slot_utc": slot_utc.isoformat(),
        "feed": feed,
        "fetched_at_utc": None,
        "status": None,
        "bytes": None,
        "sha256": None,
        "latency_ms": None,
        "file": None,
        "error": None,
    }
    started = time.monotonic()
    record["fetched_at_utc"] = datetime.now(timezone.utc).isoformat()
    try:
        resp = requests.get(BASE + feed, timeout=REQUEST_TIMEOUT)
        record["status"] = resp.status_code
        record["latency_ms"] = round((time.monotonic() - started) * 1000)
        if resp.status_code != 200:
            record["error"] = f"HTTP {resp.status_code}"  # 429 也在这里，不重试
        elif not resp.content:
            record["error"] = "empty body"
        else:
            record["bytes"] = len(resp.content)
            record["sha256"] = hashlib.sha256(resp.content).hexdigest()
            myt = slot_utc.astimezone(MYT)
            out_dir = DATA_DIR / f"feed={feed}" / f"date={myt:%Y-%m-%d}" / f"hour={myt:%H}"
            out_dir.mkdir(parents=True, exist_ok=True)
            path = out_dir / f"{slot_utc:%Y%m%dT%H%M%SZ}.pb"
            tmp = path.with_suffix(".pb.tmp")
            tmp.write_bytes(resp.content)
            tmp.replace(path)  # 原子写入，避免留下写到一半的文件
            record["file"] = str(path.relative_to(DATA_DIR))
    except requests.RequestException as e:
        record["error"] = f"{type(e).__name__}: {e}"
    except OSError as e:
        record["error"] = f"write failed: {e}"

    write_health(record, slot_utc)
    state = "ok" if record["error"] is None else f"FAIL ({record['error']})"
    print(f"{record['slot_utc']} {feed}: {state}", flush=True)


def write_health(record: dict, slot_utc: datetime) -> None:
    try:
        health_dir = DATA_DIR / "_health"
        health_dir.mkdir(parents=True, exist_ok=True)
        path = health_dir / f"feed_health_{slot_utc.astimezone(MYT):%Y-%m-%d}.jsonl"
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError as e:
        print(f"健康日志写入失败: {e}", flush=True)


def main() -> None:
    signal.signal(signal.SIGTERM, lambda *_: stop.set())
    signal.signal(signal.SIGINT, lambda *_: stop.set())
    print(f"开始采集 {FEEDS}，输出目录 {DATA_DIR}", flush=True)

    while not stop.is_set():
        # 下一个 15 秒整点；若上一轮超时错过了槽，直接跳到当前之后的下一个槽，不补发
        slot_ts = (int(time.time()) // SLOT_SECONDS + 1) * SLOT_SECONDS
        if stop.wait(max(0, slot_ts - time.time())):
            break
        feed = FEEDS[(slot_ts // SLOT_SECONDS) % len(FEEDS)]
        fetch_slot(feed, slot_ts)

    print("已停止", flush=True)


if __name__ == "__main__":
    main()
