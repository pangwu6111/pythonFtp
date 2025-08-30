#!/bin/bash
# 使用Docker在macOS中编译Windows .exe文件

echo "=========================================="
echo "  使用Docker编译Windows .exe文件"
echo "  在macOS中跨平台编译解决方案"
echo "=========================================="
echo

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装"
    echo "请先安装Docker Desktop for Mac:"
    echo "https://www.docker.com/products/docker-desktop"
    exit 1
fi

echo "✅ Docker环境检查通过"

# 检查源文件
if [ ! -f "ftp_gui_complete.py" ]; then
    echo "❌ 源文件 ftp_gui_complete.py 不存在"
    exit 1
fi

echo "✅ 源文件检查通过"

# 创建Dockerfile
echo "📝 创建Docker编译环境..."
cat > Dockerfile << 'EOF'
# 使用Windows Python基础镜像
FROM python:3.9-windowsservercore

# 设置工作目录
WORKDIR /app

# 安装PyInstaller
RUN pip install pyinstaller

# 复制源文件
COPY ftp_gui_complete.py .

# 编译命令
CMD ["python", "-m", "PyInstaller", "--onefile", "--windowed", "--name", "FTP工具", "ftp_gui_complete.py"]
EOF

echo "✅ Dockerfile创建完成"

# 构建Docker镜像
echo
echo "🔨 构建Docker镜像..."
docker build -t ftp-builder .

if [ $? -ne 0 ]; then
    echo "❌ Docker镜像构建失败"
    exit 1
fi

echo "✅ Docker镜像构建成功"

# 运行编译
echo
echo "🚀 开始编译Windows .exe文件..."
docker run --rm -v $(pwd)/dist:/app/dist ftp-builder

if [ $? -eq 0 ]; then
    echo "✅ 编译成功！"
    echo
    echo "📁 输出文件: ./dist/FTP工具.exe"
    echo "💡 这是一个Windows .exe文件，可以在Windows系统上运行"
    
    # 显示文件信息
    if [ -f "./dist/FTP工具.exe" ]; then
        echo "📊 文件大小: $(ls -lh ./dist/FTP工具.exe | awk '{print $5}')"
    fi
else
    echo "❌ 编译失败"
    exit 1
fi

# 清理Docker镜像
read -p "是否清理Docker镜像以节省空间? (y/n): " choice
if [[ $choice == "y" || $choice == "Y" ]]; then
    docker rmi ftp-builder
    echo "🧹 Docker镜像已清理"
fi

echo
echo "🎉 Windows .exe文件编译完成！"
echo "现在可以将 ./dist/FTP工具.exe 复制到Windows系统上运行"