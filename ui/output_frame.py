"""
輸出文本框架元件

提供下載日誌顯示功能
"""

import re
import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, Dict, Any

try:
    from ui.theme import ThemeManager
except ImportError:
    # 如果主題管理器不可用，使用空的類別
    class ThemeManager:
        PADDING = {'small': 5, 'medium': 10, 'large': 15}
        COLORS = {
            'primary': '#3498db',
            'secondary': '#2ecc71',
            'accent': '#e74c3c',
            'success': '#27ae60',
            'warning': '#f39c12',
            'error': '#c0392b'
        }
        
        @classmethod
        def apply_modern_widget_style(cls, widget):
            pass


class OutputFrame(ttk.Frame):
    """輸出文本框架元件"""
    
    def __init__(self, parent, progress_callback: Optional[Callable] = None, **kwargs):
        """
        初始化輸出文本框架
        
        Args:
            parent: 父容器
            progress_callback: 進度更新回調函數
            **kwargs: 傳遞給 Frame 的參數
        """
        # 設置默認樣式
        kwargs.setdefault('padding', ThemeManager.PADDING['medium'])
        
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.progress_callback = progress_callback
        self.create_widgets()
    
    def create_widgets(self):
        """創建輸出文本框架內的元件"""
        # 創建標題標籤
        title_label = ttk.Label(
            self, 
            text="下載日誌", 
            font=('Microsoft JhengHei UI', 11, 'bold'),
            foreground=ThemeManager.COLORS['primary'] if hasattr(ThemeManager, 'COLORS') else '#3498db'
        )
        title_label.pack(side=tk.TOP, anchor=tk.W, padx=ThemeManager.PADDING['small'], 
                        pady=(0, ThemeManager.PADDING['small']))
        
        # 創建文本框容器
        text_container = ttk.Frame(self, borderwidth=1, relief="solid")
        text_container.pack(fill=tk.BOTH, expand=True)
        
        # 文本框
        self.output_text = tk.Text(
            text_container, 
            height=10, 
            width=80, 
            wrap=tk.WORD,
            font=('Consolas', 9),
            bg='#fafafa',
            fg='#333333',
            padx=ThemeManager.PADDING['small'],
            pady=ThemeManager.PADDING['small'],
            borderwidth=0
        )
        self.output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 設置標籤顏色
        self.output_text.tag_configure(
            'info', 
            foreground=ThemeManager.COLORS['primary'] if hasattr(ThemeManager, 'COLORS') else '#3498db'
        )
        self.output_text.tag_configure(
            'success', 
            foreground=ThemeManager.COLORS['success'] if hasattr(ThemeManager, 'COLORS') else '#27ae60'
        )
        self.output_text.tag_configure(
            'warning', 
            foreground=ThemeManager.COLORS['warning'] if hasattr(ThemeManager, 'COLORS') else '#f39c12'
        )
        self.output_text.tag_configure(
            'error', 
            foreground=ThemeManager.COLORS['error'] if hasattr(ThemeManager, 'COLORS') else '#c0392b'
        )
        self.output_text.tag_configure(
            'bold', 
            font=('Consolas', 9, 'bold')
        )
        
        # 滾動條
        scrollbar = ttk.Scrollbar(text_container, orient="vertical", command=self.output_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.output_text.configure(yscrollcommand=scrollbar.set)
        
        # 按鈕框架
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, pady=ThemeManager.PADDING['small'])
        
        # 清除按鈕
        self.clear_button = ttk.Button(
            button_frame, 
            text="清除日誌", 
            command=self.clear
        )
        self.clear_button.pack(side=tk.LEFT, padx=ThemeManager.PADDING['small'])
        
        # 自動滾動選項
        self.autoscroll_var = tk.BooleanVar(value=True)
        self.autoscroll_check = ttk.Checkbutton(
            button_frame, 
            text="自動滾動", 
            variable=self.autoscroll_var
        )
        self.autoscroll_check.pack(side=tk.RIGHT, padx=ThemeManager.PADDING['small'])
    
    def write(self, text: str):
        """
        寫入文本到輸出框
        
        Args:
            text: 要寫入的文本
        """
        try:
            # 處理 aria2c 的進度
            if "[#" in text and "CN:" in text and "DL:" in text:
                self._parse_aria2c_progress(text)
            
            # 處理 yt-dlp 的進度
            elif "[download]" in text and "%" in text:
                self._parse_ytdlp_progress(text)
            
            # 將文本添加到輸出框
            self.output_text.insert(tk.END, text)
            if self.autoscroll_var.get():
                self.output_text.see(tk.END)
            self.output_text.update()
            
        except Exception as e:
            print(f"Write error: {str(e)}")
            self.output_text.insert(tk.END, text)
            if self.autoscroll_var.get():
                self.output_text.see(tk.END)
            self.output_text.update()
    
    def _parse_aria2c_progress(self, text: str):
        """
        解析 aria2c 的進度信息
        
        Args:
            text: aria2c 輸出的文本
        """
        try:
            progress_match = re.search(r'\((\d+)%\)', text)
            speed_match = re.search(r'DL:(\d+\.?\d*)(\w+)', text)
            
            if progress_match and self.progress_callback:
                percentage = float(progress_match.group(1))
                
                speed_val = 0
                if speed_match:
                    speed_val = float(speed_match.group(1))
                    speed_unit = speed_match.group(2)
                    
                    # 轉換為 bytes/s
                    if speed_unit == 'GiB':
                        speed_val = speed_val * 1024 * 1024 * 1024
                    elif speed_unit == 'MiB':
                        speed_val = speed_val * 1024 * 1024
                    elif speed_unit == 'KiB':
                        speed_val = speed_val * 1024
                    
                self.progress_callback(percentage, speed_val)
        except Exception as e:
            print(f"Progress parsing error: {str(e)}")
    
    def _parse_ytdlp_progress(self, text: str):
        """
        解析 yt-dlp 的進度信息
        
        Args:
            text: yt-dlp 輸出的文本
        """
        try:
            # 解析進度信息
            parts = text.split()
            for part in parts:
                if "%" in part and self.progress_callback:
                    percentage = float(part.replace("%", ""))
                    
                    # 查找速度
                    speed_val = 0
                    if "at" in parts and parts.index(part) < len(parts) - 2:
                        at_index = parts.index("at")
                        if at_index + 1 < len(parts):
                            speed = parts[at_index + 1]
                            if speed.endswith("/s"):
                                if speed.endswith("KiB/s"):
                                    speed_val = float(speed[:-5]) * 1024
                                elif speed.endswith("MiB/s"):
                                    speed_val = float(speed[:-5]) * 1024 * 1024
                                elif speed.endswith("GiB/s"):
                                    speed_val = float(speed[:-5]) * 1024 * 1024 * 1024
                                else:
                                    speed_val = float(speed[:-2])
                    
                    self.progress_callback(percentage, speed_val)
                    break
        except Exception as e:
            print(f"Progress parsing error: {str(e)}")
    
    def clear(self):
        """清除輸出文本"""
        self.output_text.delete(1.0, tk.END)
    
    def flush(self):
        """實現 file-like 對象的 flush 方法"""
        pass
