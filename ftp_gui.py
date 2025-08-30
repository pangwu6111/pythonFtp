#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FTP断点续传下载工具 - GUI版本
功能完整的图形界面FTP客户端，支持断点续传、批量下载、目录同步等
"""

import os
import sys
import time
import json
import ftplib
import threading
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from tkinter.scrolledtext import ScrolledText

@dataclass
class FTPFileInfo:
    """FTP文件信息"""
    name: str
    size: int
    is_dir: bool
    modified: str
    permissions: str
    full_path: str

@dataclass
class DownloadTask:
    """下载任务"""
    remote_path: str
    local_path: str
    size: int
    downloaded: int = 0
    status: str = "等待中"  # 等待中, 下载中, 已完成, 失败, 暂停
    speed: float = 0.0
    progress: float = 0.0
    error_msg: str = ""

class FTPConnection:
    """FTP连接管理器"""
    
    def __init__(self):
        self.ftp = None
        self.host = ""
        self.port = 21
        self.username = ""
        self.password = ""
        self.current_path = "/"
        self.connected = False
        
    def connect(self, host, port, username, password, timeout=30):
        """连接FTP服务器"""
        try:
            self.ftp = ftplib.FTP()
            self.ftp.connect(host, port, timeout)
            self.ftp.login(username, password)
            self.ftp.set_pasv(True)
            
            self.host = host
            self.port = port
            self.username = username
            self.password = password
            self.current_path = self.ftp.pwd()
            self.connected = True
            return True
        except Exception as e:
            self.connected = False
            raise e
    
    def disconnect(self):
        """断开连接"""
        if self.ftp:
            try:
                self.ftp.quit()
            except:
                pass
            self.ftp = None
        self.connected = False
    
    def list_directory(self, path=None) -> List[FTPFileInfo]:
        """列出目录内容"""
        if not self.connected:
            return []
        
        if path:
            original_path = self.ftp.pwd()
            try:
                self.ftp.cwd(path)
            except:
                return []
        
        files = []
        try:
            # 获取详细列表
            lines = []
            self.ftp.retrlines('LIST', lines.append)
            
            for line in lines:
                file_info = self._parse_list_line(line)
                if file_info:
                    files.append(file_info)
                    
        except Exception as e:
            print(f"列出目录失败: {e}")
        
        if path:
            try:
                self.ftp.cwd(original_path)
            except:
                pass
        
        return files
    
    def _parse_list_line(self, line: str) -> Optional[FTPFileInfo]:
        """解析LIST命令返回的行"""
        try:
            parts = line.split()
            if len(parts) < 9:
                return None
            
            permissions = parts[0]
            is_dir = permissions.startswith('d')
            
            # 尝试获取文件大小
            try:
                size = int(parts[4]) if not is_dir else 0
            except:
                size = 0
            
            # 文件名可能包含空格
            name = ' '.join(parts[8:])
            
            # 修改时间
            modified = f"{parts[5]} {parts[6]} {parts[7]}"
            
            # 构建完整路径
            current_dir = self.ftp.pwd()
            if current_dir.endswith('/'):
                full_path = current_dir + name
            else:
                full_path = current_dir + '/' + name
            
            return FTPFileInfo(
                name=name,
                size=size,
                is_dir=is_dir,
                modified=modified,
                permissions=permissions,
                full_path=full_path
            )
        except Exception as e:
            print(f"解析文件信息失败: {line} - {e}")
            return None
    
    def change_directory(self, path: str) -> bool:
        """切换目录"""
        if not self.connected:
            return False
        
        try:
            self.ftp.cwd(path)
            self.current_path = self.ftp.pwd()
            return True
        except:
            return False
    
    def get_file_size(self, path: str) -> Optional[int]:
        """获取文件大小"""
        if not self.connected:
            return None
        
        try:
            return self.ftp.size(path)
        except:
            return None

class DownloadManager:
    """下载管理器"""
    
    def __init__(self, ftp_conn: FTPConnection):
        self.ftp_conn = ftp_conn
        self.tasks: List[DownloadTask] = []
        self.active_downloads = 0
        self.max_concurrent = 3
        self.chunk_size = 8192
        self.running = False
        
    def add_task(self, remote_path: str, local_path: str, size: int = 0):
        """添加下载任务"""
        if size == 0:
            size = self.ftp_conn.get_file_size(remote_path) or 0
        
        task = DownloadTask(
            remote_path=remote_path,
            local_path=local_path,
            size=size
        )
        self.tasks.append(task)
        return task
    
    def start_downloads(self):
        """开始下载"""
        self.running = True
        threading.Thread(target=self._download_worker, daemon=True).start()
    
    def stop_downloads(self):
        """停止下载"""
        self.running = False
    
    def _download_worker(self):
        """下载工作线程"""
        while self.running:
            # 查找等待中的任务
            pending_tasks = [t for t in self.tasks if t.status == "等待中"]
            
            if not pending_tasks:
                time.sleep(1)
                continue
            
            if self.active_downloads >= self.max_concurrent:
                time.sleep(1)
                continue
            
            task = pending_tasks[0]
            self.active_downloads += 1
            
            # 在新线程中下载
            threading.Thread(
                target=self._download_file,
                args=(task,),
                daemon=True
            ).start()
    
    def _download_file(self, task: DownloadTask):
        """下载单个文件"""
        try:
            task.status = "下载中"
            
            # 创建本地目录
            local_path = Path(task.local_path)
            local_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 检查本地文件
            local_size = 0
            if local_path.exists():
                local_size = local_path.stat().st_size
                if local_size == task.size:
                    task.status = "已完成"
                    task.progress = 100.0
                    return
                elif local_size > task.size:
                    local_path.unlink()
                    local_size = 0
            
            task.downloaded = local_size
            
            # 创建新的FTP连接用于下载
            ftp = ftplib.FTP()
            ftp.connect(self.ftp_conn.host, self.ftp_conn.port, 30)
            ftp.login(self.ftp_conn.username, self.ftp_conn.password)
            ftp.set_pasv(True)
            
            # 设置断点续传
            if local_size > 0:
                ftp.sendcmd(f'REST {local_size}')
            
            # 开始下载
            mode = 'ab' if local_size > 0 else 'wb'
            start_time = time.time()
            
            with open(local_path, mode) as f:
                def callback(data):
                    f.write(data)
                    task.downloaded += len(data)
                    
                    # 计算进度和速度
                    if task.size > 0:
                        task.progress = (task.downloaded / task.size) * 100
                    
                    elapsed = time.time() - start_time
                    if elapsed > 0:
                        task.speed = (task.downloaded - local_size) / elapsed
                
                ftp.retrbinary(f'RETR {task.remote_path}', callback, self.chunk_size)
            
            ftp.quit()
            
            if task.downloaded == task.size:
                task.status = "已完成"
                task.progress = 100.0
            else:
                task.status = "失败"
                task.error_msg = "下载不完整"
                
        except Exception as e:
            task.status = "失败"
            task.error_msg = str(e)
        finally:
            self.active_downloads -= 1

class FTPClientGUI:
    """FTP客户端GUI主界面"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("FTP断点续传下载工具 v2.0")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # 设置图标和样式
        self.setup_styles()
        
        # 初始化组件
        self.ftp_conn = FTPConnection()
        self.download_manager = DownloadManager(self.ftp_conn)
        self.config_file = "ftp_config.json"
        
        # 创建界面
        self.create_widgets()
        self.load_config()
        
        # 启动下载管理器
        self.download_manager.start_downloads()
        
        # 定时更新界面
        self.update_ui()
    
    def setup_styles(self):
        """设置界面样式"""
        style = ttk.Style()
        
        # 配置样式
        style.configure('Title.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Status.TLabel', font=('Arial', 9))
        style.configure('Tree.Treeview', rowheight=25)
    
    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建连接面板
        self.create_connection_panel(main_frame)
        
        # 创建主要内容区域
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # 创建左右分割面板
        paned = ttk.PanedWindow(content_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # 左侧：远程文件浏览
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)
        self.create_remote_browser(left_frame)
        
        # 右侧：下载管理
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=1)
        self.create_download_panel(right_frame)
        
        # 底部状态栏
        self.create_status_bar(main_frame)
    
    def create_connection_panel(self, parent):
        """创建连接面板"""
        conn_frame = ttk.LabelFrame(parent, text="FTP连接", padding=10)
        conn_frame.pack(fill=tk.X, pady=(0, 5))
        
        # 连接参数
        params_frame = ttk.Frame(conn_frame)
        params_frame.pack(fill=tk.X)
        
        # 服务器地址
        ttk.Label(params_frame, text="服务器:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.host_var = tk.StringVar()
        host_entry = ttk.Entry(params_frame, textvariable=self.host_var, width=20)
        host_entry.grid(row=0, column=1, padx=(0, 10))
        
        # 端口
        ttk.Label(params_frame, text="端口:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.port_var = tk.StringVar(value="21")
        port_entry = ttk.Entry(params_frame, textvariable=self.port_var, width=8)
        port_entry.grid(row=0, column=3, padx=(0, 10))
        
        # 用户名
        ttk.Label(params_frame, text="用户名:").grid(row=0, column=4, sticky=tk.W, padx=(0, 5))
        self.username_var = tk.StringVar()
        username_entry = ttk.Entry(params_frame, textvariable=self.username_var, width=15)
        username_entry.grid(row=0, column=5, padx=(0, 10))
        
        # 密码
        ttk.Label(params_frame, text="密码:").grid(row=0, column=6, sticky=tk.W, padx=(0, 5))
        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(params_frame, textvariable=self.password_var, show="*", width=15)
        password_entry.grid(row=0, column=7, padx=(0, 10))
        
        # 连接按钮
        self.connect_btn = ttk.Button(params_frame, text="连接", command=self.connect_ftp)
        self.connect_btn.grid(row=0, column=8, padx=(0, 5))
        
        self.disconnect_btn = ttk.Button(params_frame, text="断开", command=self.disconnect_ftp, state=tk.DISABLED)
        self.disconnect_btn.grid(row=0, column=9)
        
        # 快速连接
        quick_frame = ttk.Frame(conn_frame)
        quick_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(quick_frame, text="快速连接:").pack(side=tk.LEFT)
        
        quick_servers = [
            ("GNU FTP", "ftp.gnu.org", 21, "anonymous", ""),
            ("测试服务器", "test.rebex.net", 21, "demo", "password"),
        ]
        
        for name, host, port, user, pwd in quick_servers:
            btn = ttk.Button(quick_frame, text=name, 
                           command=lambda h=host, p=port, u=user, pw=pwd: self.quick_connect(h, p, u, pw))
            btn.pack(side=tk.LEFT, padx=(5, 0))
    
    def create_remote_browser(self, parent):
        """创建远程文件浏览器"""
        browser_frame = ttk.LabelFrame(parent, text="远程文件浏览", padding=5)
        browser_frame.pack(fill=tk.BOTH, expand=True)
        
        # 路径导航
        nav_frame = ttk.Frame(browser_frame)
        nav_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(nav_frame, text="当前路径:").pack(side=tk.LEFT)
        self.path_var = tk.StringVar(value="/")
        path_entry = ttk.Entry(nav_frame, textvariable=self.path_var, state="readonly")
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        ttk.Button(nav_frame, text="上级", command=self.go_parent).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(nav_frame, text="刷新", command=self.refresh_remote).pack(side=tk.RIGHT, padx=(5, 0))
        
        # 文件列表
        list_frame = ttk.Frame(browser_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建Treeview
        columns = ("名称", "大小", "类型", "修改时间", "权限")
        self.remote_tree = ttk.Treeview(list_frame, columns=columns, show="tree headings", style='Tree.Treeview')
        
        # 设置列
        self.remote_tree.heading("#0", text="", anchor=tk.W)
        self.remote_tree.column("#0", width=30, minwidth=30)
        
        for col in columns:
            self.remote_tree.heading(col, text=col, anchor=tk.W)
        
        self.remote_tree.column("名称", width=200, minwidth=100)
        self.remote_tree.column("大小", width=100, minwidth=80)
        self.remote_tree.column("类型", width=80, minwidth=60)
        self.remote_tree.column("修改时间", width=120, minwidth=100)
        self.remote_tree.column("权限", width=100, minwidth=80)
        
        # 滚动条
        remote_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.remote_tree.yview)
        self.remote_tree.configure(yscrollcommand=remote_scroll.set)
        
        self.remote_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        remote_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定事件
        self.remote_tree.bind("<Double-1>", self.on_remote_double_click)
        self.remote_tree.bind("<Button-3>", self.show_remote_context_menu)
        
        # 操作按钮
        btn_frame = ttk.Frame(browser_frame)
        btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(btn_frame, text="下载选中", command=self.download_selected).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="下载目录", command=self.download_directory).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="新建目录", command=self.create_directory).pack(side=tk.LEFT, padx=(0, 5))
    
    def create_download_panel(self, parent):
        """创建下载管理面板"""
        download_frame = ttk.LabelFrame(parent, text="下载管理", padding=5)
        download_frame.pack(fill=tk.BOTH, expand=True)
        
        # 下载设置
        settings_frame = ttk.Frame(download_frame)
        settings_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(settings_frame, text="保存到:").pack(side=tk.LEFT)
        self.download_path_var = tk.StringVar(value=str(Path.home() / "Downloads"))
        path_entry = ttk.Entry(settings_frame, textvariable=self.download_path_var)
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        ttk.Button(settings_frame, text="浏览", command=self.browse_download_path).pack(side=tk.RIGHT, padx=(5, 0))
        
        # 下载任务列表
        task_frame = ttk.Frame(download_frame)
        task_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # 创建任务列表
        task_columns = ("文件名", "大小", "进度", "速度", "状态")
        self.task_tree = ttk.Treeview(task_frame, columns=task_columns, show="headings", style='Tree.Treeview')
        
        for col in task_columns:
            self.task_tree.heading(col, text=col, anchor=tk.W)
        
        self.task_tree.column("文件名", width=200, minwidth=150)
        self.task_tree.column("大小", width=80, minwidth=60)
        self.task_tree.column("进度", width=100, minwidth=80)
        self.task_tree.column("速度", width=100, minwidth=80)
        self.task_tree.column("状态", width=80, minwidth=60)
        
        # 滚动条
        task_scroll = ttk.Scrollbar(task_frame, orient=tk.VERTICAL, command=self.task_tree.yview)
        self.task_tree.configure(yscrollcommand=task_scroll.set)
        
        self.task_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        task_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 下载控制按钮
        control_frame = ttk.Frame(download_frame)
        control_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(control_frame, text="开始全部", command=self.start_all_downloads).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="暂停全部", command=self.pause_all_downloads).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="清除已完成", command=self.clear_completed).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="清除全部", command=self.clear_all_tasks).pack(side=tk.LEFT, padx=(0, 5))
        
        # 下载统计
        stats_frame = ttk.Frame(download_frame)
        stats_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.stats_var = tk.StringVar(value="任务: 0 | 进行中: 0 | 已完成: 0 | 失败: 0")
        ttk.Label(stats_frame, textvariable=self.stats_var, style='Status.TLabel').pack(side=tk.LEFT)
    
    def create_status_bar(self, parent):
        """创建状态栏"""
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.status_var = tk.StringVar(value="就绪")
        ttk.Label(status_frame, textvariable=self.status_var, style='Status.TLabel').pack(side=tk.LEFT)
        
        # 连接状态指示器
        self.conn_status_var = tk.StringVar(value="未连接")
        ttk.Label(status_frame, textvariable=self.conn_status_var, style='Status.TLabel').pack(side=tk.RIGHT)
    
    def quick_connect(self, host, port, username, password):
        """快速连接"""
        self.host_var.set(host)
        self.port_var.set(str(port))
        self.username_var.set(username)
        self.password_var.set(password)
        self.connect_ftp()
    
    def connect_ftp(self):
        """连接FTP服务器"""
        host = self.host_var.get().strip()
        if not host:
            messagebox.showerror("错误", "请输入服务器地址")
            return
        
        try:
            port = int(self.port_var.get() or "21")
        except ValueError:
            messagebox.showerror("错误", "端口必须是数字")
            return
        
        username = self.username_var.get() or "anonymous"
        password = self.password_var.get()
        
        self.status_var.set("正在连接...")
        self.connect_btn.config(state=tk.DISABLED)
        
        def connect_thread():
            try:
                self.ftp_conn.connect(host, port, username, password)
                self.root.after(0, self.on_connect_success)
            except Exception as e:
                self.root.after(0, lambda: self.on_connect_error(str(e)))
        
        threading.Thread(target=connect_thread, daemon=True).start()
    
    def on_connect_success(self):
        """连接成功回调"""
        self.status_var.set("连接成功")
        self.conn_status_var.set(f"已连接到 {self.ftp_conn.host}")
        self.connect_btn.config(state=tk.DISABLED)
        self.disconnect_btn.config(state=tk.NORMAL)
        
        self.path_var.set(self.ftp_conn.current_path)
        self.refresh_remote()
        self.save_config()
    
    def on_connect_error(self, error_msg):
        """连接失败回调"""
        self.status_var.set("连接失败")
        self.connect_btn.config(state=tk.NORMAL)
        messagebox.showerror("连接失败", f"无法连接到FTP服务器:\n{error_msg}")
    
    def disconnect_ftp(self):
        """断开FTP连接"""
        self.ftp_conn.disconnect()
        self.status_var.set("已断开连接")
        self.conn_status_var.set("未连接")
        self.connect_btn.config(state=tk.NORMAL)
        self.disconnect_btn.config(state=tk.DISABLED)
        
        # 清空远程文件列表
        for item in self.remote_tree.get_children():
            self.remote_tree.delete(item)
    
    def refresh_remote(self):
        """刷新远程文件列表"""
        if not self.ftp_conn.connected:
            return
        
        self.status_var.set("正在获取文件列表...")
        
        def refresh_thread():
            try:
                files = self.ftp_conn.list_directory()
                self.root.after(0, lambda: self.update_remote_list(files))
            except Exception as e:
                self.root.after(0, lambda: self.on_refresh_error(str(e)))
        
        threading.Thread(target=refresh_thread, daemon=True).start()
    
    def update_remote_list(self, files: List[FTPFileInfo]):
        """更新远程文件列表"""
        # 清空现有列表
        for item in self.remote_tree.get_children():
            self.remote_tree.delete(item)
        
        # 添加文件
        for file_info in files:
            icon = "📁" if file_info.is_dir else "📄"
            size_str = self.format_size(file_info.size) if not file_info.is_dir else ""
            type_str = "目录" if file_info.is_dir else "文件"
            
            self.remote_tree.insert("", tk.END, 
                                  text=icon,
                                  values=(file_info.name, size_str, type_str, 
                                         file_info.modified, file_info.permissions),
                                  tags=("directory" if file_info.is_dir else "file",))
        
        self.path_var.set(self.ftp_conn.current_path)
        self.status_var.set(f"找到 {len(files)} 个项目")
    
    def on_refresh_error(self, error_msg):
        """刷新失败回调"""
        self.status_var.set("获取文件列表失败")
        messagebox.showerror("错误", f"获取文件列表失败:\n{error_msg}")
    
    def on_remote_double_click(self, event):
        """远程文件双击事件"""
        selection = self.remote_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.remote_tree.item(item, "values")
        if not values:
            return
        
        filename = values[0]
        is_dir = values[2] == "目录"
        
        if is_dir:
            # 进入目录
            new_path = self.ftp_conn.current_path
            if new_path.endswith('/'):
                new_path += filename
            else:
                new_path += '/' + filename
            
            if self.ftp_conn.change_directory(new_path):
                self.refresh_remote()
            else:
                messagebox.showerror("错误", f"无法进入目录: {filename}")
        else:
            # 下载文件
            self.download_file(filename)
    
    def go_parent(self):
        """返回上级目录"""
        if not self.ftp_conn.connected:
            return
        
        current = self.ftp_conn.current_path
        if current == '/':
            return
        
        parent = str(Path(current).parent)
        if parent == '.':
            parent = '/'
        
        if self.ftp_conn.change_directory(parent):
            self.refresh_remote()
    
    def download_selected(self):
        """下载选中的文件"""
        selection = self.remote_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择要下载的文件")
            return
        
        for item in selection:
            values = self.remote_tree.item(item, "values")
            if values and values[2] == "文件":
                self.download_file(values[0])
    
    def download_file(self, filename):
        """下载单个文件"""
        remote_path = self.ftp_conn.current_path
        if remote_path.endswith('/'):
            remote_path += filename
        else:
            remote_path += '/' + filename
        
        local_path = Path(self.download_path_var.get()) / filename
        
        # 获取文件大小
        size = self.ftp_conn.get_file_size(remote_path) or 0
        
        # 添加下载任务
        task = self.download_manager.add_task(remote_path, str(local_path), size)
        self.status_var.set(f"已添加下载任务: {filename}")
    
    def download_directory(self):
        """下载整个目录"""
        if not self.ftp_conn.connected:
            return
        
        result = messagebox.askyesno("确认", "是否下载当前目录的所有文件？")
        if not result:
            return
        
        # 获取所有文件
        files = []
        for item in self.remote_tree.get_children():
            values = self.remote_tree.item(item, "values")
            if values and values[2] == "文件":
                files.append(values[0])
        
        if not files:
            messagebox.showinfo("提示", "当前目录没有文件")
            return
        
        # 添加所有文件到下载队列
        for filename in files:
            self.download_file(filename)
        
        self.status_var.set(f"已添加 {len(files)} 个下载任务")
    
    def browse_download_path(self):
        """浏览下载路径"""
        path = filedialog.askdirectory(initialdir=self.download_path_var.get())
        if path:
            self.download_path_var.set(path)
    
    def start_all_downloads(self):
        """开始所有下载"""
        for task in self.download_manager.tasks:
            if task.status in ["等待中", "失败"]:
                task.status = "等待中"
        self.status_var.set("已开始所有下载任务")
    
    def pause_all_downloads(self):
        """暂停所有下载"""
        for task in self.download_manager.tasks:
            if task.status == "下载中":
                task.status = "暂停"
        self.status_var.set("已暂停所有下载任务")
    
    def clear_completed(self):
        """清除已完成的任务"""
        self.download_manager.tasks = [t for t in self.download_manager.tasks if t.status != "已完成"]
        self.status_var.set("已清除完成的任务")
    
    def clear_all_tasks(self):
        """清除所有任务"""
        result = messagebox.askyesno("确认", "是否清除所有下载任务？")
        if result:
            self.download_manager.tasks.clear()
            self.status_var.set("已清除所有任务")
    
    def create_directory(self):
        """创建新目录"""
        if not self.ftp_conn.connected:
            return
        
        dirname = simpledialog.askstring("新建目录", "请输入目录名称:")
        if not dirname:
            return
        
        try:
            self.ftp_conn.ftp.mkd(dirname)
            self.refresh_remote()
            self.status_var.set(f"已创建目录: {dirname}")
        except Exception as e:
            messagebox.showerror("错误", f"创建目录失败:\n{str(e)}")
    
    def show_remote_context_menu(self, event):
        """显示右键菜单"""
        # TODO: 实现右键菜单
        pass
    
    def update_ui(self):
        """定时更新界面"""
        # 更新下载任务列表
        self.update_task_list()
        
        # 更新统计信息
        self.update_stats()
        
        # 每秒更新一次
        self.root.after(1000, self.update_ui)
    
    def update_task_list(self):
        """更新下载任务列表"""
        # 清空现有列表
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
        
        # 添加任务
        for task in self.download_manager.tasks:
            filename = Path(task.remote_path).name
            size_str = self.format_size(task.size)
            progress_str = f"{task.progress:.1f}%"
            speed_str = self.format_size(task.speed) + "/s" if task.speed > 0 else ""
            
            self.task_tree.insert("", tk.END, 
                                values=(filename, size_str, progress_str, speed_str, task.status))
    
    def update_stats(self):
        """更新统计信息"""
        total = len(self.download_manager.tasks)
        downloading = len([t for t in self.download_manager.tasks if t.status == "下载中"])
        completed = len([t for t in self.download_manager.tasks if t.status == "已完成"])
        failed = len([t for t in self.download_manager.tasks if t.status == "失败"])
        
        self.stats_var.set(f"任务: {total} | 进行中: {downloading} | 已完成: {completed} | 失败: {failed}")
    
    def format_size(self, size):
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.1f}{unit}"
            size /= 1024
        return f"{size:.1f}PB"
    
    def load_config(self):
        """加载配置"""
        try:
            if Path(self.config_file).exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                self.host_var.set(config.get('host', ''))
                self.port_var.set(config.get('port', '21'))
                self.username_var.set(config.get('username', ''))
                self.download_path_var.set(config.get('download_path', str(Path.home() / "Downloads")))
        except Exception as e:
            print(f"加载配置失败: {e}")
    
    def save_config(self):
        """保存配置"""
        try:
            config = {
                'host': self.host_var.get(),
                'port': self.port_var.get(),
                'username': self.username_var.get(),
                'download_path': self.download_path_var.get()
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    def run(self):
        """运行GUI"""
        try:
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.root.mainloop()
        except KeyboardInterrupt:
            pass
    
    def on_closing(self):
        """关闭程序"""
        self.download_manager.stop_downloads()
        self.ftp_conn.disconnect()
        self.save_config()
        self.root.destroy()

def main():
    """主函数"""
    try:
        app = FTPClientGUI()
        app.run()
    except Exception as e:
        messagebox.showerror("错误", f"程序启动失败:\n{str(e)}")

if __name__ == '__main__':
    main()