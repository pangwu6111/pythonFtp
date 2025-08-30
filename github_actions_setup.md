# GitHub Actions 手动设置指南

由于认证问题，请手动在GitHub上设置自动编译：

## 步骤1：在GitHub网页上创建文件

1. 访问你的仓库：https://github.com/pangwu6111/pythonFtp
2. 点击 "Create new file"
3. 文件路径输入：`.github/workflows/build.yml`
4. 复制下面的内容到文件中：

```yaml
name: 构建跨平台可执行文件

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [windows-latest, macos-latest, ubuntu-latest]
        include:
          - os: windows-latest
            executable_suffix: .exe
            build_name: windows
          - os: macos-latest
            executable_suffix: ""
            build_name: macos
          - os: ubuntu-latest
            executable_suffix: ""
            build_name: linux

    steps:
    - uses: actions/checkout@v3
    
    - name: 设置Python环境
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: 安装依赖
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pyinstaller
    
    - name: 构建可执行文件 (Windows)
      if: matrix.os == 'windows-latest'
      run: |
        pyinstaller --onefile --windowed --name "FTP下载工具" ftp_gui_complete.py
        pyinstaller --onefile --name "FTP命令行工具" ftp_downloader.py
    
    - name: 构建可执行文件 (macOS/Linux)
      if: matrix.os != 'windows-latest'
      run: |
        pyinstaller --onefile --windowed --name "FTP下载工具" ftp_gui_complete.py
        pyinstaller --onefile --name "FTP命令行工具" ftp_downloader.py
    
    - name: 上传构建产物
      uses: actions/upload-artifact@v3
      with:
        name: ftp-tools-${{ matrix.build_name }}
        path: |
          dist/FTP下载工具${{ matrix.executable_suffix }}
          dist/FTP命令行工具${{ matrix.executable_suffix }}
```

## 步骤2：提交文件

1. 在页面底部添加提交信息：`🚀 添加GitHub Actions自动编译配置`
2. 点击 "Commit new file"

## 步骤3：查看编译结果

1. 提交后，GitHub Actions会自动开始编译
2. 访问 "Actions" 标签页查看编译进度
3. 编译完成后，在 "Artifacts" 中下载编译好的可执行文件

## 编译产物说明

- **ftp-tools-windows**: Windows .exe文件
- **ftp-tools-macos**: macOS应用程序
- **ftp-tools-linux**: Linux可执行文件

每个包都包含GUI版本和命令行版本两个工具。