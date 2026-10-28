# 学习资料索引

每完成一个模块，就在这里新增一份教学手册。建议按下面的顺序阅读。

| 顺序 | 手册 | 内容 | 状态 |
|---|---|---|---|
| 0 | [curriculum.md](curriculum.md) | 学习路线的规则：阶段 S0–S6、ticket 流程、提示规则、暂时不要读的内容、记录方式、代号 | ✅ 2026-10-27（**先读这份**） |
| 1 | [vm-collector-guide.md](vm-collector-guide.md) | 云端采集 VM：连接、部署、systemd、每种数据的采集与去重、RT 打包、`bronze_sync`、巡检 | ✅ 2026-10-23 |
| 2 | `ci-guide.md` | 自动测试与代码检查（pytest、ruff、GitHub Actions CI）、部署脚本 | ⏳ S0 结束后写 |
| 3 | 之后的模块 | S1 数据剖析、本地湖仓（Docker、MinIO、Iceberg、Spark）、dbt、Airflow、流处理、看板、RQ 实验…… | ⏳ 每个阶段结束后写 |

ticket 索引：[`../tickets/README.md`](../tickets/README.md)；工程日志：[`../engineering-log/README.md`](../engineering-log/README.md)；设计决定记录：[`../adr/README.md`](../adr/README.md)。

相关的白话说明：[`../fyp-design/rq-explained.md`](../fyp-design/rq-explained.md)（RQ1–RQ5 研究问题）。
