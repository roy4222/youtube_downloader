"""
下載格式選擇框架元件

提供下載格式選擇功能
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, Dict, Any, List


class FormatSelectionFrame(ttk.LabelFrame):
    """下載格式選擇框架元件"""
    
    def __init__(self, parent, on_format_change: Optional[Callable] = None, **kwargs):
        """
        初始化下載格式選擇框架
        
        Args:
            parent: 父容器
            on_format_change: 格式變更時的回調函數
            **kwargs: 傳遞給 LabelFrame 的參數
        """
        super().__init__(parent, text="下載格式", padding="5", **kwargs)
        self.parent = parent
        self.on_format_change = on_format_change
        self.format_var = tk.StringVar(value="1")  # 默認為 MP4
        self.format_var.trace_add("write", self._on_format_changed)
        self.create_widgets()
    
    def create_widgets(self):
        """創建下載格式選擇框架內的元件"""
        # MP4 選項
        self.mp4_radio = ttk.Radiobutton(
            self, 
            text="一般版 (MP4 + 音頻)", 
            variable=self.format_var, 
            value="1"
        )
        self.mp4_radio.grid(row=0, column=0, padx=20)
        
        # MP3 選項
        self.mp3_radio = ttk.Radiobutton(
            self, 
            text="純音樂 (MP3)", 
            variable=self.format_var, 
            value="2"
        )
        self.mp3_radio.grid(row=0, column=1, padx=20)
    
    def _on_format_changed(self, *args):
        """格式變更時的回調函數"""
        if self.on_format_change:
            self.on_format_change(self.format_var.get())
    
    def get_format(self) -> str:
        """
        獲取當前選擇的格式
        
        Returns:
            "1" 表示 MP4，"2" 表示 MP3
        """
        return self.format_var.get()
    
    def set_format(self, format_choice: str):
        """
        設置下載格式
        
        Args:
            format_choice: "1" 表示 MP4，"2" 表示 MP3
        """
        self.format_var.set(format_choice)
