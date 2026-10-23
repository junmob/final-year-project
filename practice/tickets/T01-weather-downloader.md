# Ticket 01：从零写一个天气预报归档脚本（练习）

- **类型**：练习（只提交到 `practice` 分支，永不合并进 `main`）
- **产出文件**：`practice/download_weather.py`
- **对应的正式代码**：`ingestion/download_weather.py`。**第 7 步做完之前不要打开它**，也先不要读 vm-collector-guide 里讲天气采集代码的那一节。
- **设计依据**：v0.4 §8.3.3；data-source-summary §6.1、§6.2、§7.1

## 背景

MET Malaysia 的天气预报没有历史接口：某一版预报如果当时没抓下来，以后就永远拿不到了。所以要定时抓取，**只有内容变了才存一份**，并且每次尝试（不管成功、失败还是内容没变）都记一行日志。日志用来算可用率（L1 指标）。

两个接口（URL 末尾的 `/` 不能省）：

| name | URL |
|---|---|
| `weather_forecast` | `https://api.data.gov.my/weather/forecast/` |
| `weather_warning` | `https://api.data.gov.my/weather/warning/` |

## 全局约束（每一步都要遵守）

1. **所有输出只能写到 `practice/output/` 下面**，不能写到 `data/` 下的任何地方，那里是真实数据。
2. **两次请求至少间隔 20 秒**（data-source-summary §6.1.4）。调试时也不要连续狂跑：同一个接口一分钟最多跑一次。
3. 代码、注释、print 内容、commit message **全部用英文**。
4. 时间一律用马来西亚时间（UTC+8），不要依赖电脑的时区设置。
5. 每完成一步就 commit 一次，message 格式是 `practice(weather): step N <what you did>`。

## 怎么运行

```bash
source .venv/bin/activate          # once per terminal
python practice/download_weather.py
```

## 步骤

### 第 1 步：抓取并打印

只处理 `weather_forecast`。发请求，打印：HTTP 状态码、记录条数、第一条记录。

- **验收**：状态码是 200；记录条数大约是 3000（2026-10-20 是 3080）；第一条记录是一个 dict，里面能看到地点和日期之类的字段。
- **要查的**：`requests.get`（以及它的 `timeout` 参数）、`response.status_code`、`response.json()`
- **文档**：<https://requests.readthedocs.io/en/latest/user/quickstart/>（看 "Make a Request" 和 "JSON Response Content" 两节）
- **思考题**：如果不传 `timeout`，服务器一直不回应会怎样？

### 第 2 步：把原始响应压缩存盘

把**响应的原始字节**（不是解析后的 dict）用 gzip 压缩后存到：

```
practice/output/weather_forecast/date=<YYYY-MM-DD>/fetched_at=<HHMMSS>.json.gz
```

同时把 `practice/output/` 加进 `.gitignore`：数据文件不进 git。

- **验收**：
  - 跑两次（中间隔一分钟）会生成两个文件。
  - `zcat <file> | head -c 300` 能看到 JSON 文本。
  - `git status` 里看不到 `practice/output/`。
- **要查的**：`datetime.now(tz)`、`timezone`、`timedelta`、日期格式化（`strftime`，或者 f-string 里的 `{now:%Y-%m-%d}`）、`pathlib.Path` 的 `/` 运算符、`mkdir(parents=True, exist_ok=True)`、`gzip.compress`、`Path.write_bytes`、`response.content`
- **文档**：
  - <https://docs.python.org/3/library/datetime.html>
  - <https://docs.python.org/3/library/pathlib.html>
  - <https://docs.python.org/3/library/gzip.html>
- **思考题**：目录名为什么写成 `date=2026-10-23`，而不是直接写 `2026-10-23`？（提示：搜一下 "Hive partitioning"，Spark 以后会用到。）

### 第 3 步：内容没变就不存（去重）

在 `practice/output/weather_forecast/manifest.json` 里记住**上一次存下来的那份**内容的哈希值和文件路径。每次抓到新内容：

1. 把解析后的 JSON **按 key 排序后重新序列化成字符串**，再算它的 SHA-256。
2. 和 manifest 里的哈希比较：相同就打印 `unchanged`，不存文件；不同就存文件，再更新 manifest。
3. manifest 不存在（第一次运行）时，当作"内容变了"处理。

- **验收**：连续跑两次（间隔一分钟），第二次打印 `unchanged`，并且没有生成新文件；手动删掉 manifest 再跑，又会存一份新的。
- **要查的**：`hashlib.sha256(...).hexdigest()`、`json.dumps` 的 `sort_keys` 参数、`str.encode`、`Path.exists`、`Path.read_text` / `write_text`、`json.loads`
- **文档**：
  - <https://docs.python.org/3/library/hashlib.html>
  - <https://docs.python.org/3/library/json.html>
- **思考题**：为什么不直接对 `response.content` 的原始字节算哈希？为什么要 `sort_keys`？

### 第 4 步：每次尝试都记一行日志

追加写入 `practice/output/weather_forecast/fetch_log.jsonl`，每次运行写一行 JSON，至少包含这些字段：

| 字段 | 内容 |
|---|---|
| `fetched_at_myt` | ISO 格式的时间，例如 `2026-10-23T21:05:00+08:00` |
| `status` | `changed` / `unchanged` / `failed` 三者之一 |
| `sha256` | 本次内容的哈希；失败时为 `null` |
| `records` | 记录条数 |
| `file` | 本次存下的文件路径（相对 `weather_forecast/`）；没存就是 `null` |
| `error` | 失败原因；成功时为 `null` |

- **验收**：跑 3 次，文件里正好 3 行，每一行单独拿出来都能被 `json.loads` 解析。
- **要查的**：`open(path, "a")` 里 `"a"` 的含义、`datetime.isoformat(timespec="seconds")`、什么是 JSON Lines
- **文档**：<https://jsonlines.org/>
- **思考题**：为什么用 jsonl（一行一个 JSON），而不是把所有记录放进一个大的 JSON 数组？

### 第 5 步：失败处理

网络错误、HTTP 4xx/5xx、响应不是合法 JSON，这三种情况都不能让程序直接崩溃退出。要做到：在日志里写一行 `status="failed"`（`error` 字段写明异常类型和信息），打印一条失败信息，然后程序以**退出码 1** 结束。成功时退出码是 0。

- **怎么测**：临时把 URL 改成 `https://api.data.gov.my/weather/forecastXX/`（会返回 404）。测完记得改回来。
- **验收**：日志里有一行 failed，`error` 字段里能看出是 404；运行后执行 `echo $?`，打印 `1`。
- **要查的**：`try` / `except`、`response.raise_for_status()`、`requests.RequestException`、`response.json()` 失败时抛出的是哪种异常、`sys.exit`
- **思考题**：失败时为什么也要写日志？算"可用率"时会用到哪几行？

### 第 6 步：两个接口 + 命令行参数

- 默认依次抓 `weather_forecast` 和 `weather_warning`，两次请求之间 `sleep` 20 秒。
- 加一个可选参数 `--only <name>`，只抓指定的那一个；传别的值时，argparse 要自动报错。
- 每个接口有自己的子目录、自己的 manifest 和自己的日志。
- 只要有一个接口失败，退出码就是 1。

- **验收**：
  - `python practice/download_weather.py --help` 能显示 `--only` 的说明。
  - `--only weather_warning` 只生成 warning 目录下的东西。
  - `--only abc` 会报错退出。
- **要查的**：`argparse` 的 `add_argument`（`choices`、`help`）、`parse_args`、`time.sleep`；怎样用一个 dict 存 name → URL，再用一个函数处理任意一个接口
- **文档**：<https://docs.python.org/3/howto/argparse.html>
- **思考题**：为什么把"抓一个接口"写成一个函数，而不是复制粘贴两份代码？

### 第 7 步：两个工业级细节

1. **原子写入**：先写到 `xxx.json.gz.tmp`，写完再改名成 `xxx.json.gz`。查 `Path.replace`。
   - 思考题：如果写到一半断电，不这样做会留下什么？
2. **gzip 的 `mtime=0`**：查 `gzip.compress` 的 `mtime` 参数。
   - 思考题：同样的内容压缩两次，得到的字节为什么可能不一样？为什么"相同输入得到相同字节"对数据管道很重要？

### 完成后

1. 自查：所有全局约束都满足；7 个思考题都能用自己的话回答（写在 commit message 里，或者直接告诉我都可以）。
2. 现在才打开 `ingestion/download_weather.py`，和你的版本对比：

   ```bash
   diff practice/download_weather.py ingestion/download_weather.py
   ```

   在 VS Code 里也可以：资源管理器里选中两个文件，右键选 "Compare Selected"。
3. 找出至少 3 处不同，每一处说明：哪个写法更好？为什么？还是两种都可以？
4. 告诉我 "T01 review"，我来做整体 review。
