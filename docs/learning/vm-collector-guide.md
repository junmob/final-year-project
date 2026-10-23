# 云端采集 VM 教学手册

> 写于 2026-10-23，对应 `ingestion/` 目录的现有代码和 AWS EC2 上正在运行的采集服务。本文是给自己学习用的内部文档（中文），不提交学校。
>
> **读法建议**：先读第 1、2 节建立整体印象；然后边读第 5–9 节边打开对应的代码文件对照；第 10 节的命令可以直接复制到 WSL 终端里跑；最后做第 13 节的练习，确认自己真的懂了。

## 目录

1. [为什么需要一台云端 VM](#1-为什么需要一台云端-vm)
2. [名词表](#2-名词表)
3. [VM 本身：重要参数](#3-vm-本身重要参数)
4. [怎么连接 VM：SSH](#4-怎么连接-vmssh)
5. [文件都在哪里：本地仓库与 VM](#5-文件都在哪里本地仓库与-vm)
6. [怎么把代码放上去运行](#6-怎么把代码放上去运行)
7. [systemd：让程序自己一直跑](#7-systemd让程序自己一直跑)
8. [采集代码的通用逻辑](#8-采集代码的通用逻辑)
9. [每种数据源的具体做法](#9-每种数据源的具体做法)
10. [怎么检查：日常巡检手册](#10-怎么检查日常巡检手册)
11. [安全注意事项](#11-安全注意事项)
12. [还没做、之后要做的采集策略](#12-还没做之后要做的采集策略)
13. [练习题](#13-练习题)

---

## 1. 为什么需要一台云端 VM

先记住三个事实：

1. **API 只给"此刻"的数据。**GTFS Realtime 每次只返回当下所有车辆的位置，没有"查询昨天 08:00"的历史接口。天气预报也一样。**没在那一刻抓下来的数据，就永远没有了。**
2. **你的电脑不能 24 小时开机。**
3. **处理数据需要大内存（Spark、ClickHouse 等），但采集只需要很少的资源。**

所以项目分成两个节点：

```
            24 小时运行（便宜、小）                     需要时才开机（16 GB 电脑）
┌──────────────────────────────────┐         ┌──────────────────────────────────┐
│  云端 VM（AWS EC2 t3.micro）        │         │  本地电脑（WSL + Docker）            │
│                                    │  拉取   │                                    │
│  采集程序 ──→ 磁盘上的 Bronze 文件  │ ──────→ │  bronze_sync → MinIO → Spark        │
│  （只负责"抓下来、存好"）           │（还没做）│  → Iceberg → ClickHouse → 看板      │
└──────────────────────────────────┘         └──────────────────────────────────┘
         ↑ 每 15 秒请求一次
   api.data.gov.my
```

VM 的工作非常单纯：**按时请求、原样存档、记录每一次请求的结果。**它不解析、不清洗、不算指标，这些都留给本地。好处是：
- VM 需要的资源很少，1 GB 内存的免费或便宜 VM 就够；
- 采集代码越简单，越不容易出错，而采集一旦出错，数据是补不回来的；
- 原始文件原样保存，以后清洗逻辑写错了，可以从原始文件重新算（这叫"可回放"）。

这里的原则叫**"先落盘，再处理"**：数据先完整地写到磁盘上，之后的一切处理都从这些文件开始。这些原始文件所在的层叫 **Bronze**，它是整个数据系统的**唯一事实来源**。

---

## 2. 名词表

| 名词 | 意思 |
|---|---|
| **VM**（Virtual Machine，虚拟机） | 云服务商在它的机房里分给你的一台"虚拟电脑"。你看不到实体机器，只能通过网络登录操作 |
| **EC2** | AWS 的虚拟机服务名称。"一台 EC2 实例"就是一台 VM |
| **SSH** | 安全登录远程电脑的协议。你在 WSL 里输入 `ssh fyp-collector`，之后输入的命令都在 VM 上执行 |
| **密钥对**（key pair） | SSH 登录用的一对文件，用来代替密码证明身份。`.pem` 文件是**私钥**，只在你手里；VM 上存着对应的**公钥**。私钥泄露后，任何拿到它的人都能登录这台 VM |
| **systemd** | Ubuntu 管理后台程序的系统。它负责开机自动启动程序、程序崩溃后重启、按时间表运行任务 |
| **service / timer** | systemd 的两种配置文件。service 描述"运行什么程序"；timer 描述"什么时候运行" |
| **Bronze** | 原始数据层：API 返回什么就存什么，不修改 |
| **哈希**（hash，这里用 SHA-256） | 把任意内容算成一串固定长度的"指纹"。内容完全相同，指纹一定相同；内容哪怕差一个字节，指纹就完全不同。用来判断"这次的数据和上次一样吗" |
| **manifest**（清单） | 记录"这一批数据里有哪些文件、每个文件的指纹是什么"的文件。用来校验文件是否完整、有没有被改动 |
| **原子写入** | 先写到临时文件 `xxx.tmp`，写完再一次性改名为正式文件名。这样任何时刻都不会出现"写到一半"的正式文件 |
| **幂等**（idempotent） | 同一个操作执行一次和执行很多次，结果一样。例如打包脚本重跑不会重复打包 |
| **限流**（rate limit） | API 规定的请求频率上限。data.gov.my 是每个 API 类别每分钟 4 次 |
| **MYT / UTC** | 马来西亚时间（UTC+8）/ 世界标准时间。VM 的系统时间是 UTC |
| **分区**（partition） | 按某个字段把文件分到不同目录，例如 `date=2026-10-22/`。以后查某一天的数据只要读那个目录 |

---

## 3. VM 本身：重要参数

| 参数 | 值 | 为什么重要 |
|---|---|---|
| 云服务商 | AWS，Free Plan 账户 | 赠送额度用完或到期后账户会关闭、资源会被删除 |
| **账户到期日** | **2027-04-22** | 之前必须把采集迁走，并把全部数据拉回本地（§12.6） |
| 区域 | **ap-southeast-2（悉尼）** | Free Plan 的项目被锁在悉尼。到 api.data.gov.my 的延迟约 200 ms，可以接受 |
| 实例 ID / 名称 | `i-0cf3e2c00b50bcf02` / `gtfs-collector` | 在 AWS 控制台找这台机器用 |
| 规格 | **t3.micro**：2 vCPU、1 GiB 内存 | 内存很小，所以 VM 上只跑采集，另外加了 1 GB swap |
| 系统 | Ubuntu 24.04 LTS，x86_64，Python 3.12 | |
| 磁盘 | 16 GiB gp3（已用约 3.7 GB） | 数据增长约每月 0.4 GB，用到 2027-04 足够 |
| **公网 IPv4** | `52.62.231.252` | SSH 连接的地址。**注意：没有绑定固定 IP，如果在控制台把实例"停止"再"启动"，这个 IP 会变**（重启 reboot 不会变）。变了就要改 `~/.ssh/config` 里的 `HostName` |
| 删除保护、停止保护 | 都已开启（2026-10-23） | 防止在控制台误点 Terminate 或 Stop。Stop 会中断采集，而且重新启动后公网 IP 会变。VM 从内部重启（reboot）不受影响。**真要停机或迁移时，先在 Actions → Instance settings 里把两个保护关掉** |
| 安全组 | `launch-wizard-1`：只允许你家的 IP（175.136.109.166/32）通过 SSH 端口 22 连入 | 这是 VM 的"防火墙"。家里宽带的 IP 变了就会连不上，要到 EC2 → Security Groups → 编辑入站规则，重新选 "My IP" |
| 用户名 | `ubuntu` | Ubuntu 镜像的默认用户 |
| 时间同步 | chrony（NTP），已同步 | 文件名和时间槽都依赖准确的时钟 |
| 费用估算 | 约 15 美元/月（实例约 9.6 + 公网 IPv4 约 3.6 + 磁盘约 1.9） | 从赠送额度里扣；已设置预算提醒 |

**不要做的事**：不要在 AWS 控制台点 "Upgrade plan" 或 "Activate advanced features"。那会把账户转成付费账户。

---

## 4. 怎么连接 VM：SSH

### 4.1 原理

SSH 用的是**公钥/私钥**：
- 创建 VM 时，AWS 生成了一对密钥：公钥放进 VM（`~/.ssh/authorized_keys`），私钥就是你下载的 `fyp-collector.pem`。
- 你连接时，SSH 用私钥证明"我持有与 VM 上公钥配对的私钥"，VM 用公钥验证。整个过程不需要密码，私钥本身也不会在网络上传输。

### 4.2 你电脑上的设置

私钥放在 `~/.ssh/fyp-collector.pem`，权限是 `600`（只有你自己能读写）。SSH 会拒绝使用权限太宽的私钥，所以如果看到 `UNPROTECTED PRIVATE KEY FILE` 错误，执行：

```bash
chmod 600 ~/.ssh/fyp-collector.pem
```

为了不用每次输入长命令，`~/.ssh/config` 里有一个别名：

```
Host fyp-collector
    HostName 52.62.231.252              # VM 的公网 IP
    User ubuntu                         # 登录用户
    IdentityFile ~/.ssh/fyp-collector.pem   # 私钥
    ServerAliveInterval 60              # 每 60 秒发一次心跳，避免连接闲置时被断开
```

有了它，下面两条命令是等价的：

```bash
ssh -i ~/.ssh/fyp-collector.pem ubuntu@52.62.231.252
ssh fyp-collector
```

### 4.3 两种用法

```bash
# ① 登录进去，像在 VM 上开了一个终端（输入 exit 退出）
ssh fyp-collector

# ② 不登录，只在 VM 上执行一条命令，结果显示在本地
ssh fyp-collector 'df -h /'
```

### 4.4 连不上时怎么办

| 现象 | 原因 | 处理 |
|---|---|---|
| 一直卡住，最后 `Connection timed out` | ① 家里 IP 变了，被安全组挡住；② VM 被停止后再启动，公网 IP 变了 | ① 改安全组的 "My IP"；② 在控制台查看新 IP，改 `~/.ssh/config` |
| `Permission denied (publickey)` | 私钥文件不对，或者用户名不是 `ubuntu` | 检查 `IdentityFile` 路径和 `User` |
| `UNPROTECTED PRIVATE KEY FILE` | 私钥权限太宽 | `chmod 600 ~/.ssh/fyp-collector.pem` |
| 第一次连接问 `Are you sure you want to continue connecting?` | SSH 第一次见到这台机器，要你确认它的指纹 | 输入 `yes`。之后如果突然又问，或者提示指纹变了，说明 IP 背后换了机器，要先弄清楚原因 |

---

## 5. 文件都在哪里：本地仓库与 VM

### 5.1 本地仓库（`~/final-year-project`）

| 路径 | 作用 |
|---|---|
| `ingestion/collect_gtfs_rt.py` | **RT 采集器**：常驻程序，每 15 秒请求一次 Realtime |
| `ingestion/pack_gtfs_rt.py` | **RT 每日打包**：把前一天的几千个小文件打成一个压缩包，并生成 manifest |
| `ingestion/download_gtfs_static.py` | **Static 每日检查**：下载 3 个 ZIP，只存内容变化了的文件 |
| `ingestion/download_weather.py` | **天气**：预报和警告，只存内容变化了的响应 |
| `ingestion/download_ridership.py` | **Rapid Rail OD 客流**：文件变化时才下载，保留每个版本 |
| `ingestion/requirements.txt` | VM 上要安装的 Python 套件：requests、gtfs-realtime-bindings、zstandard |
| `ingestion/deploy/*.service`、`*.timer` | systemd 配置：每个程序怎么运行、什么时候运行（§7） |
| `ingestion/deploy/install.sh` | 在一台全新 VM 上一键安装（§6.2） |
| `ingestion/bronze_sync.py` | **在本地电脑运行**：把 VM 上的 Bronze 拉回本地并校验（§12.1） |
| `.github/workflows/backup_gtfs.yml` | GitHub Actions 每天也检查一次 Static，作为**另一个地方的备份**，结果提交到仓库的 `data/github-backup/gtfs_static/` |
| `.github/workflows/weather_archive.yml` | VM 上线前的临时天气归档；和 VM 并行几天核对后删除 |
| `data/github-backup/` | GitHub Actions 备份任务存下的数据（会提交到 git） |

所有采集脚本都读一个环境变量 `BRONZE_DIR`，决定数据存到哪里：
- 在 VM 上：`BRONZE_DIR=/home/ubuntu/fyp-data/bronze`（systemd 配置里设定）；
- 在 GitHub Actions 上：`BRONZE_DIR=data/github-backup`（workflow 里设定），结果提交到仓库；
- 在本地直接运行脚本做测试时：没有设定，默认存到仓库的 `data/bronze/`，这个目录被 `.gitignore` 排除，不会进 git。

> **几个"Bronze"目录的区别**：概念上都是"原始数据，原样保存"，区别只在**放在哪里、给谁用**：
> - VM 的 `~/fyp-data/bronze/`：**正本**，采集程序写在这里；
> - 本地的 `~/fyp-data/bronze/`：`bronze_sync` 拉回来的**副本**，布局和 VM 一模一样（在仓库外面，不进 git）；
> - 仓库的 `data/github-backup/`：GitHub Actions 在另一个地方做的**备份**，只有 Static 和（暂时的）天气；
> - 仓库的 `data/bronze/`：只是本地测试脚本时的默认位置，平时是空的。

**同一份代码，靠一个环境变量适配不同环境**，这是常见的做法，避免复制出两份代码。

### 5.2 VM 上的目录

```
/home/ubuntu/
├── fyp/                         ← 代码（从本地用 rsync 同步过来，只有 ingestion/）
│   ├── ingestion/
│   └── .venv/                   ← Python 虚拟环境（VM 上自己安装的）
└── fyp-data/
    └── bronze/                  ← 所有采集到的数据
        ├── gtfs_rt/
        │   ├── feed=rapid-bus-kl/date=2026-10-23/hour=09/20261023T010000Z.pb   ← 今天的零散文件
        │   ├── feed=rapid-bus-mrtfeeder/...
        │   └── _packs/feed=rapid-bus-kl/date=2026-10-22/rt.tar.zst + manifest.json  ← 已打包的往日数据
        ├── gtfs_static/rapid-bus-kl/blobs/… + snapshots.jsonl
        ├── weather_forecast/date=…/fetched_at=…json.gz + manifest.json + fetch_log.jsonl
        ├── weather_warning/（同上）
        ├── ridership_rapidrail/year=2026/downloaded=…/fetched_at=…parquet + versions.jsonl
        └── _health/feed_health_2026-10-23.jsonl                ← RT 每次请求一行

/etc/systemd/system/             ← systemd 配置文件（从 ingestion/deploy/ 复制过来）
/swapfile                        ← 1 GB 交换空间
```

**为什么代码和数据分开放？**部署新代码时，`rsync --delete` 会让 `~/fyp/ingestion/` 和本地完全一致（多余的文件会被删掉）。如果数据也放在 `~/fyp/` 里，一个错误的同步命令就可能删掉数据。分开放之后，代码随时可以整个覆盖，数据永远不受影响。

### 5.3 为什么目录名是 `date=2026-10-22` 这种写法？

这叫 **Hive 风格分区**：目录名本身就写着"字段名=值"。Spark、Iceberg、ClickHouse 都认识这种写法，读取时可以直接把目录名变成一列，也可以只读某几天的目录（这叫"分区裁剪"）。以后本地处理时会用到。

---

## 6. 怎么把代码放上去运行

### 6.1 同步代码：rsync

```bash
cd ~/final-year-project
rsync -az --delete --exclude __pycache__ ingestion fyp-collector:fyp/
```

逐个解释：
- `rsync`：只传送有变化的部分，比整个复制快；
- `-a`（archive）：保留文件权限、时间等属性，并递归子目录；
- `-z`：传输时压缩；
- `--delete`：本地删掉的文件，VM 上也删掉，保证两边一致；
- `--exclude __pycache__`：不传 Python 的缓存文件；
- `ingestion`（结尾没有 `/`）：把整个 `ingestion` 目录传过去；
- `fyp-collector:fyp/`：目标是 VM 上的 `~/fyp/`，所以最终路径是 `~/fyp/ingestion/`。

> 小心结尾的 `/`：`ingestion/` 表示"目录里面的内容"，`ingestion` 表示"目录本身"。写错会把文件放到错的层级。

### 6.2 第一次安装：`install.sh`

这个脚本在一台全新的 Ubuntu VM 上运行一次（`ssh fyp-collector 'bash ~/fyp/ingestion/deploy/install.sh'`），做了这些事：

1. `apt-get install python3-venv zstd`：安装建立虚拟环境的工具，以及 zstd 压缩工具（方便手动解压检查）。
2. **建立 1 GB swap**：swap 是"用磁盘假装内存"。VM 只有 1 GB 内存，偶尔内存不够时，有 swap 系统会变慢而不是直接杀掉程序。
3. `python3 -m venv ~/fyp/.venv`：建立**虚拟环境**，让这个项目的 Python 套件和系统自带的 Python 互不干扰。
4. `pip install -r requirements.txt`：在虚拟环境里安装套件。
5. 把 `deploy/` 里的 service 和 timer 复制到 `/etc/systemd/system/`，然后 `systemctl daemon-reload`（让 systemd 重新读配置），再 `systemctl enable --now …`（设成开机自启，并且立刻启动）。

脚本写成"重复运行也安全"：例如已经有 swap 就跳过。以后迁移到新 VM（§12.6），只要同步代码、运行这一个脚本就能装好。

### 6.3 以后改了代码怎么更新

| 改了什么 | 要做什么 |
|---|---|
| `collect_gtfs_rt.py`（常驻程序） | rsync 后**必须重启**：`ssh fyp-collector sudo systemctl restart gtfs-rt-collector`。常驻程序只在启动时读一次代码 |
| 其他脚本（timer 触发的） | 只要 rsync。下一次 timer 触发时，会自动用新代码 |
| `requirements.txt` | rsync 后运行 `ssh fyp-collector '~/fyp/.venv/bin/pip install -r ~/fyp/ingestion/requirements.txt'` |
| `.service` 或 `.timer` 文件 | rsync 后复制到 `/etc/systemd/system/`，执行 `sudo systemctl daemon-reload`，再重启对应的 service 或 timer |

> 重启 RT 采集器会损失一两个时间槽（大约 10–15 秒），健康日志里会显示为没有记录。所以不要频繁重启，改动攒在一起做。

---

## 7. systemd：让程序自己一直跑

### 7.1 两类程序

| 类型 | 例子 | systemd 配置 |
|---|---|---|
| **常驻程序**：一直在跑 | RT 采集器 | 只有 `.service`，加上 `Restart=always` |
| **定时任务**：跑完就结束，按时间表再跑 | 打包、Static、天气、客流 | `.service`（`Type=oneshot`）+ 同名的 `.timer` |

### 7.2 RT 采集器的 service 文件（逐行解释）

```ini
[Unit]
Description=GTFS Realtime collector (rapid-bus-kl, rapid-bus-mrtfeeder)
After=network-online.target time-sync.target   # 等网络通了、时间同步了再启动
Wants=network-online.target

[Service]
User=ubuntu                                     # 用普通用户运行，不用 root（更安全）
WorkingDirectory=/home/ubuntu/fyp
ExecStart=/home/ubuntu/fyp/.venv/bin/python ingestion/collect_gtfs_rt.py   # 用虚拟环境里的 Python
Environment=PYTHONUNBUFFERED=1                  # print 立刻输出到日志，不缓存
Environment=BRONZE_DIR=/home/ubuntu/fyp-data/bronze   # 告诉程序数据存哪里
Restart=always                                  # 程序崩溃就自动重启
RestartSec=10                                   # 等 10 秒再重启，避免疯狂重启
MemoryMax=300M                                  # 内存上限，防止程序失控吃光 VM 的内存

[Install]
WantedBy=multi-user.target                      # 开机进入正常模式时启动它
```

### 7.3 定时任务：timer 文件

以天气警告为例：

```ini
[Timer]
OnCalendar=*-*-* *:35:00 Asia/Kuala_Lumpur   # 每天每小时的 35 分（马来西亚时间）
Persistent=true                              # 如果 VM 关机错过了某次，开机后补跑一次
RandomizedDelaySec=30                        # 随机延后 0–30 秒，避免几个任务挤在同一秒
```

`OnCalendar` 的格式是 `星期 年-月-日 时:分:秒 时区`：
- `*-*-* 04:17:00`：每天 04:17；
- `*-*-* 00/3:05:00`：从 0 点开始每 3 小时，在 05 分运行（00:05、03:05、06:05……）；
- `*-*-* *:35:00`：每小时的 35 分。

VM 的系统时间是 UTC，但我们在 `OnCalendar` 后面直接写了 `Asia/Kuala_Lumpur`，所以不用自己换算时区。

**为什么各个任务的分钟数错开**（:05、:35、:50）？天气预报和天气警告属于同一个 API 类别，共用每分钟 4 次的限额，错开就不会同时请求。

### 7.4 现在 VM 上的全部任务

| 名称 | 类型 | 时间（MYT） | 做什么 |
|---|---|---|---|
| `gtfs-rt-collector.service` | 常驻 | 每 15 秒 | RT 轮询 |
| `gtfs-rt-pack.timer` | 定时 | 每天 00:30 | 打包前一天的 RT |
| `fyp-static.timer` | 定时 | 每天 04:17 | Static 检查 |
| `fyp-weather-forecast.timer` | 定时 | 每 3 小时的 :05 | 天气预报 |
| `fyp-weather-warning.timer` | 定时 | 每小时的 :35 | 天气警告 |
| `fyp-ridership.timer` | 定时 | 每 3 小时的 :50 | 客流文件 |

**为什么不全部写进一个大程序？**设计书原本写的是"一个常驻进程包含所有模块"。实际实现时拆成了独立的任务：天气脚本出了 bug，最多是天气这一项失败，**绝对不会把 RT 采集拖垮**。RT 是最重要、也最不能中断的数据。

---

## 8. 采集代码的通用逻辑

每个采集脚本都遵循同一个套路：

```
① 请求 API
② 检查响应是否完整、合法
③ 计算内容指纹（SHA-256）
④ 和上一次保存的指纹比较 ──→ 一样：不存文件，只记一行日志
⑤ 不一样：原子写入新文件
⑥ 记录这一次的结果（成功、失败、没变化），无论如何都记
```

下面逐个解释这些步骤背后的道理。

### 8.1 请求：注意网址结尾的 `/`

`https://api.data.gov.my/gtfs-realtime/vehicle-position/prasarana?category=...` 这个网址（没有 `/`）会先返回 **301 重定向**，告诉你"请改用 `.../prasarana/?category=...`"。`requests` 会自动跟过去，**但这等于每次发了两个请求**，可能浪费限额。所以代码里直接写带 `/` 的网址。这是部署时用 `curl -sI` 查到的（§10.5 有这个命令）。

### 8.2 检查响应

不能只看 HTTP 200。每种数据的检查方式不同：
- RT：用 Protobuf 解析一次，确认是合法的 `FeedMessage`（§9.1）；
- Static：用 `zipfile` 测试 ZIP 是否完整（`testzip()`）；
- 天气：`resp.json()` 能解析成 JSON；
- 客流：Parquet 文件的开头和结尾都必须是 `PAR1` 这 4 个字节（Parquet 格式规定的"魔数"），否则就是下载不完整。

### 8.3 指纹：怎么做到"只存有变化的数据"

**SHA-256** 会把任意内容算成 64 个十六进制字符，例如：

```
600ca63b60d44eb5fdb6998a662faf2296890f2e1dadd4caf2dc5180bbcbf33a
```

性质：
- 同样的内容，每次算出来的指纹一样；
- 内容只要差一个字节，指纹就完全不同；
- 几乎不可能有两份不同的内容算出同一个指纹。

所以"判断这次的数据和上次一样吗"，不用逐字节比较两个大文件，**只要比较两串指纹**。上一次的指纹存在一个小文件里（天气是 `manifest.json`，Static 是 `snapshots.jsonl` 的最后一行，客流是 `versions.jsonl` 的最后一行）。

Python 里就是一行：

```python
import hashlib
digest = hashlib.sha256(data_bytes).hexdigest()
```

**一个陷阱：内容一样，字节却不一样。**例如 JSON 的键顺序变了、多了空格，意思完全相同，但字节不同，指纹也就不同。天气脚本的处理是：先把 JSON 解析出来，再用固定规则（键排序）重新序列化，然后才算指纹。这叫**规范化**（canonicalisation）：

```python
canonical = json.dumps(data, ensure_ascii=False, sort_keys=True).encode()
digest = hashlib.sha256(canonical).hexdigest()
```

Static 遇到的是另一种陷阱：ZIP 包重新打包时，里面的文件时间戳会变，所以**整个 ZIP 的指纹每天都不同**，即使时刻表根本没改。解决方法是拆开 ZIP，**按里面每个文件分别算指纹**（§9.3）。

### 8.4 原子写入

```python
tmp = path.with_name(path.name + ".tmp")
tmp.write_bytes(data)   # 先写临时文件
tmp.replace(path)       # 一步改名为正式文件名
```

如果写到一半断电或程序崩溃，最多留下一个 `.tmp` 文件，正式文件名下要么是完整的文件，要么根本没有文件。**下游程序永远不会读到写了一半的文件。**改名（`replace`）在同一个磁盘内是"原子"操作：要么完成，要么没发生，不存在中间状态。

### 8.5 每次都留下记录

即使请求失败、或者内容没变化，也要写一行记录（RT 是 `_health/*.jsonl`，天气是 `fetch_log.jsonl`）。原因：
- 能区分"那一刻采集失败"和"那一刻内容本来就没变"；
- 能算出可用率（成功次数 ÷ 应有次数）；
- 写报告时可以拿这些记录当证据。

记录用 **JSON Lines**（`.jsonl`）格式：每行一个 JSON 对象。好处是只要在文件末尾追加一行，不用读写整个文件；某一行坏了也不影响其他行。

### 8.6 时间规则

- **目录分区用马来西亚时间**：`date=2026-10-22` 指的是马来西亚的 10 月 22 日，因为业务（巴士运营日）是按当地时间算的。
- **RT 文件名用 UTC**：`20261022T155930Z.pb`，结尾的 `Z` 表示 UTC。UTC 没有时区歧义，适合当唯一标识。
- VM 系统时钟是 UTC，由 chrony 自动和标准时间同步。

### 8.7 失败了要不要重试？

| 数据 | 重试吗 | 原因 |
|---|---|---|
| RT | **不重试** | 限额每分钟 4 次已经用满，重试会挤掉下一次正常请求；而且 API 只给"此刻"，晚 10 秒拿到的已经是下一刻的数据，没有意义 |
| Static | 重试最多 3 次，每次间隔 60 秒 | Static 有自己独立的限额；一天只检查一次，失败一次就等于当天没检查 |
| 天气、客流 | 不在脚本内重试 | 下一次定时任务很快会再跑（1–3 小时），日志里会留下失败记录 |

---

## 9. 每种数据源的具体做法

### 9.1 GTFS Realtime（`collect_gtfs_rt.py`）

**时间槽怎么排**

两个 feed（kl、feeder）各要每 30 秒一次，合计每分钟 4 次，正好用满限额。做法是把时间切成 **15 秒一格的时间槽**，两个 feed 轮流用：

```
时间:   :00    :15    :30    :45    :00 ...
feed:   kl     feeder kl     feeder kl  ...
```

代码里的计算：

```python
slot_ts = (int(time.time()) // 15 + 1) * 15     # 下一个 15 秒整点
feed = FEEDS[(slot_ts // 15) % 2]               # 第几个时间槽，单数给 feeder、双数给 kl
```

例如现在是 `…:07` 秒，`… // 15 + 1` 得到下一个格子，乘回 15 就是 `…:15`。程序睡到那一刻才发请求。因为是按**绝对时间**计算的，所以即使程序重启，两个 feed 的节奏也不会乱。

请求的超时设为 10 秒，小于一个时间槽。如果某次请求太慢错过了下一个槽，那个槽就直接放弃，不补发（§8.7）。

**每次请求的结果分类**

| 状态 | 意思 |
|---|---|
| `ok` | 成功，有车辆数据 |
| `ok_empty` | 成功，但没有车辆（深夜 kl 常见），这不算故障 |
| `parse_error` | 返回 200 但无法解析为 Protobuf；原始内容存到 `_invalid/` 以便检查 |
| `http_error` | HTTP 状态不是 200，或内容为空 |
| `rate_limited` | HTTP 429，超过限额 |
| `timeout` | 超过 10 秒没响应 |
| `network_error` | DNS 或连接失败 |
| `write_error` | 写磁盘失败（例如磁盘满了） |

**健康日志的一行长这样**：

```json
{"slot_utc": "2026-10-21T17:44:00+00:00", "feed": "rapid-bus-kl", "instance": "ip-172-31-47-41",
 "requested_at_utc": "2026-10-21T17:44:00.001+00:00", "status": "ok_empty", "http_status": 200,
 "latency_ms": 337, "bytes": 15, "sha256": "600ca63b…", "entities": 0, "header_ts": 1792604612,
 "file": "gtfs_rt/feed=rapid-bus-kl/date=2026-10-22/hour=01/20261021T174400Z.pb", "error": null}
```

- `instance` 是 VM 的主机名。以后迁移到新 VM 时，可以看出哪段数据是哪台机器采的。
- `header_ts` 是 feed 自己声明的生成时间，和 `requested_at_utc` 对比，可以知道数据源本身的延迟。

**断档怎么算**：每个 feed 每天应该有 86400 ÷ 30 = **2880** 个时间槽。拿这个"应有网格"去对照健康日志，没有记录的槽就是断档（例如 VM 宕机期间），连日志都没有的情况也能被统计出来。

**为什么 RT 不做去重？**每次快照都代表"那一刻的观测"，即使内容和上一次一模一样，也说明"车辆位置 30 秒内没更新"，这本身就是信息。而且相邻快照高度相似，打包压缩时会被压得很小（§9.2），存储成本不高。去重留到本地 Silver 层按"车辆 + 时间戳"去做。

### 9.2 RT 每日打包（`pack_gtfs_rt.py`）

**为什么要打包？**

RT 每天产生 2 × 2880 = **5760 个小文件**，一年超过 200 万个。小文件太多会带来几个问题：
- 同步到本地时，每个文件都要单独比对和传输，非常慢；
- 文件系统管理大量小文件的效率很低；
- 一个约 8 KB 的 Protobuf 文件，单独压缩效果很差；而几千个相似的文件放在一起压缩，可以压到原来的 1/5 到 1/7。

**打包的意思**是：每天 00:30，把**前一天**的所有 `.pb` 文件放进一个包里压缩，生成 manifest（文件清单），确认无误后删掉零散文件。

- **tar**：把很多文件串成一个文件，本身不压缩；
- **zstd**（`.zst`）：一种又快、压缩率又高的压缩算法；
- 所以 `rt.tar.zst` = 先用 tar 合并成一个文件、再用 zstd 压缩。

**步骤（顺序很重要）**

```
① 找出所有"日期早于今天"、还有零散文件的 feed 和日期（绝不打包今天，因为今天还在写入）
② 计算每个零散文件的 SHA-256
③ 写入 rt.tar.zst（先写 .tmp，完成后改名，§8.4）
④ 重新打开压缩包，逐个读出里面的文件、重新计算 SHA-256，和 ② 的结果比对
    └─ 不一致 → 删掉这个坏的包，零散文件保留，报错退出
⑤ 写 manifest.json（文件清单）
⑥ 逐个删除零散文件：只删"指纹和 manifest 记录一致"的文件
```

关键在 ④：**先证明包里的东西完好，才删除原件。**这样任何一步出错，都不会丢数据。

**manifest.json 的内容**（10-22 kl 的真实例子，`files` 部分省略）：

```json
{
 "feed": "rapid-bus-kl", "date_myt": "2026-10-22",
 "pack_sha256": "e4ec9396…", "pack_bytes": 2892499, "raw_bytes": 20575914,
 "file_count": 2672,
 "first_file": "hour=01/20261021T174400Z.pb", "last_file": "hour=23/20261022T155930Z.pb",
 "expected_slots": 2880, "recorded_slots": 2672, "no_record_slots": 208,
 "status_counts": {"ok": 2278, "ok_empty": 394},
 "files": [{"name": "hour=01/20261021T174400Z.pb", "sha256": "600ca63b…"}, …]
}
```

可以读出：原始 20.6 MB 压成 2.9 MB（约 7 倍）；208 个没有记录的槽，正好是采集器 01:44 才启动之前的 104 分钟（104 × 2）；当天其余时间零失败。

**重跑安全（幂等）**：如果某一天已经有 manifest，脚本不会重新打包，只会重新校验，并清理可能残留的零散文件（例如上次删到一半时 VM 断电）。在 manifest 里找不到的零散文件不会被删除，只会被报告出来。

### 9.3 GTFS Static（`download_gtfs_static.py`）

**难点**（summary §3.7.1 的实测发现）：
- mrtfeeder 每天重新导出 `calendar.txt`，起始日期跟着下载日期滚动，所以**ZIP 每天都"变"**，但时刻表并没有改（伪版本）；
- rapid-rail-kl 的 ZIP 里夹带 macOS 打包时产生的垃圾文件（`__MACOSX/`），每次打包都不同；
- 但 rapid-bus-kl 确实会在两天内真的修改 `frequencies.txt` 和 `stop_times.txt`。

所以不能用"整个 ZIP 的指纹"来判断，要**拆开、按文件比较**。

**做法：内容寻址存储**（content-addressed storage）

```
gtfs_static/rapid-bus-kl/
├── blobs/
│   ├── 4f/4f2e84f9…c49.gz        ← agency.txt 的内容，文件名就是内容的指纹
│   ├── 79/793fd8a6…18aea.gz      ← calendar.txt 的内容
│   └── …
└── snapshots.jsonl               ← 每天一行：这一天 ZIP 里每个文件对应哪个指纹
```

- 每个文件的内容以**它自己的指纹为文件名**存进 `blobs/`（前两个字符作为子目录，避免一个目录下文件太多）。
- 如果某个指纹的 blob 已经存在，说明这个内容以前存过，**直接跳过，不重复存**。这就是去重。
- `snapshots.jsonl` 每天追加一行，记录：检查时间、整个 ZIP 的指纹、**每个文件名 → 指纹**、哪些文件和上一次不同（`changed_files`）、哪些是垃圾文件（`junk_files`）。

**要还原任意一天的完整 Static**：找到那天的那一行，按里面列出的指纹，从 `blobs/` 取出每个文件并解压即可。（ZIP 外壳本身的时间戳等不保留，只保留内容。）

**哪些变化算"真正的新版本"**，Bronze 层不做判断，只负责忠实记录。判断留给 Silver 层的 SCD2 处理：按实体比较，忽略起始日期滚动和行顺序变化（设计书 §6 D3）。

### 9.4 天气预报和警告（`download_weather.py`）

- 预报一次请求就返回全国 7 天的预报（3080 行，约 0.9 MB，gzip 后约 24 KB）。
- **没有历史接口**，而且预报一天之内会被修订，所以每 3 小时检查一次。警告变化更快，每小时检查一次。
- 用**规范化 JSON 的指纹**判断是否变化（§8.3）。
- `manifest.json` 只存"最后一次保存的指纹和文件名"；`fetch_log.jsonl` 记录**每一次**尝试的结果（`changed`、`unchanged`、`failed`）。以后可以用这份日志推算"官方大概几点更新预报"（V01 还没确认的问题）。
- 保存的是**原始响应**（gzip 压缩，`mtime=0` 让同样的内容压出同样的字节），不是规范化后的版本，因为 Bronze 要求原样保存。
- 记录里没有官方发布时间，所以用采集时间代替（E35），这也是文件名写 `fetched_at=` 的原因。

### 9.5 Rapid Rail OD 客流（`download_ridership.py`）

- 文件在 `storage.data.gov.my`（文件服务器），**不受 OpenAPI 限额约束**。
- 每年一个文件，约 5 MB，**每天整份覆盖**；旧年份的文件也会被修订（2025 年的文件在 2026-04-02 还被更新过）。所以要**保留每一个不同的版本**，才能知道历史数据被改过哪些。

**怎么做到不重复下载：HEAD + ETag**
- `GET` 请求会下载整个文件；`HEAD` 请求**只问"文件信息"**，不下载内容，几乎不花流量。
- 服务器回复的信息里有 **ETag**（服务器给每个版本的标签，内容变了标签就变）和 **Last-Modified**（最后修改时间）。
- 脚本先发 HEAD：ETag 和上次一样 → 什么都不做；不一样 → 才真正下载，算 SHA-256，如果指纹也是新的就存起来，并在 `versions.jsonl` 记一行。
- 每次同时检查**今年和去年**两个文件：去年的文件还会被修订；1 月初今年的文件还不存在时，服务器返回 404，脚本会当作正常情况。

这是**两层去重**：ETag 先挡掉绝大多数"没变"的情况（省流量），SHA-256 再挡掉"ETag 变了但内容其实一样"的少数情况（省磁盘）。

### 9.6 公共假期：不需要采集

官方没有假期 API。做法是在代码库里维护一份人工核对过的假期表（dbt seed：`seeds/seed_public_holidays.csv`），每年根据政府公告更新一次，临时假期随时补上。改动历史由 git 记录。

### 9.7 汇总：每种数据怎么"只存有变化的"

| 数据 | 判断"变了没"的方法 | 没变时 | 变了时 |
|---|---|---|---|
| RT | 不判断（每次都是新的观测） | — | 每次都存，靠每日打包压缩 |
| Static | 拆开 ZIP，每个文件算 SHA-256 | 那个文件不再存，只在 snapshots 里记一行 | 新内容存成一个 blob |
| 天气 | 规范化 JSON 后算 SHA-256 | 只写 fetch_log | 存一个新的 `.json.gz` |
| 客流 | 先比 ETag，再比 SHA-256 | 不下载，不记录 | 存一个新的 `.parquet`，写 versions.jsonl |

---

## 10. 怎么检查：日常巡检手册

下面的命令都在 **WSL 里**执行（用 `ssh fyp-collector '...'` 把命令送到 VM 上执行）。

### 10.1 每天看一次（1 分钟）

```bash
# RT 采集器在不在跑（应显示 active）
ssh fyp-collector systemctl is-active gtfs-rt-collector

# 最近 10 条采集日志
ssh fyp-collector journalctl -u gtfs-rt-collector -n 10 -o cat

# 所有定时任务：下次什么时候跑（NEXT）、上次什么时候跑过（LAST）
ssh fyp-collector systemctl list-timers --no-pager 'fyp-*' 'gtfs-*'

# 磁盘和内存
ssh fyp-collector 'df -h / | tail -1; free -m | sed -n 2p'
```

**健康的样子**：采集器 `active`；日志每 15 秒一行，大部分是 `ok`（深夜 kl 是 `ok_empty`）；每个 timer 都有 LAST 时间；磁盘使用率低于 80%。

### 10.2 看某一天的采集统计

```bash
ssh fyp-collector 'python3 - <<EOF
import json, collections
c = collections.Counter()
for line in open("/home/ubuntu/fyp-data/bronze/_health/feed_health_2026-10-23.jsonl"):
    r = json.loads(line)
    c[(r["feed"], r["status"])] += 1
for k, v in sorted(c.items()):
    print(k, v)
EOF'
```

### 10.3 看打包结果

```bash
# 打包任务的日志
ssh fyp-collector journalctl -u gtfs-rt-pack -o cat -n 10

# 某天 manifest 的摘要（不显示几千行的文件清单）
ssh fyp-collector 'python3 -c "import json;m=json.load(open(\"/home/ubuntu/fyp-data/bronze/gtfs_rt/_packs/feed=rapid-bus-kl/date=2026-10-22/manifest.json\"));m.pop(\"files\");print(m)"'

# 列出压缩包里的前几个文件（不解压）
ssh fyp-collector 'tar --zstd -tf ~/fyp-data/bronze/gtfs_rt/_packs/feed=rapid-bus-kl/date=2026-10-22/rt.tar.zst | head'
```

### 10.4 看其他数据源

```bash
# 某个定时任务最近的输出
ssh fyp-collector journalctl -u fyp-weather-warning -o cat -n 5
ssh fyp-collector journalctl -u fyp-static -o cat -n 5
ssh fyp-collector journalctl -u fyp-ridership -o cat -n 5

# 天气每次尝试的记录（最后 3 次）
ssh fyp-collector tail -3 fyp-data/bronze/weather_forecast/fetch_log.jsonl

# 各数据源占用的空间
ssh fyp-collector 'du -sh ~/fyp-data/bronze/*'
```

### 10.5 手动立刻跑一次某个任务

```bash
ssh fyp-collector sudo systemctl start fyp-weather-warning.service   # 跑完会自己结束
ssh fyp-collector journalctl -u fyp-weather-warning -o cat -n 3       # 看结果
```

检查某个网址会不会被重定向（§8.1 就是这样发现 301 的）：

```bash
curl -sI "https://api.data.gov.my/gtfs-realtime/vehicle-position/prasarana?category=rapid-bus-kl" | grep -iE "^(HTTP|location)"
```

### 10.6 常见问题排查

| 现象 | 先看什么 | 可能原因 |
|---|---|---|
| 采集器不是 `active` | `journalctl -u gtfs-rt-collector -n 50` | 代码出错（看 Traceback）；内存超过 300 MB 被系统杀掉 |
| 大量 `timeout` 或 `network_error` | 同一时段的日志 | VM 网络或 API 那边有问题；如果持续很久，到 AWS 控制台看实例状态 |
| 出现 `rate_limited`（429） | 是不是有别的程序也在请求 RT | 例如本地又启动了一个采集器。**同一时间只能有一个采集实例** |
| timer 的 LAST 一直是空的 | `systemctl status fyp-xxx.timer` | timer 没有 enable；或 `.timer` 文件改了却没有 `daemon-reload` |
| 磁盘快满了 | `du -sh ~/fyp-data/bronze/*` | 打包没有正常执行，零散文件越积越多 |
| SSH 连不上 | §4.4 | 家里 IP 变了，或 VM 的公网 IP 变了 |

---

## 11. 安全注意事项

1. **私钥 `.pem` 绝不能进 git。**`.gitignore` 已经排除了 `*.pem` 和 `*.key`。私钥只放在 `~/.ssh/`，Windows 下载文件夹另有一份备份。不要放进仓库目录，不要发给任何人。
2. **安全组只开放 SSH，而且只对你家的 IP 开放。**不要为了方便改成 `0.0.0.0/0`（全世界都能尝试连入）。
3. **程序用普通用户 `ubuntu` 运行**，不用 root。
4. **代码里没有任何密码或密钥。**data.gov.my 的 API 不需要密钥。
5. **AWS 账户不要升级**，预算提醒已设置。
6. 你的邮箱等个人信息不要写进代码或请求头。

---

## 12. 还没做、之后要做的采集策略

### 12.1 `bronze_sync`：把 VM 的数据拉回本地 ✅（2026-10-23 完成第一版）

> 这一节放在"还没做"一章里，是因为它只完成了第一版；最后一步"写进 MinIO"要等本地湖仓搭起来。

**是什么**：在本地电脑运行的同步程序（`ingestion/bronze_sync.py`），把 VM 上的 Bronze 拉回本地 `~/fyp-data/bronze/`，然后逐项校验。以后会变成 Airflow 流程的第一个任务。

**为什么是"本地去拉"，而不是"VM 推过来"？**你的电脑在家里的路由器后面（NAT），外面的机器连不进来，而且电脑经常关机。所以只能由本地主动连 VM 去拿（拉取式）。VM 永远不需要知道本地在哪里。

**为什么现在就做，而不是等湖仓建好**：在它之前，RT 数据**只存在 VM 一个地方**。VM 磁盘坏了、AWS 账户出问题，数据就全没了。同步之后，至少有两份。

**怎么用**（在 WSL 的仓库目录下）：

```bash
.venv/bin/python ingestion/bronze_sync.py                 # 拉取 + 校验
.venv/bin/python ingestion/bronze_sync.py --verify-only   # 不拉取，只校验本地副本
```

建议每次开机做别的事之前先跑一次。本地关机一周后再开机，它会一次补拉这一周的数据，不会丢，因为 VM 一直在采集和保存。

**它做了什么**：

```
① rsync 拉取：除了"今天的零散 RT 文件"（还在写入、还没打包）和 .tmp 文件，其他全部拉回。
   本地永远不删除文件，VM 上也不删除任何东西。
② 校验：
   - RT 打包：整个包的 SHA-256 要和 manifest 的 pack_sha256 一致；再解包逐个比对文件指纹和文件数。
     通过的包记进 _sync/verified_packs.jsonl，下次不再重复解包（省时间）。
   - Static：每个 blob 解压后的指纹要等于它的文件名；snapshots.jsonl 引用到的每个 blob 都要存在。
   - 天气：fetch_log.jsonl 里每一个"changed"的文件都要存在，而且规范化后的指纹和日志一致。
   - 客流：versions.jsonl 里每一个版本都要存在，而且指纹一致。
③ 在 ~/fyp-data/_sync/sync_log.jsonl 写一行本次同步的摘要；有问题就逐条列出，退出码为 1。
```

**校验为什么有用**：传输中断、磁盘错误、或者有人误改了文件，都会让指纹对不上。测试时我故意改坏了一个压缩包的 1 个字节、删掉一个 Static blob，程序都抓出来了。也就是：用 VM 写下的 manifest，逐项检查本地收到的文件。

**rsync 的关键参数**：
- `--exclude=/gtfs_rt/feed=*`：开头的 `/` 表示"从同步的根目录算起"，只排除 `gtfs_rt/` 下面以 `feed=` 开头的零散目录，不会误伤 `_packs/` 里同名的子目录；
- `--partial-dir=.rsync-partial`：传到一半中断的文件先放在隐藏目录里，下次接着传，不会留下不完整的正式文件；
- 没有 `--delete`：VM 上删掉的文件，本地照样保留。

**还没做的部分**：
- 写进本地 MinIO：等本地湖仓（Docker 的 `lake` profile）搭好后加上，路径保持和现在一样；
- 用 Airflow 定时触发：等 Airflow 搭好后；
- VM 端清理：现在磁盘够用，VM 保留完整副本作为第二份备份；磁盘紧张时，才删除"本地已校验通过"的旧打包。

### 12.2 监控与告警

- **`/metrics`**：让采集器通过一个网页接口暴露指标（成功率、最近一次成功的时间、磁盘使用率），本地的 Prometheus 来抓取，Grafana 画图。
- **离线告警**：本地电脑关机时，Prometheus 也没在跑，没人知道 VM 出问题了。计划让 VM 在"连续 N 个时间槽失败"或"磁盘超过 80%"时，直接调用一个免费的推送服务发通知到你手机。具体用哪个服务还没定。

### 12.3 把数据送进 Kafka：中继与回放

做流处理（RQ3）时，需要数据流进 Kafka：
- **`rt_relay`（中继）**：本地开机时，每 30 秒通过 SSH 从 VM 拉取当天新增的 `.pb`，解析后发布到本地 Kafka。比真正实时晚 30–60 秒，在 RQ3 里要单独说明这段额外延迟。
- **`bronze_replayer`（回放）**：读取 Bronze 历史数据，按原本的时间顺序发布到 Kafka，可以选 1 倍、10 倍或不限速。用于 RQ3 实验，也用于修改流处理逻辑后重新计算。

**注意：不能在本地再开一个采集器直接请求 API**，那会让请求数翻倍，超过限额。数据只从 VM 这一个出口来。

### 12.4 GitHub Actions 的角色

- `backup_gtfs.yml`：继续每天检查 Static，作为另一个地方的备份。
- `weather_archive.yml`：和 VM 并行几天，核对两边存的天气内容一致后**删除**（约 2026-10-26）。

### 12.5 健康日志的长期处理

健康日志每天约 1.7 MB，一年约 600 MB，目前直接保留。以后可以把旧的健康日志也压缩，或者随 `bronze_sync` 拉回本地后在 VM 上删除。

### 12.6 迁移到下一台 VM（2027-04-22 之前）

AWS 账户 2027-04-22 关闭，而 Azure for Students 已证实不可行，所以之后用哪台 VM 还没定（Oracle 继续重试、每月约 4–6 美元的小 VPS、或最后几个月只在本地开机时采集）。不管换到哪里，**迁移规程**都一样（设计书 §8.3.4）：

```
① 在新 VM 上：同步代码，运行 install.sh，但先不启动 RT 采集器
② 选一个时间槽 T：旧 VM 在 T 之后停止 RT 采集器
③ 新 VM 从 T + 15 秒的时间槽开始采集（最多损失一个时间槽）
④ 健康日志里，这一段标记为 cutover；instance 字段会显示新的主机名
⑤ 用 bronze_sync 把旧 VM 的全部数据拉回本地并校验，然后才删除旧 VM
```

**两个采集器绝对不能同时运行**，否则请求数翻倍，会触发限流。这次迁移本身可以写进报告，作为一次"切换演练"（零丢失、零重复的证据）。

---

## 13. 练习题

动手做一遍，比读十遍有用。每题都只读不写，不会影响正在运行的采集。

1. **连接**：用 `ssh fyp-collector` 登录 VM，执行 `hostname` 和 `date`，再 `exit` 退出。VM 显示的时间是 UTC 还是 MYT？为什么文件分区却是 MYT？
2. **找文件**：登录 VM 后，找出今天 kl 最新的一个 `.pb` 文件：`find ~/fyp-data/bronze/gtfs_rt/feed=rapid-bus-kl/date=$(TZ=Asia/Kuala_Lumpur date +%F) -name '*.pb' | sort | tail -1`。为什么目录用 MYT 的日期，而文件名用 UTC？
3. **指纹**：在 WSL 里执行 `echo hello | sha256sum`，再执行 `echo hellp | sha256sum`。只差一个字母，两个指纹有多少相同？
4. **健康日志**：用 §10.2 的命令统计昨天的状态。算一算：kl 的可用率是多少（`ok` + `ok_empty` 除以 2880）？
5. **打包**：用 §10.3 的命令看昨天 feeder 的 manifest。压缩倍数是多少？为什么 feeder 比 kl 压缩得差？（提示：深夜 kl 的文件只有 15 字节。）
6. **Static 去重**：执行 `ssh fyp-collector tail -1 fyp-data/bronze/gtfs_static/rapid-bus-mrtfeeder/snapshots.jsonl`，找到 `changed_files`。今天哪些文件变了？是不是又只有 `calendar.txt`？
7. **ETag**：执行 `curl -sI https://storage.data.gov.my/transportation/rail/rapidrail_2026_daily.parquet`，找到 `etag` 和 `last-modified`。和 VM 上 `versions.jsonl` 最后一行的 ETag 一样吗？
8. **思考题**：如果打包脚本在"写完 manifest、删了一半零散文件"时 VM 断电了，第二天再运行会发生什么？（答案在 §9.2 "重跑安全"。）
9. **思考题**：为什么 RT 失败不重试，Static 却重试？
10. **思考题**：如果你在本地电脑也跑 `collect_gtfs_rt.py`，会发生什么问题？
