# download_weather.py
# 作用：P0 采集服务上线前的临时天气归档（设计书 v0.4 §12.3、§15.3 第 10 项）。
#       下载天气预报和天气警告，内容与上一次不同时才保存（gzip 压缩）。
# 依据：docs/data-source/data-source-summary.md §6.1、§6.2、§7.1
#   - 预报接口一次返回全国全部地点的 7 天预报（2026-10-20 实测 3080 行、约 0.9 MB，无需分页）
#   - 记录中没有发布时间，用采集时间代替（E35），所以文件名记录采集时间
# 输出：data/raw/weather_forecast/date=<YYYY-MM-DD>/fetched_at=<HHMMSS>.json.gz（马来西亚时间）
#       data/raw/weather_warning/date=<YYYY-MM-DD>/fetched_at=<HHMMSS>.json.gz
#       最近一次保存的内容哈希记录在各自目录的 manifest.json
import gzip
import hashlib
import json
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "data" / "raw"
# 不带结尾斜杠会先返回 301
ENDPOINTS = {
    "weather_forecast": "https://api.data.gov.my/weather/forecast/",
    "weather_warning": "https://api.data.gov.my/weather/warning/",
}
REQUEST_GAP_SECONDS = 20  # data-source-summary.md §6.1.4：每次请求间隔 ≥ 20 秒
MYT = timezone(timedelta(hours=8))


def main() -> int:
    now = datetime.now(MYT)
    failed = False

    for i, (name, url) in enumerate(ENDPOINTS.items()):
        if i:
            time.sleep(REQUEST_GAP_SECONDS)
        try:
            resp = requests.get(url, timeout=60)
            resp.raise_for_status()
            data = resp.json()  # 确认是合法 JSON
        except (requests.RequestException, ValueError) as e:
            print(f"[失败] {name}: {e}")
            failed = True
            continue

        # 按规范化后的 JSON 计算哈希，避免空格或键顺序差异被当成新内容
        canonical = json.dumps(data, ensure_ascii=False, sort_keys=True).encode()
        digest = hashlib.sha256(canonical).hexdigest()
        manifest_path = OUT_DIR / name / "manifest.json"
        previous = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
        if digest == previous.get("sha256"):
            print(f"[无变化] {name}: 与 {previous['file']} 内容相同，跳过")
            continue

        out_dir = OUT_DIR / name / f"date={now:%Y-%m-%d}"
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / f"fetched_at={now:%H%M%S}.json.gz"
        # 原样保存响应内容；mtime=0 让相同内容的 gzip 字节也相同
        path.write_bytes(gzip.compress(resp.content, mtime=0))
        manifest = {
            "sha256": digest,
            "file": str(path.relative_to(OUT_DIR / name)),
            "records": len(data) if isinstance(data, list) else None,
        }
        manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
        print(f"[新内容] {name}: 已保存 {path.relative_to(ROOT)}（{len(resp.content)/1024:.0f} KB 原始）")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
