#!/bin/bash

echo "🔧 修复GitHub上传问题"
echo "========================"

# 1. 修复分支名
echo "📝 修复分支名..."
git branch -m master main 2>/dev/null || echo "分支已经是main"

# 2. 确保GitHub Actions文件在正确位置
echo "📁 确保GitHub Actions文件位置正确..."
mkdir -p .github/workflows
if [ -f "github_actions_build.yml" ]; then
    mv github_actions_build.yml .github/workflows/
    echo "✅ GitHub Actions文件已移动"
fi

# 3. 添加所有文件
echo "📦 添加文件..."
git add .

# 4. 检查是否有变更
if git diff --staged --quiet; then
    echo "ℹ️  没有新的变更需要提交"
else
    echo "💾 创建提交..."
    git commit -m "🔧 修复GitHub配置

- 修复分支名称为main
- 添加GitHub Actions自动编译配置
- 确保所有文件正确提交"
fi

# 5. 设置远程仓库
echo "🔗 设置远程仓库..."
git remote remove origin 2>/dev/null || true
git remote add origin https://github.com/pangwu6111/pythonFtp.git

# 6. 推送到GitHub
echo "🚀 推送到GitHub..."
echo "💡 如果失败，请确保："
echo "   1. GitHub仓库 https://github.com/pangwu6111/pythonFtp 已创建"
echo "   2. 你有推送权限"
echo "   3. 网络连接正常"
echo

git push -u origin main

if [ $? -eq 0 ]; then
    echo
    echo "🎉 上传成功！"
    echo "📋 接下来："
    echo "1. 访问: https://github.com/pangwu6111/pythonFtp"
    echo "2. 点击 Actions 查看编译进度"
    echo "3. 编译完成后下载可执行文件"
else
    echo
    echo "❌ 推送失败"
    echo "💡 请确保在GitHub上创建了仓库: https://github.com/pangwu6111/pythonFtp"
    echo "📖 或查看详细说明: GitHub上传指南.md"
fi