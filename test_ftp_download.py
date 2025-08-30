#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FTP下载工具测试脚本
用于测试各种FTP服务器和下载场景
"""

import os
import sys
import time
import tempfile
from pathlib import Path
from ftp_downloader import FTPDownloader, parse_ftp_url

def test_public_ftp():
    """测试公共FTP服务器"""
    print("🧪 测试公共FTP服务器...")
    
    # 一些公共FTP测试服务器
    test_servers = [
        "ftp://ftp.gnu.org/gnu/",
        "ftp://test.rebex.net/",  # 用户名: demo, 密码: password
        "ftp://speedtest.tele2.net/",
    ]
    
    for server in test_servers:
        print(f"\n📡 测试服务器: {server}")
        try:
            host, port, username, password, path = parse_ftp_url(server)
            downloader = FTPDownloader(host, username, password, port)
            
            if downloader.connect():
                print("✓ 连接成功")
                files = downloader.list_files(path)
                if files:
                    print(f"✓ 找到 {len(files)} 个文件/目录")
                    # 显示前5个文件
                    for i, file_info in enumerate(files[:5]):
                        print(f"  {file_info}")
                    if len(files) > 5:
                        print(f"  ... 还有 {len(files) - 5} 个文件")
                else:
                    print("⚠ 目录为空或无法访问")
                downloader.disconnect()
            else:
                print("✗ 连接失败")
                
        except Exception as e:
            print(f"✗ 测试失败: {e}")

def test_download_small_file():
    """测试下载小文件"""
    print("\n🧪 测试下载小文件...")
    
    # 使用GNU FTP服务器的小文件进行测试
    test_url = "ftp://ftp.gnu.org/gnu/hello/hello-2.12.tar.gz"
    
    try:
        host, port, username, password, remote_path = parse_ftp_url(test_url)
        downloader = FTPDownloader(host, username, password, port)
        
        if downloader.connect():
            # 创建临时目录
            with tempfile.TemporaryDirectory() as temp_dir:
                local_path = Path(temp_dir) / "hello-2.12.tar.gz"
                
                print(f"📥 下载到: {local_path}")
                success = downloader.download_with_resume(remote_path, str(local_path))
                
                if success and local_path.exists():
                    file_size = local_path.stat().st_size
                    print(f"✓ 下载成功，文件大小: {file_size} 字节")
                    
                    # 测试断点续传
                    print("\n🔄 测试断点续传...")
                    # 删除文件的后半部分来模拟中断
                    with open(local_path, 'r+b') as f:
                        f.seek(file_size // 2)
                        f.truncate()
                    
                    truncated_size = local_path.stat().st_size
                    print(f"📊 模拟中断，剩余大小: {truncated_size} 字节")
                    
                    # 重新下载
                    success = downloader.download_with_resume(remote_path, str(local_path))
                    if success:
                        final_size = local_path.stat().st_size
                        print(f"✓ 断点续传成功，最终大小: {final_size} 字节")
                    else:
                        print("✗ 断点续传失败")
                else:
                    print("✗ 下载失败")
            
            downloader.disconnect()
        else:
            print("✗ 连接失败")
            
    except Exception as e:
        print(f"✗ 测试失败: {e}")

def test_url_parsing():
    """测试URL解析功能"""
    print("\n🧪 测试URL解析...")
    
    test_urls = [
        "ftp://ftp.example.com/file.zip",
        "ftp://user:pass@ftp.example.com:2121/path/file.zip",
        "ftp://anonymous@ftp.example.com/pub/file.zip",
        "ftp://ftp.example.com/",
    ]
    
    for url in test_urls:
        try:
            host, port, username, password, path = parse_ftp_url(url)
            print(f"✓ {url}")
            print(f"  主机: {host}:{port}")
            print(f"  用户: {username}")
            print(f"  密码: {'*' * len(password) if password else '(空)'}")
            print(f"  路径: {path}")
        except Exception as e:
            print(f"✗ {url} - {e}")

def main():
    """主测试函数"""
    print("🚀 FTP下载工具测试套件")
    print("=" * 50)
    
    # 测试URL解析
    test_url_parsing()
    
    # 测试公共FTP服务器连接
    test_public_ftp()
    
    # 测试小文件下载和断点续传
    test_download_small_file()
    
    print("\n✅ 测试完成")

if __name__ == '__main__':
    main()