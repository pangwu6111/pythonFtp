#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FTP断点续传下载工具 - 高级GUI版本
包含文件同步、批量操作、传输队列管理等高级功能
"""

import os
import sys
import time
import json
import ftplib
import hashlib
import threading
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any, Callable

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from tkinter.scrolledtext import ScrolledText

# 导入基础GUI类
from ftp_gui import FTPClientGUI, FTPConnection, DownloadManager, DownloadTask, FTPFileInfo

class SyncProfile:
    """同步配置文件"""
    
    def __init__(self, name: str = ""):
        self.name = name
        self.remote_path = "/"
        self.local_path = ""
        self.sync_mode = "download"  # download, upload, bidirectional
        self.file_filters = ["*"]
        self.exclude_patterns = []
        self.delete_extra = False
        self.preserve_timestamps = True
        self.auto_sync = False
        self.sync_interval = 300  # 5分钟
        
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data):
        profile = cls()
        for key, value in data.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        return profile

class TransferQueue:
    """传输队列管理器"""
    
    def __init__(self):
        self.queue: List[DownloadTask] = []
        self.completed: List[DownloadTask] = []
        self.failed: List[DownloadTask] = []
        self.max_concurrent = 3
        self.active_transfers = 0
        self.paused = False
        
    def add_task(self, task: DownloadTask):
        """添加任务到队列"""
        self.queue.append(task)
    
    def get_next_task(self) -> Optional[DownloadTask]:
        """获取下一个待执行任务"""
        if self.paused or self.active_transfers >= self.max_concurrent:
            return None
        
        for task in self.queue:
            if task.status == "等待中":
                return task
        return None
    
    def move_to_completed(self, task: DownloadTask):
        """移动任务到已完成列表"""
        if task in self.queue:
            self.queue.remove(task)
        self.completed.append(task)
    
    def move_to_failed(self, task: DownloadTask):
        """移动任务到失败列表"""
        if task in self.queue:
            self.queue.remove(task)
        self.failed.append(task)

class AdvancedFTPGUI(FTPClientGUI):
    """高级FTP GUI客户端"""
    
    def __init__(self):
        # 初始化高级功能
        self.sync_profiles: List[SyncProfile] = []
        self.transfer_queue = TransferQueue()
        self.log_messages: List[str] = []
        self.bookmarks: Dict[str, Dict] = {}
        
        # 调用父类初始化
        super().__init__()
        
        # 添加高级功能界面
        self.create_advanced_widgets()
        self.load_advanced_config()
    
    def create_advanced_widgets(self):
        """创建高级功能界面"""
        # 创建菜单栏
        self.create_menu_bar()
        
        # 在主界面添加标签页
        self.create_tabbed_interface()
    
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="新建连接", command=self.new_connection)
        file_menu.add_command(label="保存会话", command=self.save_session)
        file_menu.add_command(label="加载会话", command=self.load_session)
        file_menu.add_separator()
        file_menu.add_command(label="导入书签", command=self.import_bookmarks)
        file_menu.add_command(label="导出书签", command=self.export_bookmarks)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.on_closing)
        
        # 传输菜单
        transfer_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="传输", menu=transfer_menu)
        transfer_menu.add_command(label="传输队列", command=self.show_transfer_queue)
        transfer_menu.add_command(label="传输设置", command=self.show_transfer_settings)
        transfer_menu.add_separator()
        transfer_menu.add_command(label="暂停所有", command=self.pause_all_transfers)
        transfer_menu.add_command(label="恢复所有", command=self.resume_all_transfers)
        transfer_menu.add_command(label="取消所有", command=self.cancel_all_transfers)
        
        # 同步菜单
        sync_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="同步", menu=sync_menu)
        sync_menu.add_command(label="同步配置", command=self.show_sync_profiles)
        sync_menu.add_command(label="立即同步", command=self.start_sync)
        sync_menu.add_command(label="同步历史", command=self.show_sync_history)
        
        # 工具菜单
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="工具", menu=tools_menu)
        tools_menu.add_command(label="文件比较", command=self.compare_files)
        tools_menu.add_command(label="批量重命名", command=self.batch_rename)
        tools_menu.add_command(label="计算校验和", command=self.calculate_checksums)
        tools_menu.add_separator()
        tools_menu.add_command(label="清理临时文件", command=self.cleanup_temp_files)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="使用说明", command=self.show_help)
        help_menu.add_command(label="快捷键", command=self.show_shortcuts)
        help_menu.add_command(label="关于", command=self.show_about)
    
    def create_tabbed_interface(self):
        """创建标签页界面"""
        # 在现有界面基础上添加标签页
        # 这里需要重构现有界面结构
        pass
    
    def show_transfer_queue(self):
        """显示传输队列窗口"""
        queue_window = tk.Toplevel(self.root)
        queue_window.title("传输队列管理")
        queue_window.geometry("800x600")
        queue_window.transient(self.root)
        
        # 创建队列列表
        frame = ttk.Frame(queue_window, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 队列统计
        stats_frame = ttk.Frame(frame)
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        queue_count = len(self.transfer_queue.queue)
        completed_count = len(self.transfer_queue.completed)
        failed_count = len(self.transfer_queue.failed)
        
        ttk.Label(stats_frame, text=f"队列中: {queue_count} | 已完成: {completed_count} | 失败: {failed_count}").pack(side=tk.LEFT)
        
        # 队列列表
        columns = ("文件名", "大小", "进度", "状态", "速度", "剩余时间")
        tree = ttk.Treeview(frame, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 控制按钮
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(btn_frame, text="暂停选中", command=lambda: self.pause_selected_tasks(tree)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="恢复选中", command=lambda: self.resume_selected_tasks(tree)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="取消选中", command=lambda: self.cancel_selected_tasks(tree)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="清除已完成", command=lambda: self.clear_completed_tasks(tree)).pack(side=tk.LEFT, padx=(0, 5))
        
        # 填充队列数据
        self.populate_queue_tree(tree)
    
    def show_sync_profiles(self):
        """显示同步配置窗口"""
        sync_window = tk.Toplevel(self.root)
        sync_window.title("同步配置管理")
        sync_window.geometry("900x700")
        sync_window.transient(self.root)
        
        # 主框架
        main_frame = ttk.Frame(sync_window, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左侧：配置列表
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        ttk.Label(left_frame, text="同步配置", font=('Arial', 12, 'bold')).pack(anchor=tk.W)
        
        # 配置列表
        profile_listbox = tk.Listbox(left_frame, width=25)
        profile_listbox.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # 配置按钮
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(btn_frame, text="新建", command=lambda: self.new_sync_profile(profile_listbox)).pack(fill=tk.X, pady=(0, 2))
        ttk.Button(btn_frame, text="删除", command=lambda: self.delete_sync_profile(profile_listbox)).pack(fill=tk.X, pady=(0, 2))
        ttk.Button(btn_frame, text="复制", command=lambda: self.copy_sync_profile(profile_listbox)).pack(fill=tk.X)
        
        # 右侧：配置详情
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        ttk.Label(right_frame, text="配置详情", font=('Arial', 12, 'bold')).pack(anchor=tk.W)
        
        # 配置表单
        form_frame = ttk.Frame(right_frame)
        form_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # 这里添加配置表单字段
        self.create_sync_profile_form(form_frame)
        
        # 填充配置列表
        self.populate_sync_profiles(profile_listbox)
    
    def create_sync_profile_form(self, parent):
        """创建同步配置表单"""
        # 配置名称
        ttk.Label(parent, text="配置名称:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.sync_name_var = tk.StringVar()
        ttk.Entry(parent, textvariable=self.sync_name_var, width=40).grid(row=0, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        # 远程路径
        ttk.Label(parent, text="远程路径:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.sync_remote_var = tk.StringVar()
        ttk.Entry(parent, textvariable=self.sync_remote_var, width=40).grid(row=1, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        # 本地路径
        ttk.Label(parent, text="本地路径:").grid(row=2, column=0, sticky=tk.W, pady=2)
        path_frame = ttk.Frame(parent)
        path_frame.grid(row=2, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        self.sync_local_var = tk.StringVar()
        ttk.Entry(path_frame, textvariable=self.sync_local_var, width=30).pack(side=tk.LEFT)
        ttk.Button(path_frame, text="浏览", command=self.browse_sync_local_path).pack(side=tk.LEFT, padx=(5, 0))
        
        # 同步模式
        ttk.Label(parent, text="同步模式:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.sync_mode_var = tk.StringVar(value="download")
        mode_frame = ttk.Frame(parent)
        mode_frame.grid(row=3, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        ttk.Radiobutton(mode_frame, text="仅下载", variable=self.sync_mode_var, value="download").pack(side=tk.LEFT)
        ttk.Radiobutton(mode_frame, text="仅上传", variable=self.sync_mode_var, value="upload").pack(side=tk.LEFT, padx=(10, 0))
        ttk.Radiobutton(mode_frame, text="双向同步", variable=self.sync_mode_var, value="bidirectional").pack(side=tk.LEFT, padx=(10, 0))
        
        # 文件过滤
        ttk.Label(parent, text="文件过滤:").grid(row=4, column=0, sticky=tk.NW, pady=2)
        filter_frame = ttk.Frame(parent)
        filter_frame.grid(row=4, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        self.sync_filters_var = tk.StringVar(value="*")
        ttk.Entry(filter_frame, textvariable=self.sync_filters_var, width=40).pack(anchor=tk.W)
        ttk.Label(filter_frame, text="支持通配符，多个模式用分号分隔", font=('Arial', 8)).pack(anchor=tk.W)
        
        # 排除模式
        ttk.Label(parent, text="排除模式:").grid(row=5, column=0, sticky=tk.NW, pady=2)
        exclude_frame = ttk.Frame(parent)
        exclude_frame.grid(row=5, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        self.sync_exclude_var = tk.StringVar()
        ttk.Entry(exclude_frame, textvariable=self.sync_exclude_var, width=40).pack(anchor=tk.W)
        ttk.Label(exclude_frame, text="要排除的文件模式，多个模式用分号分隔", font=('Arial', 8)).pack(anchor=tk.W)
        
        # 选项
        options_frame = ttk.LabelFrame(parent, text="同步选项", padding=5)
        options_frame.grid(row=6, column=0, columnspan=2, sticky=tk.W+tk.E, pady=(10, 0))
        
        self.delete_extra_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="删除本地多余文件", variable=self.delete_extra_var).pack(anchor=tk.W)
        
        self.preserve_timestamps_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="保持文件时间戳", variable=self.preserve_timestamps_var).pack(anchor=tk.W)
        
        self.auto_sync_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="自动同步", variable=self.auto_sync_var).pack(anchor=tk.W)
        
        # 同步间隔
        interval_frame = ttk.Frame(options_frame)
        interval_frame.pack(anchor=tk.W, pady=(5, 0))
        
        ttk.Label(interval_frame, text="同步间隔:").pack(side=tk.LEFT)
        self.sync_interval_var = tk.StringVar(value="300")
        ttk.Entry(interval_frame, textvariable=self.sync_interval_var, width=10).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Label(interval_frame, text="秒").pack(side=tk.LEFT, padx=(2, 0))
        
        # 保存按钮
        save_frame = ttk.Frame(parent)
        save_frame.grid(row=7, column=0, columnspan=2, pady=(20, 0))
        
        ttk.Button(save_frame, text="保存配置", command=self.save_sync_profile).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(save_frame, text="测试同步", command=self.test_sync_profile).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(save_frame, text="立即同步", command=self.execute_sync_profile).pack(side=tk.LEFT)
    
    def show_log_window(self):
        """显示日志窗口"""
        log_window = tk.Toplevel(self.root)
        log_window.title("操作日志")
        log_window.geometry("800x500")
        log_window.transient(self.root)
        
        # 日志文本区域
        log_text = ScrolledText(log_window, wrap=tk.WORD, font=('Consolas', 9))
        log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 填充日志内容
        for message in self.log_messages:
            log_text.insert(tk.END, message + "\n")
        
        log_text.config(state=tk.DISABLED)
        
        # 控制按钮
        btn_frame = ttk.Frame(log_window)
        btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Button(btn_frame, text="清除日志", command=lambda: self.clear_log(log_text)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="保存日志", command=lambda: self.save_log(log_text)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="刷新", command=lambda: self.refresh_log(log_text)).pack(side=tk.LEFT)
    
    def add_log_message(self, message: str, level: str = "INFO"):
        """添加日志消息"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        self.log_messages.append(log_entry)
        
        # 限制日志数量
        if len(self.log_messages) > 1000:
            self.log_messages = self.log_messages[-500:]
    
    def show_help(self):
        """显示帮助窗口"""
        help_window = tk.Toplevel(self.root)
        help_window.title("使用说明")
        help_window.geometry("700x500")
        help_window.transient(self.root)
        
        help_text = ScrolledText(help_window, wrap=tk.WORD, font=('Arial', 10))
        help_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        help_content = """
FTP断点续传下载工具 - 使用说明

=== 基本功能 ===

1. 连接FTP服务器
   - 输入服务器地址、端口、用户名和密码
   - 点击"连接"按钮建立连接
   - 支持匿名登录（用户名留空或输入anonymous）

2. 浏览远程文件
   - 双击目录进入子目录
   - 点击"上级"按钮返回上级目录
   - 点击"刷新"按钮更新文件列表

3. 下载文件
   - 双击文件开始下载
   - 选中文件后点击"下载选中"
   - 点击"下载目录"下载当前目录所有文件

=== 高级功能 ===

1. 断点续传
   - 下载中断后重新开始会自动续传
   - 支持大文件的可靠传输

2. 批量下载
   - 支持多文件同时下载
   - 可设置最大并发数

3. 文件同步
   - 创建同步配置文件
   - 支持定时自动同步
   - 支持双向同步

4. 传输队列
   - 查看所有传输任务
   - 暂停、恢复、取消任务
   - 传输进度和速度监控

=== 快捷键 ===

F5 - 刷新文件列表
Ctrl+D - 下载选中文件
Ctrl+N - 新建连接
Ctrl+Q - 退出程序
Ctrl+L - 显示日志窗口

=== 技巧提示 ===

1. 使用书签保存常用服务器
2. 配置文件过滤器只下载需要的文件
3. 启用自动同步实现文件夹镜像
4. 查看日志了解详细操作信息
        """
        
        help_text.insert(tk.END, help_content)
        help_text.config(state=tk.DISABLED)
    
    def show_about(self):
        """显示关于对话框"""
        about_text = """
FTP断点续传下载工具 v2.0

一个功能强大的FTP客户端，支持：
• 断点续传下载
• 批量文件传输
• 目录同步
• 传输队列管理
• 文件比较和校验

开发者：CodeBuddy
技术支持：基于Python + tkinter
        """
        
        messagebox.showinfo("关于", about_text)
    
    # 实现其他方法的占位符
    def new_connection(self): pass
    def save_session(self): pass
    def load_session(self): pass
    def import_bookmarks(self): pass
    def export_bookmarks(self): pass
    def show_transfer_settings(self): pass
    def pause_all_transfers(self): pass
    def resume_all_transfers(self): pass
    def cancel_all_transfers(self): pass
    def start_sync(self): pass
    def show_sync_history(self): pass
    def compare_files(self): pass
    def batch_rename(self): pass
    def calculate_checksums(self): pass
    def cleanup_temp_files(self): pass
    def show_shortcuts(self): pass
    def populate_queue_tree(self, tree): pass
    def pause_selected_tasks(self, tree): pass
    def resume_selected_tasks(self, tree): pass
    def cancel_selected_tasks(self, tree): pass
    def clear_completed_tasks(self, tree): pass
    def populate_sync_profiles(self, listbox): pass
    def new_sync_profile(self, listbox): pass
    def delete_sync_profile(self, listbox): pass
    def copy_sync_profile(self, listbox): pass
    def browse_sync_local_path(self): pass
    def save_sync_profile(self): pass
    def test_sync_profile(self): pass
    def execute_sync_profile(self): pass
    def clear_log(self, text_widget): pass
    def save_log(self, text_widget): pass
    def refresh_log(self, text_widget): pass
    def load_advanced_config(self): pass

def main():
    """主函数"""
    try:
        app = AdvancedFTPGUI()
        app.run()
    except Exception as e:
        messagebox.showerror("错误", f"程序启动失败:\n{str(e)}")

if __name__ == '__main__':
    main()