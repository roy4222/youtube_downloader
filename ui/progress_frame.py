"""
下載進度顯示框架元件

提供下載進度顯示和管理功能
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional


class ProgressFrame(ttk.LabelFrame):
    """下載進度顯示框架元件"""
    
    def __init__(self, parent, **kwargs):
        """
        初始化下載進度顯示框架
        
        Args:
            parent: 父容器
            **kwargs: 傳遞給 LabelFrame 的參數
        """
        super().__init__(parent, text="下載進度", padding="5", **kwargs)
        self.parent = parent
        self.progress_var = tk.DoubleVar()
        self.create_widgets()
    
    def create_widgets(self):
        """創建下載進度顯示框架內的元件"""
        # 進度條
        self.progress_bar = ttk.Progressbar(
            self,
            variable=self.progress_var,
            mode='determinate',
            length=400
        )
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # 進度標籤
        self.progress_label = ttk.Label(self, text="準備下載...")
        self.progress_label.grid(row=1, column=0, sticky=(tk.W), padx=5, pady=2)
        
        # 速度標籤
        self.speed_label = ttk.Label(self, text="")
        self.speed_label.grid(row=2, column=0, sticky=(tk.W), padx=5, pady=2)
        
        # 配置 grid 權重
        self.columnconfigure(0, weight=1)
    
    def update_progress(self, percentage: float, speed: float = 0):
        """
        更新下載進度和速度
        
        Args:
            percentage: 進度百分比 (0-100)
            speed: 下載速度 (bytes/s)
        """
        self.progress_var.set(percentage)
        speed_text = f"下載速度: {speed/1024/1024:.1f} MB/s" if speed > 0 else ""
        self.progress_label.config(text=f"下載進度: {percentage:.1f}%")
        self.speed_label.config(text=speed_text)
        self.update()
    
    def update_status(self, status: str):
        """
        更新狀態文本
        
        Args:
            status: 狀態文本
        """
        self.progress_label.config(text=status)
        self.update()
    
    def reset(self):
        """重置進度顯示"""
        self.progress_var.set(0)
        self.progress_label.config(text="準備下載...")
        self.speed_label.config(text="")
        self.update()
