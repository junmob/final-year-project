# Ticket 01：从零写一个天气预报归档脚本（练习）

- **类型**：练习（只提交到 `t01-weather-downloader` 分支，永不合并进 `main`）
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

#### 第 2 步的迷你文档

建议拆成四小步来做，每做完一小步就运行一次：

- **2a**：得到当前的马来西亚时间 `now` 并打印出来。
- **2b**：用 `now` 拼出目录路径并打印出来。
- **2c**：创建目录，把压缩后的内容写进文件。
- **2d**：修改 `.gitignore`。

##### ① `datetime`：模块和类同名

`datetime` 既是一个**模块**的名字，也是这个模块里一个**类**的名字。`now()` 这类函数属于类，不属于模块。

```python
import datetime
datetime.today()        # AttributeError: module 'datetime' has no attribute 'today'
                        # (this is the module, it has no today())

from datetime import datetime, timezone, timedelta   # take the class out of the module
datetime.now()          # works
```

记住：在文件开头写 `from datetime import datetime, timezone, timedelta`，后面直接用 `datetime.now(...)`。

##### ② 带时区的当前时间：`datetime.now(tz)`、`timezone`、`timedelta`

- `timedelta(hours=9)` 表示"一段长度为 9 小时的时间"。
- `timezone(timedelta(hours=9))` 表示"UTC+9 这个时区"，也就是日本时间。
- `datetime.now(某个时区)` 返回那个时区的当前时间，并且时间本身记住了它属于哪个时区。

```python
from datetime import datetime, timezone, timedelta

print(datetime.now())                 # 2026-10-24 01:48:31.291767         <- no timezone attached
print(datetime.now(timezone.utc))     # 2026-10-23 17:48:31.291833+00:00   <- UTC
JST = timezone(timedelta(hours=9))    # Japan, UTC+9
print(datetime.now(JST))              # 2026-10-24 02:48:31.291869+09:00
```

**常见的坑**：`datetime.now()` 不传时区时，用的是电脑自己的时区。你的 WSL 设的是马来西亚时间，所以看起来没问题；但采集 VM 的系统时间是 UTC，同样的代码在 VM 上会慢 8 小时，文件也会存进错误的日期目录。所以一定要明确传入时区。马来西亚是 UTC+8，你照着上面 JST 的写法改一下即可。时区这种不会变的值，习惯上放在文件开头，名字全部大写（比如 `MYT`）。

##### ③ 把时间格式化成字符串：`strftime` 或 f-string

两种写法的结果完全一样：

```python
t = datetime.now(JST)
t.strftime("%Y-%m-%d")    # '2026-10-24'
t.strftime("%H%M%S")      # '024831'
f"{t:%Y-%m-%d}"           # '2026-10-24'   <- the same format codes inside an f-string
```

常用的格式代码：`%Y` 是四位年份，`%m` 是两位月份，`%d` 是两位日期，`%H` 是 24 小时制的小时，`%M` 是分钟，`%S` 是秒。注意大小写：`%m` 是月份，`%M` 是分钟。

##### ④ 路径：`pathlib.Path` 和 `/` 运算符

`Path` 是"文件路径"类型。两个 `Path`（或者一个 `Path` 加一个字符串）之间用 `/` 连接，得到更长的路径，不用自己拼斜杠。

```python
from pathlib import Path

p = Path("practice") / "output" / "demo" / f"date={t:%Y-%m-%d}"
print(p)                  # practice/output/demo/date=2026-10-24
p.mkdir(parents=True, exist_ok=True)   # create the directory
```

- `parents=True`：上层目录（`practice/output/`、`practice/output/demo/`）不存在时，一并创建。
- `exist_ok=True`：目录已经存在时不报错。不加的话，第二次运行就会报 `FileExistsError`。

在目录后面再 `/` 一个文件名，就得到文件路径，例如 `p / "fetched_at=024831.json.gz"`。

##### ⑤ 原始字节与 gzip：`response.content`、`gzip.compress`、`Path.write_bytes`

- `response.content` 是服务器发来的**原始字节**，类型是 `bytes`，样子是 `b'...'`。它和 `response.json()` 返回的 Python dict/list 不是一回事。第 2 步要存的是原始字节。
- `gzip.compress(bytes)` 把字节压缩，返回压缩后的字节。
- `path.write_bytes(bytes)` 把字节写进文件：文件不存在就新建，已经存在就覆盖。

```python
import gzip

raw = b'{"a": 1}'
z = gzip.compress(raw)
print(z[:4])                 # b'\x1f\x8b\x08\x00'  <- every gzip file starts with \x1f\x8b
print(gzip.decompress(z))    # b'{"a": 1}'          <- decompresses back to the original
Path("practice/output/demo/test.json.gz").write_bytes(z)
```

在终端检查：`zcat practice/output/demo/test.json.gz` 会打印出解压后的内容。

##### ⑥ `.gitignore`

`.gitignore` 是仓库根目录下的一个文本文件，每一行是一个"不要纳入 git"的路径规则。末尾带 `/` 表示一个目录，例如现有的 `data/bronze/`。在文件末尾加一行你自己的规则，再用 `git status` 检查。

**常见的坑**：`.gitignore` 只对**还没有被 git 跟踪**的文件生效。所以要在第一次 `git add` 输出文件**之前**就加好这条规则。

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
- **额外约束（顺序很重要）**：必须**先存好 `.json.gz` 文件，再更新 manifest**。想一想：如果顺序反过来，更新完 manifest、还没来得及存文件程序就崩溃了，下一次运行会发生什么？

#### 第 3 步的迷你文档

建议拆成四小步，每做完一小步就运行一次：

- **3a**：算出这次内容的哈希，打印出来。连续跑两次（间隔一分钟），两次的哈希应该一样（如果 MET 刚好在这一分钟内更新了预报，哈希会不一样，这是正常的）。
- **3b**：存完 `.json.gz` 之后，把哈希和文件路径写进 `manifest.json`。用 `cat` 查看 manifest 的内容。
- **3c**：在存文件**之前**读取 manifest，和这次的哈希比较。相同就打印 `unchanged` 并且不存文件；不同就照常存文件、更新 manifest。
- **3d**：删掉 manifest 再运行，确认没有报错，而且会存一个新文件。

##### ① 哈希：`hashlib.sha256(...).hexdigest()`

哈希函数把任意长度的数据变成一串固定长度的"指纹"。SHA-256 的指纹是 64 个十六进制字符。它有两个特点：
- 内容完全相同，指纹一定相同。
- 内容哪怕只差一个字符，指纹也会完全不同。

所以比较两份约 0.9 MB 的数据是否一样，只要比较两个 64 字符的指纹就可以了，manifest 里也只需要存这个指纹。

```python
import hashlib

s = "hello"
b = s.encode()                       # str -> bytes
print(b)                             # b'hello'
print(hashlib.sha256(b).hexdigest()) # 2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824

hashlib.sha256(s)                    # TypeError: Strings must be encoded before hashing
```

**常见的坑**：`sha256()` 只接受**字节**（`bytes`），不接受字符串（`str`）。字符串要先用 `.encode()` 转成字节。

##### ② 把数据变回字符串：`json.dumps` 和它的 `sort_keys` 参数

`json.loads` 把 JSON 文本变成 Python 的 dict 或 list；`json.dumps` 反过来，把 dict 或 list 变成 JSON 文本（`str`）。

```python
import json

x = {"b": 2, "a": 1}
y = {"a": 1, "b": 2}
print(x == y)                         # True   <- same content to Python
print(json.dumps(x))                  # {"b": 2, "a": 1}
print(json.dumps(y))                  # {"a": 1, "b": 2}   <- different text!
print(json.dumps(x, sort_keys=True))  # {"a": 1, "b": 2}
print(json.dumps(y, sort_keys=True))  # {"a": 1, "b": 2}   <- now identical text

# The first 16 characters of each hash:
#   json.dumps(x)                -> d5b8aed265256c89
#   json.dumps(y)                -> d8497d9d82770a70   (different)
#   json.dumps(x, sort_keys=True) -> d8497d9d82770a70
#   json.dumps(y, sort_keys=True) -> d8497d9d82770a70   (same)
```

`ensure_ascii` 参数：默认情况下，非英文字符会被写成 `–` 这种转义形式；加上 `ensure_ascii=False` 就会保留原字符。用来算哈希时两种都可以，只要每次都用同一种写法。但写给人看的文件（比如 manifest）建议加上，更好读。

```python
json.dumps({"name": "Kuala Terengganu – Pantai"})
# {"name": "Kuala Terengganu – Pantai"}
json.dumps({"name": "Kuala Terengganu – Pantai"}, ensure_ascii=False)
# {"name": "Kuala Terengganu – Pantai"}
```

所以算哈希的完整过程是：解析后的数据 → `json.dumps(..., sort_keys=True)` → `.encode()` → `sha256` → `.hexdigest()`。

##### ③ 读写小的文本文件：`Path.exists`、`write_text`、`read_text`、`json.loads`

```python
from pathlib import Path
import json

m = Path("demo_out") / "state.json"
print(m.exists())                                         # False  <- first time
m.write_text(json.dumps({"sha256": "ab12", "file": "x.gz"}, indent=2))
print(m.read_text())
# {
#   "sha256": "ab12",
#   "file": "x.gz"
# }
info = json.loads(m.read_text())                          # text -> dict
print(info["file"])                                       # x.gz
```

- `write_text(字符串)`：把字符串写进文件，文件已经存在就覆盖。
- `read_text()`：把整个文件读成一个字符串。
- `indent=2`：输出时换行并缩进 2 个空格，方便人看。只影响格式，不影响内容。

##### ④ 安全地取 dict 的值：`dict.get`

第一次运行时没有 manifest。一种常见写法是：文件不存在时用一个空 dict `{}` 代替。但空 dict 里没有 `"sha256"` 这个 key，直接用方括号取会报错：

```python
empty = {}
empty["sha256"]          # KeyError: 'sha256'
print(empty.get("sha256"))   # None   <- .get returns None instead of crashing
```

一个哈希值永远不会等于 `None`，所以"没有 manifest"自然会被当成"内容变了"。这样第一次运行不需要单独写一个分支来处理。

##### ⑤ 相对路径：`Path.relative_to`

manifest 里不要存完整的绝对路径。完整路径里包含你电脑上的用户目录，换一台机器（比如采集 VM）就不对了。只存相对于 `weather_forecast/` 的那一段：

```python
from pathlib import Path

full = Path("/home/u/practice/output/weather_warning/date=2026-10-24/fetched_at=101500.json.gz")
base = Path("/home/u/practice/output/weather_warning")
print(full.relative_to(base))          # date=2026-10-24/fetched_at=101500.json.gz
```

`relative_to` 返回的还是 `Path`。要放进 `json.dumps`，先用 `str(...)` 转成字符串，否则会报 `TypeError: Object of type PosixPath is not JSON serializable`。

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

#### 第 4 步的迷你文档

建议拆成四小步，每做完一小步就运行一次（同一个接口一分钟最多跑一次）：

- **4a**：先不写文件。把这次运行的 6 个字段放进一个 dict，用 `print(json.dumps(...))` 打印出来，检查字段名和值对不对。
- **4b**：把这一行追加写进 `fetch_log.jsonl`，用 `cat` 查看。
- **4c**：删掉 `fetch_log.jsonl`，从头再跑 3 次，用 `wc -l` 数行数。
- **4d**：逐行用 `json.loads` 解析一遍（见 ②），确认每一行都能解析。

这一步运行时只会出现 `changed` 和 `unchanged`。`failed` 要等第 5 步加上失败处理以后才会出现：现在请求一失败，程序就直接崩溃退出了，走不到写日志的那一行。

##### ① 追加写入：`open(path, "a")` 和 `with`

```python
from pathlib import Path

p = Path("demo_out") / "notes.txt"
p.parent.mkdir(parents=True, exist_ok=True)
with open(p, "a", encoding="utf-8") as f:
    f.write("first\n")
with open(p, "a", encoding="utf-8") as f:
    f.write("second\n")
print(p.read_text(encoding="utf-8"))
# first
# second
```

| 模式 | 打开时 | 写在哪里 | 文件不存在时 |
|---|---|---|---|
| `"w"` | 先清空（`write_text` 就是这样） | 从头开始写 | 新建 |
| `"a"` | 不清空 | 接在原有内容的末尾 | 新建 |

- 两种模式都**不会**自动创建目录，目录必须已经存在。
- `with ... as f:`：缩进的代码块结束时自动关闭文件。文件关闭以后，写进去的内容才一定已经保存到文件里。
- `f.write(字符串)` **不会**自动加换行，需要自己在末尾加 `"\n"`。
- `encoding="utf-8"`：不写的话，用的是系统的默认编码。明确写出来，在哪台机器上结果都一样。

##### ② JSON Lines（`.jsonl`）

JSON Lines 的规则只有一条：**每一行是一个完整的 JSON 值（通常是一个对象），行与行之间用换行分隔。** 整个文件不是一个合法的 JSON，但每一行单独拿出来都是。

```text
{"n": 1, "ok": true}
{"n": 2, "ok": false}
```

写入：`json.dumps(dict)` 默认就输出成一行。**不要加 `indent`**，`indent` 会在里面插入换行，一条记录就变成了好几行。

```python
from pathlib import Path
import json

log = Path("demo_out") / "events.jsonl"
for n in [1, 2]:
    with open(log, "a", encoding="utf-8") as f:
        f.write(json.dumps({"n": n, "ok": n == 1}) + "\n")

for line in log.read_text(encoding="utf-8").splitlines():   # splitlines: split the text into lines
    row = json.loads(line)
    print(type(row), row["n"])
# <class 'dict'> 1
# <class 'dict'> 2
```

数行数：`wc -l demo_out/events.jsonl` 输出 `2 demo_out/events.jsonl`。`wc -l` 数的是换行符的个数，所以每一行末尾都要有 `"\n"`。

##### ③ Python 的 `None` 写进 JSON 是 `null`

```python
import json

print(json.dumps({"sha256": None, "ok": True, "n": 3}))
# {"sha256": null, "ok": true, "n": 3}
```

| Python | JSON |
|---|---|
| `None` | `null` |
| `True` / `False` | `true` / `false` |
| `dict` | 对象 `{...}` |
| `list` | 数组 `[...]` |

用 `json.loads` 读回来时，会反过来再变回 Python 的值。

##### ④ ISO 格式的时间：`isoformat(timespec="seconds")`

```python
from datetime import datetime, timezone, timedelta

MYT = timezone(timedelta(hours=8))
t = datetime(2026, 10, 23, 21, 5, 0, 123456, tzinfo=MYT)
print(t.isoformat())                      # 2026-10-23T21:05:00.123456+08:00
print(t.isoformat(timespec="seconds"))    # 2026-10-23T21:05:00+08:00
print(datetime(2026, 10, 23, 21, 5, 0).isoformat(timespec="seconds"))
# 2026-10-23T21:05:00                     <- no tzinfo, so no "+08:00"
```

- `timespec="seconds"`：只保留到秒，去掉微秒。
- 末尾的 `+08:00` 表示"比 UTC 早 8 小时"，只有带时区的时间才会有。

### 第 5 步：失败处理

网络错误、HTTP 4xx/5xx、响应不是合法 JSON，这三种情况都不能让程序直接崩溃退出。要做到：在日志里写一行 `status="failed"`（`error` 字段写明异常类型和信息），打印一条失败信息，然后程序以**退出码 1** 结束。成功时退出码是 0。

- **怎么测**：临时把 URL 改成 `https://api.data.gov.my/weather/forecastXX/`（会返回 404）。测完记得改回来。
- **验收**：日志里有一行 failed，`error` 字段里能看出是 404；运行后执行 `echo $?`，打印 `1`。
- **要查的**：`try` / `except`、`response.raise_for_status()`、`requests.RequestException`、`response.json()` 失败时抛出的是哪种异常、`sys.exit`
- **思考题**：失败时为什么也要写日志？算"可用率"时会用到哪几行？

#### 第 5 步的迷你文档

建议拆成四小步（同一个接口一分钟最多跑一次，404 网址也算）：

- **5a**：先**不改代码**，只把 URL 临时改成 `forecastXX`。运行之前，先写下你的预测：会打印什么？会不会生成新的 `.gz`？`manifest.json` 会不会变？日志里会多一行什么？退出码（`echo $?`）是多少？然后运行，逐项对照。
- **5b**：改代码，让失败时：日志写一行 `status="failed"`、打印一条失败信息、以退出码 1 结束。
- **5c**：用 404 网址再跑一次，检查：
  - 日志最后一行：`status` 是 `failed`，`error` 里能看出 404，6 个字段都在；
  - `echo $?` 打印 `1`；
  - 没有生成新的 `.gz` 文件，`manifest.json` 的内容和运行之前一样。
- **5d**：把 URL 改回正确的网址，再跑一次，`echo $?` 打印 `0`，日志是 `changed` 或 `unchanged`。

如果 5a 的运行在 `practice/output/` 里留下了不该有的东西，可以删掉。那里只是练习输出。

##### ① `try` / `except` / `else` / `finally` 的执行顺序

```python
def run(fail):
    print("--- fail =", fail)
    try:
        print("try: start")
        if fail:
            raise ValueError("bad value")     # raise: throw an exception on purpose
        print("try: end")
    except ValueError as e:
        print("except:", e)
    else:
        print("else")
    finally:
        print("finally")
    print("after")

run(False)
run(True)
```

输出：

```text
--- fail = False          --- fail = True
try: start                try: start
try: end                  except: bad value
else                      finally
finally                   after
after
```

| 块 | 什么时候执行 |
|---|---|
| `try` | 总是从这里开始；一旦某一行抛出异常，`try` 里剩下的行就**不再执行**，直接跳去找匹配的 `except` |
| `except 某类异常 as e` | `try` 里抛出的异常属于这一类（或它的子类）时执行；`e` 就是那个异常对象 |
| `else` | `try` 里**没有**抛出异常时执行 |
| `finally` | 不管有没有异常，最后都会执行 |

- 异常被某个 `except` 接住以后，程序会接着执行整个 `try` 结构**后面**的代码（上面的 `after`）。接住异常不等于程序停下来。
- 如果抛出的异常没有任何一个 `except` 能接住，`finally` 执行完以后，程序就带着这个异常崩溃退出。

##### ② `requests` 的异常：一个父类管住全部

`requests` 里所有的异常都是 `requests.RequestException` 的子类，所以 `except requests.RequestException` 能接住下面这些（在项目的 `.venv` 里验证过，requests 2.34）：

| 异常 | 什么时候出现 |
|---|---|
| `requests.ConnectionError` | 连不上服务器（没网、域名错误） |
| `requests.Timeout` | 超过 `timeout` 秒服务器都没有回应 |
| `requests.HTTPError` | `response.raise_for_status()` 遇到 4xx/5xx |
| `requests.exceptions.JSONDecodeError` | `response.json()` 发现内容不是合法的 JSON（它同时也是 `ValueError` 的子类） |

不联网也能看到 `HTTPError` 长什么样：自己造一个状态码是 404 的响应对象。

```python
import requests

r = requests.Response()          # an empty response built by hand, no network
r.status_code = 404
r.reason = "Not Found"
r.url = "https://example.com/missing"
try:
    r.raise_for_status()
except requests.RequestException as e:
    print(f"{type(e).__name__}: {e}")
# HTTPError: 404 Client Error: Not Found for url: https://example.com/missing
```

- `type(e).__name__`：异常的类名，比如 `HTTPError`。
- `str(e)`（或者在 f-string 里直接写 `{e}`）：异常的信息。
- 两个拼在一起，就是 ticket 要求的"异常类型和信息"。

##### ③ 退出码：`sys.exit` 和 `echo $?`

程序结束时会给操作系统留一个整数，叫**退出码**：`0` 表示成功，非 `0` 表示失败。VM 上的定时任务（systemd）、以后的 Airflow，都是看这个数字来判断一次运行成功还是失败的，它们不会去读你打印的文字。

```python
# exit_demo.py
import sys

print("about to exit")
sys.exit(1)
print("never printed")
```

```bash
python exit_demo.py
echo $?        # 1
python -c "print('ok')"
echo $?        # 0   <- a script that ends normally exits with 0
```

- `echo $?` 打印的是**上一条命令**的退出码，所以要紧接着运行，中间不要插别的命令。
- 程序正常跑到最后，退出码自动是 `0`，不需要写 `sys.exit(0)`。
- 程序因为没接住的异常崩溃时，退出码也是 `1`。但那样日志里不会有 `failed` 这一行，所以第 5 步要自己接住异常、写完日志，再主动退出。
- `sys.exit` 的原理是抛出一个叫 `SystemExit` 的特殊异常，所以外面的 `finally` 仍然会执行；`except requests.RequestException` 不会接住它。

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

#### 第 6 步的迷你文档

两个接口的网址：

| name | URL |
|---|---|
| `weather_forecast` | `https://api.data.gov.my/weather/forecast/` |
| `weather_warning` | `https://api.data.gov.my/weather/warning/` |

输出目录用 name 命名：`practice/output/weather_forecast/`（已经有了）和 `practice/output/weather_warning/`（新的）。

建议拆成四小步。现在一次完整的运行会请求两个接口，所以两次运行之间仍然至少隔一分钟：

- **6a**：把"处理一个接口"的全部步骤（抓取、哈希、比较并保存、写日志）变成一个函数，接口的 name 和 URL 作为参数传进去，返回这个接口的退出码（0 或 1）。先只用 `weather_forecast` 调用它，确认结果和第 5 步一样：输出仍然写进原来的目录，原来的 manifest 和日志继续有效。
- **6b**：用一个 dict 存 name → URL，循环处理两个接口，两次请求之间 `sleep` 20 秒。检查 `weather_warning/` 目录下有没有它自己的 `.gz`、manifest 和日志。
- **6c**：加 `--only`。分别试 `--help`、`--only weather_warning`、`--only abc`。
- **6d**：把 warning 的网址临时改成会返回 404 的网址，不带参数运行：forecast 应该照常处理，warning 记一行 `failed`，`echo $?` 打印 `1`。测完改回来。

##### ① 用 dict 存 name → URL，再循环

```python
FEEDS = {
    "kl": "https://example.com/kl",
    "feeder": "https://example.com/feeder",
}

print(list(FEEDS))         # ['kl', 'feeder']   <- the keys, in the order they were written
print(FEEDS["kl"])         # https://example.com/kl
for name, url in FEEDS.items():
    print(name, url)
# kl https://example.com/kl
# feeder https://example.com/feeder
```

- `.items()` 每次给出一对 `(key, value)`，`for name, url in ...` 把这一对拆成两个变量。
- dict 会记住 key 写进去的顺序，所以循环的顺序就是你写的顺序。

##### ② 只在两次请求之间等待：`time.sleep` 和 `enumerate`

```python
import time

for i, (name, url) in enumerate(FEEDS.items()):
    if i > 0:              # not before the first one
        time.sleep(2)      # pause the program for 2 seconds
    print(i, name, time.strftime("%H:%M:%S"))
# 0 kl 04:22:53
# 1 feeder 04:22:55        <- 2 seconds later
```

- `time.sleep(秒数)`：让程序停在这一行，等够了再继续往下执行。
- `enumerate(...)`：在每个元素前面加一个从 0 开始的序号。`(name, url)` 外面的括号不能省略，因为 `enumerate` 给出的是 `(序号, (key, value))`。
- 用 `if i > 0` 判断，第一个之前不等，最后一个之后也不会多等。

##### ③ 命令行参数：`argparse`

```python
# feeds_demo.py
import argparse

FEEDS = {"kl": "https://example.com/kl", "feeder": "https://example.com/feeder"}

parser = argparse.ArgumentParser(description="Print the URL of one or all feeds.")
parser.add_argument(
    "--only",
    choices=list(FEEDS),          # ["kl", "feeder"]; any other value is an error
    help="process only this feed (default: all feeds)",
)
args = parser.parse_args()        # reads what was typed after the script name
print("args.only =", repr(args.only))
```

| 命令 | 输出 | 退出码 |
|---|---|---|
| `python feeds_demo.py` | `args.only = None` | 0 |
| `python feeds_demo.py --only kl` | `args.only = 'kl'` | 0 |
| `python feeds_demo.py --help` | 见下面 | 0 |
| `python feeds_demo.py --only abc` | 见下面 | **2** |

```text
$ python feeds_demo.py --help
usage: feeds_demo.py [-h] [--only {kl,feeder}]

Print the URL of one or all feeds.

options:
  -h, --help          show this help message and exit
  --only {kl,feeder}  process only this feed (default: all feeds)

$ python feeds_demo.py --only abc
usage: feeds_demo.py [-h] [--only {kl,feeder}]
feeds_demo.py: error: argument --only: invalid choice: 'abc' (choose from 'kl', 'feeder')
```

- 以 `--` 开头的参数是**可选的**：没写时，它的值是 `None`。
- 参数名 `--only` 变成 `args.only`。如果名字里有 `-`，比如 `--out-dir`，会变成 `args.out_dir`。
- `choices`：值不在列表里时，argparse 自己打印错误并退出（退出码 2），你的代码不会继续执行。
- `help`：`--help` 时显示的说明文字。`-h` / `--help` 是 argparse 自动加上的。

##### ④ 多个结果里"只要有一个失败"：`any`

```python
codes = [0, 1, 0]                          # exit codes of three runs
print(any(code != 0 for code in codes))    # True   <- at least one is not 0
print(any(code != 0 for code in [0, 0]))   # False
```

`any(...)`：只要里面有一个是 `True`，结果就是 `True`。括号里的 `code != 0 for code in codes` 会对 `codes` 里的每一个值算一次 `code != 0`。

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
