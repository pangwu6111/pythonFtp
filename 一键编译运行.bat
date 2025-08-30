@echo off
chcp 65001 >nul
title FTP工具 - 一键编译运行

echo.
echo ╔══════════════════════════════════════╗
echo ║        FTP工具 - 一键编译运行        ║
echo ╚══════════════════════════════════════╝
echo.

echo [1/4] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装，请先安装Python
    pause
    exit /b 1
)
echo ✅ Python环境正常

echo.
echo [2/4] 安装/检查PyInstaller...
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo 📦 正在安装PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo ❌ PyInstaller安装失败
        pause
        exit /b 1
    )
)
echo ✅ PyInstaller准备就绪

echo.
echo [3/4] 编译可执行文件...
echo 🔨 正在编译，请稍候...

pyinstaller --onefile --windowed --name "FTP工具" ftp_gui_complete.py >nul 2>&1

if errorlevel 1 (
    echo ❌ 编译失败，尝试详细模式...
    pyinstaller --onefile --windowed --name "FTP工具" ftp_gui_complete.py
    pause
    exit /b 1
)

echo ✅ 编译成功

echo.
echo [4/4] 启动程序...
if exist "dist\FTP工具.exe" (
    echo 🚀 正在启动FTP工具...
    start "" "dist\FTP工具.exe"
    echo.
    echo ✅ 程序已启动！
    echo 📁 可执行文件位置: %cd%\dist\FTP工具.exe
    echo.
    echo 💡 提示: 可以将exe文件复制到任何Windows电脑上运行
) else (
    echo ❌ 可执行文件未找到
    pause
    exit /b 1
)

echo.
echo 🎉 完成！按任意键退出...
pause >nul