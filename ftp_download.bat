@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM FTP断点续传下载工具 - Windows批处理包装器

if "%~1"=="" (
    echo.
    echo FTP断点续传下载工具
    echo.
    echo 用法:
    echo   %~nx0 ^<FTP_URL^> [选项]
    echo.
    echo 示例:
    echo   %~nx0 ftp://user:pass@ftp.example.com/path/file.zip
    echo   %~nx0 ftp://ftp.example.com/pub/file.zip -o D:\Downloads\file.zip
    echo   %~nx0 ftp://ftp.example.com/pub/ -l
    echo.
    echo 选项:
    echo   -o, --output PATH     指定本地保存路径
    echo   -c, --chunk-size N    设置下载块大小 ^(默认: 8192^)
    echo   -r, --retries N       设置最大重试次数 ^(默认: 3^)
    echo   -t, --timeout N       设置连接超时时间 ^(默认: 30秒^)
    echo   -l, --list            列出远程目录文件
    echo   -h, --help            显示帮助信息
    echo.
    goto :eof
)

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ✗ 错误: 未找到Python，请先安装Python 3.6+
    echo   下载地址: https://www.python.org/downloads/
    pause
    goto :eof
)

REM 检查脚本文件是否存在
if not exist "%~dp0ftp_downloader.py" (
    echo ✗ 错误: 未找到 ftp_downloader.py 文件
    echo   请确保该文件与 %~nx0 在同一目录下
    pause
    goto :eof
)

REM 执行Python脚本
python "%~dp0ftp_downloader.py" %*

REM 如果有错误，暂停显示
if errorlevel 1 (
    echo.
    echo 按任意键退出...
    pause >nul
)