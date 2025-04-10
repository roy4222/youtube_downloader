"""
基礎 UI 元件模組

提供所有 UI 元件的基礎類別和共用功能
"""

import tkinter as tk
from tkinter import ttk
from abc import ABC, abstractmethod
from typing import Optional, Callable, Any, Dict

try:
    from ui.theme import ThemeManager
except ImportError:
    # 如果主題管理器不可用，使用空的類別
    class ThemeManager:
        PADDING = {'small': 5, 'medium': 10, 'large': 15}
        
        @classmethod
        def get_button_style(cls, button_type='default'):
            return 'TButton'
        
        @classmethod
        def get_label_style(cls, label_type='default'):
            return 'TLabel'
        
        @classmethod
        def apply_modern_widget_style(cls, widget):
            pass


class BaseFrame(ttk.Frame):
    """UI 元件的基礎框架類別"""
    
    def __init__(self, parent, **kwargs):
        """
        初始化基礎框架
        
        Args:
            parent: 父容器
            **kwargs: 傳遞給 ttk.Frame 的參數
        """
        # 設置默認樣式
        kwargs.setdefault('padding', ThemeManager.PADDING['medium'])
        kwargs.setdefault('style', 'TFrame')
        
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.create_widgets()
        
    @abstractmethod
    def create_widgets(self):
        """創建框架內的元件，子類必須實現此方法"""
        pass
    
    def update_ui(self):
        """更新 UI 狀態，可由子類覆寫"""
        pass
    
    def create_label(self, parent, text, style='default', **kwargs):
        """創建帶有主題樣式的標籤"""
        label = ttk.Label(
            parent, 
            text=text, 
            style=ThemeManager.get_label_style(style),
            **kwargs
        )
        return label
    
    def create_button(self, parent, text, command=None, style='default', **kwargs):
        """創建帶有主題樣式的按鈕"""
        button = ttk.Button(
            parent, 
            text=text, 
            command=command, 
            style=ThemeManager.get_button_style(style),
            **kwargs
        )
        return button
    
    def create_entry(self, parent, **kwargs):
        """創建帶有主題樣式的輸入框"""
        entry = ttk.Entry(parent, **kwargs)
        return entry
    
    def create_text(self, parent, **kwargs):
        """創建帶有主題樣式的文本框"""
        text = tk.Text(parent, **kwargs)
        ThemeManager.apply_modern_widget_style(text)
        return text


class BaseDialog(tk.Toplevel):
    """對話框的基礎類別"""
    
    def __init__(self, parent, title="對話框", **kwargs):
        """
        初始化基礎對話框
        
        Args:
            parent: 父視窗
            title: 對話框標題
            **kwargs: 傳遞給 Toplevel 的參數
        """
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.title(title)
        self.result = None
        
        # 設置為模態對話框
        self.transient(parent)
        self.grab_set()
        
        # 設置對話框樣式
        self.configure(background=ThemeManager.COLORS['background'] if hasattr(ThemeManager, 'COLORS') else '#f5f5f5')
        
        # 創建主框架
        self.main_frame = ttk.Frame(self, padding=ThemeManager.PADDING['medium'])
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 創建元件
        self.create_widgets()
        
        # 創建按鈕
        self.create_buttons()
        
        # 綁定事件
        self.bind("<Escape>", lambda e: self.cancel())
        
        # 設置焦點
        self.set_focus()
        
        # 調整大小
        self.adjust_size()
    
    @abstractmethod
    def create_widgets(self):
        """創建對話框內的元件，子類必須實現此方法"""
        pass
    
    def create_buttons(self):
        """創建確定和取消按鈕"""
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, pady=(ThemeManager.PADDING['medium'], 0))
        
        cancel_button = ttk.Button(
            button_frame, 
            text="取消", 
            command=self.cancel,
            style=ThemeManager.get_button_style()
        )
        cancel_button.pack(side=tk.RIGHT, padx=ThemeManager.PADDING['small'])
        
        ok_button = ttk.Button(
            button_frame, 
            text="確定", 
            command=self.ok,
            style=ThemeManager.get_button_style('primary')
        )
        ok_button.pack(side=tk.RIGHT, padx=ThemeManager.PADDING['small'])
        
        # 綁定回車鍵到確定按鈕
        self.bind("<Return>", lambda e: ok_button.invoke())
    
    def set_focus(self):
        """設置初始焦點，可由子類覆寫"""
        self.focus_set()
    
    def adjust_size(self):
        """調整對話框大小以適應內容"""
        self.update_idletasks()
        width = self.winfo_reqwidth() + 20
        height = self.winfo_reqheight() + 20
        self.geometry(f"{width}x{height}")
        
        # 居中顯示
        x = self.parent.winfo_rootx() + (self.parent.winfo_width() - width) // 2
        y = self.parent.winfo_rooty() + (self.parent.winfo_height() - height) // 2
        self.geometry(f"+{x}+{y}")
    
    def ok(self):
        """確定按鈕的回調函數，可由子類覆寫"""
        self.destroy()
    
    def cancel(self):
        """取消按鈕的回調函數"""
        self.result = None
        self.destroy()
    
    def wait_for_result(self):
        """等待對話框結果"""
        self.wait_window()
        return self.result
    
    def create_label(self, parent, text, style='default', **kwargs):
        """創建帶有主題樣式的標籤"""
        label = ttk.Label(
            parent, 
            text=text, 
            style=ThemeManager.get_label_style(style),
            **kwargs
        )
        return label
    
    def create_button(self, parent, text, command=None, style='default', **kwargs):
        """創建帶有主題樣式的按鈕"""
        button = ttk.Button(
            parent, 
            text=text, 
            command=command, 
            style=ThemeManager.get_button_style(style),
            **kwargs
        )
        return button
