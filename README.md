# 🚀 FTP断点续传下载工具

[![GitHub release](https://img.shields.io/github/release/pangwu6111/pythonFtp.svg)](https://github.com/pangwu6111/pythonFtp/releases)
[![Build Status](https://github.com/pangwu6111/pythonFtp/workflows/构建跨平台可执行文件/badge.svg)](https://github.com/pangwu6111/pythonFtp/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

一个功能强大的**Windows 11 FTP命令行断点续传下载工具**，支持GUI界面和跨平台使用。解决了Windows原生FTP命令不支持断点续传的问题，特别适合下载大文件或在网络不稳定的环境中使用。

## ✨ 功能特性

### 🔄 断点续传核心功能
- ✅ **真正的断点续传**: 使用FTP REST命令实现标准断点续传
- ✅ **智能重试机制**: 网络中断自动重连，支持自定义重试次数
- ✅ **文件完整性**: 自动验证文件大小，确保下载完整性
- ✅ **大文件支持**: 支持GB级别大文件的稳定下载

### 📊 用户体验
- 🎯 **实时进度显示**: 下载进度、传输速度、剩余时间、完成百分比
- 🖥️ **多界面选择**: 命令行版本 + 多个GUI版本满足不同需求
- 🔍 **目录浏览**: 可视化浏览FTP服务器目录结构
- 📁 **批量操作**: 支持多文件、整个目录的批量下载

### 🌐 跨平台支持
- 🪟 **Windows**: 原生.exe可执行文件
- 🍎 **macOS**: 应用程序包(.app)
- 🐧 **Linux**: 可执行文件

## 🚀 快速开始

### 方法1: 下载预编译版本 (推荐)

1. 访问 [**Releases页面**](https://github.com/pangwu6111/pythonFtp/releases) 
2. 根据你的系统下载对应版本：
   - `ftp-tools-windows.zip` - Windows 10/11
   - `ftp-tools-macos.zip` - macOS 10.14+
   - `ftp-tools-linux.zip` - Ubuntu 18.04+
3. 解压后双击运行，无需安装Python环境

### 方法2: 从源码运行

```bash
# 1. 克隆仓库
git clone https://github.com/pangwu6111/pythonFtp.git
cd pythonFtp

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行GUI版本 (推荐新手)
python ftp_gui_complete.py

# 4. 运行命令行版本 (适合高级用户)
python ftp_downloader.py ftp://example.com/file.zip
```

## 📖 使用指南

### 🖥️ GUI版本使用

1. **启动程序**: 运行 `FTP下载工具.exe` 或 `python ftp_gui_complete.py`
2. **连接FTP**: 输入服务器地址、用户名、密码
3. **浏览文件**: 双击目录进入，使用搜索框查找文件
4. **下载文件**: 选择文件后点击下载，支持断点续传

**GUI功能亮点**:
- 🔗 支持匿名和认证连接
- 📂 可视化目录树浏览
- 🔍 实时文件搜索过滤
- 📊 多种排序方式 (名称/大小/日期/类型)
- ⬆️ 一键返回上级目录
- 📥 拖拽式批量下载

### ⌨️ 命令行版本使用

```bash
# 基本下载
ftp_downloader.py ftp://ftp.example.com/file.zip

# 带认证下载
ftp_downloader.py ftp://user:pass@ftp.example.com/file.zip

# 指定保存路径
ftp_downloader.py ftp://ftp.example.com/file.zip -o /path/to/save/

# 列出目录内容
ftp_downloader.py ftp://ftp.example.com/pub/ -l

# 断点续传 (自动检测已下载部分)
ftp_downloader.py ftp://ftp.example.com/largefile.zip
```

**命令行参数**:
- `-o, --output`: 指定下载保存路径
- `-l, --list`: 列出目录内容而不下载
- `-r, --retry`: 设置重试次数 (默认3次)
- `-t, --timeout`: 设置连接超时时间

## 🏗️ 项目架构

```
pythonFtp/
├── 📁 核心文件
│   ├── ftp_downloader.py      # 🔧 命令行版本 (核心引擎)
│   ├── ftp_gui_complete.py    # 🖥️ 完整GUI版本 (推荐)
│   ├── ftp_gui_enhanced.py    # 🔬 增强版 (调试功能)
│   └── ftp_gui_simple.py      # 📱 简化版 (轻量级)
├── 📁 配置文件  
│   ├── requirements.txt       # Python依赖列表
│   ├── ftp_config.json       # 配置文件模板
│   └── .gitignore            # Git忽略规则
├── 📁 编译工具
│   ├── build_exe.py          # Windows编译脚本
│   ├── build_macos.sh        # macOS编译脚本
│   └── docker_build.sh       # Docker跨平台编译
├── 📁 自动化
│   └── .github/workflows/    # GitHub Actions CI/CD
└── 📁 文档
    ├── README.md             # 项目说明 (本文件)
    ├── 编译说明.md            # 详细编译指南
    └── LICENSE               # MIT开源协议
```

## 🔧 技术实现

### 断点续传原理
```python
# 核心实现逻辑
1. 检测本地文件大小 → local_size = os.path.getsize(local_file)
2. 发送REST命令 → ftp.sendcmd(f'REST {local_size}')  
3. 继续下载 → ftp.retrbinary('RETR filename', callback, rest=local_size)
4. 验证完整性 → 比较本地和远程文件大小
```

### 网络优化策略
- **连接池管理**: 复用FTP连接，减少握手开销
- **智能重试**: 指数退避算法，避免服务器过载
- **传输监控**: 实时监控传输速度，自动调整缓冲区大小
- **超时处理**: 多层超时机制，防止程序假死

### 安全特性
- 🔐 **密码保护**: 不在日志中记录敏感信息
- 🛡️ **路径验证**: 防止目录遍历攻击
- 🔒 **FTPS支持**: 支持FTP over TLS加密传输
- ✅ **文件校验**: 下载完成后自动校验文件完整性

## 🛠️ 编译部署

### 本地编译

```bash
# 安装编译工具
pip install pyinstaller

# 编译GUI版本 (Windows)
pyinstaller --onefile --windowed --name "FTP下载工具" ftp_gui_complete.py

# 编译命令行版本
pyinstaller --onefile --name "FTP命令行工具" ftp_downloader.py

# macOS编译 (生成.app包)
pyinstaller --onefile --windowed --name "FTP下载工具" ftp_gui_complete.py
```

### 🤖 自动编译 (GitHub Actions)

项目配置了完整的CI/CD流程：

- ✅ **多平台同时编译**: Windows + macOS + Linux
- ✅ **自动测试**: 代码质量检查和功能测试  
- ✅ **版本管理**: 自动生成版本号和更新日志
- ✅ **发布管理**: 自动打包并发布到Releases

每次代码推送都会触发自动编译，编译产物可在 [Actions页面](https://github.com/pangwu6111/pythonFtp/actions) 下载。

## 💻 系统要求

| 组件 | 最低要求 | 推荐配置 |
|------|----------|----------|
| **操作系统** | Windows 10, macOS 10.14, Ubuntu 18.04 | Windows 11, macOS 12+, Ubuntu 20.04+ |
| **Python** | 3.8+ (源码运行) | 3.11+ |
| **内存** | 512MB | 1GB+ |
| **磁盘空间** | 100MB | 1GB+ (用于大文件下载) |
| **网络** | 支持FTP协议 | 稳定宽带连接 |

## ❓ 常见问题

<details>
<summary><strong>🔌 连接问题</strong></summary>

**Q: 连接FTP服务器失败怎么办？**

A: 请按以下步骤排查：
1. ✅ 确认服务器地址和端口正确 (默认21端口)
2. ✅ 检查用户名密码是否正确
3. ✅ 确认防火墙没有阻止FTP连接
4. ✅ 尝试切换主动/被动模式
5. ✅ 检查服务器是否支持你的IP访问

```bash
# 测试连接命令
telnet ftp.example.com 21
```
</details>

<details>
<summary><strong>🔄 断点续传问题</strong></summary>

**Q: 断点续传功能不工作？**

A: 可能的原因和解决方案：
1. ❌ **服务器不支持**: 确保FTP服务器支持REST命令
2. ❌ **文件被占用**: 关闭其他程序对目标文件的访问
3. ❌ **磁盘空间不足**: 确保有足够的剩余空间
4. ❌ **权限问题**: 确保对目标目录有写入权限

```python
# 测试服务器是否支持REST命令
ftp.sendcmd('REST 0')  # 如果返回350则支持
```
</details>

<details>
<summary><strong>🖥️ GUI界面问题</strong></summary>

**Q: GUI界面显示异常或乱码？**

A: 尝试以下解决方案：
1. 🔄 更新到最新版本
2. 🎨 检查系统是否支持中文字体
3. 👑 尝试以管理员权限运行
4. 🖥️ 调整系统DPI缩放设置
5. 🔧 重新安装Visual C++ Redistributable (Windows)
</details>

## 🤝 贡献指南

我们欢迎所有形式的贡献！无论是bug报告、功能建议还是代码提交。

### 🐛 报告Bug
1. 在 [Issues](https://github.com/pangwu6111/pythonFtp/issues) 页面创建新issue
2. 使用bug报告模板，提供详细信息
3. 包含错误截图和日志信息

### 💡 功能建议  
1. 先搜索是否已有类似建议
2. 详细描述功能需求和使用场景
3. 如果可能，提供设计草图或示例

### 🔧 代码贡献
```bash
# 1. Fork本仓库到你的账号
# 2. 克隆你的fork
git clone https://github.com/你的用户名/pythonFtp.git

# 3. 创建功能分支
git checkout -b feature/amazing-feature

# 4. 提交更改
git commit -m 'Add some amazing feature'

# 5. 推送到分支
git push origin feature/amazing-feature

# 6. 创建Pull Request
```

### 📋 开发规范
- 🐍 遵循PEP 8 Python代码规范
- 📝 为新功能添加适当的注释和文档
- ✅ 确保所有测试通过
- 🔄 保持向后兼容性

## 📄 开源协议

本项目采用 [MIT License](LICENSE) 开源协议。

```
MIT License - 你可以自由地：
✅ 使用、复制、修改、分发本软件
✅ 用于商业用途
✅ 私人使用
❗ 需要保留版权声明和许可证声明
```

## 📈 更新日志

### 🎉 v1.0.0 (2024-08-30) - 首次发布
- ✨ **核心功能**: 实现FTP断点续传下载
- 🖥️ **多界面**: 提供GUI和命令行两种使用方式  
- 🌐 **跨平台**: 支持Windows/macOS/Linux三大平台
- 📁 **文件管理**: 目录浏览、搜索、排序功能
- 🔄 **智能重试**: 网络中断自动重连机制
- 🚀 **自动编译**: GitHub Actions CI/CD流程

### 🔮 计划中的功能 (v1.1.0)
- 📊 下载队列管理
- 🎨 主题和界面自定义
- 📱 移动端支持
- 🔐 更多安全认证方式
- 📈 下载统计和历史记录

## 🌟 致谢

感谢以下开源项目和贡献者：

- 🐍 **Python ftplib**: 提供FTP协议基础支持
- 🖼️ **tkinter**: GUI界面框架
- 📦 **PyInstaller**: 可执行文件打包工具
- 🤖 **GitHub Actions**: 自动化CI/CD平台
- 👥 **所有贡献者**: 感谢每一个issue、PR和建议

## 📞 联系方式

- 👤 **开发者**: [@pangwu6111](https://github.com/pangwu6111)
- 🏠 **项目主页**: https://github.com/pangwu6111/pythonFtp
- 🐛 **问题反馈**: [Issues](https://github.com/pangwu6111/pythonFtp/issues)
- 💬 **功能建议**: [Discussions](https://github.com/pangwu6111/pythonFtp/discussions)

---

<div align="center">

### ⭐ 如果这个项目对你有帮助，请给个Star支持一下！⭐

**让更多人发现这个实用的FTP工具** 🚀

[![Star History Chart](https://api.star-history.com/svg?repos=pangwu6111/pythonFtp&type=Date)](https://star-history.com/#pangwu6111/pythonFtp&Date)

</div>