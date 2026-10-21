# 1. 我的最新个人与环境决策（用来更新待定项）
1. **本地硬件配置**：我的电脑是 **16GB RAM**。这符合 `docs/fyp-design/archive/fyp_project_design_v0.3.md`（现已由 v0.4 取代） 中 Docker Compose 分 profile 启动的规划（开发时开 `batch` + `serve` 约 7-9GB，可以跑得动）。
2. **数据采集运行环境**：我的个人电脑**不能 24 小时开机**。因此，24小时不间断的采集服务（`ingest` profile）我决定后续部署在**免费的云端常驻虚拟机（如 GCP Always Free `e2-micro` 或 Oracle Cloud Free Tier）**上。
3. **当前阶段重心（2026-10-20 更新）**：采集代码**已经开始写，不再是"先不写"**。当前状态：
   - **GTFS Static 每日检查已上线**（2026-10-21 起）：`scripts/download_gtfs_static.py` + GitHub Actions（`.github/workflows/backup_gtfs.yml`，每天 04:17 MYT），按文件、按内容哈希去重，存到 `data/raw/gtfs_static/<category>/`（`blobs/` + `snapshots.jsonl`）。之前是每周一次、整包指纹，已发现会漏掉真实修改并产生伪版本（summary §3.7.1）。
   - **GTFS Realtime 采集脚本已写好并本地测试通过**：`ingestion/collect_gtfs_rt.py`（每 30 秒、两个 feed 错开 15 秒、只存原始 `.pb`、写健康日志）+ systemd 服务文件。**尚未部署**：云端 VM 选定 Oracle Cloud Always Free（新加坡），因该区域暂无容量（A1.Flex 和 E2.1.Micro 均 Out of capacity），正在每天重试；备选 GCP e2-micro。
   - **V06/V07 实测**：由一次性 workflow（`realtime_probe.yml`）在 2026-10-21（周三）马来西亚时间 08:00/13:00/18:00/23:00 自动运行，证据存 `docs/evidence/realtime_probe/`。
   - **仍待完成**：设计书定稿（本文件第 1 点之后的任务）、Proposal 报告重写、采集服务上线。设计书不应再写"先不写采集代码"。现有 `ingestion/` 原型作为可行性证据，并按设计书 v0.4 §8.3 演进为完整的采集服务（2026-10-20 确认）。
   - **设计书现状**：`docs/fyp-design/fyp_project_design_v0.4.md` 是当前有效基线，取代 v0.2、v0.3，后续会继续迭代。
   - **天气临时归档**：P0 上线前由 `.github/workflows/weather_archive.yml` 每 3 小时归档到 `data/raw/weather_*`。

---

# 2. 学校背景、换题政策与报告演进逻辑（极其重要）
我就读于马来西亚 UTAR。学校的 FYP 分为三个阶段：**Preliminary Proposal Report (课程代号 IIPSPW)** $\rightarrow$ **FYP 1** $\rightarrow$ **FYP 2**。

- **换题现状**：我在休学前已经用旧题目（太阳耀斑预测 Deep Learning + DE）通过了 IIPSPW 课程并拿到了分数。但我申请了休学（目前正在休学中），并决定在明年复学进入 FYP 1 时，**正式换题为本项目：巴生谷巴士服务可靠性数据平台（数据工程项目）**。
- **学校硬性规定**：
  > "For B) Change of area of study and/or project type: For FYP1, the student must submit a new IIPSPW report according to the new project title and area of study..."
- **这意味着**：
  1. 我必须在 **2027年1月/2月复学之前**，重写并提交一份全新的 **Preliminary Proposal Report (IIPSPW report)**。
  2. 这份重交的报告**只走换题审批流程，不再重新算分**（因为课程已经 pass 了），且我**只需要写 Proposal Report 本体**，完全不需要理会 Guideline 里提到的 Class Assessment 和 Presentation。
  3. 这是一份**纯文字报告，不包含任何代码实现**。
  4. **核心演进关系**：虽然重交不算分，但**不能敷衍**！因为 IIPSPW Report、FYP 1 Report 和 FYP 2 Report 的内容是**逐步进化、一脉相承**的（部分章节在 FYP 1 会直接复用、扩写或修改）。我必须现在就把底子打好，直接为 FYP 1 省下大量写报告的时间。
  5. 学校官方的 Guidelines（含 Marking Scheme）和 Report Templates 已放在 `docs/context/proposal/`、`docs/context/fyp1/`、`docs/context/fyp2/`。三个报告的结构要求各不相同，必须严格按学校的章节框架来映射本项目内容；template 里的示例（如 U-Net、图像分割）是旧占位内容，不得照搬。

---

# 3. 2027 真实时间线与求职倒逼的开发节奏（关键调整！）
`docs/fyp-design/` 里 v0.2/v0.3 假设 FYP 在 2027年4月提交，**这个时间线是错的**。项目的 **Roadmap（路线图）** 必须严格按照以下 UTAR 2027 真实校历与我的求职策略制定：

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

# 4. 导师、换题流程与提交方式（2026-10-20 更新）

- **新 FYP 标题（2026-10-20 确定）**：DEVELOPMENT AND EVALUATION OF AN OPEN LAKEHOUSE DATA PIPELINE FOR BUS SERVICE RELIABILITY MONITORING USING MALAYSIA'S GTFS REALTIME OPEN DATA

- **沟通渠道**：学校和导师之间用 **Microsoft Teams**。
- **现任导师**：**Ms. Ashikin**（专长 Deep Learning，旧题目太阳耀斑项目的导师）。
  - 约 2026-10-13 已在 Teams 发消息，说明要把题目和研究领域换成数据工程（基于 data.gov.my 开放数据，去掉深度学习部分），并询问：① 她是否愿意继续指导，还是需要换一位数据工程方向的导师；② 是否需要提交 amendment form 并重写 IIPSPW report。
  - **截至 2026-10-20 尚未回复**。现在是学期假期；下一个学期（short sem）**2026-10-26 开始**（本人仍在休学），预计她开学后才会回复。
- **候选导师**：**Sir Wong Chee Siang**。思路清晰，自己开了数据工程方向的 FYP 题目，但内容以数据科学为主，不是本项目这种数据平台型项目。全校目前没有确认做企业级数据工程的老师。
- **换题流程**（本人了解到的）：
  1. 先在 Teams 和导师沟通，让导师知道并同意换题；如果要换导师，也要同意换导师。
  2. 同意后，提交**新的 IIPSPW Proposal** 和 **FYP 1 amendment form**。
  3. amendment form 需要导师签名；**如果换导师，需要新旧两位导师都签名**。
- **Proposal 提交方式**：**Word 和 PDF 各一份**（先写 Word，提交时另存为 PDF），**通过邮件发给导师**。Proposal 阶段只有导师，**没有 moderator**；FYP 1、FYP 2 开始才有 moderator。
- **Proposal 重交截止日（非官方推算）**：约为 **Sem 1 的 Week 8 星期五 17:00**。依据：最近一个学期 2026-06-07 开学，重交截止为 2026-08-07 17:00。照此推算，2027 年 Sem 1（01-25 开学）的截止日约为 **2027-03-19**（如果中间有假期周，可能是 03-26）。**计划仍以复学前完成为目标**，推算的截止日只作为最后防线。

---

# 5. 云端采集 VM 的选择与过渡方案（2026-10-22 更新）

- **Oracle Cloud**：新加坡区一直无法创建实例（Out of capacity / Invalid Parameter）。另外，Oracle 在 2026 年把免费 A1 额度从 4 OCPU / 24 GB 减为 2 OCPU / 12 GB。可以继续在后台重试，但不再依赖它。
- **Azure for Students**：用 1utar.my 邮箱验证时显示 "You do not have access"，推测是休学期间学生身份状态被改动。正在请在校朋友测试他们能否开通：如果能，说明问题出在本人账号的状态，**复学（2027-01-25）后再申请 Azure for Students 作为长期方案**。
- **过渡方案（现在到复学）**：
  1. **先试 GCP e2-micro**（美国区，Standard 磁盘 30 GB，默认 IPv4）。上线 2–3 天后在 Billing 报表查看 SKU 明细。**如果外部 IPv4 收费，就不继续用 GCP**（不采用只用 IPv6 的方案），转第 2 步。
  2. **AWS 新账户 Free Plan**（最多 200 美元额度，6 个月后自动关闭）作为过渡。
  3. 复学后转到 Azure for Students。每次迁移都按设计书 §8.3.4 的交接规程执行，作为切换演练 D1。

**AWS 账户已开通（2026-10-22）**：Free Plan，赠送额度 100 美元，另可通过 5 项新手任务各得 20 美元（最多再得 100 美元）。**Free Plan 到期日：2027-04-22**，到期或额度用完时账户关闭、资源被删除。**最迟在 2027-04 上旬前**把采集迁移到 Azure（或其他方案），并把全部数据同步回本地。区域使用 ap-southeast-1（新加坡）。

**AWS EC2 采集 VM（2026-10-22 建好）**：
- 实例 `i-0cf3e2c00b50bcf02`（名称 `gtfs-collector`），**区域 ap-southeast-2（悉尼）**：Free Plan 的项目被锁定在悉尼，切换到新加坡需要升级为付费方案（不要升级）。
- t3.micro（x86，2 vCPU / 1 GiB）：Free Plan 只列出 "Free tier eligible" 机型，没有 t4g。Ubuntu 24.04，16 GiB gp3，Credit specification = Standard，公网 IPv4 `52.62.231.252`。
- 安全组 `launch-wizard-1` 只允许本人 IP 的 SSH（175.136.109.166/32）。家用宽带 IP 变了就到 Security Groups 重新选 "My IP"。
- 登录：WSL 中 `ssh fyp-collector`（`~/.ssh/config` 别名；密钥在 `~/.ssh/fyp-collector.pem`，Windows 下载文件夹另有备份；**绝不能提交到 git**）。
- 费用估算约 15 美元/月；额度 120 美元（做完 EC2 任务后应为 140 美元），到期日 2027-04-22。
- 实测：VM 能访问 api.data.gov.my（网址不带结尾 `/` 时会 301 跳转，`requests` 会自动跟随）。

# 6. 交接：下一步待办（2026-10-22）

1. **部署 RT 采集器到 EC2**（P0，最优先）：把 `ingestion/collect_gtfs_rt.py` 改成英文；输出路径改为设计书 §8.3.3 的 `bronze/gtfs_rt/...`；加每日 `tar.zst` 打包 + manifest；systemd 开机自启；开启 NTP。之后再把 Static、天气模块并入采集服务。
2. **AWS 新手任务**：确认 "Launch an instance using EC2" 已完成（+20 美元）。Bedrock、Lambda、RDS 三项暂不做。
3. **10/21 实测收尾**：等最后一次（23:00 那次）结果提交后，把 V06/V07 结论写进 summary；删除 `.github/workflows/realtime_probe.yml`；清理 `data/raw/gtfs_static/` 下旧的平铺 ZIP 和 `manifest.json`（新格式已导入）。
4. **导师**：给 Sir Wong 发消息（草稿在对话中，可再生成）；10-26 开学后跟进 Ms. Ashikin。
5. **Proposal**：第 1 步，起草 Ch2 大纲（英文，写在 `reports/proposal/ch2-lit-review.md`），然后检索文献。
6. 复学后申请 Azure for Students；**2027-04 上旬前**从 AWS 迁出。
