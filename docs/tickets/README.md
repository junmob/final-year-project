# Tickets

> 学习材料（中文），提交学校前排除。规则与流程见 [`docs/learning/curriculum.md`](../learning/curriculum.md)。
> ticket 由 Claude 一次发一个；格式见 [`TEMPLATE.md`](TEMPLATE.md)。

## 索引

| ID | 标题 | 阶段 | 状态 | 分支 / PR |
|---|---|---|---|---|
| [T01](T01-weather-downloader.md) | 从零写一个天气预报归档脚本（练习） | S0 | 进行中（第 3 步） | `t01-weather-downloader`（练习，不合并） |

状态：未发出 → 进行中 → review 中 → 已合并 / 已归档。

## T01 的特殊之处

- T01 是练习：重写一个已经在运行的脚本（`ingestion/download_weather.py`），所以**不开 PR、不合并**，代码直接 commit、push 到 `t01-weather-downloader` 分支，放在分支里的 `practice/` 文件夹。
- T01 进行中补充的迷你文档提交在 `t01-weather-downloader` 分支上；T01 结束时，Claude 把最终版同步到 main 的 `docs/tickets/T01-weather-downloader.md`。

## T01 收尾（截止 11-06）

1. 做完第 3–7 步，按 ticket 最后一步把你的版本和 `ingestion/download_weather.py` 对比。
2. Claude 出几道对比题，你在聊天里回答。
3. 打 tag 并推送，标记完成：
   ```bash
   git switch t01-weather-downloader
   git tag t01-done
   git push origin t01-done
   ```
4. 分支保留、不删、不合并（它和 `ingestion/download_weather.py` 做的是同一件事，合并后 main 里会有两份）。
5. 11-06 还没做完：第 7 步改为读懂 `ingestion/download_weather.py` 里对应的代码并讲给 Claude 听。

## 每个 ticket 的分支流程（从 T02 开始）

```bash
# 1. 从最新的 main 开分支（weather_archive workflow 每天往 GitHub 上的 main 提交，所以先 pull）
git switch main
git pull
git switch -c t02-collector-tests        # t + 编号 + 简短英文名

# 2. 写代码，小步提交（commit 信息用英文）
git add <文件>
git commit -m "test(collector): add tests for write_atomic"

# 3. 推送
git push -u origin t02-collector-tests
```

4. 在 GitHub 网页上开 PR：base 选 `main`，描述里放预测、检查输出、ticket 要求的内容。把 PR 编号发给 Claude。
5. Claude 在本地看 diff，在聊天里按 `文件:行号` review。你修改后继续 commit、push，PR 会自动更新。
6. review 通过、复盘四问回答完、工程日志写好之后，在网页上选 **Create a merge commit** 合并（不要选 Squash，否则 v1 的 commit 会消失）。
7. 回到 main：
   ```bash
   git switch main
   git pull
   git branch -d t02-collector-tests
   ```

## 文件命名

`docs/tickets/T02-collector-tests.md`、`docs/tickets/R01-gtfs-primer.md`：编号 + 简短英文名。标题只描述目标。
