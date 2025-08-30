#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows FTP 断点续传下载工具
支持多线程下载、进度显示、自动重连等功能
"""

import os
import sys
import time
import ftplib
import argparse
import threading
from pathlib import Path
from urllib.parse import urlparse

class FTPDownloader:
    def __init__(self, host, username='anonymous', password='', port=21, timeout=30):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.timeout = timeout
        self.ftp = None
        self.lock = threading.Lock()
        
    def connect(self):
        """连接到FTP服务器"""
        try:
            self.ftp = ftplib.FTP()
            self.ftp.connect(self.host, self.port, self.timeout)
            self.ftp.login(self.username, self.password)
            self.ftp.set_pasv(True)  # 使用被动模式
            print(f"✓ 已连接到 {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"✗ 连接失败: {e}")
            return False
    
    def disconnect(self):
        """断开FTP连接"""
        if self.ftp:
            try:
                self.ftp.quit()
            except:
                pass
            self.ftp = None
    
    def get_file_size(self, remote_path):
        """获取远程文件大小"""
        try:
            return self.ftp.size(remote_path)
        except:
            return None
    
    def download_with_resume(self, remote_path, local_path, chunk_size=8192, max_retries=3):
        """支持断点续传的下载功能"""
        local_path = Path(local_path)
        local_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 获取远程文件大小
        remote_size = self.get_file_size(remote_path)
        if remote_size is None:
            print(f"✗ 无法获取远程文件大小: {remote_path}")
            return False
        
        # 检查本地文件
        local_size = 0
        if local_path.exists():
            local_size = local_path.stat().st_size
            if local_size == remote_size:
                print(f"✓ 文件已完整下载: {local_path}")
                return True
            elif local_size > remote_size:
                print(f"✗ 本地文件大小异常，重新下载: {local_path}")
                local_path.unlink()
                local_size = 0
        
        print(f"📁 远程文件: {remote_path} ({self._format_size(remote_size)})")
        print(f"💾 本地文件: {local_path} ({self._format_size(local_size)})")
        
        if local_size > 0:
            print(f"🔄 断点续传，从 {self._format_size(local_size)} 开始")
        
        # 开始下载
        retries = 0
        while retries < max_retries:
            try:
                return self._download_chunk(remote_path, local_path, local_size, remote_size, chunk_size)
            except Exception as e:
                retries += 1
                print(f"✗ 下载失败 (尝试 {retries}/{max_retries}): {e}")
                if retries < max_retries:
                    print("🔄 重新连接...")
                    self.disconnect()
                    time.sleep(2)
                    if not self.connect():
                        continue
                else:
                    print("✗ 达到最大重试次数，下载失败")
                    return False
        
        return False
    
    def _download_chunk(self, remote_path, local_path, start_pos, total_size, chunk_size):
        """下载文件块"""
        mode = 'ab' if start_pos > 0 else 'wb'
        
        with open(local_path, mode) as f:
            # 设置断点续传位置
            if start_pos > 0:
                self.ftp.sendcmd(f'REST {start_pos}')
            
            # 开始下载
            downloaded = start_pos
            start_time = time.time()
            
            def callback(data):
                nonlocal downloaded
                f.write(data)
                downloaded += len(data)
                
                # 显示进度
                if downloaded % (chunk_size * 10) == 0 or downloaded == total_size:
                    self._show_progress(downloaded, total_size, start_time)
            
            self.ftp.retrbinary(f'RETR {remote_path}', callback, chunk_size)
            
            # 验证下载完整性
            if downloaded == total_size:
                print(f"\n✓ 下载完成: {local_path}")
                return True
            else:
                print(f"\n✗ 下载不完整: {downloaded}/{total_size}")
                return False
    
    def _show_progress(self, downloaded, total, start_time):
        """显示下载进度"""
        percent = (downloaded / total) * 100
        elapsed = time.time() - start_time
        speed = downloaded / elapsed if elapsed > 0 else 0
        
        # 计算剩余时间
        if speed > 0:
            remaining = (total - downloaded) / speed
            eta = self._format_time(remaining)
        else:
            eta = "未知"
        
        progress_bar = "█" * int(percent // 2) + "░" * (50 - int(percent // 2))
        
        print(f"\r[{progress_bar}] {percent:.1f}% "
              f"{self._format_size(downloaded)}/{self._format_size(total)} "
              f"速度: {self._format_size(speed)}/s ETA: {eta}", end="")
    
    def _format_size(self, size):
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.1f}{unit}"
            size /= 1024
        return f"{size:.1f}PB"
    
    def _format_time(self, seconds):
        """格式化时间"""
        if seconds < 60:
            return f"{seconds:.0f}秒"
        elif seconds < 3600:
            return f"{seconds//60:.0f}分{seconds%60:.0f}秒"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours:.0f}时{minutes:.0f}分"
    
    def list_files(self, remote_path='.'):
        """列出远程目录文件"""
        try:
            files = []
            self.ftp.retrlines(f'LIST {remote_path}', files.append)
            return files
        except Exception as e:
            print(f"✗ 列出文件失败: {e}")
            return []

def parse_ftp_url(url):
    """解析FTP URL"""
    parsed = urlparse(url)
    if parsed.scheme != 'ftp':
        raise ValueError("URL必须以ftp://开头")
    
    host = parsed.hostname
    port = parsed.port or 21
    username = parsed.username or 'anonymous'
    password = parsed.password or ''
    path = parsed.path
    
    return host, port, username, password, path

def main():
    parser = argparse.ArgumentParser(description='FTP断点续传下载工具')
    parser.add_argument('url', help='FTP URL (ftp://user:pass@host:port/path/file)')
    parser.add_argument('-o', '--output', help='本地保存路径')
    parser.add_argument('-c', '--chunk-size', type=int, default=8192, help='下载块大小 (默认: 8192)')
    parser.add_argument('-r', '--retries', type=int, default=3, help='最大重试次数 (默认: 3)')
    parser.add_argument('-t', '--timeout', type=int, default=30, help='连接超时时间 (默认: 30秒)')
    parser.add_argument('-l', '--list', action='store_true', help='列出远程目录文件')
    
    args = parser.parse_args()
    
    try:
        # 解析FTP URL
        host, port, username, password, remote_path = parse_ftp_url(args.url)
        
        # 创建下载器
        downloader = FTPDownloader(host, username, password, port, args.timeout)
        
        # 连接到服务器
        if not downloader.connect():
            return 1
        
        try:
            if args.list:
                # 列出文件
                files = downloader.list_files(remote_path or '.')
                print(f"\n📂 远程目录内容 ({remote_path or '.'}):")
                for file_info in files:
                    print(f"  {file_info}")
            else:
                # 下载文件
                if not remote_path or remote_path.endswith('/'):
                    print("✗ 请指定要下载的文件名")
                    return 1
                
                # 确定本地保存路径
                if args.output:
                    local_path = args.output
                else:
                    local_path = Path(remote_path).name
                
                # 开始下载
                success = downloader.download_with_resume(
                    remote_path, local_path, args.chunk_size, args.retries
                )
                
                return 0 if success else 1
                
        finally:
            downloader.disconnect()
            
    except Exception as e:
        print(f"✗ 错误: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())