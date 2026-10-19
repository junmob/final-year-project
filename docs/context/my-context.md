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