# GitHub 新手一步步获取过去一年的风速数据

本文示例以 macOS 用户、想要下载“赤峰”过去一年的风速历史数据为例，覆盖从第一次使用 GitHub 到运行 `wind-logger-csv` 的全部操作步骤。

---

## 1. 注册 GitHub 并获取项目代码

1. 打开 [https://github.com/signup](https://github.com/signup) 注册账号，按照页面提示完成邮箱验证。
2. 登录后访问项目仓库：`https://github.com/<your-username>/wind-logger-csv`。
   - 如果你已经将本仓库推送到自己的账号，直接打开自己的仓库页面即可。
   - 如果仓库还不在你的账号下，可先点击右上角 **Fork** 或 **Use this template**，在自己的账号下创建一份副本，然后进入新仓库页面。
3. 在仓库页面点击绿色的 **Code** 按钮，选择 **HTTPS**，复制仓库地址（如 `https://github.com/<your-username>/wind-logger-csv.git`）。

> 若尚未安装 Git，可先在 macOS 终端输入 `git --version`，系统会提示安装 Xcode Command Line Tools，按照弹窗说明完成安装即可。

---

## 2. 把仓库克隆到本地并安装依赖

1. 打开“终端”（Spotlight 搜索 Terminal）。
2. 创建一个保存项目的文件夹并进入，例如：
   ```bash
   mkdir -p ~/Projects
   cd ~/Projects
   ```
3. 克隆仓库并进入目录：
   ```bash
   git clone https://github.com/<your-username>/wind-logger-csv.git
   cd wind-logger-csv
   ```
4. 创建并激活 Python 虚拟环境：
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
5. 安装依赖和可执行脚本：
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

---

## 3. 配置采集地点和默认输出

1. 复制示例环境变量文件并打开编辑：
   ```bash
   cp .env.example .env
   open -e .env  # 也可以使用 nano 或其他编辑器
   ```
2. 在 `.env` 中设置你关心的地点：
   ```env
   PLACE_NAME=赤峰
   HISTORY_CSV_FILE=wind_history.csv
   ```
   若需要更精确位置，也可改为经纬度：
   ```env
   # PLACE_NAME 注释掉
   LAT=42.2586
   LON=118.8869
   ```

保存后关闭文件。CLI 会自动读取 `.env` 中的配置，历史导出默认写入 `wind_history.csv`。

---

## 4. 计算过去一年的日期区间

假设今天是 2024-05-01，可按下面方式得到过去一年的起止日期：

```bash
# macOS 终端命令（返回 365 天前的日期）
START_DATE=$(date -v-1y +%F)
END_DATE=$(date +%F)
echo "起始日期: $START_DATE"
echo "结束日期: $END_DATE"
```

如果你的系统不支持 `-v-1y` 参数，也可以手动在日历上确认，比如起始日期为去年的同一天（闰年可适当调整）。

---

## 5. 运行历史数据下载命令

1. 保证仍在项目目录且虚拟环境已激活（提示符开头有 `(.venv)`）。
2. 执行历史下载命令：
   ```bash
   wind-csv history --start-date "$START_DATE" --end-date "$END_DATE" --timezone Asia/Shanghai
   ```
   - 如未事先定义 `START_DATE`/`END_DATE` 变量，可直接填具体日期，例如：
     ```bash
     wind-csv history --place 赤峰 --start-date 2023-05-01 --end-date 2024-04-30 --timezone Asia/Shanghai
     ```
   - 若在命令中写明 `--place`、`--lat/--lon` 或 `--csv`，会覆盖 `.env` 中的默认值。

命令成功后会打印类似信息：

```
[history] 赤峰 2023-05-01 → 2024-04-30 | 共 8760 条记录，已保存至 wind_history.csv
```

这表示从 Open-Meteo 归档接口下载的每小时数据已经写入 `wind_history.csv`。

---

## 6. 验证 CSV 并进行后续分析

1. 在终端中查看前几行：
   ```bash
   head wind_history.csv
   ```
2. 你也可以使用 `wind-csv show --csv wind_history.csv --limit 20` 查看最近记录。
3. 将 `wind_history.csv` 导入 Excel、Numbers 或数据分析工具进行进一步处理。

至此，即便是第一次使用 GitHub，也可以完整地克隆仓库、安装脚本，并用 `wind-csv history` 命令获取过去一年的赤峰风速数据。
