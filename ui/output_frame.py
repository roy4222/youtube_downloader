"""
輸出文本框架元件

提供下載日誌顯示功能
"""

import re
import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, Dict, Any


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
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.progress_callback = progress_callback
        self.create_widgets()
    
    def create_widgets(self):
        """創建輸出文本框架內的元件"""
        # 文本框
        self.output_text = tk.Text(self, height=10, width=80, wrap=tk.WORD)
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 滾動條
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.output_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.output_text.configure(yscrollcommand=scrollbar.set)
        
        # 按鈕框架
        button_frame = ttk.Frame(self)
        button_frame.grid(row=1, column=0, columnspan=2, pady=(5, 0))
        
        # 清除按鈕
        self.clear_button = ttk.Button(button_frame, text="清除日誌", command=self.clear)
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        # 配置 grid 權重
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
    
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
            self.output_text.see(tk.END)
            self.output_text.update()
            
        except Exception as e:
            print(f"Write error: {str(e)}")
            self.output_text.insert(tk.END, text)
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
