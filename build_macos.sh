#!/bin/bash
# FTP工具 - macOS编译脚本

echo "=========================================="
echo "    FTP工具 - macOS编译脚本"
echo "    编译为macOS应用程序"
echo "=========================================="
echo

# 检查Python环境
echo "🔍 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3未安装，请先安装Python3"
    echo "   可以通过Homebrew安装: brew install python"
    exit 1
fi

echo "✅ Python3环境正常"
python3 --version

# 检查pip
echo
echo "🔍 检查pip..."
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3未找到"
    exit 1
fi

# 安装PyInstaller
echo
echo "📦 检查/安装PyInstaller..."
if ! python3 -c "import PyInstaller" &> /dev/null; then
    echo "正在安装PyInstaller..."
    pip3 install pyinstaller
    if [ $? -ne 0 ]; then
        echo "❌ PyInstaller安装失败"
        exit 1
    fi
fi
echo "✅ PyInstaller准备就绪"

# 检查源文件
if [ ! -f "ftp_gui_complete.py" ]; then
    echo "❌ 源文件 ftp_gui_complete.py 不存在"
    exit 1
fi

# 编译macOS应用
echo
echo "🔨 正在编译macOS应用程序..."
python3 -m PyInstaller \
    --onefile \
    --windowed \
    --name "FTP工具" \
    --distpath "./dist" \
    --workpath "./build" \
    --specpath "." \
    ftp_gui_complete.py

if [ $? -eq 0 ]; then
    echo "✅ 编译成功！"
    echo
    echo "📁 输出文件: ./dist/FTP工具"
    echo "💡 这是一个macOS可执行文件，不是Windows .exe文件"
    echo
    
    # 询问是否运行
    read -p "是否立即运行编译好的程序? (y/n): " choice
    if [[ $choice == "y" || $choice == "Y" ]]; then
        echo "🚀 正在启动程序..."
        open "./dist/FTP工具"
    fi
else
    echo "❌ 编译失败"
    exit 1
fi

echo
echo "🎉 编译完成！"