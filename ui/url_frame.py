"""
URL 輸入框架元件

提供 URL 輸入和處理功能
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional

from core.url_utils import clean_url, detect_platform
try:
    from ui.theme import ThemeManager
except ImportError:
    # 如果主題管理器不可用，使用空的類別
    class ThemeManager:
        PADDING = {'small': 5, 'medium': 10, 'large': 15}
        COLORS = {'primary': '#3498db', 'secondary': '#2ecc71', 'accent': '#e74c3c'}


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
        # 設置默認樣式
        kwargs.setdefault('padding', ThemeManager.PADDING['medium'])
        
        super().__init__(parent, text="影片網址 (支援 YouTube 和 Bilibili)", **kwargs)
        self.parent = parent
        self.on_url_change = on_url_change
        self.url_var = tk.StringVar()
        self.url_var.trace_add("write", self._on_url_changed)
        self.create_widgets()
    
    def create_widgets(self):
        """創建 URL 輸入框架內的元件"""
        # 創建主容器框架
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=ThemeManager.PADDING['small'], 
                        pady=ThemeManager.PADDING['small'])
        
        # URL 輸入框
        self.url_entry = ttk.Entry(main_frame, textvariable=self.url_var, width=70)
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, 
                           padx=ThemeManager.PADDING['small'])
        
        # 按鈕框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(side=tk.RIGHT, padx=ThemeManager.PADDING['small'])
        
        # 貼上按鈕
        self.paste_button = ttk.Button(
            button_frame, 
            text="貼上", 
            command=self.paste_url,
            style=ThemeManager.get_button_style('primary')
        )
        self.paste_button.pack(side=tk.LEFT, padx=ThemeManager.PADDING['small'])
        
        # 清除按鈕
        self.clear_button = ttk.Button(
            button_frame, 
            text="清除", 
            command=self.clear_url
        )
        self.clear_button.pack(side=tk.LEFT, padx=ThemeManager.PADDING['small'])
        
        # 平台標籤
        self.platform_var = tk.StringVar()
        self.platform_label = ttk.Label(
            self, 
            textvariable=self.platform_var,
            foreground=ThemeManager.COLORS['primary'] if hasattr(ThemeManager, 'COLORS') else '#3498db',
            font=('Microsoft JhengHei UI', 9, 'italic')
        )
        self.platform_label.pack(side=tk.LEFT, padx=ThemeManager.PADDING['medium'], 
                                pady=(0, ThemeManager.PADDING['small']))
    
    def _on_url_changed(self, *args):
        """URL 變更時的回調函數"""
        url = self.url_var.get().strip()
        
        # 更新平台標籤
        if url:
            platform = detect_platform(url)
            if platform != "unknown":
                self.platform_var.set(f"平台: {platform.capitalize()}")
            else:
                self.platform_var.set("未知平台")
        else:
            self.platform_var.set("")
        
        if self.on_url_change:
            self.on_url_change(url)
    
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
