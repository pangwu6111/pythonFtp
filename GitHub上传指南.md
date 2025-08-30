# GitHub上传指南

## 🎯 目标
将FTP工具上传到GitHub并设置自动编译，生成Windows/macOS/Linux三个平台的可执行文件。

## 📋 准备工作

### 1. 确保你有GitHub账号
如果没有，请访问 https://github.com 注册账号

### 2. 安装Git (如果未安装)
```bash
# macOS (使用Homebrew)
brew install git

# 或者下载Git官方安装包
# https://git-scm.com/download/mac
```

### 3. 配置Git (首次使用)
```bash
# 设置用户名和邮箱
git config --global user.name "你的用户名"
git config --global user.email "你的邮箱@example.com"
```

## 🚀 上传步骤

### 第一步: 在GitHub创建仓库

1. 登录GitHub
2. 点击右上角的 "+" 按钮
3. 选择 "New repository"
4. 填写仓库信息:
   - **Repository name**: `ftp-download-tool` (或你喜欢的名字)
   - **Description**: `FTP断点续传下载工具 - 支持目录浏览、文件搜索、批量下载`
   - **Public/Private**: 选择Public (这样GitHub Actions免费)
   - **Initialize**: 不要勾选任何选项 (我们已经有文件了)
5. 点击 "Create repository"

### 第二步: 本地初始化Git仓库

在你的项目文件夹中打开终端，执行以下命令:

```bash
# 1. 初始化Git仓库
git init

# 2. 添加所有文件
git add .

# 3. 创建第一次提交
git commit -m "🎉 初始提交: FTP断点续传下载工具

✨ 功能特性:
- 断点续传下载
- 目录浏览和搜索
- 文件排序功能
- 批量下载支持
- 跨平台编译支持
- GitHub Actions自动编译"

# 4. 添加远程仓库 (替换为你的GitHub用户名和仓库名)
git remote add origin https://github.com/你的用户名/ftp-download-tool.git

# 5. 推送到GitHub
git push -u origin main
```

### 第三步: 设置GitHub Actions

1. 在GitHub仓库页面，点击 "Actions" 标签
2. 如果看到工作流程，说明自动编译已经开始
3. 等待编译完成 (大约5-10分钟)

### 第四步: 创建目录结构

确保你的项目目录结构如下:
```
ftp-download-tool/
├── .github/
│   └── workflows/
│       └── github_actions_build.yml
├── ftp_gui_complete.py
├── README.md
├── requirements.txt
├── LICENSE
├── .gitignore
├── build_macos.sh
├── docker_build.sh
├── 编译说明.md
└── GitHub上传指南.md
```

## 🔧 命令行操作详解

### 完整的上传命令序列:

```bash
# 进入项目目录
cd /path/to/your/ftp-project

# 初始化Git (如果还没有)
git init

# 创建.github/workflows目录
mkdir -p .github/workflows

# 移动GitHub Actions配置文件
mv github_actions_build.yml .github/workflows/

# 添加所有文件到Git
git add .

# 查看将要提交的文件
git status

# 创建提交
git commit -m "🎉 FTP工具初始版本

功能包括:
- 断点续传下载
- 目录浏览搜索
- 文件排序
- 批量下载
- 跨平台支持"

# 添加远程仓库 (记得替换用户名和仓库名)
git remote add origin https://github.com/你的用户名/ftp-download-tool.git

# 推送到GitHub
git push -u origin main
```

## 🎯 验证上传成功

### 1. 检查仓库内容
访问你的GitHub仓库页面，确认所有文件都已上传

### 2. 检查GitHub Actions
1. 点击 "Actions" 标签
2. 应该看到一个正在运行或已完成的工作流程
3. 点击工作流程查看详细进度

### 3. 等待编译完成
- Windows编译: 约3-5分钟
- macOS编译: 约3-5分钟  
- Linux编译: 约2-3分钟

### 4. 下载编译结果
编译完成后:
1. 在Actions页面点击最新的工作流程
2. 在页面底部找到 "Artifacts" 部分
3. 下载对应平台的可执行文件

## 🔄 后续更新

当你修改代码后，使用以下命令更新:

```bash
# 添加修改的文件
git add .

# 提交更改
git commit -m "✨ 添加新功能: 描述你的更改"

# 推送到GitHub
git push
```

每次推送都会自动触发编译，生成新的可执行文件。

## 🎉 创建Release

当你想发布正式版本时:

```bash
# 创建标签
git tag -a v1.0.0 -m "🎉 发布v1.0.0版本"

# 推送标签
git push origin v1.0.0
```

这会自动创建一个Release，包含所有平台的可执行文件。

## 🆘 常见问题

### 1. 推送失败 (认证问题)
```bash
# 如果使用HTTPS遇到认证问题，可以使用Personal Access Token
# 在GitHub Settings > Developer settings > Personal access tokens 创建token
# 然后使用token作为密码
```

### 2. 文件太大
```bash
# 如果有大文件，添加到.gitignore
echo "大文件名" >> .gitignore
git add .gitignore
git commit -m "忽略大文件"
```

### 3. GitHub Actions失败
- 检查 `.github/workflows/github_actions_build.yml` 文件路径是否正确
- 查看Actions页面的错误日志
- 确保仓库是Public (Private仓库有使用限制)

## 💡 提示

1. **仓库名建议**: 使用有意义的名字，如 `ftp-download-tool`
2. **描述要清楚**: 让别人知道这是什么项目
3. **README重要**: 好的README能吸引更多用户
4. **定期更新**: 保持项目活跃，修复bug和添加功能

完成上传后，你的FTP工具就可以自动编译并分发给全世界的用户了！🎉