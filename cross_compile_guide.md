# macOS编译Windows .exe文件指南

## 🎯 问题说明
在macOS中直接编译Windows .exe文件是有挑战的，因为需要跨平台编译。以下是几种解决方案：

## 🛠️ 解决方案

### 方案一：使用Docker (推荐)

#### 1. 安装Docker
```bash
# 安装Docker Desktop for Mac
# 从官网下载: https://www.docker.com/products/docker-desktop
```

#### 2. 创建Windows编译环境
```bash
# 拉取Windows Python镜像
docker pull python:3.9-windowsservercore

# 创建编译容器
docker run -it --name ftp-builder -v $(pwd):/app python:3.9-windowsservercore
```

#### 3. 在容器中编译
```cmd
# 进入容器后执行
cd /app
pip install pyinstaller
pyinstaller --onefile --windowed --name "FTP工具" ftp_gui_complete.py
```

### 方案二：使用Wine (复杂)

#### 1. 安装Wine
```bash
# 使用Homebrew安装
brew install --cask wine-stable

# 或使用MacPorts
sudo port install wine
```

#### 2. 安装Windows Python
```bash
# 下载Windows版Python安装包
# 使用Wine运行安装程序
wine python-3.9.0.exe
```

#### 3. 编译
```bash
# 使用Wine运行PyInstaller
wine python -m pip install pyinstaller
wine python -m PyInstaller --onefile --windowed ftp_gui_complete.py
```

### 方案三：虚拟机 (最可靠)

#### 1. 安装虚拟机软件
- **Parallels Desktop** (付费，性能最好)
- **VMware Fusion** (付费)
- **VirtualBox** (免费)

#### 2. 安装Windows系统
- 下载Windows 10/11 ISO
- 在虚拟机中安装Windows
- 安装Python和PyInstaller

#### 3. 在Windows中编译
```cmd
# 在Windows虚拟机中执行
pip install pyinstaller
pyinstaller --onefile --windowed --name "FTP工具" ftp_gui_complete.py
```

### 方案四：云编译服务

#### GitHub Actions (免费)
创建 `.github/workflows/build.yml`:

```yaml
name: Build Windows EXE

on: [push]

jobs:
  build:
    runs-on: windows-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        pip install pyinstaller
    
    - name: Build EXE
      run: |
        pyinstaller --onefile --windowed --name "FTP工具" ftp_gui_complete.py
    
    - name: Upload artifact
      uses: actions/upload-artifact@v2
      with:
        name: FTP工具
        path: dist/FTP工具.exe
```

### 方案五：在线编译服务

#### 1. Replit
- 访问 https://replit.com
- 创建Python项目
- 上传代码
- 使用在线终端编译

#### 2. CodeSandbox
- 访问 https://codesandbox.io
- 创建Python环境
- 编译项目

## 🍎 macOS本地编译 (推荐)

如果你主要在macOS上使用，建议编译为macOS应用：

### 使用提供的脚本
```bash
# 给脚本执行权限
chmod +x build_macos.sh

# 运行编译脚本
./build_macos.sh
```

### 手动编译
```bash
# 安装PyInstaller
pip3 install pyinstaller

# 编译macOS应用
pyinstaller --onefile --windowed --name "FTP工具" ftp_gui_complete.py

# 运行
./dist/FTP工具
```

## 📦 创建macOS应用包 (.app)

```bash
# 编译为.app包
pyinstaller --onefile --windowed --name "FTP工具" --add-data "README.md:." ftp_gui_complete.py

# 创建DMG安装包 (需要安装create-dmg)
brew install create-dmg
create-dmg --volname "FTP工具" --window-pos 200 120 --window-size 600 300 --icon-size 100 --icon "FTP工具.app" 175 120 --hide-extension "FTP工具.app" --app-drop-link 425 120 "FTP工具.dmg" "dist/"
```

## 🎯 推荐方案

### 对于个人使用：
1. **macOS版本**: 使用 `build_macos.sh` 编译macOS应用
2. **Windows版本**: 使用虚拟机或Docker

### 对于分发：
1. **GitHub Actions**: 自动化编译多平台版本
2. **云服务**: 使用在线编译服务

### 对于开发：
1. **Docker**: 一次配置，多次使用
2. **虚拟机**: 最接近真实Windows环境

## 💡 注意事项

1. **跨平台编译限制**: PyInstaller通常只能编译当前平台的可执行文件
2. **依赖问题**: Windows和macOS的系统依赖不同
3. **测试重要性**: 跨平台编译的程序需要在目标平台测试
4. **文件大小**: 跨平台编译可能产生更大的文件

## 🚀 快速开始

如果你现在就想在macOS上编译：

```bash
# 1. 给脚本执行权限
chmod +x build_macos.sh

# 2. 运行编译
./build_macos.sh

# 3. 运行程序
./dist/FTP工具
```

这将创建一个macOS可执行文件，虽然不是.exe，但功能完全相同！