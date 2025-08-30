# FTP断点续传下载工具 - 项目结构

## 📁 项目文件说明

```
winftp/
├── 📄 ftp_downloader.py          # 核心Python实现 (命令行版本)
├── 📄 ftp_download.bat           # Windows批处理包装器
├── 📄 ftp_download.ps1           # PowerShell版本
├── 📄 ftp_gui.py                 # 基础GUI版本
├── 📄 ftp_gui_advanced.py        # 高级GUI版本 (完整功能)
├── 📄 ftp_gui_simple.py          # 简化GUI版本 (轻量级)
├── 📄 run_ftp_gui.bat            # GUI启动脚本
├── 📄 test_ftp_download.py       # 功能测试脚本
├── 📄 README.md                  # 命令行版本说明
├── 📄 GUI_README.md              # GUI版本详细说明
└── 📄 PROJECT_STRUCTURE.md       # 项目结构说明 (本文件)
```

## 🚀 版本选择指南

### 1. 命令行版本 (推荐新手)
**文件**: `ftp_downloader.py` + `ftp_download.bat`

**特点**:
- ✅ 轻量级，资源占用少
- ✅ 适合脚本自动化
- ✅ 支持所有核心功能
- ✅ 兼容性最好

**使用场景**:
- 服务器环境下载
- 批处理脚本集成
- 资源受限环境
- 命令行爱好者

**启动方式**:
```cmd
# Windows
ftp_download.bat ftp://ftp.example.com/file.zip

# 直接Python
python ftp_downloader.py ftp://ftp.example.com/file.zip
```

### 2. 简化GUI版本 (推荐一般用户)
**文件**: `ftp_gui_simple.py`

**特点**:
- ✅ 图形界面，操作直观
- ✅ 功能精简，稳定可靠
- ✅ 资源占用适中
- ✅ 启动速度快

**使用场景**:
- 日常文件下载
- 不需要复杂功能
- 追求稳定性
- 初学者使用

**启动方式**:
```cmd
python ftp_gui_simple.py
```

### 3. 基础GUI版本 (推荐进阶用户)
**文件**: `ftp_gui.py` + `run_ftp_gui.bat`

**特点**:
- ✅ 完整的GUI功能
- ✅ 支持批量下载
- ✅ 传输队列管理
- ✅ 配置文件保存

**使用场景**:
- 需要批量操作
- 频繁使用FTP
- 需要进度监控
- 多任务下载

**启动方式**:
```cmd
# Windows (推荐)
run_ftp_gui.bat

# 直接Python
python ftp_gui.py
```

### 4. 高级GUI版本 (推荐专业用户)
**文件**: `ftp_gui_advanced.py`

**特点**:
- ✅ 最完整的功能集
- ✅ 文件同步功能
- ✅ 书签和会话管理
- ✅ 高级文件操作
- ✅ 详细的日志系统

**使用场景**:
- 专业FTP管理
- 文件同步需求
- 复杂的传输任务
- 企业级应用

**启动方式**:
```cmd
python ftp_gui_advanced.py
```

## 🔧 功能对比表

| 功能特性 | 命令行版 | 简化GUI | 基础GUI | 高级GUI |
|---------|---------|---------|---------|---------|
| 断点续传 | ✅ | ✅ | ✅ | ✅ |
| 批量下载 | ✅ | ✅ | ✅ | ✅ |
| 进度显示 | ✅ | ✅ | ✅ | ✅ |
| 自动重试 | ✅ | ✅ | ✅ | ✅ |
| 图形界面 | ❌ | ✅ | ✅ | ✅ |
| 目录浏览 | ❌ | ✅ | ✅ | ✅ |
| 传输队列 | ❌ | ✅ | ✅ | ✅ |
| 配置保存 | ❌ | ❌ | ✅ | ✅ |
| 文件同步 | ❌ | ❌ | ❌ | ✅ |
| 书签管理 | ❌ | ❌ | ❌ | ✅ |
| 会话管理 | ❌ | ❌ | ❌ | ✅ |
| 操作日志 | ❌ | ❌ | ❌ | ✅ |
| 文件比较 | ❌ | ❌ | ❌ | ✅ |
| 批量操作 | ❌ | ❌ | ❌ | ✅ |

## 📋 系统要求

### 最低要求
- **Python**: 3.6+
- **内存**: 256MB
- **磁盘**: 10MB

### 推荐配置
- **Python**: 3.8+
- **内存**: 512MB+
- **磁盘**: 50MB+
- **网络**: 稳定的互联网连接

### GUI版本额外要求
- **tkinter**: 通常随Python安装
- **显示器**: 1024x768以上分辨率

## 🛠️ 安装部署

### 1. 环境准备
```bash
# 检查Python版本
python --version

# 检查tkinter (仅GUI版本需要)
python -c "import tkinter; print('tkinter可用')"
```

### 2. 文件部署
```bash
# 下载所有文件到同一目录
# 确保文件权限正确 (Linux/macOS)
chmod +x *.py
chmod +x *.bat
```

### 3. 配置文件 (可选)
```bash
# 创建配置目录
mkdir config

# 复制示例配置
cp ftp_config.json.example config/ftp_config.json
```

## 🔍 测试验证

### 1. 功能测试
```bash
# 运行测试脚本
python test_ftp_download.py

# 测试命令行版本
python ftp_downloader.py ftp://ftp.gnu.org/gnu/hello/hello-2.12.tar.gz -o test_download.tar.gz

# 测试GUI版本
python ftp_gui_simple.py
```

### 2. 连接测试
使用以下公共FTP服务器测试连接:
- `ftp://ftp.gnu.org/` (匿名)
- `ftp://test.rebex.net/` (用户名: demo, 密码: password)

## 📝 配置文件说明

### ftp_config.json (基础配置)
```json
{
  "host": "ftp.example.com",
  "port": "21",
  "username": "anonymous",
  "download_path": "C:\\Users\\Username\\Downloads",
  "max_concurrent": 3,
  "chunk_size": 8192,
  "timeout": 30,
  "auto_retry": true,
  "retry_count": 3
}
```

### sync_profiles.json (同步配置)
```json
{
  "profiles": [
    {
      "name": "网站同步",
      "remote_path": "/public_html",
      "local_path": "D:\\Website",
      "sync_mode": "download",
      "file_filters": ["*.html", "*.css", "*.js"],
      "exclude_patterns": ["*.log", "cache/*"],
      "auto_sync": false,
      "sync_interval": 3600
    }
  ]
}
```

### bookmarks.json (书签配置)
```json
{
  "bookmarks": [
    {
      "name": "公司FTP",
      "host": "ftp.company.com",
      "port": 21,
      "username": "employee",
      "default_path": "/home/employee"
    }
  ]
}
```

## 🚨 故障排除

### 常见问题

#### 1. Python相关
```bash
# 问题: 找不到Python
# 解决: 安装Python 3.6+并添加到PATH

# 问题: 找不到tkinter
# 解决: 重新安装Python，确保包含tkinter
```

#### 2. 连接问题
```bash
# 问题: 连接超时
# 解决: 检查网络、防火墙、服务器地址

# 问题: 认证失败
# 解决: 确认用户名密码，尝试匿名登录
```

#### 3. 下载问题
```bash
# 问题: 下载中断
# 解决: 程序支持断点续传，重新开始即可

# 问题: 权限错误
# 解决: 检查本地目录写权限
```

## 📈 性能优化

### 1. 下载速度优化
- 调整并发数 (max_concurrent)
- 增大块大小 (chunk_size)
- 使用有线网络连接

### 2. 内存使用优化
- 减少并发下载数
- 定期清理下载列表
- 关闭不需要的功能

### 3. 稳定性优化
- 启用自动重试
- 增加超时时间
- 使用被动模式连接

## 🔄 版本升级

### 升级步骤
1. 备份配置文件
2. 下载新版本文件
3. 替换旧文件
4. 恢复配置文件
5. 测试功能正常

### 配置迁移
- 配置文件通常向后兼容
- 新功能可能需要新的配置项
- 建议查看更新日志

## 📞 技术支持

### 获取帮助
1. 查看内置帮助文档
2. 检查操作日志
3. 运行测试脚本
4. 查看配置文件格式

### 报告问题
请提供以下信息:
- 操作系统版本
- Python版本
- 错误信息截图
- 操作步骤描述
- 配置文件内容 (去除敏感信息)

## 📄 许可证

本项目基于MIT许可证开源，可自由使用和修改。