@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ========================================
echo    FTP断点续传下载工具 - 完整版
echo    ✓ 完整的目录排序和搜索功能
echo    ✓ 智能导航和文件管理
echo    ✓ 优化的FTP连接兼容性
echo    ✓ 修复所有已知问题
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
if not exist "%~dp0ftp_gui_complete.py" (
    echo ✗ 错误: 未找到 ftp_gui_complete.py 文件
    echo   请确保该文件与 %~nx0 在同一目录下
    echo.
    pause
    goto :eof
)

echo ✓ 正在启动FTP GUI客户端 (完整版)...
echo.
echo 🎯 主要功能:
echo   • 智能FTP连接 (支持各种服务器配置)
echo   • 文件排序 (名称/大小/日期/类型，升序/降序)
echo   • 实时搜索过滤
echo   • 目录导航 (上级目录/根目录/路径显示)
echo   • 断点续传下载
echo   • 批量文件操作
echo   • 详细连接日志和调试信息
echo.
echo 🚀 针对你的FTP服务器 192.168.31.6:2121 进行了特别优化！
echo.

REM 启动GUI程序
python "%~dp0ftp_gui_complete.py"

REM 如果有错误，暂停显示
if errorlevel 1 (
    echo.
    echo 程序异常退出，按任意键关闭...
    pause >nul
)