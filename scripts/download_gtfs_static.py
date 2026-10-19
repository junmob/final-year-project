# download_gtfs_static.py
# 作用：下载 3 个核心 GTFS Static ZIP，仅当内容与最近一次保存的版本不同时才存档。
# 变化检测：对 ZIP 内每个文件的内容计算 SHA-256（忽略 ZIP 自身的时间戳等元数据），
#           再合成一个"内容指纹"。指纹变化 = 新版本。
# 输出：data/raw/gtfs_static/<category>_<YYYYMMDD>.zip，指纹记录在 manifest.json
import hashlib
import io
import json
import sys
import time
import zipfile
from datetime import date
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "data" / "raw" / "gtfs_static"
MANIFEST = OUT_DIR / "manifest.json"
URL = "https://api.data.gov.my/gtfs-static/prasarana?category="
CATEGORIES = ["rapid-bus-kl", "rapid-bus-mrtfeeder", "rapid-rail-kl"]
REQUEST_GAP_SECONDS = 20  # data-source-summary.md：每个请求间隔 ≥ 20 秒


def content_fingerprint(zip_bytes: bytes) -> str:
    """ZIP 内所有文件（按文件名排序）的内容指纹，与压缩方式、打包时间无关。"""
    h = hashlib.sha256()
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
        for name in sorted(n for n in z.namelist() if not n.endswith("/")):
            h.update(name.encode())
            h.update(hashlib.sha256(z.read(name)).digest())
    return h.hexdigest()


def load_manifest() -> dict:
    manifest = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
    # 首次运行：用目录里已有的 ZIP 补全，避免把已有版本当成"新版本"重复保存
    for category in CATEGORIES:
        if category in manifest:
            continue
        existing = sorted(OUT_DIR.glob(f"{category}_*.zip"))
        if existing:
            latest = existing[-1]
            manifest[category] = {
                "fingerprint": content_fingerprint(latest.read_bytes()),
                "file": latest.name,
            }
    return manifest


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest = load_manifest()
    today = date.today().strftime("%Y%m%d")
    failed = False

    for i, category in enumerate(CATEGORIES):
        if i:
            time.sleep(REQUEST_GAP_SECONDS)
        try:
            resp = requests.get(URL + category, timeout=60)
            resp.raise_for_status()
            fingerprint = content_fingerprint(resp.content)
        except (requests.RequestException, zipfile.BadZipFile) as e:
            print(f"[失败] {category}: {e}")
            failed = True
            continue

        previous = manifest.get(category, {}).get("fingerprint")
        if fingerprint == previous:
            print(f"[无变化] {category}: 与 {manifest[category]['file']} 内容相同，跳过")
            continue

        path = OUT_DIR / f"{category}_{today}.zip"
        path.write_bytes(resp.content)
        manifest[category] = {"fingerprint": fingerprint, "file": path.name}
        print(f"[新版本] {category}: 已保存 {path.name} ({len(resp.content)/1024:.0f} KB)")

    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
