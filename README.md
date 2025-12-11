## finance（日线回测 MVP）

### 目标

- 读取本地 CSV（日线 OHLCV）
- 计算 SMA（fast/slow）
- 生成双均线目标仓位信号（0/1）
- 撮合：t 日收盘出信号，t+1 日开盘成交（Next-Open）
- 盯市：每日收盘 close
- 输出：`equity_curve.csv`、`trades.csv`、`metrics.json`

### CSV 数据约定

- 必需列：`date, open, high, low, close, volume`
- `date` 格式：`YYYY-MM-DD`

建议放置：`data/raw/{symbol}.csv`（也可以通过 CLI 参数指定路径）

### 运行（实现完成后）

#### 1) 创建虚拟环境并安装依赖

macOS + Homebrew Python 默认是“外部托管环境”（PEP 668），建议使用项目虚拟环境：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
```

#### 2) 运行回测

使用：

```bash
.venv/bin/python -m finance.cli.runBacktest --symbol 000001 --csv-path data/raw/000001.csv
```

回测输出会落在：`outputs/{run_id}/`。
