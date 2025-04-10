"""
下載位置選擇框架元件

提供下載位置選擇和管理功能
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog
from pathlib import Path
from typing import Callable, Optional


class PathSelectionFrame(ttk.LabelFrame):
    """下載位置選擇框架元件"""
    
    def __init__(self, parent, on_path_change: Optional[Callable] = None, **kwargs):
        """
        初始化下載位置選擇框架
        
        Args:
            parent: 父容器
            on_path_change: 路徑變更時的回調函數
            **kwargs: 傳遞給 LabelFrame 的參數
        """
        super().__init__(parent, text="下載位置", padding="5", **kwargs)
        self.parent = parent
        self.on_path_change = on_path_change
        self.path_var = tk.StringVar(value=str(Path.home() / "Downloads"))
        self.path_var.trace_add("write", self._on_path_changed)
        self.create_widgets()
    
    def create_widgets(self):
        """創建下載位置選擇框架內的元件"""
        # 路徑輸入框
        self.path_entry = ttk.Entry(self, textvariable=self.path_var, width=60)
        self.path_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # 瀏覽按鈕
        self.browse_button = ttk.Button(self, text="瀏覽", command=self.browse_path)
        self.browse_button.grid(row=0, column=1, padx=5)
        
        # 配置 grid 權重
        self.columnconfigure(0, weight=1)
    
    def _on_path_changed(self, *args):
        """路徑變更時的回調函數"""
        if self.on_path_change:
            self.on_path_change(self.path_var.get())
    
    def browse_path(self):
        """瀏覽並選擇下載位置"""
        directory = filedialog.askdirectory(initialdir=self.path_var.get())
        if directory:
            self.path_var.set(directory)
    
    def get_path(self) -> str:
        """獲取當前下載位置"""
        path = self.path_var.get().strip()
        # 確保路徑存在
        os.makedirs(path, exist_ok=True)
        return path
    
    def set_path(self, path: str):
        """設置下載位置"""
        self.path_var.set(path)
