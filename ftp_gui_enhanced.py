#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FTP断点续传下载工具 - 增强版GUI
专门优化了FTP连接兼容性，支持各种FTP服务器配置
"""

import os
import sys
import time
import ftplib
import threading
import socket
from pathlib import Path
from datetime import datetime

try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
except ImportError:
    print("错误: 未找到tkinter模块")
    sys.exit(1)

class DownloadTask:
    def __init__(self, remote_path, local_path, size=0):
        self.remote_path = remote_path
        self.local_path = local_path
        self.size = size
        self.downloaded = 0
        self.progress = 0.0
        self.speed = 0.0
        self.status = "等待中"
        self.start_time = None
        self.error_msg = ""

class EnhancedFTPGUI:
    """增强版FTP GUI客户端 - 优化连接兼容性"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("FTP下载工具 - 增强版")
        self.root.geometry("1000x700")
        
        # FTP连接
        self.ftp = None
        self.connected = False
        self.current_path = "/"
        
        # 连接配置
        self.passive_mode = True
        self.encoding = 'utf-8'
        self.timeout = 30
        
        # 下载任务
        self.download_tasks = []
        self.downloading = False
        
        # 界面变量
        self.host_var = None
        self.port_var = None
        self.username_var = None
        self.password_var = None
        self.path_var = None
        self.save_path_var = None
        self.status_var = None
        self.passive_var = None
        self.timeout_var = None
        self.search_var = None
        self.sort_var = None
        self.sort_desc_var = None
        self.show_hidden_var = None
        
        # 文件数据
        self.file_data = []  # 存储原始文件数据
        self.filtered_data = []  # 存储过滤后的数据
        
        # 界面组件
        self.connect_btn = None
        self.file_tree = None
        self.download_tree = None
        
        # 创建界面
        self.create_widgets()
        
        # 定时更新
        self.update_downloads()
    
    def create_widgets(self):
        """创建界面组件"""
        # 连接区域
        conn_frame = ttk.LabelFrame(self.root, text="FTP连接配置", padding=10)
        conn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 第一行：基本连接参数
        basic_frame = ttk.Frame(conn_frame)
        basic_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(basic_frame, text="服务器:").grid(row=0, column=0, padx=5, sticky=tk.W)
        self.host_var = tk.StringVar()
        ttk.Entry(basic_frame, textvariable=self.host_var, width=20).grid(row=0, column=1, padx=5)
        
        ttk.Label(basic_frame, text="端口:").grid(row=0, column=2, padx=5, sticky=tk.W)
        self.port_var = tk.StringVar(value="21")
        ttk.Entry(basic_frame, textvariable=self.port_var, width=8).grid(row=0, column=3, padx=5)
        
        ttk.Label(basic_frame, text="用户名:").grid(row=0, column=4, padx=5, sticky=tk.W)
        self.username_var = tk.StringVar(value="anonymous")
        ttk.Entry(basic_frame, textvariable=self.username_var, width=15).grid(row=0, column=5, padx=5)
        
        ttk.Label(basic_frame, text="密码:").grid(row=0, column=6, padx=5, sticky=tk.W)
        self.password_var = tk.StringVar()
        ttk.Entry(basic_frame, textvariable=self.password_var, show="*", width=15).grid(row=0, column=7, padx=5)
        
        self.connect_btn = ttk.Button(basic_frame, text="连接", command=self.connect)
        self.connect_btn.grid(row=0, column=8, padx=5)
        
        # 第二行：高级选项
        advanced_frame = ttk.Frame(conn_frame)
        advanced_frame.pack(fill=tk.X, pady=(5, 0))
        
        # 被动模式
        self.passive_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(advanced_frame, text="被动模式", variable=self.passive_var).pack(side=tk.LEFT, padx=5)
        
        # 超时设置
        ttk.Label(advanced_frame, text="超时:").pack(side=tk.LEFT, padx=(20, 5))
        self.timeout_var = tk.StringVar(value="30")
        ttk.Entry(advanced_frame, textvariable=self.timeout_var, width=5).pack(side=tk.LEFT, padx=2)
        ttk.Label(advanced_frame, text="秒").pack(side=tk.LEFT, padx=2)
        
        # 测试连接按钮
        ttk.Button(advanced_frame, text="测试连接", command=self.test_connection).pack(side=tk.LEFT, padx=(20, 5))
        
        # 连接日志按钮
        ttk.Button(advanced_frame, text="连接日志", command=self.show_connection_log).pack(side=tk.LEFT, padx=5)
        
        # 快速连接
        quick_frame = ttk.Frame(conn_frame)
        quick_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(quick_frame, text="快速连接:").pack(side=tk.LEFT)
        ttk.Button(quick_frame, text="GNU FTP", 
                  command=lambda: self.quick_connect("ftp.gnu.org", "21", "anonymous", "")).pack(side=tk.LEFT, padx=5)
        ttk.Button(quick_frame, text="本地测试", 
                  command=lambda: self.quick_connect("192.168.31.6", "2121", "anonymous", "")).pack(side=tk.LEFT, padx=5)
        
        # 主内容区域
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 创建左右分割的PanedWindow
        paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # 左侧：文件浏览
        left_frame = ttk.LabelFrame(paned, text="远程文件", padding=5)
        paned.add(left_frame, weight=1)
        
        self.create_file_browser(left_frame)
        
        # 右侧：下载管理
        right_frame = ttk.LabelFrame(paned, text="下载管理", padding=5)
        paned.add(right_frame, weight=1)
        
        self.create_download_manager(right_frame)
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
        
        # 连接日志
        self.connection_log = []
    
    def create_file_browser(self, parent):
        """创建文件浏览器"""
        # 路径栏
        path_frame = ttk.Frame(parent)
        path_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(path_frame, text="路径:").pack(side=tk.LEFT)
        self.path_var = tk.StringVar(value="/")
        path_entry = ttk.Entry(path_frame, textvariable=self.path_var, state="readonly")
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        ttk.Button(path_frame, text="🏠", command=self.go_home, width=3).pack(side=tk.RIGHT, padx=1)
        ttk.Button(path_frame, text="⬆️", command=self.go_up, width=3).pack(side=tk.RIGHT, padx=1)
        ttk.Button(path_frame, text="🔄", command=self.refresh, width=3).pack(side=tk.RIGHT, padx=1)
        
        # 搜索和排序栏
        search_frame = ttk.Frame(parent)
        search_frame.pack(fill=tk.X, pady=(0, 5))
        
        # 搜索功能
        ttk.Label(search_frame, text="搜索:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side=tk.LEFT, padx=(5, 10))
        
        # 排序选项
        ttk.Label(search_frame, text="排序:").pack(side=tk.LEFT)
        self.sort_var = tk.StringVar(value="name")
        sort_combo = ttk.Combobox(search_frame, textvariable=self.sort_var, width=10, state="readonly")
        sort_combo['values'] = ("name", "size", "date", "type")
        sort_combo.pack(side=tk.LEFT, padx=5)
        sort_combo.bind('<<ComboboxSelected>>', self.on_sort_change)
        
        # 排序方向
        self.sort_desc_var = tk.BooleanVar()
        ttk.Checkbutton(search_frame, text="降序", variable=self.sort_desc_var, 
                       command=self.on_sort_change).pack(side=tk.LEFT, padx=5)
        
        # 显示选项
        self.show_hidden_var = tk.BooleanVar()
        ttk.Checkbutton(search_frame, text="显示隐藏文件", variable=self.show_hidden_var,
                       command=self.on_sort_change).pack(side=tk.LEFT, padx=5)
        
        # 文件列表框架
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # 文件列表
        columns = ("size", "type", "date")
        self.file_tree = ttk.Treeview(list_frame, columns=columns, show="tree headings")
        
        self.file_tree.heading("#0", text="名称", anchor=tk.W)
        self.file_tree.heading("size", text="大小", anchor=tk.W)
        self.file_tree.heading("type", text="类型", anchor=tk.W)
        self.file_tree.heading("date", text="修改时间", anchor=tk.W)
        
        self.file_tree.column("#0", width=200, minwidth=150)
        self.file_tree.column("size", width=100, minwidth=80)
        self.file_tree.column("type", width=80, minwidth=60)
        self.file_tree.column("date", width=120, minwidth=100)
        
        # 滚动条
        scrollbar1 = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=scrollbar1.set)
        
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar1.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定事件
        self.file_tree.bind("<Double-1>", self.on_double_click)
        
        # 文件操作按钮
        file_btn_frame = ttk.Frame(parent)
        file_btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(file_btn_frame, text="下载选中", command=self.download_selected).pack(side=tk.LEFT, padx=2)
        ttk.Button(file_btn_frame, text="下载全部", command=self.download_all).pack(side=tk.LEFT, padx=2)
    
    def create_download_manager(self, parent):
        """创建下载管理器"""
        # 保存路径
        save_frame = ttk.Frame(parent)
        save_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(save_frame, text="保存到:").pack(side=tk.LEFT)
        self.save_path_var = tk.StringVar(value=str(Path.home() / "Downloads"))
        save_entry = ttk.Entry(save_frame, textvariable=self.save_path_var)
        save_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(save_frame, text="浏览", command=self.browse_save_path).pack(side=tk.RIGHT)
        
        # 下载列表框架
        download_frame = ttk.Frame(parent)
        download_frame.pack(fill=tk.BOTH, expand=True)
        
        # 下载列表
        download_columns = ("progress", "speed", "status")
        self.download_tree = ttk.Treeview(download_frame, columns=download_columns, show="tree headings")
        
        self.download_tree.heading("#0", text="文件名", anchor=tk.W)
        self.download_tree.heading("progress", text="进度", anchor=tk.W)
        self.download_tree.heading("speed", text="速度", anchor=tk.W)
        self.download_tree.heading("status", text="状态", anchor=tk.W)
        
        self.download_tree.column("#0", width=200, minwidth=150)
        self.download_tree.column("progress", width=100, minwidth=80)
        self.download_tree.column("speed", width=100, minwidth=80)
        self.download_tree.column("status", width=80, minwidth=60)
        
        # 滚动条
        scrollbar2 = ttk.Scrollbar(download_frame, orient=tk.VERTICAL, command=self.download_tree.yview)
        self.download_tree.configure(yscrollcommand=scrollbar2.set)
        
        self.download_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar2.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 下载控制按钮
        download_btn_frame = ttk.Frame(parent)
        download_btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(download_btn_frame, text="开始下载", command=self.start_downloads).pack(side=tk.LEFT, padx=2)
        ttk.Button(download_btn_frame, text="暂停下载", command=self.pause_downloads).pack(side=tk.LEFT, padx=2)
        ttk.Button(download_btn_frame, text="清除列表", command=self.clear_downloads).pack(side=tk.LEFT, padx=2)
    
    def log_message(self, message):
        """记录连接日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.connection_log.append(log_entry)
        print(log_entry)  # 同时输出到控制台
        
        # 限制日志数量
        if len(self.connection_log) > 100:
            self.connection_log = self.connection_log[-50:]
    
    def quick_connect(self, host, port, username, password):
        """快速连接"""
        self.host_var.set(host)
        self.port_var.set(port)
        self.username_var.set(username)
        self.password_var.set(password)
        self.connect()
    
    def test_connection(self):
        """测试连接"""
        host = self.host_var.get().strip()
        if not host:
            messagebox.showerror("错误", "请输入服务器地址")
            return
        
        try:
            port = int(self.port_var.get() or "21")
        except ValueError:
            messagebox.showerror("错误", "端口必须是数字")
            return
        
        self.log_message(f"测试连接到 {host}:{port}")
        
        def test_thread():
            try:
                # 测试TCP连接
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(10)
                result = sock.connect_ex((host, port))
                sock.close()
                
                if result == 0:
                    self.log_message(f"TCP连接成功: {host}:{port}")
                    
                    # 测试FTP连接
                    ftp = ftplib.FTP()
                    ftp.connect(host, port, 10)
                    welcome = ftp.getwelcome()
                    ftp.quit()
                    
                    self.log_message(f"FTP连接成功: {welcome}")
                    self.root.after(0, lambda: messagebox.showinfo("测试成功", f"连接测试成功!\n服务器响应: {welcome}"))
                else:
                    self.log_message(f"TCP连接失败: {host}:{port} (错误码: {result})")
                    self.root.after(0, lambda: messagebox.showerror("测试失败", f"无法连接到 {host}:{port}\n错误码: {result}"))
                    
            except Exception as e:
                error_msg = str(e)
                self.log_message(f"连接测试失败: {error_msg}")
                self.root.after(0, lambda: messagebox.showerror("测试失败", f"连接测试失败:\n{error_msg}"))
        
        threading.Thread(target=test_thread, daemon=True).start()
    
    def connect(self):
        """连接FTP服务器"""
        host = self.host_var.get().strip()
        if not host:
            messagebox.showerror("错误", "请输入服务器地址")
            return
        
        try:
            port = int(self.port_var.get() or "21")
            timeout = int(self.timeout_var.get() or "30")
        except ValueError:
            messagebox.showerror("错误", "端口和超时时间必须是数字")
            return
        
        username = self.username_var.get() or "anonymous"
        password = self.password_var.get()
        passive = self.passive_var.get()
        
        self.status_var.set("正在连接...")
        self.connect_btn.config(state=tk.DISABLED)
        
        self.log_message(f"开始连接 {host}:{port} (用户: {username}, 被动模式: {passive})")
        
        def connect_thread():
            try:
                # 创建FTP连接
                ftp = ftplib.FTP()
                
                # 设置调试级别
                ftp.set_debuglevel(1)
                
                self.log_message(f"正在连接到 {host}:{port}...")
                ftp.connect(host, port, timeout)
                
                self.log_message(f"服务器响应: {ftp.getwelcome()}")
                
                self.log_message(f"正在登录用户: {username}")
                ftp.login(username, password)
                
                self.log_message(f"设置传输模式: {'被动' if passive else '主动'}")
                ftp.set_pasv(passive)
                
                # 尝试设置编码
                try:
                    ftp.encoding = self.encoding
                    self.log_message(f"设置编码: {self.encoding}")
                except:
                    self.log_message("无法设置编码，使用默认编码")
                
                # 获取当前路径
                current_path = ftp.pwd()
                self.log_message(f"当前路径: {current_path}")
                
                # 连接成功，更新界面
                self.root.after(0, lambda: self.on_connect_success(ftp, current_path))
                
            except Exception as e:
                error_msg = str(e)
                self.log_message(f"连接失败: {error_msg}")
                self.root.after(0, lambda: self.on_connect_error(error_msg))
        
        threading.Thread(target=connect_thread, daemon=True).start()
    
    def on_connect_success(self, ftp, current_path):
        """连接成功回调"""
        self.ftp = ftp
        self.connected = True
        self.current_path = current_path
        
        self.status_var.set(f"已连接到 {self.host_var.get()}")
        self.connect_btn.config(text="断开", command=self.disconnect, state=tk.NORMAL)
        self.path_var.set(self.current_path)
        
        self.log_message("连接成功，开始获取文件列表")
        self.refresh()
    
    def on_connect_error(self, error_msg):
        """连接失败回调"""
        self.status_var.set("连接失败")
        self.connect_btn.config(state=tk.NORMAL)
        messagebox.showerror("连接失败", f"无法连接到FTP服务器:\n{error_msg}\n\n请检查连接日志获取详细信息")
    
    def disconnect(self):
        """断开连接"""
        if self.ftp:
            try:
                self.ftp.quit()
                self.log_message("已断开FTP连接")
            except:
                self.log_message("强制断开FTP连接")
            self.ftp = None
        
        self.connected = False
        self.status_var.set("已断开连接")
        self.connect_btn.config(text="连接", command=self.connect)
        
        # 清空文件列表
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
    
    def show_connection_log(self):
        """显示连接日志"""
        log_window = tk.Toplevel(self.root)
        log_window.title("连接日志")
        log_window.geometry("600x400")
        log_window.transient(self.root)
        
        # 日志文本区域
        from tkinter.scrolledtext import ScrolledText
        log_text = ScrolledText(log_window, wrap=tk.WORD, font=('Consolas', 9))
        log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 填充日志内容
        for message in self.connection_log:
            log_text.insert(tk.END, message + "\n")
        
        log_text.config(state=tk.DISABLED)
        
        # 控制按钮
        btn_frame = ttk.Frame(log_window)
        btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Button(btn_frame, text="清除日志", command=lambda: self.clear_log(log_text)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="刷新", command=lambda: self.refresh_log(log_text)).pack(side=tk.LEFT)
    
    def clear_log(self, log_text):
        """清除日志"""
        self.connection_log.clear()
        log_text.config(state=tk.NORMAL)
        log_text.delete(1.0, tk.END)
        log_text.config(state=tk.DISABLED)
    
    def refresh_log(self, log_text):
        """刷新日志"""
        log_text.config(state=tk.NORMAL)
        log_text.delete(1.0, tk.END)
        for message in self.connection_log:
            log_text.insert(tk.END, message + "\n")
        log_text.config(state=tk.DISABLED)
        log_text.see(tk.END)
    
    def refresh(self):
        """刷新文件列表"""
        if not self.connected or not self.ftp:
            return
        
        self.status_var.set("正在获取文件列表...")
        self.log_message("开始获取文件列表")
        
        def refresh_thread():
            try:
                files = []
                
                # 尝试不同的LIST命令
                try:
                    self.ftp.retrlines('LIST', files.append)
                    self.log_message(f"使用LIST命令获取到 {len(files)} 行数据")
                except Exception as e:
                    self.log_message(f"LIST命令失败: {e}")
                    # 尝试NLST命令
                    try:
                        files = self.ftp.nlst()
                        self.log_message(f"使用NLST命令获取到 {len(files)} 个文件")
                        # 转换为LIST格式
                        formatted_files = []
                        for filename in files:
                            if filename not in ['.', '..']:
                                formatted_files.append(f"-rw-r--r-- 1 user user 0 Jan 1 00:00 {filename}")
                        files = formatted_files
                    except Exception as e2:
                        self.log_message(f"NLST命令也失败: {e2}")
                        raise e
                
                self.root.after(0, lambda: self.update_file_list(files))
            except Exception as e:
                error_msg = str(e)
                self.log_message(f"获取文件列表失败: {error_msg}")
                self.root.after(0, lambda: self.on_refresh_error(error_msg))
        
        threading.Thread(target=refresh_thread, daemon=True).start()
    
    def update_file_list(self, files):
        """更新文件列表"""
        self.log_message(f"解析 {len(files)} 个文件项")
        
        # 解析文件信息到内部数据结构
        self.file_data = []
        parsed_count = 0
        
        for line in files:
            try:
                if isinstance(line, str) and len(line.strip()) > 0:
                    parts = line.split()
                    if len(parts) >= 9:
                        permissions = parts[0]
                        is_dir = permissions.startswith('d')
                        
                        try:
                            size = int(parts[4]) if not is_dir else 0
                        except (ValueError, IndexError):
                            size = 0
                        
                        filename = ' '.join(parts[8:])
                        if filename in ['.', '..']:
                            continue
                        
                        try:
                            date_str = f"{parts[5]} {parts[6]} {parts[7]}"
                        except IndexError:
                            date_str = "未知"
                        
                        # 存储文件信息
                        file_info = {
                            'name': filename,
                            'size': size,
                            'is_dir': is_dir,
                            'date': date_str,
                            'permissions': permissions
                        }
                        self.file_data.append(file_info)
                        parsed_count += 1
                        
                    elif len(parts) >= 1:
                        # 简单文件名列表
                        filename = parts[0]
                        if filename not in ['.', '..']:
                            file_info = {
                                'name': filename,
                                'size': 0,
                                'is_dir': False,
                                'date': "未知",
                                'permissions': "-rw-r--r--"
                            }
                            self.file_data.append(file_info)
                            parsed_count += 1
            except Exception as e:
                self.log_message(f"解析文件行失败: {line} - {e}")
                continue
        
        self.path_var.set(self.current_path)
        self.log_message(f"成功解析 {parsed_count} 个文件项")
        
        # 应用搜索和排序
        self.apply_filter_and_sort()
    
    def on_refresh_error(self, error_msg):
        """刷新失败回调"""
        self.status_var.set("获取文件列表失败")
        messagebox.showerror("错误", f"获取文件列表失败:\n{error_msg}\n\n请检查连接日志获取详细信息")
    
    def on_double_click(self, event):
        """双击事件处理"""
        selection = self.file_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        text = self.file_tree.item(item, "text")
        values = self.file_tree.item(item, "values")
        
        if not values or len(values) < 2:
            return
        
        # 提取文件名
        filename = text.split(" ", 1)[1] if " " in text else text.replace("📁 ", "").replace("📄 ", "")
        is_dir = values[1] == "目录"
        
        if is_dir:
            # 进入目录
            self.change_directory(filename)
        else:
            # 下载文件
            self.add_download_task(filename)
    
    def change_directory(self, dirname):
        """切换目录"""
        if not self.connected or not self.ftp:
            messagebox.showwarning("提示", "请先连接FTP服务器")
            return
        
        self.log_message(f"切换目录: {dirname}")
        
        try:
            old_path = self.current_path
            
            if dirname == "..":
                # 返回上级目录
                if self.current_path == "/" or self.current_path == "":
                    messagebox.showinfo("提示", "已经在根目录")
                    return
                
                # 计算上级目录路径
                path_parts = self.current_path.strip('/').split('/')
                if len(path_parts) > 1:
                    parent_path = '/' + '/'.join(path_parts[:-1])
                else:
                    parent_path = '/'
                
                self.log_message(f"计算上级目录: {self.current_path} -> {parent_path}")
                self.ftp.cwd(parent_path)
            else:
                # 进入子目录
                if self.current_path.endswith('/'):
                    new_path = self.current_path + dirname
                else:
                    new_path = self.current_path + '/' + dirname
                
                self.log_message(f"进入子目录: {self.current_path} -> {new_path}")
                self.ftp.cwd(new_path)
            
            # 获取实际当前路径
            self.current_path = self.ftp.pwd()
            self.log_message(f"目录切换成功，当前路径: {self.current_path}")
            
            # 清空搜索框
            if self.search_var:
                self.search_var.set("")
            
            self.refresh()
            
        except Exception as e:
            error_msg = str(e)
            self.log_message(f"切换目录失败: {error_msg}")
            messagebox.showerror("错误", f"无法进入目录: {dirname}\n{error_msg}")
            
            # 尝试恢复到原路径
            try:
                self.ftp.cwd(old_path)
                self.current_path = self.ftp.pwd()
            except:
                pass
    
    def go_up(self):
        """返回上级目录"""
        if not self.connected or not self.ftp:
            messagebox.showwarning("提示", "请先连接FTP服务器")
            return
        self.change_directory("..")
    
    def go_home(self):
        """返回根目录"""
        if not self.connected or not self.ftp:
            messagebox.showwarning("提示", "请先连接FTP服务器")
            return
        try:
            self.ftp.cwd("/")
            self.current_path = self.ftp.pwd()
            self.log_message(f"返回根目录: {self.current_path}")
            self.refresh()
        except Exception as e:
            error_msg = str(e)
            self.log_message(f"返回根目录失败: {error_msg}")
            messagebox.showerror("错误", f"无法返回根目录:\n{error_msg}")
    
    def on_search_change(self, *args):
        """搜索内容变化时的回调"""
        self.apply_filter_and_sort()
    
    def on_sort_change(self, *args):
        """排序选项变化时的回调"""
        self.apply_filter_and_sort()
    
    def apply_filter_and_sort(self):
        """应用搜索过滤和排序"""
        if not hasattr(self, 'file_data'):
            return
        
        # 获取搜索关键词
        search_text = self.search_var.get().lower() if self.search_var else ""
        show_hidden = self.show_hidden_var.get() if self.show_hidden_var else False
        
        # 过滤文件
        self.filtered_data = []
        for file_info in self.file_data:
            filename = file_info['name']
            
            # 隐藏文件过滤
            if not show_hidden and filename.startswith('.'):
                continue
            
            # 搜索过滤
            if search_text and search_text not in filename.lower():
                continue
            
            self.filtered_data.append(file_info)
        
        # 排序
        sort_key = self.sort_var.get() if self.sort_var else "name"
        sort_desc = self.sort_desc_var.get() if self.sort_desc_var else False
        
        if sort_key == "name":
            self.filtered_data.sort(key=lambda x: x['name'].lower(), reverse=sort_desc)
        elif sort_key == "size":
            self.filtered_data.sort(key=lambda x: x['size'], reverse=sort_desc)
        elif sort_key == "date":
            self.filtered_data.sort(key=lambda x: x['date'], reverse=sort_desc)
        elif sort_key == "type":
            # 目录优先，然后按文件名排序
            self.filtered_data.sort(key=lambda x: (not x['is_dir'], x['name'].lower()), reverse=sort_desc)
        
        # 目录始终在前面（除非按类型排序且降序）
        if sort_key != "type" or not sort_desc:
            dirs = [f for f in self.filtered_data if f['is_dir']]
            files = [f for f in self.filtered_data if not f['is_dir']]
            self.filtered_data = dirs + files
        
        # 更新显示
        self.update_tree_display()
    
    def update_tree_display(self):
        """更新树形控件显示"""
        # 清空现有列表
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        
        # 添加过滤后的文件
        for file_info in self.filtered_data:
            filename = file_info['name']
            size = file_info['size']
            is_dir = file_info['is_dir']
            date_str = file_info['date']
            
            size_str = self.format_size(size) if not is_dir else ""
            type_str = "目录" if is_dir else "文件"
            icon = "📁" if is_dir else "📄"
            
            self.file_tree.insert("", tk.END, 
                                text=f"{icon} {filename}",
                                values=(size_str, type_str, date_str),
                                tags=("directory" if is_dir else "file",))
        
        # 更新状态
        total_files = len([f for f in self.filtered_data if not f['is_dir']])
        total_dirs = len([f for f in self.filtered_data if f['is_dir']])
        total_size = sum(f['size'] for f in self.filtered_data if not f['is_dir'])
        
        status_msg = f"目录: {total_dirs}, 文件: {total_files}"
        if total_size > 0:
            status_msg += f", 总大小: {self.format_size(total_size)}"
        
        search_text = self.search_var.get() if self.search_var else ""
        if search_text:
            status_msg += f" (搜索: '{search_text}')"
        
        self.status_var.set(status_msg)
    
    def download_selected(self):
        """下载选中文件"""
        selection = self.file_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择要下载的文件")
            return
        
        for item in selection:
            text = self.file_tree.item(item, "text")
            values = self.file_tree.item(item, "values")
            
            if values and len(values) >= 2 and values[1] == "文件":
                filename = text.split(" ", 1)[1] if " " in text else text.replace("📄 ", "")
                self.add_download_task(filename)
    
    def download_all(self):
        """下载所有文件"""
        files = []
        for item in self.file_tree.get_children():
            text = self.file_tree.item(item, "text")
            values = self.file_tree.item(item, "values")
            
            if values and len(values) >= 2 and values[1] == "文件":
                filename = text.split(" ", 1)[1] if " " in text else text.replace("📄 ", "")
                files.append(filename)
        
        if not files:
            messagebox.showinfo("提示", "当前目录没有文件")
            return
        
        result = messagebox.askyesno("确认", f"是否下载当前目录的所有 {len(files)} 个文件？")
        if result:
            for filename in files:
                self.add_download_task(filename)
    
    def add_download_task(self, filename):
        """添加下载任务"""
        remote_path = self.current_path
        if remote_path.endswith('/'):
            remote_path += filename
        else:
            remote_path += '/' + filename
        
        local_path = Path(self.save_path_var.get()) / filename
        
        # 获取文件大小
        size = 0
        if self.ftp:
            try:
                size = self.ftp.size(remote_path) or 0
                self.log_message(f"文件大小: {filename} = {size} 字节")
            except Exception as e:
                self.log_message(f"无法获取文件大小: {filename} - {e}")
                size = 0
        
        task = DownloadTask(remote_path, str(local_path), size)
        self.download_tasks.append(task)
        
        self.status_var.set(f"已添加下载任务: {filename}")
        self.log_message(f"添加下载任务: {filename} -> {local_path}")
    
    def browse_save_path(self):
        """浏览保存路径"""
        path = filedialog.askdirectory(initialdir=self.save_path_var.get())
        if path:
            self.save_path_var.set(path)
    
    def start_downloads(self):
        """开始下载"""
        if not self.download_tasks:
            messagebox.showinfo("提示", "没有下载任务")
            return
        
        if self.downloading:
            messagebox.showinfo("提示", "下载正在进行中")
            return
        
        self.downloading = True
        self.status_var.set("开始下载...")
        self.log_message("开始下载任务")
        threading.Thread(target=self.download_worker, daemon=True).start()
    
    def pause_downloads(self):
        """暂停下载"""
        self.downloading = False
        self.status_var.set("下载已暂停")
        self.log_message("下载已暂停")
    
    def clear_downloads(self):
        """清除下载列表"""
        if self.downloading:
            result = messagebox.askyesno("确认", "下载正在进行中，是否强制清除？")
            if not result:
                return
            self.downloading = False
        
        self.download_tasks.clear()
        self.status_var.set("已清除下载列表")
        self.log_message("已清除下载列表")
    
    def download_worker(self):
        """下载工作线程"""
        for task in self.download_tasks:
            if not self.downloading:
                break
            
            if task.status in ["已完成", "下载中"]:
                continue
            
            try:
                self.download_file(task)
            except Exception as e:
                task.status = "失败"
                task.error_msg = str(e)
                self.log_message(f"下载失败: {task.remote_path} - {e}")
        
        self.downloading = False
        self.root.after(0, lambda: self.status_var.set("下载完成"))
        self.log_message("所有下载任务完成")
    
    def download_file(self, task):
        """下载单个文件"""
        task.status = "下载中"
        task.start_time = time.time()
        
        self.log_message(f"开始下载: {task.remote_path}")
        
        # 创建本地目录
        local_path = Path(task.local_path)
        local_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 检查本地文件
        local_size = 0
        if local_path.exists():
            local_size = local_path.stat().st_size
            if local_size == task.size and task.size > 0:
                task.status = "已完成"
                task.progress = 100.0
                self.log_message(f"文件已存在且完整: {task.remote_path}")
                return
            elif local_size > task.size and task.size > 0:
                local_path.unlink()
                local_size = 0
                self.log_message(f"本地文件大小异常，重新下载: {task.remote_path}")
        
        task.downloaded = local_size
        
        # 创建新的FTP连接用于下载
        try:
            ftp = ftplib.FTP()
            ftp.connect(self.host_var.get(), int(self.port_var.get()), int(self.timeout_var.get()))
            ftp.login(self.username_var.get(), self.password_var.get())
            ftp.set_pasv(self.passive_var.get())
            
            # 设置断点续传
            if local_size > 0:
                ftp.sendcmd(f'REST {local_size}')
                self.log_message(f"断点续传从 {local_size} 字节开始")
            
            # 开始下载
            mode = 'ab' if local_size > 0 else 'wb'
            
            with open(local_path, mode) as f:
                def callback(data):
                    if not self.downloading:
                        return
                    
                    f.write(data)
                    task.downloaded += len(data)
                    
                    # 计算进度和速度
                    if task.size > 0:
                        task.progress = (task.downloaded / task.size) * 100
                    
                    elapsed = time.time() - task.start_time
                    if elapsed > 0:
                        task.speed = (task.downloaded - local_size) / elapsed
                
                ftp.retrbinary(f'RETR {task.remote_path}', callback, 8192)
            
            ftp.quit()
            
            # 检查下载完整性
            if task.size == 0 or task.downloaded >= task.size:
                task.status = "已完成"
                task.progress = 100.0
                self.log_message(f"下载完成: {task.remote_path}")
            else:
                task.status = "失败"
                task.error_msg = "下载不完整"
                self.log_message(f"下载不完整: {task.remote_path} ({task.downloaded}/{task.size})")
                
        except Exception as e:
            task.status = "失败"
            task.error_msg = str(e)
            self.log_message(f"下载异常: {task.remote_path} - {e}")
            raise e
    
    def update_ui(self):
        """定时更新界面"""
        self.update_download_list()
        self.root.after(1000, self.update_ui)
    
    def update_download_list(self):
        """更新下载列表"""
        # 清空现有列表
        for item in self.download_tree.get_children():
            self.download_tree.delete(item)
        
        # 添加任务
        for task in self.download_tasks:
            filename = Path(task.remote_path).name
            progress_str = f"{task.progress:.1f}%"
            speed_str = self.format_size(task.speed) + "/s" if task.speed > 0 else ""
            
            self.download_tree.insert("", tk.END, 
                                    text=filename,
                                    values=(progress_str, speed_str, task.status))
    
    def update_downloads(self):
        """定时更新下载状态"""
        self.update_download_list()
        self.root.after(1000, self.update_downloads)
    
    def format_size(self, size):
        """格式化文件大小"""
        if size == 0:
            return "0B"
        
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.1f}{unit}"
            size /= 1024
        return f"{size:.1f}PB"
    
    def run(self):
        """运行GUI"""
        try:
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.root.mainloop()
        except KeyboardInterrupt:
            pass
    
    def on_closing(self):
        """关闭程序"""
        self.downloading = False
        if self.ftp:
            try:
                self.ftp.quit()
            except:
                pass
        self.root.destroy()

def main():
    """主函数"""
    try:
        app = EnhancedFTPGUI()
        app.run()
    except Exception as e:
        print(f"程序启动失败: {e}")
        if 'messagebox' in globals():
            messagebox.showerror("错误", f"程序启动失败:\n{str(e)}")

if __name__ == '__main__':
    main()