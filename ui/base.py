"""
基礎 UI 元件模組

提供所有 UI 元件的基礎類別和共用功能
"""

import tkinter as tk
from tkinter import ttk
from abc import ABC, abstractmethod
from typing import Optional, Callable, Any, Dict


class BaseFrame(ttk.Frame):
    """UI 元件的基礎框架類別"""
    
    def __init__(self, parent, **kwargs):
        """
        初始化基礎框架
        
        Args:
            parent: 父容器
            **kwargs: 傳遞給 ttk.Frame 的參數
        """
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
        
        # 創建主框架
        self.main_frame = ttk.Frame(self, padding="10")
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
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        cancel_button = ttk.Button(button_frame, text="取消", command=self.cancel)
        cancel_button.pack(side=tk.RIGHT, padx=5)
        
        ok_button = ttk.Button(button_frame, text="確定", command=self.ok)
        ok_button.pack(side=tk.RIGHT, padx=5)
        
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
