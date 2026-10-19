# 任务：产出 `fyp_project_design_v0.4_final.md`（终极整合版项目设计书）

> 本文件是给 Claude Opus 的任务说明（在 Claude Code 里读取本文件后执行）。
> 旧版 prompt 依赖"这个聊天室的历史对话"，已作废；本版所有信息都来自仓库文件，**不需要也不应该假设任何聊天历史**。
> 旧版 prompt 保留在 git 历史中（`git log -- docs/fyp-design/Opus_Design_Prompt.md`）。

---

## 0. 角色与总目标

你是我的 FYP 首席架构师与学术顾问。我是 UTAR FICT 学生，做这个 FYP 的**首要目的是找数据工程（DE）实习和正职**。

请把已有的设计碎片合并、修订成**一份**最终基线设计书：`docs/fyp-design/fyp_project_design_v0.4_final.md`。

**本次任务只产出这一份设计书。** 不要写 Proposal / FYP 报告正文，不要写采集或管道代码，不要修改 `docs/data-source/data-source-summary.md`（它是已完成的数据源档案，见第 1 节）。

---

## 1. 必读文件与"以谁为准"（冲突时按此顺序裁决）

| 优先级 | 文件 | 角色 |
|---|---|---|
| 1 | `docs/context/my-context.md` | 我的最新决策、学校政策、2027 真实时间线、当前进度。**最高优先级** |
| 2 | `docs/data-source/data-source-summary.md` | 数据源**事实**、实测证据、数据脏点（E01–E13…）、限流约束（§2.3）、辅助数据源采用决策（§9）。这些以它为准，不要重新裁决。**但它的 §7.3"部署分工"是早期的设计决定，不是约束，你可以重新设计**（见第 3 节） |
| 3 | `docs/fyp-design/fyp_project_design_v0.3.md` | **架构与技术栈的唯一依据**（全本地 Docker 湖仓）。取代 v0.2 的 §8、§9、RQ4 |
| 4 | `docs/fyp-design/Job_Market.md` | **工具选型的约束来源**（见第 2 节） |
| 5 | `docs/fyp-design/fyp_project_design_v0.2.md` | 业务、指标、数据质量规则、论文结构的原文基础（见第 3 节） |
| 6 | `docs/context/{proposal,fyp1,fyp2}/guidelines.md` 与 `template.md`，`docs/context/fyp-index.md` | 学校对三份报告的硬性要求（见第 4 节） |
| 7 | `ingestion/collect_gtfs_rt.py`、`scripts/download_gtfs_static.py`、`.github/workflows/*.yml` | **已有的采集原型**，只是参考和可行性证据，**不是约束**（见第 3、5 节） |

> 三份报告（Proposal、FYP1、FYP2）都还没有开始写。`docs/context/proposal/report/` 下的 ch1–ch4、abstract、appendices、references 目前**全是空文件**（0 字节），只是目录骨架；FYP1、FYP2 还没有对应的报告目录。本次**不要往任何报告目录里写内容**，只在设计书里按 **Proposal、FYP1、FYP2 三个阶段**分别说明：该阶段交付什么、对应设计书的哪些章节、哪些内容是上一阶段的延续或扩写（见第 4 节）。

---

## 2. 硬约束：工具选型必须对齐招聘 JD

我做 FYP 是为了找工作，所以**工具选型的第一原则是和 `Job_Market.md` 里 15 家公司的 JD 对齐**：

1. 能用 JD 里高频出现的工具（Kafka、Spark/PySpark、Iceberg、ClickHouse、dbt、Airflow、PostgreSQL、Docker、Git CI/CD、Python、SQL）实现的，**就不要引入 JD 里没出现的工具**。
2. 以 v0.3 的组件清单为准（Kafka KRaft + MinIO + Iceberg + Spark + ClickHouse + dbt + Airflow + PostgreSQL + Metabase/Superset + Prometheus/Grafana）。**不得引入** Redpanda、PostGIS 强依赖、Flink、Delta Lake、Hudi 等；如果 v0.2 里残留这些，按 v0.3 替换，PostgreSQL 只承担元数据库和 RQ4 对比基线。
3. 设计书里**每一个工具**都要有一行可追溯的理由：它对应 `Job_Market.md` 里哪几家公司的 JD、承担什么真实职责。必要时输出一张"工具 → JD 对标表"。
4. Snowflake、Databricks、Fabric 等在 JD 中出现但不满足"全本地、零成本"的，**不要加入架构**；在"雇主对齐"一节里说明本项目用哪些开源组件覆盖了同类技能（例如 dbt + ClickHouse + Iceberg 对应 Snowflake + dbt + Iceberg 的技能迁移）。
5. 任何偏离 v0.3 或偏离 JD 的工具建议，必须单独列出来让我确认，不要直接写进正文。

---

## 3. 合并规则：以 v0.3 修改 v0.2

- **保留 v0.2 全部精华**：§0–§7（业务场景、利益相关者、痛点、指标体系与公式、21 条数据质量规则、流批范式讨论）和 §11–§13（论文大纲、雇主对齐、SLA/切换演练/实体对齐），内容不删减，只做以下修订：
  - 把 v0.2 里的架构、技术栈、RQ4 实验设计，**整体替换为 v0.3 的版本**（对应 v0.2 的 §8、§9、RQ4）。
  - 清理一切与 v0.3 冲突的遗留（消息队列统一为 Apache Kafka；空间计算统一为 Spark（Haversine/Sedona）+ ClickHouse）。
  - v0.3 里指向 `C:/Users/.../.gemini/...` 的绝对路径链接已失效，改为仓库相对路径。
  - 按 `data-source-summary.md` 的数据源决策更新范围：天气预报、公共假期、Rapid Rail OD 客流（次核心）、行政区人口（可选）的采用方式、粒度、清洗规则，以及 E01–E13 脏点对应的数据质量规则编号，保持一致。
- **采集层（Ingestion）由你来设计，不要被现有代码绑住。** 早期设计（v0.3）是把采集、Kafka、MinIO 作为一个整体来做；后来因为我的电脑不能 24 小时开机，才临时写了一个轻量原型（见第 5 节）。请你从头判断最合理的采集架构，包括：
  - 采集服务运行在哪里（免费云 VM 还是本地）、`.pb` 原始文件先落在哪里（VM 本地磁盘、直接写 MinIO、还是其他）、如何同步到 Bronze；
  - Kafka 和 MinIO 在采集链路里扮演什么角色、是否需要部署在云端 VM 上；
  - 采集失败、限流（4 次/分钟，见 summary §2.3）、断档和回放的处理。
  若你的设计要求 ingestion 必须直接写入 MinIO 或 Kafka，就这样设计，**不要因为"已经写了某种脚本"就否定它**。
  设计必须满足这些**事实**约束：我的电脑不能 24 小时开机；采集必须 24 小时不间断，因为数据错过就补不回来；云端只有免费 VM，规格取决于最终能拿到哪一种（Oracle A1 最多 4 核 24 GB、Oracle E2.1.Micro 与 GCP e2-micro 均为约 1 GB 内存），目前尚未拿到，所以请在设计里给出**不同 VM 规格下的方案**；总预算为零成本。
  若你的设计与现有 `ingestion/` 代码或 summary §7.3 不一致，不要修改它们，在"合并说明与待确认事项"里列出哪些需要之后随设计改动。
- 用你的判断列出你在合并中发现的**其他**冲突或遗漏，写进设计书末尾的"合并说明与待确认事项"。

---

## 4. 引入学校的 guideline 和 template，再做一次设计

合并完成后，用学校的要求**再过一遍设计**（不是写报告，是检查设计能否支撑三份报告）：

1. 读 `docs/context/proposal|fyp1|fyp2` 的 guidelines（含评分标准）与 template，了解三份报告各自的章节结构和要求。
   （`CLAUDE.md` 和 `fyp-index.md` 里"只读目标阶段目录、不要跨阶段混用"的规则，针对的是**撰写报告正文**；本任务是跨阶段的设计检查，**允许同时读取三个阶段的文件**，但映射时仍要保持三者章节与评分标准分开，不得混用。）注意：**template 里的示例内容（U-Net、深度学习、图像分割、笔记本规格等）是旧占位例子，与本项目无关，不得照搬**；本项目是 **Development-Based Data Engineering Project**，不能出现 IoT/硬件类内容。
2. 在设计书里新增/重写一节"**与 UTAR 三份报告的映射**"，**必须按 Proposal、FYP1、FYP2 三个阶段分别写，三者平等，不能只写 Proposal**。每个阶段都要写清楚：①该阶段学校要求交付什么（含评分重点）；②本项目在该阶段具体交付什么、做到什么程度；③报告每一章对应设计书的哪些章节、可以直接复用哪些内容；④该阶段的时间节点（见 `my-context.md` 的真实时间线）。
   - **IIPSPW Proposal**（纯文字、无代码；Ch1 Background、Ch2 Literature Review、Ch3 Scope & Objectives、Ch4 Methods）：设计书各部分分别支撑哪一章。注意 guideline 要求的七项内容（purpose、novelty、理论基础、方法、工具、测试评估方法、复杂度论证），设计书要能直接提供素材，尤其是 **novelty 和 project complexity 的论证**。
   - **FYP1**（Ch1 Introduction、Ch2 Literature Review、Ch3 Proposed Method、Ch4 Preliminary Work、Ch5 Conclusion）：Ch4 需要**已有的初步工作成果和可行性证据**，指出哪些已有成果（数据源实测、Static 自动下载、采集脚本、V06/V07 实测等）可以作为证据，哪些要在 FYP1 前补齐。
   - **FYP2**（Ch1–Ch6+，含 System Design、Implementation、Evaluation）：RQ1–RQ4 实验设计分别落在哪几章。
   - 三份报告章节哪些**逐步复用/扩写**，哪些必须**独立重写**，避免跨阶段混淆（遵守 `docs/context/fyp-index.md` 的"不交叉污染"规则）。
3. 如果学校要求暴露了设计里的缺口（例如缺少某类评估、缺少 novelty 论证、范围过大或过小），在"合并说明与待确认事项"里指出，并给出建议，但**不要擅自改变架构**。

---

## 5. 当前真实进度（设计书必须与此一致）

| 项 | 状态（截至 2026-10-20） |
|---|---|
| GTFS Static 自动下载 | **已上线**：`scripts/download_gtfs_static.py` + GitHub Actions 每周一（`backup_gtfs.yml`），按 ZIP 内容指纹判断变化，有变化才存档 |
| GTFS Realtime 采集 | 有一个**轻量原型**，本地测试通过（`ingestion/collect_gtfs_rt.py`：每 30 秒、两个 feed 错开 15 秒、只存原始 `.pb` 到本地磁盘、健康日志 `.jsonl`、systemd 服务文件）。它是为"电脑不能 24 小时开机"临时写的，**可以被你的设计取代**；若架构改变，原型会随之改写 |
| 云端 VM 部署 | **未完成**：选定 Oracle Cloud Always Free（新加坡），A1.Flex 和 E2.1.Micro 目前均 Out of capacity，持续重试；备选 GCP e2-micro。拿到哪种规格会影响采集层方案，设计书不要把 VM 写成已就绪 |
| V06/V07 实测 | **待完成**：一次性 workflow 将在 2026-10-21（周三）马来西亚时间 08:00/13:00/18:00/23:00 运行，结果存 `docs/evidence/realtime_probe/`。**设计书不必等它**：涉及这些数字（匹配率、全天车辆数曲线、规模估算）的地方，沿用 summary 已有估算并标注"待 V06/V07 实测校准"，后续只改个别数字 |
| Proposal / FYP 报告 | 尚未开始写；`proposal/report/` 全是空文件 |
| 核心管道（Spark / Iceberg / ClickHouse / dbt / Airflow / 看板） | 尚未开始 |

时间线以 `my-context.md` 第 3 节为准（休学期 → 2027-01-25 FYP1 → 2027-06-07 FYP2 并开始投实习 → 10 月实习）。

---

## 6. 重写 §10（Roadmap）与 §11（论文结构映射）

- 按 `my-context.md` 的 **UTAR 2027 真实学期时间线**与"**6 月初投实习简历倒逼开发**"的策略，重新制定从现在（2026 年 10 月）到 2027 年 9 月的路线图。
- 明确标注：哪些模块必须在 **2027 年 5 月底前**（投简历前）完成；哪些实验（RQ1–RQ4 的补充对比）可以留到 6–8 月（FYP2 期间）。
- 必须包含：IIPSPW 重写版 Proposal 的提交节点（2027 年 1 月复学前）、采集服务上线（P0）、各里程碑的验收标准。
- v0.2 里"2027 年 4 月提交"的旧假设全部作废。

## 7. §12（待定事项）

硬件（16 GB RAM，Docker Compose 分 profile 启动）和采集环境（免费云 VM，Oracle 优先、GCP 备选）更新为"**已确认决策**"，并把未决的事项（例如 VM 容量、V06/V07 校准）列为待办。

---

## 8. 执行方式（请严格遵守）

1. **先不要写正文。** 先读完第 1 节所有文件，然后只输出一份简短的"**合并计划与冲突清单**"（不超过一页）：你发现了哪些冲突/遗漏、你打算怎么处理、哪些需要我确认。**等我确认后再动手写。**
2. 确认后，把设计书**分章节写入文件** `docs/fyp-design/fyp_project_design_v0.4_final.md`（用 Write/Edit 逐段追加，不要在聊天里整篇输出，文档预计 40–50 KB）。每写完一大块（例如 §0–§7 / §8–§9 / §10–§13 / 报告映射），停下来让我检查，再继续。
3. **不允许出现"此处省略""见前文""同 v0.2"这类偷懒字样**：保留 v0.2 的章节要真的写出来，不是引用。
4. 语言：设计书用中文；技术名词保留英文。
5. 全程不要修改 `docs/data-source/data-source-summary.md`、`ingestion/`、`scripts/`、`.github/` 下的任何文件。发现它们与设计书不一致（包括采集层设计与现有原型的差异），写进"合并说明与待确认事项"，由我之后决定怎么改。

## 9. 验收清单（写完后你自己先逐条自查并汇报结果）

- [ ] 全文无 Redpanda、无 PostGIS 强依赖、无 Flink / Delta Lake / Hudi 作为选型（对比讨论除外）；Postgres 只作元数据与 RQ4 基线。
- [ ] 每个工具都有对应 `Job_Market.md` 的 JD 依据（有对标表）。
- [ ] 采集层有一套完整、自洽的设计，满足第 3 节列出的事实约束，并说明在不同 VM 规格下怎么落地；与现有原型或 summary §7.3 的差异已列入"合并说明与待确认事项"。
- [ ] 路线图基于 2027 真实时间线，没有"2027 年 4 月提交"。
- [ ] v0.2 §0–§7、§11–§13 的内容完整保留（对照 v0.2 的小节标题逐一检查）。
- [ ] 数据质量规则编号（DQ01…）与 `data-source-summary.md` 中引用的编号一致；E01–E13 脏点都有对应处理。
- [ ] 辅助数据源（天气、假期、客流、人口）的采用方式与 summary §9 一致。
- [ ] 有"与 UTAR 三份报告的映射"一节，覆盖 Proposal、FYP1、FYP2，没有跨阶段混淆，没有照搬 template 的旧示例内容。
- [ ] 文末有"合并说明与待确认事项"，诚实列出不确定之处，包括哪些数字待 V06/V07 校准。
