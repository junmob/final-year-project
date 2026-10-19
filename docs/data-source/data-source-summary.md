# 数据源全景剖析与实测档案（gtfs_data_source.md）

> **用途**：本项目所有数据源的参考手册，可直接作为论文第 3 章（需求与数据分析）中数据源识别、数据剖析、数据质量评估、数据源选择理由的素材。
>
> **版本**：v1.0（2026-10-19）
>
> **证据来源**：
> 1. developer.data.gov.my 官方 OpenAPI 文档（11 页，你提供的全文）
> 2. 你下载并检查的 GTFS Static 样本：`rapid-bus-kl`、`rapid-bus-mrtfeeder`、`rapid-rail-kl`、`KTMB`、`BAS.MY Ipoh`（下载于 2026-10-05 前后）
> 3. 两次 GTFS Realtime 实测：**2026-10-05（星期一）约 19:53** 和 **2026-10-11（星期日）约 20:35**，使用 `check_realtime.py`
> 4. 你查证的辅助数据源官方页面：MET Malaysia 天气 API、Rapid Rail OD 客流、DOSM 行政区人口、公共假期现状（2026-10-14 前后）
>
> **状态标记**：✅ 已验证（有官方文档或实测证据）｜ 🟡 部分验证 ｜ ❓ 待验证 ｜ 💡 推测（需要证据确认）
>
> **关于行数**：文中样本文件的"行数"是你统计的数字，未确认是否包含表头行，误差最多 1 行。

---

## 目录

1. 数据源总览与采用决策
2. data.gov.my OpenAPI 机制
3. GTFS Static 剖析
4. GTFS Realtime 剖析与实测
5. 数据脏点与异常证据目录
6. 外部辅助数据源评估
7. 采集设计与请求预算
8. 辅助数据源的数据质量规则
9. 采用决策汇总
10. 待验证事项清单
11. 与论文第 3 章的映射

---

## 1. 数据源总览与采用决策

| # | 数据源 | 提供方 | 获取方式 | 更新频率 | 格式 | 角色 | 决定 |
|---|---|---|---|---|---|---|---|
| S1 | GTFS Realtime：`rapid-bus-kl` | Prasarana，经 data.gov.my | OpenAPI | 30 秒 | Protobuf | 主事实 | ✅ **核心** |
| S2 | GTFS Realtime：`rapid-bus-mrtfeeder` | Prasarana，经 data.gov.my | OpenAPI | 30 秒 | Protobuf | 主事实 | ✅ **核心** |
| S3 | GTFS Static：`rapid-bus-kl` | Prasarana | OpenAPI | 按需 | ZIP（CSV） | 参考与维度 | ✅ **核心** |
| S4 | GTFS Static：`rapid-bus-mrtfeeder` | Prasarana | OpenAPI | 按需 | ZIP | 参考与维度 | ✅ **核心** |
| S5 | GTFS Static：`rapid-rail-kl` | Prasarana | OpenAPI | 按需 | ZIP | 轨道站点维度 | ✅ **采用**（接驳分析与客流关联） |
| S6 | 天气预报（7 天） | MET Malaysia，经 data.gov.my | OpenAPI | 每天 | JSON | 环境维度 | ✅ **采用**（P0 起归档，P3 建模） |
| S7 | 天气警告 | MET Malaysia，经 data.gov.my | OpenAPI | 按需 | JSON | 事件 | 🟡 **只归档**，分析放到 Future Work |
| S8 | 公共假期 | 政府公告（没有官方 API） | dbt seed（人工维护） | 每年 + 临时公告 | CSV | 日期维度 | ✅ **采用**（MVP） |
| S9 | Rapid Rail OD 每日客流（巴生谷） | Prasarana，经 data.gov.my | 文件下载 | 每天 | Parquet / CSV | 次事实 | ✅ **采用（次核心）**，FYP 1 中后段 |
| S10 | 行政区人口 | DOSM | 文件下载 | 每年 | Parquet / CSV | 地区维度属性 | 🟡 **可选**，取决于县界数据是否可得 |
| S11 | 实际观测天气（例如 Open-Meteo） | 第三方 | API | 每小时 | JSON | 环境维度 | ❓ **待定**，FYP 2 可选 |
| — | GTFS：KTMB、BAS.MY、Penang、Kuantan | 多家 | OpenAPI | | | | ❌ 不纳入（KTMB 和 BAS.MY 可作可选扩展） |
| — | 洪水警告 `/flood-warning` | data.gov.my | OpenAPI | 实时 | JSON | | ❓ 未评估，Future Work 候选 |

详细理由见 §6 和 §9。

---

## 2. data.gov.my OpenAPI 机制

### 2.1 基础信息 ✅

| 项目 | 说明 |
|---|---|
| Base URL | `https://api.data.gov.my` |
| 请求方法 | HTTP GET |
| 认证 | **不需要 API token** |
| 后端 | RESTful API，Django 框架 |
| 交互工具 | 官方提供 Postman Collection |
| 联系方式 | 500 错误时可以邮件 `help.dtsa@jdn.gov.my` |

### 2.2 版本历史 ✅

| 版本 | 日期 | 内容 |
|---|---|---|
| 1.0.0 | 2023-09-13 | 首次发布：`/data-catalogue`、`/opendosm`、`/flood-warning` |
| 1.1.0 | 2023-10-09 | Weather API：`/weather/forecast`、`/weather/warning`、`/weather/warning/earthquake` |
| 1.2.0 | 2023-11-06 | GTFS Static API：myBAS Johor Bahru、KTMB、Prasarana |
| 1.3.0 | 2023-11-14 | GTFS Realtime API：myBAS Johor Bahru、KTMB、Prasarana |
| 1.4.0 | 2024-04-01 | GTFS Realtime 新增 MRT Feeder Bus |
| 1.5.0 | 2025-10-10 | GTFS Realtime 新增 BAS.MY 五个城市：Kangar、Alor Setar、Kota Bharu、Kuala Terengganu、Kuching |
| 1.6.0 | 2025-10-13 | GTFS Realtime 新增 BAS.MY Melaka |

**观察**：
- API 仍在持续扩展，说明数据源是活跃维护的，适合作为长期项目的数据源。
- 文档提到 **trip updates 和 service alerts 计划在 2026 年推出**，截至本文档日期尚未在 changelog 中出现。**需要每月检查一次**（V13），因为一旦推出，到站推断和 RQ1 的验证方式都会受影响。

### 2.3 限流 ✅

| API | 限额 |
|---|---|
| Data Catalogue | 每分钟 4 次 |
| OpenDOSM | 每分钟 4 次 |
| Weather | 每分钟 4 次 |
| GTFS Static | 每分钟 4 次 |
| GTFS Realtime | 每分钟 4 次 |

超出限额时返回 `429 Too Many Requests`，后续请求会失败。

**分析**：
- 文档按 **API 类别**分别列出限额，💡 推测是每个类别各自计数（Realtime 和 Static 不互相占用）。但文档没有说明是按 IP、按 endpoint 还是按类别计数 ❓（V02）。
- **关键约束**：`rapid-bus-kl` 和 `rapid-bus-mrtfeeder` 都属于 "GTFS Realtime" 类别。两个 feed 各每 30 秒一次 = **每分钟 4 次，正好等于上限**。这意味着：
  - 任何一次重试都可能触发 429
  - 不能再增加第三个 Realtime feed（除非限额是按 endpoint 计算）
- **应对**：两个 feed 错开 15 秒请求；失败时不立即重试，而是跳过本轮、等下一个时间槽；所有 429 记录到 `fct_feed_health`。

### 2.4 响应码 ✅

| 状态码 | 含义 |
|---|---|
| 200 | 成功 |
| 400 | 请求无效，查看错误信息 |
| 404 | 资源不存在 |
| 429 | 被限流 |
| 500 | 服务器错误 |

**JSON 类 API**（Data Catalogue、OpenDOSM、Weather）：
- 默认返回记录列表
- 加上 `?meta=true` 时返回 `{"meta": {...}, "data": [...]}`，`meta` 包含资源信息和已应用的过滤条件
- 错误时返回 `{status: <int>, errors: [...]}`

**GTFS API**：返回二进制文件（Static 是 ZIP，Realtime 是 Protobuf），不适用上面的 JSON 格式。

### 2.5 查询参数（只适用于 JSON 类 API）✅

| 参数 | 类型 | 说明 | 语法 |
|---|---|---|---|
| `filter` | string | 精确匹配，区分大小写 | `?filter=<value>@<column>`，多列用逗号分隔 |
| `ifilter` | string | 精确匹配，不区分大小写 | `?ifilter=<value>@<column>` |
| `contains` | string | 部分匹配，区分大小写 | `?contains=<value>@<column>` |
| `icontains` | string | 部分匹配，不区分大小写 | `?icontains=<value>@<column>` |
| `range` | string | 数值范围（含两端） | `?range=<column>[<begin>:<end>]` |
| `sort` | string | 排序，`-` 前缀表示降序 | `?sort=<col1>,-<col2>` |
| `date_start` / `date_end` | date | 日期范围（含两端） | `?date_start=YYYY-MM-DD@<date_column>` |
| `timestamp_start` / `timestamp_end` | datetime | 时间戳范围 | `?timestamp_start=YYYY-MM-DD HH:MM:SS@<column>` |
| `limit` | integer | 最多返回的记录数 | `?limit=<n>` |
| `include` / `exclude` | string | 选择或排除列，`include` 优先 | `?include=<col1>,<col2>` |

- **嵌套字段**用双下划线访问，例如 `location__location_name`
- 文档**没有说明默认返回多少条、是否分页** ❓。采集天气时需要实测（V01），否则可能只拿到部分数据而不自知。

---

## 3. GTFS Static 剖析

### 3.1 端点与运营商 ✅

| 运营商 | 端点 | 本项目 |
|---|---|---|
| KTMB | `/gtfs-static/ktmb` | 不纳入（可选扩展） |
| Prasarana `rapid-bus-kl` | `/gtfs-static/prasarana?category=rapid-bus-kl` | ✅ 核心 |
| Prasarana `rapid-bus-mrtfeeder` | `/gtfs-static/prasarana?category=rapid-bus-mrtfeeder` | ✅ 核心 |
| Prasarana `rapid-rail-kl` | `/gtfs-static/prasarana?category=rapid-rail-kl` | ✅ 维度 |
| Prasarana `rapid-bus-penang` | `/gtfs-static/prasarana?category=rapid-bus-penang` | ❌ |
| Prasarana `rapid-bus-kuantan` | `/gtfs-static/prasarana?category=rapid-bus-kuantan` | ❌ |
| BAS.MY Kangar | `/gtfs-static/mybas-kangar` | ❌ |
| BAS.MY Alor Setar | `/gtfs-static/mybas-alor-setar` | ❌ |
| BAS.MY Kota Bharu | `/gtfs-static/mybas-kota-bharu` | ❌ |
| BAS.MY Kuala Terengganu | `/gtfs-static/mybas-kuala-terengganu` | ❌ |
| BAS.MY Ipoh | `/gtfs-static/mybas-ipoh` | ❌（已看样本，可作多运营商标准化的可选扩展） |
| BAS.MY Seremban（两家运营商） | `/gtfs-static/mybas-seremban-a`、`/gtfs-static/mybas-seremban-b` | ❌ |
| BAS.MY Melaka | `/gtfs-static/mybas-melaka` | ❌ |
| BAS.MY Johor Bahru | `/gtfs-static/mybas-johor` | ❌ |
| BAS.MY Kuching | `/gtfs-static/mybas-kuching` | ❌ |

**特别说明**：
- Seremban 有两个 endpoint，因为两家运营商分别提供数据，官方说明需要两个都查询才能得到完整图景。这是"同一业务实体、多个数据提供方"的例子。
- `rapid-bus-kl` 约有 **2% 的班次**因运营问题从 `stop_times.txt` 中被移除，完整列表在 `https://openapi-malaysia-transport.s3.ap-southeast-1.amazonaws.com/prasarana/problematic_trips.csv`。你检查过，**这个 CSV 只有 `trip_id` 一列**，没有原因、日期或恢复计划。

### 3.2 更新频率 ✅

| 运营商 | 更新频率 |
|---|---|
| KTMB | 每天 00:01:00 |
| Prasarana | 按需（as required） |
| BAS.MY | 按需 |

官方建议：如果用定时任务，**每天至少刷新一次，时间在凌晨 4 点**，也就是全国轨道和巴士服务开始运营之前。

### 3.3 文件构成 ✅

| 类型 | 文件 | 说明 |
|---|---|---|
| 必备（所有运营商都提供） | `agency.txt` | 运营机构 |
| | `stops.txt` | 站点 |
| | `routes.txt` | 路线 |
| | `trips.txt` | 班次及其路线 |
| | `stop_times.txt` | 各班次在各站的时刻 |
| | `calendar.txt` | 服务日期 |
| 可选（有才提供） | `frequencies.txt` | 按发车间隔排班 |
| | `shapes.txt` | 路线几何形状 |
| | `calendar_dates.txt` | 服务日期例外 |

参考标准：GTFS Schedule Reference（gtfs.org/schedule/reference）。

### 3.4 各运营商样本剖析

#### 3.4.1 `rapid-bus-kl` ✅

| 文件 | 列 | 行数 | 样本 |
|---|---|---|---|
| `agency.txt` | agency_id, agency_name, agency_url, agency_timezone, agency_phone, agency_lang | 1 | `rapidkl, Rapid KL, http://www.myrapid.com.my, Asia/Kuala_Lumpur, 60378852585, en` |
| `calendar.txt` | service_id, monday–sunday, start_date, end_date | 2 | `weekday,1,1,1,1,1,0,0,20200401,20270331`；`weekend,0,0,0,0,0,1,1,20200401,20270331` |
| `frequencies.txt` | trip_id, start_time, end_time, headway_secs, exact_times | 2094 | `weekday_S1040_S104002_0, 06:00:00, 19:30:00, 1800, 0` |
| `routes.txt` | route_id, agency_id, route_short_name, route_long_name, route_type, route_color, route_text_color | 138 | `B1000, rapidkl, SUNWAY LINE, BRT USJ 7 - BRT Setia Jaya, 3, 21618C, FFFFFF` |
| `shapes.txt` | shape_id, shape_pt_lat, shape_pt_lon, shape_pt_sequence | 69231 | `U222002, 3.228029547, 101.745625356, 1` |
| `stop_times.txt` | trip_id, arrival_time, departure_time, stop_id, stop_sequence, stop_headsign | 87802 | `weekday_B1000_B100001_0, 06:15:00, 06:15:00, 1005840, 1,`（`stop_headsign` 为空） |
| `stops.txt` | stop_id, stop_name, stop_desc, stop_lat, stop_lon | 4053 | `1005840, STESEN BRT SETIA JAYA, BRT LALUAN SUNWAY, 3.082856, 101.612238` |
| `trips.txt` | route_id, service_id, trip_id, shape_id, trip_headsign, direction_id | 2097 | `S1040, weekday, weekday_S1040_S104002_0, S104002, , 0`（`trip_headsign` 为空） |

**特点**：
- **按发车间隔排班**：`frequencies.txt` 中 `exact_times=0`，表示"大约每 `headway_secs` 秒一班"，不是精确时刻表。`stop_times.txt` 里的时间是**模板**，实际班次时间 = 频率窗口起点 + 模板中的相对偏移。
- `trip_id` 结构：`{service_id}_{route_id}_{shape_id}_{序号}`，例如 `weekday_S1040_S104002_0`。
- 服务只有 `weekday` 和 `weekend` 两种，有效期 2020-04-01 到 **2027-03-31**。
- 站点名称和描述是马来文，全大写（`STESEN BRT SETIA JAYA`、`BRT LALUAN SUNWAY`）。
- `trips.txt` 有 2097 行，`frequencies.txt` 有 2094 行，💡 可能有 3 个班次没有频率定义（或是行数统计差异），待确认。

#### 3.4.2 `rapid-bus-mrtfeeder` ✅

| 文件 | 列 | 行数 | 样本 |
|---|---|---|---|
| `agency.txt` | agency_name, agency_url, agency_timezone, agency_phone, agency_lang（**没有 agency_id**） | 1 | `MRT Feeder Bus, https://www.myrapid.com.my/traveling-with-us/how-to-travel-with-us/rapid-kl/mrt/mrt-feeder-bus, Asia/Kuala_Lumpur, 03-7885-2585, en` |
| `calendar.txt` | service_id, monday–sunday, start_date, end_date | 2 | `26100201,1,1,1,1,1,0,0,20261005,20261113`；`26100203,1,0,0,0,0,1,1,20261010,20261115` |
| `calendar_dates.txt` | service_id, date, exception_type | 5 | `26100201, 20261109, 2` |
| `routes.txt` | route_id, agency_id, route_short_name, route_long_name, route_type | 91 | `30000143, , , T117, 3`；`30000044, , , T413, 3`；`30000117, , , T459, 3` |
| `shapes.txt` | shape_id, shape_pt_lat, shape_pt_lon, shape_pt_sequence, shape_dist_traveled | 35,030 | `1000000061, 3.1498746, 101.5922941, 1, 0.0` |
| `stop_times.txt` | trip_id, arrival_time, departure_time, stop_id, stop_sequence, stop_headsign, shape_dist_traveled | 175,718 | `261002010001S10, 19:10:00, 19:10:00, 12003044, 1, XIAO EN CENTER, 0.11169799999999999` |
| `stops.txt` | stop_id, stop_code, stop_name, stop_lat, stop_lon | 2118 | `12000321, PJ785, KOMPLEKS MUHIBBAH (BARAT), 3.15800900, 101.57040000` |
| `trips.txt` | route_id, service_id, trip_id, trip_headsign, direction_id, shape_id | 6291 | `30000009, 26100201, 261002010049S10, MRT SURIAN - SEK 11 KOTA DAMANSARA, 0, 1000000061` |

**特点**：
- **精确班次排班**：每个班次都有完整的时刻表，可以计算准点率。
- **`service_id` 命名**：💡 推测为 `YYMMDD + 两位类型码`。`261002` 可能是版本日期 2026-10-02，`01` 是平日，`03` 是周末类。
- **`trip_id` 结构**：💡 `{service_id}{4 位序号}S{n}`，例如 `261002010049S10`。
- **有效期约 6 周**：`26100201` 是 2026-10-05 到 **2026-11-13**；`26100203` 是 2026-10-10 到 **2026-11-15**。所以 **11 月中旬会出现新版本**。
- **`26100203` 的星期组合异常**：Monday=1、Saturday=1、Sunday=1。同时 `calendar_dates` 在 **2026-11-09（星期一）**移除了平日服务 `26100201`。💡 推测是公共假期的处理方式（2026-11-08 屠妖节是星期日，11-09 可能是补假），但只有看完 `calendar_dates` 全部 5 行才能确定（V04）。
- **路线编号放错字段**：`route_id` 是内部 8 位编号（`30000143`），乘客认识的路线编号（`T117`）放在 `route_long_name` 里，`agency_id` 和 `route_short_name` 都是空的。
- `trip_headsign` 有值，内容是起讫点（`MRT SURIAN - SEK 11 KOTA DAMANSARA`），可以用来识别接驳的 MRT 站。
- `stop_code` 带有地区前缀（`PJ785`），💡 `PJ` 可能代表 Petaling Jaya，可以作为站点归属地区的线索（待验证）。
- `shape_dist_traveled` 单位未说明，💡 首站值 0.1117 推测单位是公里。

#### 3.4.3 `rapid-rail-kl` ✅

| 文件 | 列 | 行数 | 样本 |
|---|---|---|---|
| `agency.txt` | agency_id, agency_name, agency_url, agency_timezone, agency_phone, agency_lang | 1 | `rapidrail, rapidrail, http://www.myrapid.com.my, Asia/Kuala_Lumpur, 60378852585, en` |
| `calendar.txt` | service_id, monday–sunday, start_date, end_date | 8 | `Sun,0,0,0,0,0,0,1,20190101,20261231` |
| `frequencies.txt` | trip_id, start_time, end_time, headway_secs（**没有 exact_times**） | 106 | `AGL_MonFri_0, 6:00:00, 9:00:00, 180` |
| `routes.txt` | route_id, agency_id, route_short_name, route_long_name, route_desc, route_type, route_color, route_text_color, **category, status** | 8 | `AG, rapidrail, AGL, LRT Ampang Line, Ampang ~ Sentul Timur, 1, e57200, FFFFFF, LRT, valid` |
| `shapes.txt` | shape_id, **shape_pt_lon, shape_pt_lat**, shape_pt_sequence | 7280 | `shp_AG_0, 101.760359, 3.150787, 1` |
| `stop_times.txt` | **route_id, direction_id**, trip_id, arrival_time, departure_time, stop_id, stop_sequence | 1122 | `AGL, 0, AGL_MonFri_0, 6:00:00, 6:00:18, AG18, 1` |
| `stops.txt` | stop_id, stop_name, stop_lat, stop_lon, **category, route_id, geometry, isOKU, status, search** | 187 | `AG18, AMPANG, 3.150318, 101.760049, LRT, AG, [object Object], true, valid, LRT AMPANG` |
| `trips.txt` | route_id, service_id, trip_id, trip_headsign, direction_id, shape_id | 48 | `AG, MonFri, AGL_MonFri_0, From Ampang to Sentul Timur, 0, shp_AG_0` |

**特点**：
- **按发车间隔排班**（例如早高峰每 180 秒一班），没有精确班次，所以**无法计算轨道延误**。
- **没有稳定的 Realtime 数据**（官方文档说明）。
- **用途**：提供 MRT/LRT/Monorail 站点维度，用于：① 接驳巴士与 MRT 站的对应；② 关联 Rapid Rail OD 客流（§6.4）。
- `stop_id` 格式是 `线路代码 + 编号`（`AG18`），💡 和 OD 客流数据中的站点代码（`AG01: Sentul Timur`）格式一致，有可能直接关联（V09）。
- 有效期到 **2026-12-31**，2027 年 1 月需要留意新版本。
- 有多个非标准字段（`category`、`status`、`isOKU`、`search` 等），其中 `isOKU`（是否无障碍）是有用的属性。

#### 3.4.4 KTMB ✅（不纳入范围，作为对比参考）

| 文件 | 列 | 行数 | 样本 |
|---|---|---|---|
| `agency.txt` | agency_id, agency_name, agency_url, agency_timezone, agency_phone, agency_lang | 1 | `ktmb, Keretapi Tanah Melayu, https://www.ktmb.com.my/, Asia/Kuala_Lumpur, 60322671200, en` |
| `calendar.txt` | service_id, monday–sunday, start_date, end_date | 6 | `ets,1,1,1,1,1,1,1,20260818,20261019` |
| `calendar_dates.txt` | service_id, date, exception_type | 6 | `komuter_weekday, 20260825, 2` |
| `routes.txt` | **agency_id, route_id**, route_type, route_short_name, route_long_name, route_desc, route_url, route_color, route_text_color | 9 | `ktmb, KC05_KB18, 0, Seremban Line, KTM Batu Caves - Pulau Sebang/Tampin, , https://www.ktmb.com.my/komuter-routes-map.html, 3C5A9F, FFFFFF` |
| `stop_times.txt` | trip_id, arrival_time, departure_time, stop_id, stop_sequence, shape_dist_traveled | 5157 | `1004, 22:30:00, 22:30:00, 19100, 1, 0` |
| `stops.txt` | stop_id, stop_name, stop_lat, stop_lon | 156 | `50500, TAMAN WAHYU, 3.21451, 101.672178` |
| `trips.txt` | route_id, service_id, trip_id, direction_id | 374 | `ETS, ets, 1004, 0` |

**特点**：
- 每天 00:01 重新生成，`calendar` 是滚动窗口。
- **没有 `shapes.txt`**，但 `stop_times.txt` 有 `shape_dist_traveled`；`trips.txt` 没有 `shape_id`。
- Komuter 线路的 `route_type` 是 `0`（GTFS 标准中 0 = 有轨电车或轻轨），💡 一般重轨应为 `2`，疑似分类错误。

#### 3.4.5 BAS.MY Ipoh ✅（不纳入范围，作为对比参考）

| 文件 | 列 | 行数 | 样本 |
|---|---|---|---|
| `agency.txt` | agency_id, agency_name, agency_url, agency_timezone, agency_phone, agency_lang | 1 | `TCBMYBIPH, THE COMBINE BUS MYBUS IPOH, https://www.nssit.com.my/, Asia/Kuala_Lumpur, ,`（电话和语言为空） |
| `calendar.txt` | service_id, monday–sunday, start_date, end_date | 1 | `Bas.my,1,1,1,1,1,1,1,20261005,20261005` |
| `routes.txt` | route_id, agency_id, route_short_name, route_long_name, route_type | 17 | `A100, TCBMYBIPH, BANDARAYA IPOH, BANDARAYA IPOH, 3` |
| `shapes.txt` | shape_id, shape_pt_lat, shape_pt_lon, shape_pt_sequence | 1515 | `R2402001, 4.5942240, 101.0723600, 1` |
| `stop_times.txt` | trip_id, arrival_time, departure_time, stop_id, stop_sequence, pickup_type, drop_off_type | 18,788 | `R2402001_T1, 06:24:00, 06:24:00, AMANJAYA_T30A, 25, 0, 0` |
| `stops.txt` | stop_id, stop_code, stop_name, stop_lat, stop_lon, parent_station | 2079 | `ACSIPOH_T36, T36, ACS IPOH, 4.59044011, 101.07339263,` |
| `trips.txt` | route_id, service_id, trip_id, shape_id, direction_id | 369 | `A30A, Bas.my, R2402001_T1, R2402001, 0` |

**特点**：
- **`calendar` 只对下载当天有效**（start_date = end_date = 20261005），说明每天重新生成一次。
- `route_short_name` 和 `route_long_name` 完全相同。
- `stop_id` 是"名称 + 代码"的组合（`AMANJAYA_T30A`、`ACSIPOH_T36`）。17 条路线却有 2079 个站点，💡 推测同一个物理站点可能按路线重复出现。
- `stop_times.txt` 第一行的 `stop_sequence` 是 25，说明**文件没有按顺序排列**，处理时必须先排序。

### 3.5 跨运营商 Schema 差异对照

#### 3.5.1 文件是否存在

| 文件 | rapid-bus-kl | mrtfeeder | rapid-rail-kl | KTMB | Ipoh |
|---|---|---|---|---|---|
| agency | ✅ | ✅（缺 agency_id 列） | ✅ | ✅ | ✅ |
| calendar | ✅ | ✅ | ✅ | ✅ | ✅ |
| calendar_dates | ❌ | ✅ | ❌ | ✅ | ❌ |
| frequencies | ✅（有 exact_times） | ❌ | ✅（无 exact_times） | ❌ | ❌ |
| routes | ✅ | ✅ | ✅ | ✅ | ✅ |
| shapes | ✅ | ✅（有 shape_dist_traveled） | ✅（**经度在前**） | ❌ | ✅ |
| stop_times | ✅ | ✅ | ✅（多 route_id、direction_id） | ✅ | ✅ |
| stops | ✅ | ✅ | ✅（多 6 个非标准列） | ✅ | ✅ |
| trips | ✅ | ✅ | ✅ | ✅（无 shape_id） | ✅ |

#### 3.5.2 ID 格式

| 运营商 | route_id | trip_id | stop_id | shape_id | service_id |
|---|---|---|---|---|---|
| rapid-bus-kl | 字母 + 4 位（`B1000`、`S1040`、`U2500`） | `{service}_{route}_{shape}_{n}` | 7 位数字（`1005840`） | 路线 + 2 位（`S104002`） | `weekday`、`weekend` |
| mrtfeeder | 8 位数字（`30000143`）；公开编号在 long_name（`T117`） | `{service_id}{4位}S{n}`（`261002010049S10`） | 8 位数字（`12000321`），另有 `stop_code`（`PJ785`） | 10 位数字（`1000000061`） | 日期 + 类型（`26100201`） |
| rapid-rail-kl | 线路代码（`AG`），但 stop_times 用 `AGL` | `{线路简称}_{service}_{n}`（`AGL_MonFri_0`） | 线路 + 编号（`AG18`） | `shp_AG_0` | `MonFri`、`Sun` 等 |
| KTMB | `KC05_KB18`、`ETS` | 数字（`1004`） | 5 位数字（`50500`） | 无 | `ets`、`komuter_weekday` |
| Ipoh | `A100`、`A30A` | `{shape}_{T代码}`（`R2402001_T1`） | 名称 + 代码（`AMANJAYA_T30A`） | `R2402001` | `Bas.my` |

**含义**：
- **不同运营商的数字 `stop_id` 有冲突风险**（rapid-bus-kl 7 位、mrtfeeder 8 位、KTMB 5 位）。目前没有观察到冲突，但合并时必须用 **"运营商 + 原始 ID"** 作为代理键。
- 💡 Penang 的 Realtime `trip_id` 格式（`30000001_1000000855_053000_02`，见 §4.3）中的 `30000001`、`1000000855` 与 mrtfeeder 的 `route_id`（`3000xxxx`）、`shape_id`（`1000000061`）格式相同，推测两者使用同一家供应商的系统。

#### 3.5.3 格式细节

| 项目 | rapid-bus-kl | mrtfeeder | rapid-rail-kl | KTMB | Ipoh |
|---|---|---|---|---|---|
| 时间格式 | `06:15:00` | `19:10:00` | **`6:00:00`（无前导零）** | `22:30:00` | `06:24:00` |
| shapes 列顺序 | lat, lon | lat, lon | **lon, lat** | 无 shapes | lat, lon |
| shapes 坐标精度 | 9 位小数 | 7 位 | 6 位 | | 7 位 |
| stops 坐标精度 | 6 位 | 8 位 | 6 位 | 6 位 | 8 位 |
| 电话格式 | `60378852585` | `03-7885-2585`（**同一个号码，格式不同**） | `60378852585` | `60322671200` | 空 |
| agency_url 协议 | http | https | http | https | https |
| agency_lang | en | en | en | en | 空 |
| 站名语言 | 马来文，全大写 | 英文和马来文混合，全大写 | 全大写 | 全大写 | 全大写 |

### 3.6 排班模式差异

| | 精确班次型 | 发车间隔型 |
|---|---|---|
| 运营商 | mrtfeeder、KTMB、Ipoh | rapid-bus-kl、rapid-rail-kl |
| 关键文件 | `stop_times.txt` 有完整时刻 | `frequencies.txt` + `stop_times.txt` 模板 |
| 乘客体验 | 按时刻表候车 | 随到随等 |
| **适合的可靠性指标** | **准点率（OTP）**：实际到站 − 计划到站 | **发车间隔稳定性**：间隔变异系数、额外等待时间（EWT）、串车率 |
| Realtime 关联 | 用 `trip_id` 关联时刻表 | GTFS-RT 规范要求用 `trip_id` + `start_time` 区分同一模板的不同班次；rapid-bus-kl 的 Realtime 确实带有 `startTime` |

**这决定了本项目要同时实现两套指标**，也是研究设计的一部分。

### 3.7 有效期与版本更替

| 运营商 | 当前版本有效期结束 | 影响 |
|---|---|---|
| KTMB | 2026-10-19（每天滚动） | 每天一版 |
| Ipoh | 2026-10-05（每天一版） | 每天一版 |
| **mrtfeeder** | **2026-11-13 / 2026-11-15** | **11 月中旬换新版。采集服务上线前，旧版本可能就过期了** |
| **rapid-rail-kl** | **2026-12-31** | 2027 年 1 月需要留意 |
| **rapid-bus-kl** | **2027-03-31** | FYP 1 期间会换版 |

> [!IMPORTANT]
> **在采集服务上线之前，请每周手动下载一次三个核心 Static ZIP**（kl、mrtfeeder、rail），按日期命名保存。mrtfeeder 现行版本会在 11 月中过期，错过就无法再取得，之后也无法用它计算这段时间的准点率。

---

## 4. GTFS Realtime 剖析与实测

### 4.1 端点 ✅

格式：`GET https://api.data.gov.my/gtfs-realtime/vehicle-position/<agency>`

| Feed | 端点 | Static 可用 | Realtime 状态 | 本项目 |
|---|---|---|---|---|
| KTMB | `/vehicle-position/ktmb` | ✅ | 可用（未实测） | ❌ |
| rapid-bus-kl | `/vehicle-position/prasarana?category=rapid-bus-kl` | ✅ | ✅ 实测可用 | ✅ 核心 |
| rapid-bus-mrtfeeder | `/vehicle-position/prasarana?category=rapid-bus-mrtfeeder` | ✅ | ✅ 实测可用 | ✅ 核心 |
| rapid-bus-kuantan | `/vehicle-position/prasarana?category=rapid-bus-kuantan` | ✅ | 有已知错误 E003/E004 | ❌ |
| rapid-bus-penang | `/vehicle-position/prasarana?category=rapid-bus-penang` | ✅ | 有已知错误 E003/E004 和 trip_id 前缀问题 | ❌ |
| rapid-rail-kl | 无 | ✅ | **没有稳定的 Realtime** | 只用 Static |
| BAS.MY 各城市 | `/vehicle-position/mybas-<city>`（kangar、alor-setar、kota-bharu、kuala-terengganu、ipoh、seremban-a、seremban-b、melaka、johor、kuching） | ✅ | 可用（未实测） | ❌ |

### 4.2 更新频率与格式 ✅

- 所有 vehicle position feed **每 30 秒更新一次**
- 格式：标准 GTFS Realtime Protobuf（`.proto`）
- 解析：官方语言绑定，Python 使用 `gtfs-realtime-bindings`：

```python
from google.transit import gtfs_realtime_pb2
from google.protobuf.json_format import MessageToDict
feed = gtfs_realtime_pb2.FeedMessage()
feed.ParseFromString(response.content)
vehicle_positions = [MessageToDict(entity.vehicle) for entity in feed.entity]
```

- **目前只有 vehicle positions**。trip updates 和 service alerts 在官方 2026 年计划中，尚未推出。所以**到站时间、延误都必须自己从 GPS 推断**。

### 4.3 官方已知问题 ✅

| 编号 | 影响范围 | 内容 | 官方解释 |
|---|---|---|---|
| **E028** | 所有巴士 feed | 车辆位置落在 Static 定义的服务区域之外 | Static 数据没有错，原因是车载应答器偶尔回报错误的 GPS |
| **E003** | Kuantan、Penang | Realtime 的 `trip_id` 在 Static 中不存在 | 运营系统老旧（部分超过十年），无法正确追踪班次和路线 |
| **E004** | Kuantan、Penang | Realtime 的 `route_id` 在 Static 中不存在 | 同上 |
| trip_id 前缀 | Penang | Realtime 的 `30000001_1000000855_053000_02` 对应 Static 的 `weekend_...`、`weekday_...`、`23102302_...` 等带前缀版本，需要去掉 service 前缀再比对 | 官方选择不修改 Realtime 数据以免影响性能，将来会修复 |
| 无轨道实时 | rapid-rail-kl | 没有稳定的 Realtime feed | |

（错误编号来自 MobilityData 的 GTFS Realtime Validator。）

### 4.4 实测记录 ✅

**方法**：`check_realtime.py` 依次下载两个 feed（间隔 20 秒），解析 Protobuf，保存原始 `.pb` 和 CSV，计算时间戳范围，并与本地 Static 的 `trips.txt` 比对 `trip_id` 和 `route_id`。

> [!NOTE]
> 比对用的 Static 是 10 月 5 日前后下载的版本，不是每次实测当天重新下载的。这可能影响 10/11 的 `trip_id` 匹配率（V06）。

| 项目 | 10/5（一）kl | 10/5（一）feeder | 10/11（日）kl | 10/11（日）feeder |
|---|---|---|---|---|
| HTTP 状态 | 200 | 200 | 200 | 200 |
| 文件大小 | 11.4 KB | 9.6 KB | 8.8 KB | 6.3 KB |
| 在线车辆数 | 106 | 123 | 82 | 80 |
| 最新 GPS 时间 | 19:53:59 | **2029-10-07 05:45:56** | 20:36:30 | **2029-10-07 05:45:56** |
| 最旧 GPS 时间 | 19:52:35 | 19:53:41 | 20:35:07 | 20:35:58 |
| `tripId` 匹配率 | **87.7%**（93/106） | **90.2%**（111/123） | **87.8%**（72/82） | **86.2%**（69/80） |
| `routeId` 匹配率 | 100%（106/106） | **0%**（0/123） | 100%（82/82） | **0%**（0/80） |
| `tripId` 缺失 | 0 | 0 | 0 | 0 |
| `trip_id` 前缀 | `weekday_` | | `weekend_` | |

**观察**：
- 星期一的车辆数多于星期日，`trip_id` 前缀也正确反映了平日和周末。
- 两次实测都只在晚上进行，**没有白天高峰的数据**，车辆数和规模估算可能偏低（V07）。

### 4.5 字段剖析

| 字段（`MessageToDict` 扁平化后） | rapid-bus-kl | mrtfeeder | 观察 |
|---|---|---|---|
| `timestamp` | ✅ | ✅ | UTC epoch 秒（例如 `1791722184`），需要转换为 `Asia/Kuala_Lumpur` |
| `trip.tripId` | ✅ | ✅ | 见 §4.6 |
| `trip.startTime` | ✅（例如 `20:34:24`） | ❌ **缺失** | 发车间隔型班次需要它来区分班次实例 |
| `trip.startDate` | ✅（例如 `20261011`） | ❌ **缺失** | mrtfeeder 的服务日期只能从时间戳推断，跨午夜班次有风险 |
| `trip.routeId` | ✅（与 Static 一致） | ✅ 但填的是 `route_long_name`（`T154`、`T543`、`T459`、`T507`、`T815`、`T400`、`T114`、`T490`、`T101`、`T412`） | |
| `position.latitude` / `longitude` | ✅ | ✅ | |
| `position.bearing` | ✅（小数，例如 `298.0`、`12.2`、`152.6`） | ✅（**全部是整数**，例如 `280.0`、`335.0`、`92.0`） | |
| `position.speed` | ✅（两位小数） | ✅（**全部是整数**） | 见下方速度分析 |
| `vehicle.id` | ✅ | ✅ | 大多是车牌（`WB3552P`、`JPG4977`、`VAJ2876`），也有内部编号（`RAPID443`、`RPD429`） |
| `vehicle.licensePlate` | ✅ | ✅ | 样本中与 `vehicle.id` 相同 |

**速度单位分析** 🟡：

| | rapid-bus-kl 样本 | mrtfeeder 样本 |
|---|---|---|
| 数值 | 14.82, 12.2, 24.08, 6.30, 0.00, 7.41, 18.52, 22.04, 15.37, 22.22 | 0.0, 43.0, 0.0, 35.0, 46.0, 31.0, 37.0, 0.0, 0.0, 28.0 |
| 特征 | 两位小数；`22.22 = 80 ÷ 3.6`、`18.52 ≈ 66.7 ÷ 3.6`、`7.41 ≈ 26.7 ÷ 3.6` | 全部是整数 |
| 推断 | 符合 GTFS 规范的 **m/s**（可能是由 km/h 换算而来） | 若是 m/s，46 m/s ≈ 166 km/h，对市区巴士不合理 → **很可能是 km/h** |

结论需要更大样本的速度分布确认（V08）。

**未检查的字段**：实测脚本只提取了 `entity.vehicle`，没有检查 `FeedHeader.timestamp`（feed 生成时间）、`entity.id`，以及 `vehicle.current_status`、`stop_id`、`congestion_level` 等可选字段是否存在。采集服务应**保存完整的原始 `.pb`**，并在 Silver 层解析 header 时间戳，用于计算 feed 自身的新鲜度。

### 4.6 ID 匹配分析

#### `routeId`（mrtfeeder：0%）✅
- **原因**（你发现的）：Realtime 的 `routeId` 填的是 `routes.txt` 里的 `route_long_name`（例如 `T117`），而不是 `route_id`（例如 `30000143`）。
- **修正**：用 `routes.txt` 建立 `route_long_name → route_id` 映射表。**前提**：`route_long_name` 在同一版本中唯一（需要 dbt 唯一性测试）。
- **注意**：映射关系要按 Static 版本维护（SCD2），因为新版本可能改变映射。

#### `tripId`（86% 到 90%）🟡

| Feed | 对不上的例子 | 💡 可能原因 | 验证方法 |
|---|---|---|---|
| rapid-bus-kl | `weekday_U2500_U250001_23`、`weekday_U2500_U250001_22`、`weekday_U8210_U821002_5`、`weekday_U7520_U752001_9`、`weekend_U1730_U173002_5`、`weekend_T4068_T406802_7`、`weekend_U7700_U770001_7`、`weekend_U8210_U821002_5`、`weekend_U4500_U450001_11` | 末尾序号超出 Static 中已定义的范围（发车间隔型模板与实际班次编号不一致） | 列出 Static 中 `U2500` 路线的所有 `trip_id`，看序号范围；去掉末尾序号后再匹配（V05） |
| mrtfeeder | `261002030114S2`、`261002010196S14` 等 | Static 版本与 Realtime 日期不一致；或这些班次属于 `problematic_trips` | 实测当天重新下载 Static 后再比对（V06） |

### 4.7 规模估算

| 项目 | 数值 | 依据 |
|---|---|---|
| 每个 feed 的在线车辆数 | 80–123（晚上） | 实测 |
| 每次下载大小 | 6–11 KB | 实测 |
| 每个 feed 每天采集次数 | 2880 | 86400 ÷ 30 |
| **每天行数**（两个 feed，含重复） | 约 50 万到 60 万 | 约 200 辆 × 2880 |
| **每天原始数据** | 约 50 到 60 MB | 约 10 KB × 2 × 2880 |
| **6 个月** | 约 **1 亿行**，原始数据约 **10 GB** | |

- 白天高峰车辆可能更多，实际规模可能更大（V07）。
- 去重后的有效行数会更少，因为同一个 GPS 点可能被连续多次采集到。
- 同一次快照内，车辆时间戳跨度约 **83 到 84 秒**（例如 10/5 kl：19:52:35 到 19:53:59），说明部分车辆的位置更新间隔超过 30 秒，或者 feed 中保留了较旧的位置。

---

## 5. 数据脏点与异常证据目录

> 这是论文第 3 章"数据质量评估"的核心表格。**处理方式**：🔴 隔离 ｜ 🟡 标记 ｜ 🔧 修正 ｜ 📊 监控告警 ｜ 📝 只记录

### 5.1 GTFS Realtime

| ID | 问题 | 证据 | 影响 | 处理 | 规则或难点 |
|---|---|---|---|---|---|
| E01 | mrtfeeder `routeId` 填成 `route_long_name` | 10/5：0/123；10/11：0/80 | 无法直接关联路线 | 🔧 版本化映射表 | DQ10 |
| E02 | `tripId` 匹配率不足 | kl 87.7%、87.8%；feeder 90.2%、86.2% | 约 10–14% 的点无法关联时刻表 | 🟡 + 后备推断；匹配率 < 80% 时📊 | DQ09 |
| E03 | **未来时间戳** | 三次实测都出现完全相同的 **2029-10-07 05:45:56（+08:00）**（10/5、10/11，以及 10/20 02:11 MYT 云端探测，后者 mrtfeeder 当时唯一在线的车辆 `VAL4552`，同一快照 `tripId` 241209021024S2、`routeId` T105 均对不上 Static），跨度约 15 天 → 推测是某一台设备持续输出的固定错误值 | 破坏时间分区、新鲜度和时序计算 | 🔴 | DQ02 |
| E04 | 速度单位疑似不一致 | feeder 全为整数 28–46；kl 两位小数且符合 km/h ÷ 3.6 | 速度类指标和异常检测出错 | 🔧 统一为 m/s + 🟡 | DQ06 |
| E05 | mrtfeeder 缺少 `startTime`、`startDate` | 两次实测的字段列表 | 服务日期需要推断，跨午夜班次有风险 | 🔧 用时间戳和时刻表推断 | 难点 D4 |
| E06 | 车辆 ID 格式不统一 | `WB3552P`、`JPG4977` 与 `RAPID443`、`RPD429` | 车辆维度对齐困难 | 🔧 标准化 | DQ12 |
| E07 | 轮询产生重复记录 | 设计必然：GPS 更新间隔 ≠ 采集间隔 | 重复计算 | 🔧 按 `(feed, vehicle_id, timestamp)` 去重 | DQ08 |
| E08 | 快照内时间戳跨度约 84 秒 | 10/5 kl 19:52:35–19:53:59；10/11 kl 20:35:07–20:36:30 | 部分位置偏旧 | 🟡 过期标记 | DQ03 |
| E09 | GPS 漂移到服务区之外 | 官方 E028 | 错误的到站推断 | 🟡 | DQ05 |
| E10 | Penang/Kuantan 的 ID 不存在于 Static | 官方 E003/E004 | | 📝 排除出范围 | 范围决定 |
| E11 | Penang `trip_id` 带前缀问题 | 官方文档 | | 📝 排除出范围 | 范围决定 |
| E12 | rapid-rail-kl 没有稳定的 Realtime | 官方文档 | 轨道无法算延误 | 📝 只用 Static | 范围决定 |
| E13 | 没有 trip updates 和 service alerts | 官方文档 | 到站和延误要自己推断 | 📝 | 难点 D1 |

### 5.2 GTFS Static

| ID | 问题 | 证据 | 影响 | 处理 | 规则或难点 |
|---|---|---|---|---|---|
| E14 | rapid-bus-kl 约 2% 班次从 `stop_times` 移除 | 官方文档；CSV 只有 `trip_id` | 这些班次无法计算指标；缺少原因和日期等元数据 | 🟡 黑名单 | DQ17 |
| E15 | `geometry` 值为 `[object Object]` | rapid-rail `stops.txt` | 上游 JavaScript 序列化失败，字段无效 | 🔧 置为 NULL | DQ18 |
| E16 | 同一个 ID 在不同表里写法不同 | rapid-rail：`trips.route_id = AG`，`stop_times.route_id = AGL` | 直接 JOIN 失败 | 🟡 引用完整性检查 | DQ15 |
| E17 | 非标准字段 | rapid-rail：`stop_times` 多 `route_id`、`direction_id`；`stops` 多 `category`、`route_id`、`geometry`、`isOKU`、`status`、`search`；`routes` 多 `category`、`status` | 标准 GTFS 工具会忽略或报错 | 🔧 schema 标准化，保留有用字段 | DQ13 |
| E18 | `shapes.txt` 经纬度列顺序相反 | rapid-rail 是 `lon, lat`，其他是 `lat, lon` | 按位置读取会导致坐标错乱 | 🔧 一律按列名读取 | 难点 D6 |
| E19 | 时间格式不统一 | rapid-rail `6:00:00`（无前导零） | 字符串比较和解析出错 | 🔧 统一解析 | 难点 D6 |
| E20 | mrtfeeder 缺 `agency_id`；`routes.agency_id`、`route_short_name` 为空；公开编号放在 `route_long_name` | 样本 | 多运营商合并困难；routeId 映射问题的根源 | 🔧 补默认值、重新映射 | DQ13 |
| E22 | 浮点精度问题，单位未说明 | `0.11169799999999999` | 比较时出错；单位不明确 | 🔧 四舍五入；📝 单位假设 | — |
| E23 | `calendar` 只对下载当天有效 | Ipoh：start = end = 20261005 | 必须每天保存快照 | 📝 | 难点 D3 |
| E24 | 名称重复、站点可能按路线重复 | Ipoh：short_name = long_name；`stop_id` 为"名称 + 代码"，17 条路线有 2079 个站点 | 站点维度膨胀 | 📝（不在范围内） | — |
| E25 | 文件未按顺序排列 | Ipoh `stop_times.txt` 第一行 `stop_sequence = 25` | 依赖文件顺序的逻辑会出错 | 🔧 按 `trip_id, stop_sequence` 排序 | DQ16 |
| E26 | `route_type` 疑似分类错误 | KTMB Komuter 线路 `route_type = 0` | 交通方式分类出错 | 📝（不在范围内） | — |
| E27 | 有距离字段但没有形状文件 | KTMB `stop_times` 有 `shape_dist_traveled`，没有 `shapes.txt` | | 📝（不在范围内） | — |
| E28 | 联系信息格式不统一 | 同一号码 `60378852585` 与 `03-7885-2585`；http 与 https 混用 | 次要，但能说明各数据由不同系统产生 | 📝 | — |
| E29 | 字段为空 | rapid-bus-kl `trip_headsign`、`stop_headsign` | 缺少方向描述 | 📝 用终点站名补充 | — |
| E30 | `trips` 与 `frequencies` 行数不一致 | rapid-bus-kl：2097 与 2094 | 可能有班次没有频率定义 | 🟡 | DQ15 |
| E31 | 数字 `stop_id` 跨运营商冲突风险 | 7 位、8 位、5 位数字 | 合并后主键冲突 | 🔧 代理键 = 运营商 + 原始 ID | 设计决定 |
| E32 | 版本有效期在项目期间到期 | feeder 2026-11-13/15；rail 2026-12-31；kl 2027-03-31 | 必须版本化 | 🔧 SCD2 | 难点 D3 |
| E33 | 服务组合异常 | mrtfeeder `26100203` 为 星期一 + 周末；`calendar_dates` 在 2026-11-09 移除平日服务 | 计划班次数计算错误 | 🟡 待 V04 确认 | — |

### 5.3 辅助数据源

| ID | 问题 | 来源 | 处理 | 规则 |
|---|---|---|---|---|
| E34 | 天气预报文字只有马来文，是固定枚举 | 官方文档 | 🔧 映射表；出现新值时📊 | DQ22 |
| E35 | 天气地点没有坐标；记录没有发布时间 | 官方文档 | 🔧 地点映射表；用采集时间代替发布时间 | DQ23 |
| E36 | 客流数据混有 `A0: All Stations` 汇总行 | 官方样本 | 🔧 分离汇总行与明细行 | DQ24 |
| E37 | 站点字段是"代码: 名称"组合字符串 | 官方样本 `AG01: Sentul Timur` | 🔧 拆分成代码和名称 | DQ27 |
| E38 | `date` 列实际是日期时间字符串 | 官方样本 `2026-10-13 00:00:00` | 🔧 转为日期 | — |
| E39 | 客流文件按年份命名，并且每天整份覆盖 | 官方 URL `rapidrail_2026_daily.parquet` | 🔧 文件名按年份动态生成；增量识别 | DQ26 |
| E40 | 人口表混合多个切片，单位是千人且为浮点数 | 官方样本与变量定义 | 🔧 只取 overall 切片，乘以 1000 | DQ29 |
| E41 | 公共假期没有官方 API | 你的查证 | 🔧 dbt seed 人工维护 | DQ28 |

---

## 6. 外部辅助数据源评估

### 6.1 天气预报（MET Malaysia）

#### 6.1.1 官方结构 ✅

- **端点**：`GET https://api.data.gov.my/weather/forecast`
- **更新**：每天一次，提供 7 天预报
- **支持**：标准查询参数，嵌套字段用双下划线

```json
{
  "location": {
    "location_id": "Ds001",
    "location_name": "Langkawi"
  },
  "date": "1957-08-31",
  "morning_forecast": "Hujan di satu dua tempat",
  "afternoon_forecast": "Ribut petir di satu dua tempat",
  "night_forecast": "Tiada hujan",
  "summary_forecast": "Ribut petir di satu dua tempat",
  "summary_when": "Petang",
  "min_temp": 26,
  "max_temp": 32
}
```

（`1957-08-31` 是文档中的占位日期。）

| 字段 | 类型 | 说明 |
|---|---|---|
| `location_id` | string | 格式 `AA000`；前缀表示地点类型：`St` 州、`Rc` 休闲中心、`Ds` 县、`Tn` 镇、`Dv` 省（Division） |
| `location_name` | string | 地点名称 |
| `date` | date | 预报的目标日期 |
| `morning_forecast` / `afternoon_forecast` / `night_forecast` | string | 早、午、晚三个时段的预报 |
| `summary_forecast` | string | 当天总结 |
| `summary_when` | string | 总结所描述的时段 |
| `min_temp` / `max_temp` | integer | 摄氏度 |

#### 6.1.2 预报文字映射表（设计为 dbt seed：`seed_weather_forecast_map.csv`）

我设计了一个严重程度等级（0 到 5），用于分析和排序：

| 马来文原文 | 官方英文 | 类别 | 严重程度 | 范围 | 区域 |
|---|---|---|---|---|---|
| `Tiada hujan` | No rain | no_rain | 0 | — | — |
| `Berjerebu` | Hazy | haze | 0（另设 `is_haze` 标记） | — | — |
| `Hujan di satu dua tempat` | Isolated rain | rain | 1 | isolated | — |
| `Hujan di satu dua tempat di kawasan pantai` | Isolated rain over coastal areas | rain | 1 | isolated | coastal |
| `Hujan di satu dua tempat di kawasan pedalaman` | Isolated rain over inland areas | rain | 1 | isolated | inland |
| `Hujan di beberapa tempat` | Scattered rain | rain | 2 | scattered | — |
| `Hujan` | Rain | rain | 2 | general | — |
| `Ribut petir di satu dua tempat` | Isolated thunderstorms | thunderstorm | 3 | isolated | — |
| `Ribut petir di satu dua tempat di kawasan pantai` | Isolated thunderstorms over coastal areas | thunderstorm | 3 | isolated | coastal |
| `Ribut petir di satu dua tempat di kawasan pedalaman` | Isolated thunderstorms over inland areas | thunderstorm | 3 | isolated | inland |
| `Ribut petir di beberapa tempat` | Scattered thunderstorms | thunderstorm | 4 | scattered | — |
| `Ribut petir di beberapa tempat di kawasan pedalaman` | Scattered thunderstorms over inland areas | thunderstorm | 4 | scattered | inland |
| `Ribut petir` | Thunderstorms | thunderstorm | 5 | general | — |

派生字段：`is_wet = 严重程度 ≥ 1`，`is_thunderstorm = 严重程度 ≥ 3`。

**`summary_when` 映射**：

| 原文 | 英文 | 覆盖时段 |
|---|---|---|
| `Pagi` | Morning | 早 |
| `Petang` | Afternoon | 午 |
| `Malam` | Night | 晚 |
| `Pagi dan Petang` | Morning and Afternoon | 早 + 午 |
| `Pagi dan Malam` | Morning and Night | 早 + 晚 |
| `Petang dan Malam` | Afternoon and Night | 午 + 晚 |
| `Sepanjang Hari` | Throughout the Day | 全天 |

**时段到小时的映射（项目假设，MET 没有官方定义）**：早 06:00–11:59，午 12:00–18:59，晚 19:00–05:59。这个假设要写进论文的假设与局限部分，并可以在敏感性分析中调整。分析时**优先使用三个分时段字段**，`summary_*` 只作补充。

#### 6.1.3 坑点

| # | 坑点 | 处理 |
|---|---|---|
| 1 | **只有马来文**。文字本身是 ASCII，没有编码问题，风险在于上游可能出现**文档没列出的新值**、大小写或空格变化 | 规范化（去空格、统一大小写）后再映射；未知值告警（DQ22） |
| 2 | **这是预报，不是实际观测** | 研究问题措辞要准确："预报有雷暴的时段"；实际观测天气作为 FYP 2 可选（§6.1.6） |
| 3 | **没有历史接口**（💡 推测，需 V01 确认） | 从 P0 开始每天归档 |
| 4 | **记录中没有发布时间** | 用采集时间作为发布时间；保存每次快照 |
| 5 | **同一个目标日期会被预报 7 次**（提前 0 到 6 天），而且每天可能修订 | 建模时保留"预报提前天数"（lead time） |
| 6 | **地点没有坐标** | 建 `seed_met_location_map.csv`，把巴生谷的地点对应到县和州 |
| 7 | 地点名称与 DOSM 县名可能不一致 | 人工映射表（实体对齐的一部分） |
| 8 | `contains` 等过滤是区分大小写的 | 使用 `icontains` 或先确认实际名称 |
| 9 | 默认返回条数、是否分页未知 | V01 实测；必要时按地点类型分次请求 |
| 10 | 更新时间（每天几点）未知 | 每天采集两次，用内容哈希去重 |

#### 6.1.4 采集设计

| 项目 | 设计 |
|---|---|
| 频率 | 每天两次（例如 07:00 和 19:00），用内容哈希去重，同时捕捉当天的修订 |
| 请求 | 💡 视 V01 结果：一次取全部，或者按 `St` 和 `Ds` 前缀分 2 到 3 次请求，每次间隔 ≥ 20 秒 |
| 范围 | 巴生谷相关的州（W.P. Kuala Lumpur、Selangor、W.P. Putrajaya）及其县、镇（具体 `location_id` 待 V01 确认） |
| Bronze | `bronze/weather_forecast/date=YYYY-MM-DD/fetched_at=HHMMSS.json`，原样保存 |
| 部署 | 放在 24 小时运行的云端采集服务里，和 GTFS 一起 |

#### 6.1.5 建模与对齐

| 层 | 表 | 粒度 |
|---|---|---|
| Silver | `weather_forecast_snapshot` | 地点 × 目标日期 × 采集时间 |
| Gold | `dim_weather_daily` | 地点 × 目标日期，取**当天早上采集的预报**（提前 0 天）作为"最佳可得预报" |
| Gold（可选） | `fct_weather_forecast` | 地点 × 目标日期 × 提前天数，用于分析预报的稳定性 |

**空间对齐**：
- **MVP**：州级。每个站点按坐标判断属于 W.P. Kuala Lumpur、Selangor 还是 Putrajaya，关联州级预报。
- **P3**：县级。站点 → 县（需要县界数据，V11）→ MET 的 `Ds` 地点（通过映射表）。

**时间对齐**：`fct_stop_arrival` 的本地小时 → 所属时段（早、午、晚）→ 对应时段的预报类别和严重程度。

#### 6.1.6 决定

> ✅ **采用。P0 起每天归档，P3 建模和分析。**
>
> - **理由**：没有历史接口，越早开始归档越好；采集成本极低（每天 2 到 3 次请求）；支持业务问题"天气与准点率"；马来文映射和预报快照建模都是很好的数据工程话题（枚举标准化、快照事实表、提前天数建模）。
> - **实际观测天气**（例如 Open-Meteo 历史接口）：可以弥补"预报不等于实际"的局限，还能顺便计算预报准确率。但它会增加一个外部依赖，**放到 FYP 2（6 到 8 月）作为可选**，需要先完成验证（条款、延迟、粒度）。

### 6.2 天气警告

- **端点**：`/weather/warning`（另有 `/weather/warning/earthquake`，与本项目无关）
- **结构**：`warning_issue`（`issued`、`title_bm`、`title_en`）、`valid_from`、`valid_to`、`heading_en`、`text_en`、`instruction_en`、`heading_bm`、`text_bm`、`instruction_bm`
- **更新**：有需要时发布
- **坑点**：受影响的地区写在自由文本里，要从文本中解析地区（接近自然语言处理），成本高；双语字段内容可能不完全对应。

> 🟡 **只归档，不分析。** 每小时采集一次存进 Bronze（每天 24 次请求，在限额之内）。如果 FYP 2 有时间，可以把"雷暴警告生效期间"作为一个事件标记加入天气分析；否则列为 Future Work。

### 6.3 公共假期

#### 6.3.1 现状 ✅
data.gov.my **没有**公共假期的官方 API，只有第三方网站或 Python 库等非官方渠道。

#### 6.3.2 方案比较

| 方案 | 优点 | 缺点 |
|---|---|---|
| 在管道中实时调用第三方 API | 自动 | 外部依赖、可用性和条款不确定、来源不权威 |
| 在管道中直接使用 Python `holidays` 库 | 免费，支持马来西亚及各州 | 💡 伊斯兰节日按月相决定，库里的日期可能与政府最终公布的不同；**临时假期**（例如大选后、体育赛事后宣布的假期）无法提前预测 |
| **dbt seed + 人工核对**（推荐） | 权威、可审计、有版本历史、可测试 | 需要每年维护 |

#### 6.3.3 决定：dbt seed

> ✅ **采用，MVP 阶段就加入 `dim_date`。**

**做法**：
1. 先用 Python `holidays` 库生成 2026 到 2027 年 W.P. Kuala Lumpur、Selangor、W.P. Putrajaya 的假期草稿
2. 与政府正式公布的年度假期列表**逐条核对**，记录来源网址
3. 存成 `seeds/seed_public_holidays.csv`，提交到 Git（每次修改都有记录）
4. 临时假期公布时，手动追加一行

**Seed 结构**：

| 列 | 例子 | 说明 |
|---|---|---|
| `holiday_date` | 2026-11-09 | |
| `state_code` | SGR / WPKL / WPPJ | 各州假期不同 |
| `holiday_name_en` | Deepavali (replacement) | |
| `holiday_name_ms` | Cuti Ganti Deepavali | |
| `holiday_type` | national / state / replacement / adhoc | |
| `source_url` | 官方公告网址 | 可追溯 |
| `verified_on` | 2026-12-15 | 核对日期 |

**为什么要分州**：巴士路线跨越 KL 和 Selangor，而两地假期不同，例如联邦直辖区日（2 月 1 日）只在 W.P. 放假，雪兰莪苏丹寿辰只在 Selangor 放假。`dim_date` 设计为 `is_holiday_wpkl`、`is_holiday_selangor`、`is_holiday_putrajaya`、`is_holiday_any` 四个字段。

**自动提醒**（DQ28）：dbt 测试检查 seed 是否覆盖到"今天 + 90 天"，覆盖不足时测试失败，提醒你更新下一年的假期。

**可选**：学校假期（教育部校历）会影响客流，可以用同样方法建 `seed_school_holidays.csv`，P3 再决定。

### 6.4 Rapid Rail OD 每日客流（巴生谷）

#### 6.4.1 官方结构 ✅

- **名称**：Daily Origin-Destination Ridership: Rapid Rail (KV)
- **内容**：覆盖巴生谷整个 Rapid Rail 网络的每日起讫点客流
- **来源**：Rapid 闸机进出站（tap-in-tap-out）的匿名交易数据
- **规模**：官方说明 2023 年起每年的完整数据都超过 Excel 行数上限（1,048,576），建议使用 Parquet
- **更新**：每天。例如 "Data as of 13 Oct 2026, 23:59"，"Last updated 14 Oct 2026, 19:03"，"Next update 15 Oct 2026, 22:00"
- **下载**：
  - CSV：`https://storage.data.gov.my/transportation/rail/rapidrail_2026_daily.csv`
  - Parquet：`https://storage.data.gov.my/transportation/rail/rapidrail_2026_daily.parquet`

| 字段 | 类型 | 说明 |
|---|---|---|
| `date` | Date | YYYY-MM-DD（样本中实际是 `2026-10-13 00:00:00`） |
| `origin` | String | 起点站 |
| `destination` | String | 终点站 |
| `ridership` | Integer | 从起点到终点的出行次数 |

**样本**：

| origin | destination | date | ridership |
|---|---|---|---|
| A0: All Stations | AG01: Sentul Timur | 2026-10-13 00:00:00 | 5281 |
| AG01: Sentul Timur | A0: All Stations | 2026-01-01 00:00:00 | 2914 |
| AG01: Sentul Timur | AG06: Bandaraya | 2026-04-05 00:00:00 | 259 |

#### 6.4.2 语义解读

| 行类型 | 含义（💡 根据样本推断） | 用途 |
|---|---|---|
| `origin = A0`，`destination = X` | 所有起点到 X 的总和 = **X 站的出站量** | 站点出站 |
| `origin = X`，`destination = A0` | X 到所有终点的总和 = **X 站的进站量** | 站点进站 |
| `origin = X`，`destination = Y` | X 到 Y 的出行次数 | OD 矩阵 |
| `origin = A0`，`destination = A0`（如果存在） | 全网总量 | 网络总量 |

#### 6.4.3 坑点

| # | 坑点 | 处理 |
|---|---|---|
| 1 | **汇总行（A0）与明细行混在一起**，直接求和会重复计算 | Silver 层拆成 `rail_od_daily`（明细）和 `rail_station_daily`（进出站汇总）两张表 |
| 2 | 站点是"代码: 名称"组合字符串 | 拆分为 `station_code` 和 `station_name`；**用代码做键**，因为站名可能更改 |
| 3 | 换乘站可能有多个代码（不同线路） | 通过 `dim_location` 合并为同一个物理站点 |
| 4 | `date` 实际是日期时间字符串 | 转换为日期 |
| 5 | **文件按年份命名**，2027 年 1 月 1 日后会有新文件 | 文件名由年份动态生成；跨年时两个文件都要处理（典型的跨年 bug 来源） |
| 6 | **每天整份覆盖**，不是只追加新的一天 | 用文件哈希判断是否更新；按 `(date, origin, destination)` 做 MERGE；记录被修订的历史行数 |
| 7 | 约有 1 天延迟 | 新鲜度 SLO 按"T+1"设计 |
| 8 | 💡 客流为 0 的 OD 组合可能直接不出现 | V09 确认；计算时补 0 |
| 9 | 💡 明细之和是否等于 A0 汇总值 | **对账测试**：每站 `Σ 明细 = A0 行`（DQ25），V09 先确认 |
| 10 | **只有轨道，没有巴士客流** | 无法直接衡量巴士需求，只能作为接驳巴士所服务 MRT 站的需求代理 |
| 11 | 计算的是出行次数，不是人数 | 论文中准确表述 |
| 12 | 💡 是否包含 BRT Sunway Line 不确定（BRT 在巴士 GTFS 中） | V09 检查站点代码列表 |

#### 6.4.4 可以支持的分析

| 分析 | 粒度 | 说明 |
|---|---|---|
| **需求加权可靠性** | 路线 × 日 | 接驳路线所服务的 MRT 站客流越大，该路线的不准时影响越大：`优先级 = (1 − OTP) × 站点进站量`，直接服务于规划人员"先改善哪里" |
| 可靠性与客流的关联 | MRT 站 × 日 | 接驳巴士准点率与该站进站量的相关性（描述性，不推断因果） |
| 假期和天气对客流的影响 | 站 × 日 | 与假期 seed、天气预报关联 |
| RQ4 附加工作负载（可选） | | 大表 JOIN（客流 × 到站事件）作为额外的基准测试场景 |

**接驳关系的建立**：mrtfeeder 的 `trip_headsign`（例如 `MRT SURIAN - SEK 11 KOTA DAMANSARA`）和终点站坐标，与 rapid-rail-kl 的 `stops.txt` 做名称匹配加距离匹配，生成 `bridge_route_rail_station`（路线 ↔ MRT 站）。

#### 6.4.5 决定

> ✅ **采用，作为次核心数据源。在 FYP 1 中后段（MVP 完成之后）接入。**
>
> **理由**：
> 1. **数据工程价值高、成本低**：一天一个 Parquet 文件，却能演示**历史回填（2023 年起）、增量识别、Iceberg MERGE、汇总行拆分、对账测试、跨年文件切换**，这些都是面试常问的批处理问题
> 2. **真实的数据量**：每年超过 100 万行，与 GPS 数据合起来让湖仓更有说服力
> 3. **业务价值**：需求加权可靠性让项目从"测量"走向"决策支持"
> 4. **与已有维度契合**：站点代码很可能可以直接关联 rapid-rail-kl 的 `stop_id`
> 5. **没有时间压力**：数据有完整历史，**不需要现在开始采集**，可以等 MVP 完成后再一次性回填
>
> **限制**：只有轨道、日粒度，所以不作为可靠性指标本身的输入，只作为需求背景和关联分析。

### 6.5 行政区人口（DOSM）

#### 6.5.1 官方结构 ✅

- **名称**：Population Table: Administrative Districts
- **内容**：2020 到 2026 年，按县、性别、年龄组、族群划分的人口
- **更新**：每年。最近更新 2026-10-07；下次更新 2027-10-31
- **下载**：
  - CSV：`https://storage.dosm.gov.my/population/population_district.csv`
  - Parquet：`https://storage.dosm.gov.my/population/population_district.parquet`

| 字段 | 类型 | 说明 |
|---|---|---|
| `date` | Date | 每年 01-01 |
| `state` | Categorical | 16 个州之一 |
| `district` | Categorical | 160 个行政县之一；Perlis 和三个联邦直辖区没有下级划分，县名等于州名 |
| `sex` | Categorical | `both`、`male`、`female` |
| `age` | Categorical | `overall` 或 5 岁一组（0-4 到 85+） |
| `ethnicity` | Categorical | `overall`、`bumi_malay`、`bumi_other`、`chinese`、`indian`、`other_citizen`、`other_noncitizen` |
| `population` | Float | **单位：千人** |

**样本**：

| state | district | date | sex | age | ethnicity | population |
|---|---|---|---|---|---|---|
| W.P. Kuala Lumpur | W.P. Kuala Lumpur | 2024-01-01 | both | overall | overall | 2067.5 |
| W.P. Kuala Lumpur | W.P. Kuala Lumpur | 2022-01-01 | both | 0-4 | overall | 115.4 |
| W.P. Kuala Lumpur | W.P. Kuala Lumpur | 2022-01-01 | both | overall | chinese | 730.7 |
| Selangor | Gombak | 2020-01-01 | both | overall | overall | 942.4 |

#### 6.5.2 坑点

| # | 坑点 | 处理 |
|---|---|---|
| 1 | **一张表混合了多个切片**（总计、按性别、按年龄、按族群）。直接按县求和会把人口算好几倍 | 只取 `sex = both`、`age = overall`、`ethnicity = overall`（DQ29） |
| 2 | 单位是千人，而且是浮点数 | 乘以 1000，四舍五入 |
| 3 | 💡 2020 年是普查年，之后的年份可能是估算值 | 论文中说明 |
| 4 | W.P. Kuala Lumpur 和 Putrajaya 的县名等于州名，粒度比 Selangor 的县粗 | 不同地区的对比要说明粒度差异 |
| 5 | 县名与 MET 天气地点名称可能不一致 | 映射表 |
| 6 | **需要"站点 → 县"的映射**，也就需要县界地理数据 | 依赖 V11 |
| 7 | 族群、年龄等敏感维度 | **不使用**，避免不必要的敏感分析 |

#### 6.5.3 决定

> 🟡 **可选。P3 与 `dim_location` 一起做；如果找不到可用的县界数据，就放弃，列入 Future Work。**
>
> **理由**：
> - 能提供的只是"每 10 万居民的服务量"这类背景指标，对核心研究问题帮助有限
> - 真正的成本不在下载，而在"站点 → 县"的空间映射，而这一步与县级天气共用同一个依赖（县界数据）。**如果县界数据可得**，两者可以一起做，边际成本很低；**如果不可得**，不值得为它投入时间
> - 实现方式很简单：`seed` 或一次性下载，取最新年份的 overall 行，作为 `dim_location` 的属性

### 6.6 其他已知但不采用的数据源

| 数据源 | 原因 |
|---|---|
| KTMB 客流 | KTMB 不在范围内 |
| 全网汇总客流 | 有滞后，而且粒度太粗 |
| 选区人口表（停留在 2022/2024 年） | 粒度与本项目无关，且未更新 |
| 全国和州级人口表 | 粒度太粗，县级表已包含所需信息 |
| 洪水警告 `/flood-warning` | 尚未评估。巴生谷的突发洪水确实会影响巴士，是有意思的 Future Work |
| KTMB、BAS.MY 的 GTFS | 不在核心范围；BAS.MY（例如 Ipoh）可作为"多运营商标准化"的可选扩展 |
| Penang、Kuantan 的 GTFS | 官方已知 ID 问题，排除 |

---

## 7. 采集设计与请求预算

### 7.1 各数据源的采集方式

| 数据源 | 方式 | 时间 | 每天请求数 | Bronze 路径 | 自然键 | 变更检测 |
|---|---|---|---|---|---|---|
| GTFS-RT kl | OpenAPI | 每 30 秒 | 2880 | `bronze/gtfs_rt/feed=rapid-bus-kl/date=/hour=/<UTC时间>.pb` | `(feed, vehicle_id, timestamp)` | — |
| GTFS-RT feeder | OpenAPI | 每 30 秒（与 kl 错开 15 秒） | 2880 | `bronze/gtfs_rt/feed=rapid-bus-mrtfeeder/...` | 同上 | — |
| GTFS Static × 3 | OpenAPI | 每天 04:00，每个间隔 ≥ 20 秒 | 3 | `bronze/gtfs_static/feed=/date=/gtfs.zip` + `.sha256` | 文件哈希 | 哈希变化 → 新版本（SCD2） |
| 天气预报 | OpenAPI | 每天 07:00、19:00 | 2–6 | `bronze/weather_forecast/date=/fetched_at=.json` | `(location_id, date, 采集时间)` | 内容哈希 |
| 天气警告 | OpenAPI | 每小时 | 24 | `bronze/weather_warning/date=/hour=.json` | `(issued, title_en, valid_from)` | 内容哈希 |
| Rapid Rail OD 客流 | 文件下载 | 每天 23:00（官方 22:00 更新之后） | 1 | `bronze/ridership_rapidrail/year=2026/downloaded=YYYY-MM-DD/rapidrail_2026_daily.parquet` + `.sha256` | `(date, origin, destination)` | 文件哈希 + 最大日期 |
| 行政区人口 | 文件下载 | 每月检查一次 | ≈ 0 | `bronze/population_district/downloaded=/population_district.parquet` | `(state, district, date, sex, age, ethnicity)` | 文件哈希 |
| 公共假期 | dbt seed（Git） | 每年 + 临时公告 | 0 | `seeds/seed_public_holidays.csv` | `(holiday_date, state_code)` | Git 历史 |

### 7.2 限流预算

| API 类别 | 限额 | 本项目用量 | 余量 |
|---|---|---|---|
| GTFS Realtime | 4 次/分钟 | **4 次/分钟**（2 个 feed × 2） | **0**，不能立即重试 |
| GTFS Static | 4 次/分钟 | 每天 3 次 | 充足 |
| Weather | 4 次/分钟 | 每天约 30 次 | 充足 |
| `storage.data.gov.my` / `storage.dosm.gov.my` 文件下载 | 💡 静态文件托管，可能不受 API 限流 | 每天约 1 次 | 充足 |

> [!WARNING]
> 如果 V02 发现限额是**按 IP 全局计算**（所有 API 共用 4 次/分钟），那么 Static 和天气的请求必须"借用" Realtime 的时间槽，也就是在那一分钟跳过一次 GTFS-RT 采集，并在 `fct_feed_health` 中标记为"计划内跳过"。

### 7.3 部署分工（已决定使用免费云 VM）

| 位置 | 运行内容 | 原因 |
|---|---|---|
| **免费云 VM**（24 小时） | 只运行**轻量采集服务**：GTFS-RT、GTFS Static、天气预报、天气警告、客流文件下载；写入 VM 本地磁盘 | 免费 VM 内存很小（通常约 1 GB），不能运行 Kafka 或 Spark |
| **本地电脑**（16 GB） | 定期把 VM 上的文件同步回本地 MinIO（Bronze）；运行 Kafka、Spark、Iceberg、ClickHouse、dbt、Airflow | 计算组件都在本地 |
| **流处理** | 实验时从 Bronze **回放**到 Kafka；演示时在本地临时启动一个采集实例直接写 Kafka | 云端不运行 Kafka |

**磁盘**：GPS 原始数据每天约 50–60 MB，6 个月约 10 GB。免费 VM 的磁盘额度有限（以官方条款为准），需要**定期同步回本地后清理 VM 上的旧文件**，同步前先比对文件数和哈希，确认没有遗漏。客流的历史回填（2023 年起）直接在本地完成，不经过 VM。

---

## 8. 辅助数据源的数据质量规则

> 接在设计书中 GTFS 相关的 DQ01–DQ21 之后。

| ID | 对象 | 规则 | 维度 | 处理 |
|---|---|---|---|---|
| DQ22 | 天气预报 | 规范化后的预报文字必须存在于映射表中，出现新值时告警 | 有效性 | 📊 + 🟡 |
| DQ23 | 天气预报 | 每个目标地点每天至少有一份预报；`min_temp ≤ max_temp` | 完整性、有效性 | 🟡 |
| DQ24 | 客流 | A0 汇总行与明细行分离；明细表中不能出现 `A0` | 一致性 | 🔧 |
| DQ25 | 客流 | 对账：每站每天 `Σ 明细 = A0 汇总行`（容许误差待 V09 确定） | 一致性 | 📊 |
| DQ26 | 客流 | `(date, origin, destination)` 唯一；`ridership ≥ 0`；最新日期不早于"今天 − 2 天" | 唯一性、有效性、时效性 | 🔴 / 📊 |
| DQ27 | 客流 | 站点代码能关联到 rapid-rail-kl 的站点（覆盖率 ≥ 95%，未匹配的列出） | 一致性 | 📊 |
| DQ28 | 公共假期 | `(holiday_date, state_code)` 唯一；seed 覆盖到"今天 + 90 天" | 唯一性、完整性 | 📊（失败时提醒更新） |
| DQ29 | 人口 | 只保留 `sex = both`、`age = overall`、`ethnicity = overall`；转换为人数后为正数 | 一致性、有效性 | 🔧 |

---

## 9. 采用决策汇总

| 数据源 | 决定 | 角色 | 采集开始 | 建模阶段 | 一句话理由 |
|---|---|---|---|---|---|
| GTFS-RT kl / feeder | ✅ 核心 | 主事实 | **P0（越早越好）** | MVP | 项目核心；没有历史接口 |
| GTFS Static kl / feeder | ✅ 核心 | 维度（SCD2） | **现在起每周手动下载，P0 后自动每日** | MVP | 时刻表会过期，过期后拿不到 |
| GTFS Static rail | ✅ 采用 | 轨道站点维度 | 同上 | P3 | 接驳分析与客流关联的桥梁 |
| 天气预报 | ✅ 采用 | 环境维度 | **P0** | P3（州级 MVP，县级可选） | 没有历史；成本低；有建模话题 |
| 天气警告 | 🟡 只归档 | 事件 | P0 | Future Work | 地区信息在自由文本中，解析成本高 |
| 公共假期 | ✅ 采用 | 日期维度（seed） | 不需要采集 | **MVP** | 没有官方 API；seed 权威、可审计、可测试 |
| Rapid Rail OD 客流 | ✅ 次核心 | 次事实 | FYP 1 中后段（一次回填） | FYP 1 中后段 | 批处理技能展示价值高；有完整历史，不急 |
| 行政区人口 | 🟡 可选 | 地区属性 | 需要时一次下载 | P3 或 Future | 价值有限；取决于县界数据 |
| 实际观测天气 | ❓ 待定 | 环境维度 | FYP 2 | FYP 2 可选 | 弥补预报的局限，但增加外部依赖 |

---

## 10. 待验证事项清单（由你执行）

> 按优先级排列。**"写 Proposal 前"** 的项目会影响报告内容；**"写代码前"** 的项目影响实现。

| ID | 事项 | 方法 | 优先级 |
|---|---|---|---|
| **V00** | **每周手动下载三个核心 Static ZIP**（kl、mrtfeeder、rail），按日期命名保存 | 浏览器直接打开端点 | 🔴 **立即开始，持续到 P0 上线** |
| V01 | 天气预报实测：响应结构；默认返回条数、是否分页；巴生谷所有相关地点的 `location_id` 和名称；能否查询过去日期；每天几点更新 | 浏览器打开 `/weather/forecast?limit=5&meta=true`，以及 `?icontains=Kuala Lumpur@location__location_name`、`?contains=St@location__location_id`、`?date_start=2026-09-01@date` | 写 Proposal 前 |
| V02 | 限流规则：按 IP 全局、按类别，还是按 endpoint | 连续快速请求 Realtime 6 次后，立即请求一次 Static 或天气，看是否 429 | 写代码前 |
| V04 | mrtfeeder `calendar_dates` 全部 5 行内容 | 打开文件 | 写 Proposal 前 |
| V05 | rapid-bus-kl `trip_id` 序号：Static 中 `U2500` 路线有哪些 `trip_id`？有没有 `_22`、`_23`？ | 在 `trips.txt` 中搜索 `U2500` | 写代码前 |
| V06 | mrtfeeder 对不上的 `trip_id`：同一天下载 Static 后重新比对，匹配率是否提高；是否出现在 `problematic_trips.csv` | 当天下载 Static 后运行 `check_realtime.py` | 写代码前 |
| V07 | 全天车辆数曲线 | 同一个平日在 08:00、13:00、18:00、23:00 各运行一次 `check_realtime.py` | 写 Proposal 前（用于规模估算） |
| V08 | 速度单位 | 采集服务上线后，统计一天的速度分布 | P0 后 |
| V09 | 客流：2023、2024、2025 年文件是否存在（把 URL 中的 `2026` 改成对应年份）；各年文件大小和行数；不同站点代码数量；代码是否与 rapid-rail-kl 的 `stop_id` 一致；是否包含 BRT；客流为 0 的组合是否省略；明细之和是否等于 A0 行 | 下载 Parquet，用 pandas 检查 | FYP 1 中后段前（也可提前，用于 Proposal 数据章节） |
| V10 | 人口：巴生谷各县的名称列表（W.P. Kuala Lumpur、W.P. Putrajaya、Selangor 下各县） | 下载 Parquet | P3 前 |
| V11 | 有没有开放的**县界 GeoJSON**（data.gov.my 或其他官方来源） | 搜索 data.gov.my 和 DOSM | P3 前（决定人口和县级天气是否采用） |
| V12 | 2026、2027 年 W.P. Kuala Lumpur、Selangor、W.P. Putrajaya 的官方假期列表来源 | 政府官方公告 | MVP 前（2027 年列表通常在前一年下半年公布） |
| V13 | trip updates、service alerts 是否已推出 | 每月看一次 developer.data.gov.my 的 changelog | 持续 |
| V14 | `problematic_trips.csv` 的行数，其中的 `trip_id` 是否出现在 Realtime 中 | 下载并比对 | 写代码前 |

**回报格式**：每项写"结论 + 证据"（截图、返回内容的片段或数字）。

---

## 11. 与论文第 3 章的映射

> 这是通用映射。收到 UTAR 的 IIPSPW、FYP 1、FYP 2 模板后，我会按学校的章节编号重新对应。

| 论文小节（暂定） | 本文档内容 |
|---|---|
| 3.x Data Source Identification | §1 总览；§3.1、§4.1 端点清单；§6 各辅助数据源的官方结构 |
| 3.x API Characteristics and Constraints | §2 OpenAPI 机制（限流、响应格式、查询参数）；§7.2 限流预算 |
| 3.x Data Profiling | §3.4 各运营商样本剖析；§3.5 跨运营商对照；§3.6 排班模式；§4.4–§4.7 实测、字段剖析、ID 匹配、规模估算 |
| 3.x Data Quality Assessment | §5 异常证据目录（E01–E41）；§8 辅助数据质量规则 |
| 3.x Data Source Selection and Justification | §6 各数据源的评估与决定；§9 决策汇总 |
| 3.x Assumptions and Limitations | 天气时段与小时映射的假设；预报与实际观测的差别；客流只有轨道；速度单位推断；行数统计误差 |
| 附录 | 实测截图（10/5、10/11）；样本文件；`problematic_trips.csv`；映射表（天气、路线、站点）；假期 seed |

> [!TIP]
> 建议在项目仓库里建一个 `docs/evidence/` 文件夹，保存两次实测的截图和 CSV、Static 样本 ZIP、官方文档页面的 PDF 存档（官方文档会更新，要保留你引用时的版本）。论文引用证据时可以直接指向这些文件。
