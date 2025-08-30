# FTP断点续传下载工具

一个功能强大的FTP客户端，支持断点续传、目录浏览、文件搜索和批量下载。

## 🌟 功能特性

### 🚀 核心功能
- ✅ **断点续传下载** - 网络中断后自动续传
- ✅ **目录浏览** - 直观的文件管理界面
- ✅ **文件搜索** - 实时搜索过滤功能
- ✅ **批量下载** - 支持多文件并发下载
- ✅ **智能导航** - 上级目录、根目录快速切换

### 📊 高级功能
- ✅ **文件排序** - 按名称、大小、日期、类型排序
- ✅ **连接测试** - 智能FTP连接诊断
- ✅ **详细日志** - 完整的操作记录和调试信息
- ✅ **会话管理** - 保存连接配置
- ✅ **进度监控** - 实时显示下载进度和速度

### 🔧 技术特性
- ✅ **跨平台支持** - Windows、macOS、Linux
- ✅ **GUI界面** - 基于Tkinter的现代化界面
- ✅ **多线程下载** - 高效的并发处理
- ✅ **错误恢复** - 智能重连和错误处理

## 📥 下载使用

### 直接下载可执行文件
访问 [Releases](../../releases) 页面下载对应平台的可执行文件：

- **Windows用户**: 下载 `FTP工具-Windows.exe`
- **macOS用户**: 下载 `FTP工具-macOS`
- **Linux用户**: 下载 `FTP工具-Linux`

### 从源码运行
```bash
# 克隆仓库
git clone https://github.com/你的用户名/ftp-download-tool.git
cd ftp-download-tool

# 安装依赖
pip install -r requirements.txt

# 运行程序
python ftp_gui_complete.py
```

## 🚀 快速开始

### 1. 连接FTP服务器
- 输入服务器地址和端口
- 填写用户名和密码
- 点击"测试连接"验证
- 点击"连接"建立连接

### 2. 浏览文件
- 双击目录进入
- 使用搜索框过滤文件
- 选择排序方式
- 点击导航按钮切换目录

### 3. 下载文件
- 选择要下载的文件
- 设置保存路径
- 点击"下载选中"或"下载全部"
- 监控下载进度

## 🛠️ 开发环境

### 系统要求
- Python 3.6+
- tkinter (通常随Python安装)
- 支持的操作系统: Windows 7+, macOS 10.12+, Linux

### 依赖包
```
# 核心依赖 (Python标准库)
tkinter
ftplib
threading
socket
pathlib
datetime

# 编译依赖 (可选)
pyinstaller
```

### 本地开发
```bash
# 克隆项目
git clone https://github.com/你的用户名/ftp-download-tool.git
cd ftp-download-tool

# 运行开发版本
python ftp_gui_complete.py

# 编译可执行文件 (Windows)
pyinstaller --onefile --windowed --name "FTP工具" ftp_gui_complete.py

# 编译可执行文件 (macOS)
chmod +x build_macos.sh
./build_macos.sh

# Docker跨平台编译
chmod +x docker_build.sh
./docker_build.sh
```

## 📖 使用说明

### 连接配置
- **服务器**: FTP服务器地址 (如: ftp.example.com 或 192.168.1.100)
- **端口**: FTP端口 (默认21，也支持其他端口如2121)
- **用户名**: FTP用户名 (匿名连接使用 anonymous)
- **密码**: FTP密码 (匿名连接可留空)
- **被动模式**: 推荐开启，解决防火墙问题
- **超时**: 连接超时时间，网络较慢时可增加

### 文件操作
- **双击目录**: 进入子目录
- **双击文件**: 添加到下载队列
- **⬆️ 按钮**: 返回上级目录
- **🏠 按钮**: 返回根目录
- **🔄 按钮**: 刷新当前目录

### 搜索和排序
- **搜索框**: 输入关键词实时过滤文件
- **排序选项**: 按名称、大小、日期、类型排序
- **升序/降序**: 切换排序方向
- **显示隐藏文件**: 显示以"."开头的文件

### 下载管理
- **保存路径**: 设置文件下载位置
- **下载选中**: 下载当前选中的文件
- **下载全部**: 下载当前目录所有文件
- **进度监控**: 查看下载进度、速度、状态
- **断点续传**: 自动从中断位置继续下载

## 🔧 编译说明

### Windows编译
```cmd
# 安装PyInstaller
pip install pyinstaller

# 编译单文件版本
pyinstaller --onefile --windowed --name "FTP工具" ftp_gui_complete.py

# 使用自动化脚本
一键编译运行.bat
```

### macOS编译
```bash
# 给脚本执行权限
chmod +x build_macos.sh

# 运行编译脚本
./build_macos.sh
```

### 跨平台编译 (Docker)
```bash
# 安装Docker后运行
chmod +x docker_build.sh
./docker_build.sh
```

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

### 开发流程
1. Fork本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

### 代码规范
- 使用Python PEP 8代码风格
- 添加适当的注释和文档字符串
- 确保新功能有相应的测试
- 保持向后兼容性

## 📝 更新日志

### v1.0.0 (2025-08-30)
- ✨ 初始版本发布
- ✅ 基础FTP连接功能
- ✅ 断点续传下载
- ✅ 目录浏览和导航
- ✅ 文件搜索和排序
- ✅ 批量下载支持
- ✅ 跨平台编译支持

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- 感谢Python社区提供的优秀工具和库
- 感谢所有贡献者和用户的支持
- 特别感谢tkinter提供的GUI框架支持

## 📞 联系方式

- 项目主页: https://github.com/你的用户名/ftp-download-tool
- 问题反馈: [Issues](../../issues)
- 功能建议: [Discussions](../../discussions)

## 🌟 Star History

如果这个项目对你有帮助，请给个Star⭐支持一下！

[![Star History Chart](https://api.star-history.com/svg?repos=你的用户名/ftp-download-tool&type=Date)](https://star-history.com/#你的用户名/ftp-download-tool&Date)