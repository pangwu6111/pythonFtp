#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FTP工具编译脚本
使用PyInstaller将Python脚本编译为可执行文件
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_python():
    """检查Python环境"""
    print("✓ 检查Python环境...")
    print(f"Python版本: {sys.version}")
    return True

def install_pyinstaller():
    """安装PyInstaller"""
    try:
        import PyInstaller
        print("✓ PyInstaller已安装")
        return True
    except ImportError:
        print("⚠️  正在安装PyInstaller...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✓ PyInstaller安装成功")
            return True
        except subprocess.CalledProcessError:
            print("✗ PyInstaller安装失败")
            return False

def build_executable():
    """编译可执行文件"""
    script_dir = Path(__file__).parent
    source_file = script_dir / "ftp_gui_complete.py"
    
    if not source_file.exists():
        print(f"✗ 源文件不存在: {source_file}")
        return False
    
    print("🚀 开始编译...")
    
    # PyInstaller命令参数
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",                    # 打包成单个文件
        "--windowed",                   # 无控制台窗口
        "--name", "FTP下载工具",         # 可执行文件名称
        "--distpath", str(script_dir / "dist"),  # 输出目录
        "--workpath", str(script_dir / "build"), # 工作目录
        "--specpath", str(script_dir),           # spec文件目录
        str(source_file)
    ]
    
    try:
        # 执行编译
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("✅ 编译成功！")
            
            # 检查输出文件
            exe_file = script_dir / "dist" / "FTP下载工具.exe"
            if exe_file.exists():
                size = exe_file.stat().st_size
                print(f"📁 输出文件: {exe_file}")
                print(f"📊 文件大小: {size:,} 字节 ({size/1024/1024:.1f} MB)")
                
                # 询问是否运行
                choice = input("\n是否立即运行编译好的程序? (y/n): ").lower()
                if choice == 'y':
                    print("正在启动程序...")
                    subprocess.Popen([str(exe_file)])
                
                return True
            else:
                print("✗ 可执行文件未生成")
                return False
        else:
            print("✗ 编译失败")
            print("错误输出:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"✗ 编译过程出错: {e}")
        return False

def clean_build_files():
    """清理编译临时文件"""
    script_dir = Path(__file__).parent
    
    # 清理目录
    for dir_name in ["build", "__pycache__"]:
        dir_path = script_dir / dir_name
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"🧹 已清理: {dir_path}")
    
    # 清理spec文件
    spec_files = list(script_dir.glob("*.spec"))
    for spec_file in spec_files:
        spec_file.unlink()
        print(f"🧹 已清理: {spec_file}")

def main():
    """主函数"""
    print("=" * 50)
    print("    FTP工具 - 编译为可执行文件")
    print("    使用PyInstaller打包Python程序")
    print("=" * 50)
    print()
    
    # 检查环境
    if not check_python():
        return False
    
    # 安装PyInstaller
    if not install_pyinstaller():
        return False
    
    # 编译
    success = build_executable()
    
    # 清理临时文件
    print("\n🧹 清理临时文件...")
    clean_build_files()
    
    if success:
        print("\n🎉 编译完成！")
        print("\n💡 使用说明:")
        print("  • 可执行文件位于 dist 文件夹中")
        print("  • 可以复制到任何Windows电脑上运行")
        print("  • 不需要安装Python环境")
        print("  • 首次运行可能需要几秒钟启动时间")
    else:
        print("\n❌ 编译失败，请检查错误信息")
    
    input("\n按回车键退出...")
    return success

if __name__ == "__main__":
    main()