"""
下載進度顯示框架元件

提供下載進度顯示和管理功能
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

try:
    from ui.theme import ThemeManager
except ImportError:
    # 如果主題管理器不可用，使用空的類別
    class ThemeManager:
        PADDING = {'small': 5, 'medium': 10, 'large': 15}
        COLORS = {
            'primary': '#3498db',
            'secondary': '#2ecc71',
            'accent': '#e74c3c'
        }


class ProgressFrame(ttk.LabelFrame):
    """下載進度顯示框架元件"""
    
    def __init__(self, parent, **kwargs):
        """
        初始化下載進度顯示框架
        
        Args:
            parent: 父容器
            **kwargs: 傳遞給 LabelFrame 的參數
        """
        # 設置默認樣式
        kwargs.setdefault('padding', ThemeManager.PADDING['medium'])
        
        super().__init__(parent, text="下載進度", **kwargs)
        self.parent = parent
        self.progress_var = tk.DoubleVar()
        self.create_widgets()
    
    def create_widgets(self):
        """創建下載進度顯示框架內的元件"""
        # 創建主容器
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=ThemeManager.PADDING['small'], 
                        pady=ThemeManager.PADDING['small'])
        
        # 進度條
        self.progress_bar = ttk.Progressbar(
            main_frame,
            variable=self.progress_var,
            mode='determinate',
            length=400,
            style='TProgressbar'
        )
        self.progress_bar.pack(fill=tk.X, padx=ThemeManager.PADDING['small'], 
                              pady=ThemeManager.PADDING['small'])
        
        # 信息框架
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, padx=ThemeManager.PADDING['small'])
        
        # 進度標籤
        self.progress_label = ttk.Label(
            info_frame, 
            text="準備下載...",
            foreground=ThemeManager.COLORS['primary'] if hasattr(ThemeManager, 'COLORS') else '#3498db',
            font=('Microsoft JhengHei UI', 9, 'bold')
        )
        self.progress_label.pack(side=tk.LEFT, pady=ThemeManager.PADDING['small'])
        
        # 速度標籤
        self.speed_label = ttk.Label(
            info_frame, 
            text="",
            foreground=ThemeManager.COLORS['secondary'] if hasattr(ThemeManager, 'COLORS') else '#2ecc71'
        )
        self.speed_label.pack(side=tk.RIGHT, pady=ThemeManager.PADDING['small'])
        
        # 額外信息標籤
        self.info_label = ttk.Label(main_frame, text="")
        self.info_label.pack(side=tk.LEFT, pady=(0, ThemeManager.PADDING['small']))
    
    def update_progress(self, percentage: float, speed: float = 0):
        """
        更新下載進度
        
        Args:
            percentage: 進度百分比 (0-100)
            speed: 下載速度 (KB/s)
        """
        # 更新進度條
        self.progress_var.set(percentage)
        
        # 更新進度標籤
        self.progress_label.configure(text=f"下載進度: {percentage:.1f}%")
        
        # 更新速度標籤
        if speed > 0:
            if speed >= 1024:
                self.speed_label.configure(text=f"速度: {speed/1024:.2f} MB/s")
            else:
                self.speed_label.configure(text=f"速度: {speed:.2f} KB/s")
    
    def set_status(self, status: str):
        """
        設置狀態信息
        
        Args:
            status: 狀態信息
        """
        self.info_label.configure(text=status)
    
    def reset(self):
        """重置進度條和標籤"""
        self.progress_var.set(0)
        self.progress_label.configure(text="準備下載...")
        self.speed_label.configure(text="")
        self.info_label.configure(text="")
