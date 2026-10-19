# Role & Objective
你现在是我的 FYP 首席架构师与学术顾问。在这个聊天室之前的对话中，我们已经深入讨论了马来西亚 `data.gov.my` (GTFS Realtime & Static) 的数据源细节，并先后产出了项目设计的 v0.1/v0.2 以及架构升级版 v0.3。

目前所有的信息分散在历史对话和不同的文档碎片中。在正式开始写代码（包括数据采集脚本）之前，我需要你帮我做一次**全局上下文的彻底收拢与修订**，结合我最新的硬件情况、学校官方时间线、换题政策、求职节奏，以及我最新查证的辅助数据源官方文档，产出两份最终版的核心基线文档（Markdown 格式）。

---

# 1. 我的最新个人与环境决策（用来更新待定项）
1. **本地硬件配置**：我的电脑是 **16GB RAM**。这完全符合你在 v0.3 中设计的 Docker Compose 分 profile 启动的规划（开发时开 `batch` + `serve` 约 7-9GB，完全跑得动）。
2. **数据采集运行环境**：我的个人电脑**不能 24 小时开机**。因此，24小时不间断的采集服务（`ingest` profile）我决定后续部署在**免费的云端常驻虚拟机（如 GCP Always Free `e2-micro` 或 Oracle Cloud Free Tier）**上。
3. **当前阶段重心**：我决定**先不写采集代码**，先把整个项目的上下文、数据源文档和最终版设计书彻底对齐定稿，之后再立刻上线采集服务。

---

# 2. 学校背景、换题政策与报告演进逻辑（极其重要）
我就读于马来西亚 UTAR。学校的 FYP 分为三个阶段：**Preliminary Proposal Report (课程代号 IIPSPW)** $\rightarrow$ **FYP 1** $\rightarrow$ **FYP 2**。

- **换题现状**：我在休学前已经用旧题目（太阳耀斑预测 Deep Learning + DE）通过了 IIPSPW 课程并拿到了分数。但我申请了休学（目前正在休学中），并决定在明年复学进入 FYP 1 时，**正式换题为我们现在设计的这个巴士可靠性数据工程项目**。
- **学校硬性规定**：
  > "For B) Change of area of study and/or project type: For FYP1, the student must submit a new IIPSPW report according to the new project title and area of study..."
- **这意味着**：
  1. 我必须在 **2027年1月/2月复学之前**，重写并提交一份全新的 **Preliminary Proposal Report (IIPSPW report)**。
  2. 这份重交的报告**只走换题审批流程，不再重新算分**（因为课程已经 pass 了），且我**只需要写 Proposal Report 本体**，完全不需要理会 Guideline 里提到的 Class Assessment 和 Presentation。
  3. 这是一份**纯文字报告，不包含任何代码实现**。
  4. **核心演进关系**：虽然重交不算分，但**不能敷衍**！因为 IIPSPW Report、FYP 1 Report 和 FYP 2 Report 的内容是**逐步进化、一脉相承**的（部分章节在 FYP 1 会直接复用、扩写或修改）。我必须现在就把底子打好，直接为 FYP 1 省下大量写报告的时间。
  5. 我稍后会把学校官方的《IIPSPW / FYP1 / FYP2 Guidelines (含 Marking Scheme)》和《Report Templates》发给你，三个报告的结构要求各不相同，你需要严格按学校的章节框架来映射我们的项目内容。

---

# 3. 2027 真实时间线与求职倒逼的开发节奏（关键调整！）
你之前在 v0.2/v0.3 里假设我是 2027年4月提交 FYP，**这个时间线是错的**。请严格按照以下 UTAR 2027 真实校历与我的求职策略，全面重构项目的 **Roadmap（路线图）**：

- **Now – 2027年1月中旬（休学期）**：
  - **学校任务**：完成并提交重写版 Preliminary Proposal Report (IIPSPW)。
  - **技术任务**：定稿所有设计文档；上线云端 24/7 采集服务（P0）；**抢跑开发**：因为我想用尽量完整的 FYP 去找实习，我必须在休学期就开始写核心代码！
- **2027年 1月25日 – 6月6日（Long Sem 1 = FYP 1）**：
  - **学校任务**：撰写大篇幅的 FYP 1 Report + 提交 MVP 系统演示。
  - **技术任务**：为了应对 6 月初的实习投递，我不能按部就班只做个简陋的 MVP。我需要在这个学期内尽可能把 **Spark + Iceberg + ClickHouse + dbt + Airflow + 看板** 的主体架构跑通，甚至提前把部分 P3/P4 的亮点做出来。
- **2027年 6月7日 – 10月17日（Long Sem 2 = FYP 2）**：
  - **求职任务（核心痛点）**：**6月初（Long Sem 2 一开头）我就要开始大规模投递 10 月份的 Intern 简历并参加面试！** 如果这时候我手里只有一个半成品 MVP，简历竞争力会打折扣。所以核心工程亮点必须在 6 月前完成，6月-9月主要是补齐剩余的对比实验（RQ1-RQ4）、完善最终的 FYP 2 论文和准备答辩（9月中下旬提交）。
- **2027年 10月18日 – 2028年 2月6日（Short Sem = Internship）**：
  - 全职实习。实习结束后即毕业，直接靠 **完整的 FYP + Intern 经历** 投递 Junior Data Engineer 正职。

---

# 4. 外部辅助数据源的核实与架构裁决（请你评估并做决定！）

在早期的讨论中，我们曾提到过**天气、公共假期、客流量（Ridership）和人口（Population）**，但在 v0.2/v0.3 中，你只保留了天气和假期（但没写具体 API 细节），并把客流量和人口移除了。

现在，我去 `data.gov.my` 和 OpenDOSM 把这四个辅助数据源的真实情况与官方 Metadata 都查清楚了（附上原文如下）。**请你作为首席架构师，结合我的项目定位、粒度匹配度以及“明年6月前要拿出高竞争力作品投简历”的时间压力，自己做出专业判断**：
1. 针对**天气**和**公共假期**：请核实下面的 API 格式与现状，确认它们在管道中具体该怎么采集、怎么对齐粒度、怎么清洗？
2. 针对**客流量（Rapid Rail OD Ridership）**和**人口（DOSM District Population）**：看到下面的真实字段和样本后，你认为它们**值得纳入我们的项目吗**？（比如是纳入核心范围、还是作为 P3 阶段 `dim_location` 实体对齐的补充分析、还是坚决不采用、继续留在 Out of Scope / Future Work？）请在设计书中给出你的最终决定与理由。

以下是这四份辅助数据的真实官方资料：

### 4.1 公共假期现状
`data.gov.my` 并没有提供马来西亚公共假期的官方 API（只有第三方网站或 Python 库等非官方/外部渠道）。请决定我们该如何优雅地获取并维护这份数据。

### 4.2 MET Malaysia 天气 API 官方文档
```markdown
# Weather API Endpoint
GET [https://api.data.gov.my/weather/forecast](https://api.data.gov.my/weather/forecast)
GET [https://api.data.gov.my/weather/warning](https://api.data.gov.my/weather/warning)
GET [https://api.data.gov.my/weather/warning/earthquake](https://api.data.gov.my/weather/warning/earthquake)

## Frequency of Data Update
- The 7-day general forecast data is updated daily.
- The warning data (including earthquake data) is updated when required.

# 7-day General Forecast (`GET [https://api.data.gov.my/weather/forecast](https://api.data.gov.my/weather/forecast)`)
## Querying Nested Fields
{
    "location": {
        "location_id": "Ds001", // location__location_id (Prefixes: St=State, Rc=Recreation Centre, Ds=District, Tn=Town, Dv=Division)
        "location_name": "Langkawi" // location__location_name
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

## Possible Values for `*_forecast` Fields (Only in Bahasa Melayu)
- `Berjerebu` (Hazy), `Tiada hujan` (No rain)
- `Hujan` (Rain), `Hujan di beberapa tempat` (Scattered rain), `Hujan di satu dua tempat` (Isolated Rain), `Hujan di satu dua tempat di kawasan pantai`, `Hujan di satu dua tempat di kawasan pedalaman`
- `Ribut petir` (Thunderstorms), `Ribut petir di beberapa tempat`, `Ribut petir di beberapa tempat di kawasan pedalaman`, `Ribut petir di satu dua tempat`, `Ribut petir di satu dua tempat di kawasan pantai`, `Ribut petir di satu dua tempat di kawasan pedalaman`

## Possible Values for `summary_when` Field
`Pagi`, `Malam`, `Petang`, `Pagi dan Petang`, `Pagi dan Malam`, `Petang dan Malam`, `Sepanjang Hari`

```

### 4.3 轨道交通客流数据（`Daily Origin-Destination Ridership: Rapid Rail (KV)`）

*(注：Data Catalogue 中没有公开巴士的客流明细，只有 KTMB 火车客流、滞后的全网汇总客流，以及这份每日更新的巴生谷 Rapid Rail 地铁/轻快铁站点级 OD 客流)*

```markdown
## Daily Origin-Destination Ridership: Rapid Rail (KV)
Data as of 13 Oct 2026, 23:59
Daily origin-destination ridership data covering the entire Rapid Rail network in the Klang Valley.

### Samples:
origin | destination | date | ridership
---|---|---|---
A0: All Stations | AG01: Sentul Timur | 2026-10-13 00:00:00 | 5281
AG01: Sentul Timur | A0: All Stations | 2026-01-01 00:00:00 | 2914
AG01: Sentul Timur | AG06: Bandaraya | 2026-04-05 00:00:00 | 259

### How is this data produced & Caveats:
Derived from anonymous transactional data generated by Rapid's tap-in-tap-out system at all rail stations in the Klang Valley. Because the size of the complete dataset for each year since 2023 exceeds the row limit of Microsoft Excel (1,048,576), we recommend working with the parquet files provided.

### Variable definitions:
- `date` (Date): Date in YYYY-MM-DD format
- `origin` (String): The station at which the journey began
- `destination` (String): The station at which the journey ended
- `ridership` (Integer): Number of trips taken from origin to destination

### Update schedule & URLs:
- Last updated: 14 Oct 2026, 19:03 | Next update: 15 Oct 2026, 22:00
- CSV: [https://storage.data.gov.my/transportation/rail/rapidrail_2026_daily.csv](https://storage.data.gov.my/transportation/rail/rapidrail_2026_daily.csv)
- Parquet: [https://storage.data.gov.my/transportation/rail/rapidrail_2026_daily.parquet](https://storage.data.gov.my/transportation/rail/rapidrail_2026_daily.parquet)

```

### 4.4 行政区人口数据（`Population Table: Administrative Districts`）

*(注：Data Catalogue 中另有 Malaysia/States 宏观表，以及停留在 2022/2024 年的选区表，这张 District 表是唯一更新到 2026 年的细粒度表)*

```markdown
## Population Table: Administrative Districts
Data as of 2026. Population at district level from 2020 to 2026, by sex, age group and ethnicity.

### Samples:
state | district | date | sex | age | ethnicity | population
---|---|---|---|---|---|--- 
W.P. Kuala Lumpur | W.P. Kuala Lumpur | 2024-01-01 | both | overall | overall | 2067.5
W.P. Kuala Lumpur | W.P. Kuala Lumpur | 2022-01-01 | both | 0-4 | overall | 115.4
W.P. Kuala Lumpur | W.P. Kuala Lumpur | 2022-01-01 | both | overall | chinese | 730.7
Selangor | Gombak | 2020-01-01 | both | overall | overall | 942.4

### Variable definitions:
- `date` (Date): YYYY-MM-DD format, with MM-DD set to 01-01 (annual data)
- `state` (Categorical): One of 16 states
- `district` (Categorical): One of 160 administrative districts, including the 4 states (Perlis and the 3 Federal Territories) which do not have subdivisions
- `sex` (Categorical): 'both', 'male', or 'female'
- `age` (Categorical): 'overall' or 5-year age groups (0-4, 5-9, ..., 85+)
- `ethnicity` (Categorical): 'overall', 'bumi_malay', 'bumi_other', 'chinese', 'indian', 'other_citizen', 'other_noncitizen'
- `population` (Float): Thousands of people ('000 people)

### Update schedule & URLs:
- Last updated: 07 Oct 2026, 13:00 | Next update: 31 Oct 2027, 12:00
- CSV: [https://storage.dosm.gov.my/population/population_district.csv](https://storage.dosm.gov.my/population/population_district.csv)
- Parquet: [https://storage.dosm.gov.my/population/population_district.parquet](https://storage.dosm.gov.my/population/population_district.parquet)

```

---

# 5. 你现在需要执行的任务（Output Requirements）

请回顾我们在这个聊天室的所有历史对话，并结合上述全部信息，为我生成以下**两份完整、无删减、无省略的 Markdown 文档**：

### 文档一：`gtfs_data_source.md`（数据源全景剖析与实测档案）

请把我们之前零散聊过的所有关于数据源的细节，以及上面第 4 节的外部数据源全部汇总成一份结构化的参考手册（这会直接作为我论文第 3 章的数据源剖析素材），必须包含：

1. `data.gov.my` GTFS 官方 API 的机制说明（端点、更新频率、每分钟 4 次限流机制等）。
2. 各运营商（`rapid-bus-kl`, `rapid-bus-mrtfeeder`, `rapid-rail-kl`, BAS.MY 等）的 Schema 差异与排班模式差异（如 `frequencies.txt` vs 精确班次、`shapes.txt` 列顺序、`service_id` 命名规律）。
3. 数据源的各种坑点。
4. 我们在 10/5 和 10/11 两次实测以及样本检查中发现的所有**真实数据脏点与异常证据**（如 2029年未来时间戳、`routeId` 填成 long_name 导致 0% 匹配、`trip_id` 86%-90% 匹配率、速度单位疑似 km/h、`[object Object]`、轮询重复、AG/AGL 不一致等）。
5. **外部辅助数据源评估与细节**：详细记录上述四类辅助数据（天气、假期、轨道客流、人口）的官方结构与潜在坑点（例如马来文编码、`A0: All Stations` 汇总行、千人单位等），并给出你对它们“是否采用、如何采用”的评估结论。

### 文档二：`fyp_project_design_v0.4_final.md`（终极整合版项目设计书）

请将之前的 `v0.2` 和 `v0.3` 彻底合并，并结合我上面提供的最新信息进行修订：

1. **保留全部精华并融入辅助数据决策**：一字不落地保留 v0.2 的第 0~7 节（业务场景、利益相关者、痛点、指标公式、21条质量规则、流批范式讨论）和第 11~13 节（大纲、雇主对齐、SLA/切换演练/实体对齐），根据你对辅助数据源的裁决更新相关范围与清洗设计；使用 v0.3 的全本地 Docker 湖仓架构（Kafka + MinIO + Iceberg + Spark + ClickHouse + dbt + Airflow）完全替换第 8、9 节及 RQ4 实验设计。
2. **清理遗留冲突**：确保全文所有的消息队列统一为原生的 `Apache Kafka`（彻底清除 v0.2 遗留的 Redpanda 字眼），空间计算统一为 Spark (Haversine/Sedona) + ClickHouse（清除对 PostGIS 的强依赖，Postgres 仅作元数据与 RQ4 对比基线）。
3. **重写第 10 节（Roadmap）与第 11 节（论文结构映射）**：
* 按照我上面给出的 **UTAR 2027 真实学期时间线** 与 **“6月初投实习简历倒逼开发”** 的策略，重新制定从现在（10月休学期）到 2027年9月 的详细开发与写报告路线图。
* 明确标注哪些模块必须在 **2027年5月底前（投简历前）** 完成，哪些实验可以留到 **6月-8月（FYP 2 期间）** 完成。


4. **修正第 12 节（待定事项）**：将硬件（16GB RAM）和采集环境（免费云 VM）更新为“已确认决策”。

---

*(如果字数太长受单次输出限制，请先输出**文档一：`gtfs_data_source.md**` 的完整内容，等我确认后再输出**文档二：`fyp_project_design_v0.4_final.md**`。请确保没有任何“此处省略，见前文”的敷衍字眼！)*
