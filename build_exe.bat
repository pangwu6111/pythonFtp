@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ========================================
echo    FTP工具 - 编译为可执行文件
echo    使用PyInstaller打包Python程序
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ✗ 错误: 未找到Python，请先安装Python
    pause
    goto :eof
)

echo ✓ 检测到Python环境

REM 检查PyInstaller是否安装
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  PyInstaller未安装，正在安装...
    echo.
    python -m pip install pyinstaller
    if errorlevel 1 (
        echo ✗ PyInstaller安装失败，请手动安装:
        echo   pip install pyinstaller
        pause
        goto :eof
    )
    echo ✓ PyInstaller安装成功
) else (
    echo ✓ PyInstaller已安装
)

REM 检查源文件是否存在
if not exist "%~dp0ftp_gui_complete.py" (
    echo ✗ 错误: 未找到 ftp_gui_complete.py 文件
    pause
    goto :eof
)

echo.
echo 🚀 开始编译可执行文件...
echo.

REM 创建输出目录
if not exist "%~dp0dist" mkdir "%~dp0dist"

REM 使用PyInstaller编译
echo 正在编译，请稍候...
python -m PyInstaller ^
    --onefile ^
    --windowed ^
    --name "FTP下载工具" ^
    --icon="%~dp0icon.ico" ^
    --add-data "README.md;." ^
    --hidden-import tkinter ^
    --hidden-import tkinter.ttk ^
    --hidden-import tkinter.filedialog ^
    --hidden-import tkinter.messagebox ^
    --hidden-import tkinter.scrolledtext ^
    --distpath "%~dp0dist" ^
    --workpath "%~dp0build" ^
    --specpath "%~dp0" ^
    "%~dp0ftp_gui_complete.py"

if errorlevel 1 (
    echo.
    echo ✗ 编译失败！
    echo.
    echo 💡 可能的解决方案:
    echo   1. 确保所有依赖都已安装
    echo   2. 检查Python版本兼容性
    echo   3. 尝试手动编译命令
    echo.
    pause
    goto :eof
)

echo.
echo ✅ 编译成功！
echo.
echo 📁 输出文件位置:
echo   %~dp0dist\FTP下载工具.exe
echo.
echo 📋 文件信息:
if exist "%~dp0dist\FTP下载工具.exe" (
    for %%F in ("%~dp0dist\FTP下载工具.exe") do (
        echo   文件大小: %%~zF 字节
        echo   创建时间: %%~tF
    )
) else (
    echo   ⚠️  可执行文件未找到，请检查编译过程
)

echo.
echo 🎯 使用说明:
echo   • 可执行文件是独立的，不需要安装Python
echo   • 可以复制到任何Windows电脑上运行
echo   • 首次运行可能需要几秒钟启动时间
echo   • 如果杀毒软件报警，请添加信任
echo.

REM 询问是否立即运行
set /p choice="是否立即运行编译好的程序? (y/n): "
if /i "%choice%"=="y" (
    echo 正在启动程序...
    start "" "%~dp0dist\FTP下载工具.exe"
)

echo.
echo 🎉 编译完成！按任意键退出...
pause >nul