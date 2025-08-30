@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ========================================
echo    FTP断点续传下载工具 - 修复版
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ✗ 错误: 未找到Python，请先安装Python 3.6+
    echo   下载地址: https://www.python.org/downloads/
    echo.
    pause
    goto :eof
)

REM 检查tkinter是否可用
python -c "import tkinter" >nul 2>&1
if errorlevel 1 (
    echo ✗ 错误: tkinter模块不可用
    echo   请确保Python安装时包含了tkinter模块
    echo.
    pause
    goto :eof
)

REM 检查脚本文件是否存在
if not exist "%~dp0ftp_gui_fixed.py" (
    echo ✗ 错误: 未找到 ftp_gui_fixed.py 文件
    echo   请确保该文件与 %~nx0 在同一目录下
    echo.
    pause
    goto :eof
)

echo ✓ 正在启动FTP GUI客户端 (修复版)...
echo.

REM 启动GUI程序
python "%~dp0ftp_gui_fixed.py"

REM 如果有错误，暂停显示
if errorlevel 1 (
    echo.
    echo 程序异常退出，按任意键关闭...
    pause >nul
)