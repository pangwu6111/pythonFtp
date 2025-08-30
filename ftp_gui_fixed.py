#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FTP断点续传下载工具 - 修复版GUI
修复了所有已知的错误和兼容性问题
"""

import os
import sys
import time
import ftplib
import threading
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

class FTPClientGUI:
    """FTP客户端GUI - 修复版"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("FTP下载工具 v1.1")
        self.root.geometry("1000x700")
        
        # FTP连接
        self.ftp = None
        self.connected = False
        self.current_path = "/"
        
        # 下载任务
        self.download_tasks = []
        self.downloading = False
        
        # 创建界面
        self.create_widgets()
        
        # 定时更新
        self.update_ui()
    
    def create_widgets(self):
        """创建界面组件"""
        # 连接区域
        conn_frame = ttk.LabelFrame(self.root, text="FTP连接", padding=10)
        conn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 连接参数 - 使用grid布局
        params_frame = ttk.Frame(conn_frame)
        params_frame.pack(fill=tk.X)
        
        ttk.Label(params_frame, text="服务器:").grid(row=0, column=0, padx=5, sticky=tk.W)
        self.host_var = tk.StringVar()
        ttk.Entry(params_frame, textvariable=self.host_var, width=20).grid(row=0, column=1, padx=5)
        
        ttk.Label(params_frame, text="端口:").grid(row=0, column=2, padx=5, sticky=tk.W)
        self.port_var = tk.StringVar(value="21")
        ttk.Entry(params_frame, textvariable=self.port_var, width=8).grid(row=0, column=3, padx=5)
        
        ttk.Label(params_frame, text="用户名:").grid(row=0, column=4, padx=5, sticky=tk.W)
        self.username_var = tk.StringVar(value="anonymous")
        ttk.Entry(params_frame, textvariable=self.username_var, width=15).grid(row=0, column=5, padx=5)
        
        ttk.Label(params_frame, text="密码:").grid(row=0, column=6, padx=5, sticky=tk.W)
        self.password_var = tk.StringVar()
        ttk.Entry(params_frame, textvariable=self.password_var, show="*", width=15).grid(row=0, column=7, padx=5)
        
        self.connect_btn = ttk.Button(params_frame, text="连接", command=self.connect)
        self.connect_btn.grid(row=0, column=8, padx=5)
        
        # 快速连接
        quick_frame = ttk.Frame(conn_frame)
        quick_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(quick_frame, text="快速连接:").pack(side=tk.LEFT)
        ttk.Button(quick_frame, text="GNU FTP", 
                  command=lambda: self.quick_connect("ftp.gnu.org", "21", "anonymous", "")).pack(side=tk.LEFT, padx=5)
        
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
    
    def create_file_browser(self, parent):
        """创建文件浏览器"""
        # 路径栏
        path_frame = ttk.Frame(parent)
        path_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(path_frame, text="路径:").pack(side=tk.LEFT)
        self.path_var = tk.StringVar(value="/")
        path_entry = ttk.Entry(path_frame, textvariable=self.path_var, state="readonly")
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        ttk.Button(path_frame, text="上级", command=self.go_up).pack(side=tk.RIGHT, padx=2)
        ttk.Button(path_frame, text="刷新", command=self.refresh).pack(side=tk.RIGHT, padx=2)
        
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
    
    def quick_connect(self, host, port, username, password):
        """快速连接"""
        self.host_var.set(host)
        self.port_var.set(port)
        self.username_var.set(username)
        self.password_var.set(password)
        self.connect()
    
    def connect(self):
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
                # 创建FTP连接
                ftp = ftplib.FTP()
                ftp.connect(host, port, 30)
                ftp.login(username, password)
                ftp.set_pasv(True)
                
                # 获取当前路径
                current_path = ftp.pwd()
                
                # 连接成功，更新界面
                self.root.after(0, lambda: self.on_connect_success(ftp, current_path))
                
            except Exception as e:
                error_msg = str(e)
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
        self.refresh()
    
    def on_connect_error(self, error_msg):
        """连接失败回调"""
        self.status_var.set("连接失败")
        self.connect_btn.config(state=tk.NORMAL)
        messagebox.showerror("连接失败", f"无法连接到FTP服务器:\n{error_msg}")
    
    def disconnect(self):
        """断开连接"""
        if self.ftp:
            try:
                self.ftp.quit()
            except:
                pass
            self.ftp = None
        
        self.connected = False
        self.status_var.set("已断开连接")
        self.connect_btn.config(text="连接", command=self.connect)
        
        # 清空文件列表
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
    
    def refresh(self):
        """刷新文件列表"""
        if not self.connected or not self.ftp:
            return
        
        self.status_var.set("正在获取文件列表...")
        
        def refresh_thread():
            try:
                files = []
                self.ftp.retrlines('LIST', files.append)
                self.root.after(0, lambda: self.update_file_list(files))
            except Exception as e:
                error_msg = str(e)
                self.root.after(0, lambda: self.on_refresh_error(error_msg))
        
        threading.Thread(target=refresh_thread, daemon=True).start()
    
    def update_file_list(self, files):
        """更新文件列表"""
        # 清空现有列表
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        
        # 解析文件信息
        for line in files:
            try:
                parts = line.split()
                if len(parts) < 9:
                    continue
                
                permissions = parts[0]
                is_dir = permissions.startswith('d')
                
                try:
                    size = int(parts[4]) if not is_dir else 0
                except (ValueError, IndexError):
                    size = 0
                
                filename = ' '.join(parts[8:])
                if filename in ['.', '..']:
                    continue
                
                size_str = self.format_size(size) if not is_dir else ""
                type_str = "目录" if is_dir else "文件"
                date_str = f"{parts[5]} {parts[6]} {parts[7]}" if len(parts) >= 8 else ""
                
                icon = "📁" if is_dir else "📄"
                
                self.file_tree.insert("", tk.END, 
                                    text=f"{icon} {filename}",
                                    values=(size_str, type_str, date_str),
                                    tags=("directory" if is_dir else "file",))
            except Exception as e:
                print(f"解析文件行失败: {line} - {e}")
                continue
        
        self.path_var.set(self.current_path)
        file_count = len(self.file_tree.get_children())
        self.status_var.set(f"找到 {file_count} 个项目")
    
    def on_refresh_error(self, error_msg):
        """刷新失败回调"""
        self.status_var.set("获取文件列表失败")
        messagebox.showerror("错误", f"获取文件列表失败:\n{error_msg}")
    
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
            return
        
        try:
            if dirname == "..":
                # 返回上级目录
                if self.current_path != "/":
                    parent = str(Path(self.current_path).parent)
                    if parent == "." or parent == "":
                        parent = "/"
                    self.ftp.cwd(parent)
            else:
                # 进入子目录
                new_path = self.current_path
                if new_path.endswith('/'):
                    new_path += dirname
                else:
                    new_path += '/' + dirname
                self.ftp.cwd(new_path)
            
            self.current_path = self.ftp.pwd()
            self.refresh()
        except Exception as e:
            messagebox.showerror("错误", f"无法进入目录: {dirname}\n{str(e)}")
    
    def go_up(self):
        """返回上级目录"""
        self.change_directory("..")
    
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
            except:
                size = 0
        
        task = DownloadTask(remote_path, str(local_path), size)
        self.download_tasks.append(task)
        
        self.status_var.set(f"已添加下载任务: {filename}")
    
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
        threading.Thread(target=self.download_worker, daemon=True).start()
    
    def pause_downloads(self):
        """暂停下载"""
        self.downloading = False
        self.status_var.set("下载已暂停")
    
    def clear_downloads(self):
        """清除下载列表"""
        if self.downloading:
            result = messagebox.askyesno("确认", "下载正在进行中，是否强制清除？")
            if not result:
                return
            self.downloading = False
        
        self.download_tasks.clear()
        self.status_var.set("已清除下载列表")
    
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
                print(f"下载失败: {task.remote_path} - {e}")
        
        self.downloading = False
        self.root.after(0, lambda: self.status_var.set("下载完成"))
    
    def download_file(self, task):
        """下载单个文件"""
        task.status = "下载中"
        task.start_time = time.time()
        
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
                return
            elif local_size > task.size and task.size > 0:
                local_path.unlink()
                local_size = 0
        
        task.downloaded = local_size
        
        # 创建新的FTP连接用于下载
        try:
            ftp = ftplib.FTP()
            ftp.connect(self.host_var.get(), int(self.port_var.get()), 30)
            ftp.login(self.username_var.get(), self.password_var.get())
            ftp.set_pasv(True)
            
            # 设置断点续传
            if local_size > 0:
                ftp.sendcmd(f'REST {local_size}')
            
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
            else:
                task.status = "失败"
                task.error_msg = "下载不完整"
                
        except Exception as e:
            task.status = "失败"
            task.error_msg = str(e)
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
        app = FTPClientGUI()
        app.run()
    except Exception as e:
        print(f"程序启动失败: {e}")
        if 'messagebox' in globals():
            messagebox.showerror("错误", f"程序启动失败:\n{str(e)}")

if __name__ == '__main__':
    main()