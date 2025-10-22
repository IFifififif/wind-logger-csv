# 将 wind-logger-csv 完整创建到自己的 GitHub 仓库

本文针对首次使用 GitHub 的用户，帮助你把 `wind-logger-csv` 项目完整地放到自己的 GitHub 账号下，并准备好后续下载或继续开发。

---

## 1. 准备 GitHub 账号与 Git 环境

1. 打开 [https://github.com/signup](https://github.com/signup) 注册账号，完成邮箱验证与登录。
2. 确保本机已安装 Git：在终端运行 `git --version`。
   - 如果 macOS 提示安装 Command Line Tools，按照系统弹窗完成安装即可。
   - Windows 用户建议安装 [Git for Windows](https://git-scm.com/download/win)。
3. 设置全局用户名与邮箱（用于提交历史显示）：
   ```bash
   git config --global user.name "你的 GitHub 用户名"
   git config --global user.email "你的邮箱"
   ```

---

## 2. 在 GitHub 上创建新的仓库

有两种常见方式让自己的账号拥有一份 `wind-logger-csv`：

### 方式 A：使用模板（推荐给初学者）
1. 登录后访问原始项目页面：`https://github.com/<your-username>/wind-logger-csv`（如果你已经 fork/模板化该仓库，直接进入自己的仓库即可）。
2. 点击页面右上角的 **Use this template** → **Create a new repository**。
3. 填写仓库名称（例如 `wind-logger-csv`）、描述及可见性（Public/Private），点击 **Create repository**。
4. GitHub 会自动在你的账号下生成一个新仓库，并复制当前项目所有文件与目录结构。

### 方式 B：Fork（适合想保持与上游同步的用户）
1. 在原项目页面点击右上角 **Fork**。
2. 选择要 fork 到的账号，点击 **Create fork**。
3. Fork 完成后，你的账号下会出现 `wind-logger-csv` 仓库，默认与原仓库建立上游关联，后续可以同步更新。

> 如果你已经在本地修改过项目并希望上传自己的版本，也可以先在 GitHub 创建一个空仓库（点击右上角 **+ → New repository**），再按照下一节的步骤把本地代码推送上去。

---

## 3. 推送本地项目到自己的仓库

假设你已经在电脑上下载或修改了项目代码，执行以下操作把本地内容推送到 GitHub：

1. 进入项目根目录：
   ```bash
   cd /path/to/wind-logger-csv
   ```
2. 初始化 Git 仓库（如果目录尚未是 Git 仓库）：
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```
3. 将远程地址改成你自己的仓库，例如：
   ```bash
   git remote add origin https://github.com/<your-username>/wind-logger-csv.git
   # 若已有 origin 指向旧地址，可改用：
   # git remote set-url origin https://github.com/<your-username>/wind-logger-csv.git
   ```
4. 推送到 GitHub：
   ```bash
   git branch -M main
   git push -u origin main
   ```
5. 首次推送时，Git 会要求输入 GitHub 凭据。推荐使用 [Personal Access Token](https://github.com/settings/tokens) 作为密码，或配置 [SSH 密钥](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/connecting-to-github-with-ssh)。

完成后刷新 GitHub 仓库页面，即可看到所有文件与提交历史已经上传。

---

## 4. 使用 Codespaces 或继续开发

* 在仓库页面点击 **Code → Create codespace on main**，即可在浏览器中打开 Codespaces 进行开发，容器会自动执行 `pip install -e .`。
* 若继续在本地开发，记得在每次修改后运行测试并推送：
  ```bash
  pytest
  git add <changed-files>
  git commit -m "描述你的修改"
  git push
  ```

现在，这个项目已经完全存在于你的 GitHub 账号中，后续可以随时运行 `wind-csv history` 或其他命令采集风速数据，并根据需要自定义开发。
