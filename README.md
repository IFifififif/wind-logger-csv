# wind-logger-csv

使用 Open‑Meteo 接口定时抓取风速并保存到本地 CSV (`wind_log.csv`)。

- 地名或经纬度两种定位
- 默认每 60 秒抓取一次 `wind_speed_10m` 与 `wind_direction_10m`
- 追加写入 CSV，自动带表头
- 提供 CLI：`wind-csv once` / `wind-csv run` / `wind-csv show`
- 内置 GitHub Codespaces 与 GitHub Actions CI

## 快速开始（本地）
```bash
git clone https://github.com/<your-username>/wind-logger-csv.git
cd wind-logger-csv
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
cp .env.example .env
# 编辑 .env，填写 PLACE_NAME 或 LAT/LON
wind-csv once
wind-csv run
```

### macOS 提示 “invalid active developer path” 的解决办法

如果在执行 `python3 --version` 等命令时出现如下错误：

```
xcrun: error: invalid active developer path (/Library/Developer/CommandLineTools)
```

说明系统还未安装 Xcode Command Line Tools。按顺序执行以下步骤即可恢复：

1. 在终端运行 `xcode-select --install`，按照弹窗提示完成安装。
2. 安装结束后，运行 `sudo xcode-select --switch /Library/Developer/CommandLineTools`（若提示路径不存在，可改用 `sudo xcode-select --reset`）。
3. 重新执行 `python3 --version` 验证命令是否可用，再继续后续的虚拟环境与依赖安装步骤。

命令行工具安装完成后即可继续使用本项目进行虚拟环境创建和 CLI 命令运行。

## 在 GitHub Codespaces 中打开

1. 将仓库推送到 GitHub。
2. 打开仓库页面，点击 **Code → Create codespace on main**。
3. 首次启动会自动 `pip install -e .`。随后在终端执行：

   ```bash
   cp .env.example .env && nano .env   # 编辑配置
   wind-csv once
   wind-csv run
   ```

## CLI 命令

* `wind-csv once [--place 城市名 | --lat LAT --lon LON] [--csv 输出.csv]`：立即采样一次并写入 CSV。
* `wind-csv run [--interval 秒] [--place/--lat/--lon] [--csv 输出.csv]`：持续轮询采样。
* `wind-csv show [--limit N] [--csv 输出.csv]`：打印最近 N 行（`--limit <= 0` 显示全部）。
* `wind-csv history --start-date YYYY-MM-DD --end-date YYYY-MM-DD [--hourly 字段] [--timezone 时区] [--csv 输出.csv]`：下载指定时间段的历史风速 CSV。

### 参数覆盖

* `--place` 覆盖 `PLACE_NAME`，`--lat`/`--lon` 同时提供时覆盖经纬度。
* `--csv` 覆盖 `CSV_FILE`，`--interval` 覆盖 `INTERVAL_SEC`。
* 未提供时依然使用 `.env` 或环境变量配置。

历史下载命令 `wind-csv history` 会使用 `HISTORY_CSV_FILE`（或 `--csv`）作为输出路径。

### 历史数据下载示例

```bash
# 下载 2023 全年的赤峰风速，并写入 wind_history.csv
wind-csv history --place 赤峰 --start-date 2023-01-01 --end-date 2023-12-31 \
  --timezone Asia/Shanghai --csv wind_history.csv

# 也可以自定义 hourly 字段，例如仅下载风速
wind-csv history --place 赤峰 --start-date 2023-01-01 --end-date 2023-01-31 \
  --hourly wind_speed_10m
```

> **第一次使用 GitHub？**
> * 如果你需要把整个项目放到自己的账号下，请先阅读《[将 wind-logger-csv 完整创建到自己的 GitHub 仓库](docs/github_repo_setup.md)》，了解如何创建仓库、推送本地代码或使用模板。
> * 之后可继续参考《[GitHub 新手一步步获取过去一年的风速数据](docs/github_history_walkthrough.md)》，完成虚拟环境配置与 `wind-csv history` 命令的执行。

## 配置（环境变量或 `.env`）

* `CSV_FILE=wind_log.csv`
* `INTERVAL_SEC=60`
* `PLACE_NAME=上海` *或* `LAT=31.2304`、`LON=121.4737`
* `HISTORY_CSV_FILE=wind_history.csv`（可选，历史数据默认输出文件）

## 输出示例

```
local_time,utc_time,place_name,latitude,longitude,wind_speed_ms,wind_direction_deg
2025-10-22 15:00:00,2025-10-22T07:00:00Z,上海,31.23,121.47,3.25,240
```

## 许可证

MIT

