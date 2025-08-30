#!/bin/bash
# GitHub自动上传脚本

echo "=========================================="
echo "    FTP工具 - GitHub自动上传脚本"
echo "=========================================="
echo

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查Git是否安装
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git未安装，请先安装Git${NC}"
    echo "macOS: brew install git"
    echo "或访问: https://git-scm.com/download"
    exit 1
fi

echo -e "${GREEN}✅ Git环境检查通过${NC}"

# 获取用户输入
echo
echo -e "${BLUE}📝 请输入GitHub信息:${NC}"
read -p "GitHub用户名: " github_username
read -p "仓库名称 (建议: ftp-download-tool): " repo_name

# 设置默认仓库名
if [ -z "$repo_name" ]; then
    repo_name="ftp-download-tool"
fi

echo
echo -e "${YELLOW}📋 确认信息:${NC}"
echo "GitHub用户名: $github_username"
echo "仓库名称: $repo_name"
echo "仓库地址: https://github.com/$github_username/$repo_name"
echo

read -p "信息正确吗? (y/n): " confirm
if [[ $confirm != "y" && $confirm != "Y" ]]; then
    echo "已取消操作"
    exit 0
fi

# 检查是否已经是Git仓库
if [ ! -d ".git" ]; then
    echo
    echo -e "${BLUE}🔧 初始化Git仓库...${NC}"
    git init
    echo -e "${GREEN}✅ Git仓库初始化完成${NC}"
else
    echo -e "${GREEN}✅ 检测到现有Git仓库${NC}"
fi

# 创建.github/workflows目录
echo
echo -e "${BLUE}📁 创建GitHub Actions目录...${NC}"
mkdir -p .github/workflows

# 移动GitHub Actions配置文件
if [ -f "github_actions_build.yml" ]; then
    mv github_actions_build.yml .github/workflows/
    echo -e "${GREEN}✅ GitHub Actions配置文件已移动${NC}"
else
    echo -e "${YELLOW}⚠️  未找到github_actions_build.yml文件${NC}"
fi

# 检查必要文件
echo
echo -e "${BLUE}🔍 检查项目文件...${NC}"
required_files=("ftp_gui_complete.py" "README.md" "requirements.txt" "LICENSE" ".gitignore")
missing_files=()

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ $file${NC}"
    else
        echo -e "${RED}❌ $file (缺失)${NC}"
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -gt 0 ]; then
    echo
    echo -e "${RED}❌ 缺少必要文件，请确保以下文件存在:${NC}"
    for file in "${missing_files[@]}"; do
        echo "  - $file"
    done
    exit 1
fi

# 配置Git用户信息 (如果未配置)
echo
echo -e "${BLUE}🔧 检查Git配置...${NC}"
if [ -z "$(git config user.name)" ]; then
    read -p "Git用户名: " git_username
    git config user.name "$git_username"
fi

if [ -z "$(git config user.email)" ]; then
    read -p "Git邮箱: " git_email
    git config user.email "$git_email"
fi

echo -e "${GREEN}✅ Git配置完成${NC}"

# 添加文件到Git
echo
echo -e "${BLUE}📦 添加文件到Git...${NC}"
git add .

# 显示将要提交的文件
echo
echo -e "${BLUE}📋 将要提交的文件:${NC}"
git status --short

# 创建提交
echo
echo -e "${BLUE}💾 创建提交...${NC}"
commit_message="🎉 FTP断点续传下载工具 - 初始版本

✨ 功能特性:
- 🔄 断点续传下载
- 📁 目录浏览和搜索  
- 🔍 文件排序功能
- 📦 批量下载支持
- 🖥️ 跨平台GUI界面
- 🚀 GitHub Actions自动编译
- 🐳 Docker跨平台编译支持

🛠️ 技术栈:
- Python 3.6+
- Tkinter GUI
- PyInstaller编译
- GitHub Actions CI/CD

📱 支持平台:
- Windows (.exe)
- macOS (应用程序)  
- Linux (可执行文件)"

git commit -m "$commit_message"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 提交创建成功${NC}"
else
    echo -e "${RED}❌ 提交创建失败${NC}"
    exit 1
fi

# 添加远程仓库
echo
echo -e "${BLUE}🔗 配置远程仓库...${NC}"
remote_url="https://github.com/$github_username/$repo_name.git"

# 检查是否已有远程仓库
if git remote get-url origin &> /dev/null; then
    echo -e "${YELLOW}⚠️  检测到现有远程仓库，正在更新...${NC}"
    git remote set-url origin "$remote_url"
else
    git remote add origin "$remote_url"
fi

echo -e "${GREEN}✅ 远程仓库配置完成: $remote_url${NC}"

# 推送到GitHub
echo
echo -e "${BLUE}🚀 推送到GitHub...${NC}"
echo -e "${YELLOW}💡 如果这是第一次推送，可能需要输入GitHub用户名和密码/Token${NC}"
echo

git push -u origin main

if [ $? -eq 0 ]; then
    echo
    echo -e "${GREEN}🎉 上传成功！${NC}"
    echo
    echo -e "${BLUE}📋 接下来的步骤:${NC}"
    echo "1. 访问你的仓库: https://github.com/$github_username/$repo_name"
    echo "2. 点击 'Actions' 标签查看自动编译进度"
    echo "3. 编译完成后在 'Actions' 页面下载可执行文件"
    echo "4. 或者等待自动创建Release (如果推送了标签)"
    echo
    echo -e "${GREEN}🌟 项目已成功上传到GitHub！${NC}"
    
    # 询问是否打开浏览器
    read -p "是否在浏览器中打开仓库页面? (y/n): " open_browser
    if [[ $open_browser == "y" || $open_browser == "Y" ]]; then
        if command -v open &> /dev/null; then
            open "https://github.com/$github_username/$repo_name"
        elif command -v xdg-open &> /dev/null; then
            xdg-open "https://github.com/$github_username/$repo_name"
        else
            echo "请手动访问: https://github.com/$github_username/$repo_name"
        fi
    fi
else
    echo
    echo -e "${RED}❌ 推送失败${NC}"
    echo
    echo -e "${YELLOW}💡 可能的解决方案:${NC}"
    echo "1. 确保GitHub仓库已创建"
    echo "2. 检查网络连接"
    echo "3. 验证GitHub用户名和密码/Token"
    echo "4. 如果使用2FA，需要使用Personal Access Token"
    echo
    echo -e "${BLUE}📖 详细说明请查看: GitHub上传指南.md${NC}"
    exit 1
fi