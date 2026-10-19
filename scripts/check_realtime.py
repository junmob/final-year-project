# check_realtime.py
# 作用：下载 Realtime 数据，并检查 trip_id / route_id 能否匹配 Static 数据
# pyrefly: ignore [missing-import]
from google.transit import gtfs_realtime_pb2
from google.protobuf.json_format import MessageToDict
from datetime import datetime, timezone
import pandas as pd
import requests
import time
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATIC_DIR = ROOT / "data" / "raw" / "gtfs_static"
RT_DIR = ROOT / "data" / "raw" / "gtfs_realtime"
RT_DIR.mkdir(parents=True, exist_ok=True)
FEEDS = ["rapid-bus-kl", "rapid-bus-mrtfeeder"]
BASE = "https://api.data.gov.my/gtfs-realtime/vehicle-position/prasarana?category="

for category in FEEDS:
    print("=" * 60)
    print(f"运营商: {category}")

    resp = requests.get(BASE + category, timeout=30)
    print(f"HTTP 状态码: {resp.status_code}, 文件大小: {len(resp.content)/1024:.1f} KB")
    if resp.status_code != 200:
        continue

    # 保存原始文件（之后的采集层也会这样做）
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(RT_DIR / f"raw_{category}_{stamp}.pb", "wb") as f:
        f.write(resp.content)

    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(resp.content)
    df = pd.json_normalize([MessageToDict(e.vehicle) for e in feed.entity])
    print(f"在线车辆数: {len(df)}")
    if df.empty:
        continue

    print(f"所有字段: {list(df.columns)}")
    print(df.head(5).to_string())
    df.to_csv(RT_DIR / f"rt_{category}_{stamp}.csv", index=False)

    # 数据新鲜度
    if "timestamp" in df.columns:
        ts = pd.to_numeric(df["timestamp"])
        newest = datetime.fromtimestamp(ts.max(), tz=timezone.utc)
        oldest = datetime.fromtimestamp(ts.min(), tz=timezone.utc)
        print(f"最新 GPS 时间: {newest.astimezone()}，最旧: {oldest.astimezone()}")

    # 关键检查：Realtime 与 Static 的 ID 匹配率
    static_zips = sorted(STATIC_DIR.glob(f"{category}_*.zip"))
    if not static_zips:
        print(f"⚠️ 找不到 {category} 的 Static ZIP，请先运行 scripts/download_gtfs_static.py")
        continue
    print(f"使用 Static 版本: {static_zips[-1].name}")
    with zipfile.ZipFile(static_zips[-1]) as z:
        trips = pd.read_csv(z.open("trips.txt"), dtype=str)
    for rt_col, st_col in [("trip.tripId", "trip_id"), ("trip.routeId", "route_id")]:
        if rt_col in df.columns:
            rt_ids = df[rt_col].dropna().astype(str)
            matched = rt_ids.isin(set(trips[st_col]))
            print(f"{rt_col} 匹配率: {matched.mean():.1%} "
                  f"({matched.sum()}/{len(rt_ids)}，缺失 {df[rt_col].isna().sum()} 条)")
            print(f"   对不上的例子: {rt_ids[~matched].head(5).tolist()}")
        else:
            print(f"⚠️ Realtime 数据里没有 {rt_col} 字段")

    time.sleep(20)  # 遵守限流：每分钟最多 4 次