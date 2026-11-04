# T02：给 RT 采集器写自动测试

| 项 | 内容 |
|---|---|
| 阶段 | S0 基本功收尾 |
| 类型 | 开发（测试） |
| 分支 | `t02-collector-tests` |
| 预计 | 2–3 次 session |
| 目标完成 | 11-12 |
| 思考档位 | high |

## 背景
`ingestion/collect_gtfs_rt.py` 已经在 VM 上 24 小时运行，但没有任何自动测试。以后改代码（或者升级库）时，我们需要一种办法在几秒内确认"核心行为没有被改坏"。这就是单元测试：一小段代码调用被测函数，然后检查结果是否符合预期。

你要测试的是别人（AI）写好的代码，所以**第一步是读懂它**。测试写完，你应该能逐行解释 `write_atomic`、`classify`、`fetch_slot`、`write_health` 做了什么。

设计书依据：v0.5 §14.2 测试策略（单元测试一行）、§14.1 DataOps。

## 目标
在 `tests/test_collect_gtfs_rt.py` 里为四个函数写测试，`pytest -q` 全部通过。

## 范围
- 范围内：`write_atomic`、`classify`、`fetch_slot`、`write_health`。
- 范围外：`main()`（无限循环，不测）；`pack_gtfs_rt.py`、`download_gtfs_static.py`（T03）；`bronze_sync.py`（不测）。
- **不修改 `ingestion/` 里的任何文件。**

## 输入与输出
- 输入：没有数据文件。测试需要的 protobuf 消息和 HTTP 响应都在测试代码里自己造（资料 ④⑤）。
- 输出：`tests/test_collect_gtfs_rt.py`（只有这一个新文件）。

## 约束（必须遵守）
1. **测试不访问网络。** 真实 API 每分钟只允许 4 次请求，VM 上的采集器已经用满了。所有 HTTP 请求都要用假的对象代替（资料 ④）。
2. **测试只能在 pytest 提供的临时目录里创建文件**（资料 ②）。不能在仓库里或 `~/fyp-data/` 里留下任何东西。
3. 每个测试互相独立：单独运行任何一个都能通过（`pytest -q -k 名字`）。
4. 测试代码、注释、断言信息全部用英文。

## 运行前预测（写在 PR 描述里）
在写代码之前回答：
1. `fetch_slot("rapid-bus-mrtfeeder", 1792684815)` 成功时，`.pb` 文件的相对路径应该是什么？（`1792684815` 是 UTC 时间 2026-10-22 16:00:15，自己推算）
2. 你的测试运行时，会在硬盘上创建哪些文件？在哪个目录？

## 步骤

### 第 0 步：开分支、装依赖
```bash
git switch main
git pull
git switch -c t02-collector-tests
source .venv/bin/activate
pip install -r requirements-dev.txt   # 已经装过的话会显示 "Requirement already satisfied"
pytest -q
```
现在还没有 `tests/` 目录，所以 pytest 一个测试都不会运行：会出现一条 `No files were found in testpaths` 警告，最后一行是 `1 warning in …s`。这是正常的。

### 第 1 步：读代码，写下每个函数的"输入 → 输出 / 副作用"
在 PR 描述里用中文或英文写一个小表：函数名 | 输入 | 返回值 | 对硬盘做了什么。不写代码。

### 第 2 步：测试 `write_atomic`（资料 ①②）
至少覆盖：写入后文件存在且内容正确；目录不存在时会被创建；写完后没有残留的 `.tmp` 文件；目标文件已存在时会被替换。

### 第 3 步：测试 `classify`（资料 ⑤）
至少覆盖四种情况：有车辆的合法消息 → `ok`；有 header 但没有车辆 → `ok_empty`；明显不是 protobuf 的字节（例如 `b"not a protobuf"`）→ `parse_error`；空字节 `b""` → 结果是什么？先预测，再测试，再读代码解释为什么。

### 第 4 步：测试 `write_health`（资料 ⑥）
写两条记录，确认文件里有两行、每行都是合法 JSON、内容和传入的一致。

### 第 5 步：测试 `fetch_slot`（资料 ③④⑤）
至少覆盖：
- HTTP 200 + 合法消息 → `status == "ok"`，`.pb` 文件存在且内容等于响应体，路径符合你在"预测 1"里写的，健康日志多了一行；
- HTTP 429 → `status == "rate_limited"`，没有写 `.pb`；
- 请求超时（假函数抛出 `requests.Timeout`）→ `status == "timeout"`。

### 第 6 步：隔离检查（必须做，输出贴进 PR）
```bash
git status --ignored --short > /tmp/before.txt
PYTHONDONTWRITEBYTECODE=1 pytest -q -p no:cacheprovider
git status --ignored --short > /tmp/after.txt
diff /tmp/before.txt /tmp/after.txt && echo "SAME"
```
两次输出必须完全相同（打印 `SAME`）。命令的意思见资料 ⑧。

### 第 7 步：提交、推送、开 PR
```bash
git add tests/
git commit -m "test(collector): add unit tests for collect_gtfs_rt"
git push -u origin t02-collector-tests
```
可以每写完一步就 commit 一次（小步提交），不必等到最后。然后在 GitHub 网页上开 PR（base: `main`），描述里放下面"要贴进 PR 的内容"。把 PR 编号发给我。

## 验收标准
- [ ] `pytest -q` 全部通过，至少 10 个测试。
- [ ] 第 6 步打印 `SAME`。
- [ ] 断网（或者把 Wi-Fi 关掉）时 `pytest -q` 仍然全部通过。
- [ ] `ingestion/` 没有任何改动（`git diff main -- ingestion/` 为空）。
- [ ] PR 描述包含下面列出的全部内容。

## 要贴进 PR 的内容
- 两个预测的答案（写代码之前写的，之后不要改；如果发现预测错了，在下面另写一行"实际：……"）。
- 第 1 步的函数表。
- 第 6 步的完整输出（包括 `diff` 的输出或 `SAME`）。
- `pytest -q` 的输出。

## review 时要你讲解
1. `write_atomic` 为什么先写 `.tmp` 再 `replace`？如果直接写目标文件，采集器在写到一半时被杀掉会怎样？
2. `classify` 为什么要区分 `ok` 和 `ok_empty`？深夜 0 辆车算采集失败吗？
3. 文件路径里的 `date=`、`hour=` 是哪个时区？文件名是哪个时区？为什么这样设计？
4. 你的假响应对象只实现了哪些属性？为什么够用？

## 资料

##### ① pytest 基本用法
pytest 会自动找 `tests/` 目录下名字以 `test_` 开头的文件，再执行里面名字以 `test_` 开头的函数。函数里用 `assert 条件`，条件为假就算失败。
```python
# tests/test_example.py
def add(a, b):
    return a + b

def test_add():
    assert add(2, 3) == 5

def test_add_negative():
    assert add(-1, 1) == 0
```
```bash
pytest -q                 # 运行全部测试
pytest -q -k add_negative # 只运行名字包含 add_negative 的测试
pytest -q -x              # 遇到第一个失败就停
pytest -q -s              # 显示测试里 print() 的输出（默认会被 pytest 收起来）
```
失败时 pytest 会打印 `assert` 两边的实际值，从这里开始读。
本仓库已经配置好：`tests/` 里可以直接 `import collect_gtfs_rt`（`pyproject.toml` 里的 `pythonpath` 设置）。

##### ② `tmp_path`：每个测试一个空的临时目录
在测试函数的参数里写 `tmp_path`，pytest 会自动传进来一个 `pathlib.Path`，指向一个新建的空目录（在 `/tmp/pytest-of-<用户名>/` 下面），测试之间互不影响。
```python
def test_write_file(tmp_path):
    target = tmp_path / "sub" / "a.txt"
    target.parent.mkdir(parents=True)
    target.write_text("hello")
    assert target.read_text() == "hello"
    assert list(tmp_path.rglob("*.tmp")) == []   # rglob: 递归查找
```

##### ③ `monkeypatch`：测试期间临时替换东西
参数里写 `monkeypatch`。它改的东西在测试结束后会**自动恢复**。
```python
import os
import math

def test_setattr(monkeypatch):
    # 把 math 模块的 pi 属性临时换成 3
    monkeypatch.setattr(math, "pi", 3)
    assert math.pi == 3          # 测试结束后 math.pi 自动恢复

def test_setenv(monkeypatch):
    # 临时设置一个环境变量
    monkeypatch.setenv("MY_SETTING", "abc")
    assert os.environ["MY_SETTING"] == "abc"
```
`setattr(对象, "属性名", 新值)` 可以替换模块、类或对象上的任何属性，包括函数和方法。

##### ④ 假的 HTTP 响应
`fetch_slot` 通过模块里的 `session.get(...)` 发请求，只用到了返回对象的 `.status_code` 和 `.content`。所以可以用一个只有这两个属性的对象代替真正的响应：
```python
from types import SimpleNamespace
import requests

fake = SimpleNamespace(status_code=200, content=b"\x01\x02")
print(fake.status_code, fake.content)    # 200 b'\x01\x02'

def fake_get(url, **kwargs):              # **kwargs 接收 timeout= 等关键字参数
    return SimpleNamespace(status_code=429, content=b"")

def fake_get_timeout(url, **kwargs):
    raise requests.Timeout("simulated timeout")
```
然后用 ③ 把 `session` 的 `get` 换成你的假函数：`monkeypatch.setattr(某个对象, "get", fake_get)`。想一想"某个对象"应该是什么。

##### ⑤ 造一个合法的 GTFS Realtime 消息
```python
from google.transit import gtfs_realtime_pb2

msg = gtfs_realtime_pb2.FeedMessage()
msg.header.gtfs_realtime_version = "2.0"
msg.header.timestamp = 1792684815
entity = msg.entity.add()          # 新增一个 entity
entity.id = "1"
entity.vehicle.vehicle.id = "TEST123"
entity.vehicle.position.latitude = 3.1
entity.vehicle.position.longitude = 101.6
body = msg.SerializeToString()     # bytes，和 API 返回的格式一样
print(len(body), len(msg.entity))

empty = gtfs_realtime_pb2.FeedMessage()
empty.header.gtfs_realtime_version = "2.0"
empty_body = empty.SerializeToString()   # 有 header，没有 entity
```

##### ⑥ 读 `.jsonl`（每行一个 JSON）
```python
import json
lines = path.read_text(encoding="utf-8").splitlines()
records = [json.loads(line) for line in lines]
assert len(records) == 2
assert records[-1]["status"] == "ok"
```

##### ⑦（可选）一次测多组输入：`parametrize`
```python
import pytest

@pytest.mark.parametrize("a, b, expected", [(1, 2, 3), (0, 0, 0), (-1, 1, 0)])
def test_add_many(a, b, expected):
    assert a + b == expected
```

##### ⑧ 第 6 步的命令在做什么
`git status --ignored --short` 列出仓库里所有"还没提交"和"被 `.gitignore` 忽略"的文件和目录，每行前面两个字符表示类别：
```text
?? tests/          还没提交过的新文件或目录（untracked）
!! .venv/          被 .gitignore 忽略的文件或目录（ignored）
```
注意：被忽略的文件用普通的 `git status` 看不到，所以这里要加 `--ignored`。

pytest 前后各拍一张"快照"，再用 `diff` 比较：
- `diff 文件1 文件2`：两个文件相同时不输出任何东西、退出码为 0；不同时打印不同的行（`>` 开头的行只在第二个文件里有）。
- `&& echo "SAME"`：只有前一个命令退出码为 0 时才执行，所以打印 `SAME` 就代表两次快照完全相同。

运行 pytest 时加的两个设置：Python 和 pytest 平时会自己写一些缓存文件（`__pycache__/`、`.pytest_cache/`），它们和你的测试无关。
- `PYTHONDONTWRITEBYTECODE=1`：这一次运行不写 `__pycache__/`（写在命令前面的 `变量=值` 只对这一条命令有效）。
- `-p no:cacheprovider`：这一次运行不写 `.pytest_cache/`。

这样两次快照之间如果多出任何东西，只可能是测试代码自己写的。

延伸阅读（可选，不读也能完成）：pytest 官方文档 https://docs.pytest.org/en/stable/how-to/tmp_path.html 、 https://docs.pytest.org/en/stable/how-to/monkeypatch.html
