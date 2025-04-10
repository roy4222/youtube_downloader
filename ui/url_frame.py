"""
URL 輸入框架元件

提供 URL 輸入和處理功能
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional

from core.url_utils import clean_url, detect_platform


class UrlInputFrame(ttk.LabelFrame):
    """URL 輸入框架元件"""
    
    def __init__(self, parent, on_url_change: Optional[Callable] = None, **kwargs):
        """
        初始化 URL 輸入框架
        
        Args:
            parent: 父容器
            on_url_change: URL 變更時的回調函數
            **kwargs: 傳遞給 LabelFrame 的參數
        """
        super().__init__(parent, text="影片網址 (支援 YouTube 和 Bilibili)", padding="5", **kwargs)
        self.parent = parent
        self.on_url_change = on_url_change
        self.url_var = tk.StringVar()
        self.url_var.trace_add("write", self._on_url_changed)
        self.create_widgets()
    
    def create_widgets(self):
        """創建 URL 輸入框架內的元件"""
        # URL 輸入框
        self.url_entry = ttk.Entry(self, textvariable=self.url_var, width=70)
        self.url_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # 貼上按鈕
        self.paste_button = ttk.Button(self, text="貼上", command=self.paste_url)
        self.paste_button.grid(row=0, column=1, padx=5)
        
        # 清除按鈕
        self.clear_button = ttk.Button(self, text="清除", command=self.clear_url)
        self.clear_button.grid(row=0, column=2, padx=5)
        
        # 配置 grid 權重
        self.columnconfigure(0, weight=1)
    
    def _on_url_changed(self, *args):
        """URL 變更時的回調函數"""
        if self.on_url_change:
            self.on_url_change(self.url_var.get())
    
    def paste_url(self):
        """從剪貼簿貼上 URL"""
        try:
            url = self.winfo_toplevel().clipboard_get()
            
            # 處理可能包含標題的 URL
            if "youtube.com" in url or "youtu.be" in url or "bilibili.com" in url or "b23.tv" in url:
                # 提取真正的 URL
                original_url = url
                url = clean_url(url)
                
                if url != original_url:
                    print(f"已清理 URL: {url}")
                
                self.url_var.set(url)
                print("URL 已貼上並處理完成")
                
                # 檢測平台
                platform = detect_platform(url)
                if platform != "unknown":
                    print(f"檢測到平台: {platform.capitalize()}")
        except Exception as e:
            print(f"貼上 URL 時出錯: {str(e)}")
    
    def clear_url(self):
        """清除 URL"""
        self.url_var.set("")
    
    def get_url(self) -> str:
        """獲取當前 URL"""
        return self.url_var.get().strip()
    
    def set_url(self, url: str):
        """設置 URL"""
        self.url_var.set(url)
    
    def focus(self):
        """設置焦點到 URL 輸入框"""
        self.url_entry.focus_set()
