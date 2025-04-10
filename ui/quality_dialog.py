"""
畫質選擇對話框元件

提供影片畫質選擇功能
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Any, Optional

from ui.base import BaseDialog


class QualityDialog(BaseDialog):
    """畫質選擇對話框元件"""
    
    def __init__(self, parent, formats: List[Dict[str, Any]], **kwargs):
        """
        初始化畫質選擇對話框
        
        Args:
            parent: 父視窗
            formats: 可用的畫質格式列表
            **kwargs: 傳遞給 BaseDialog 的參數
        """
        self.formats = formats
        self.quality_var = tk.StringVar(value="0")  # 默認選擇最佳畫質
        super().__init__(parent, title="選擇畫質", **kwargs)
    
    def create_widgets(self):
        """創建對話框內的元件"""
        # 標題標籤
        ttk.Label(self.main_frame, text="可用的畫質選項：", font=('', 10, 'bold')).pack(pady=(0, 10))
        
        # 選項框架
        options_frame = ttk.Frame(self.main_frame)
        options_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 添加最佳畫質選項
        ttk.Radiobutton(
            options_frame,
            text="最佳畫質 (自動選擇)",
            variable=self.quality_var,
            value="0"
        ).pack(anchor=tk.W, pady=2)
        
        # 添加分隔線
        ttk.Separator(options_frame, orient='horizontal').pack(fill='x', pady=5)
        
        # 添加其他畫質選項
        for i, fmt in enumerate(self.formats, 1):
            ttk.Radiobutton(
                options_frame,
                text=f"{fmt['quality']} ({fmt['ext']}) - {fmt['filesize_str']}",
                variable=self.quality_var,
                value=str(i)
            ).pack(anchor=tk.W, pady=2)
    
    def ok(self):
        """確定按鈕的回調函數"""
        choice = self.quality_var.get()
        if choice and choice.isdigit():
            choice_idx = int(choice)
            if choice_idx == 0:
                # 最佳畫質 (自動選擇)
                self.result = None
            elif 1 <= choice_idx <= len(self.formats):
                # 特定畫質
                self.result = self.formats[choice_idx - 1]
        
        self.destroy()
    
    def get_selected_format(self) -> Optional[Dict[str, Any]]:
        """
        獲取選擇的畫質格式
        
        Returns:
            選擇的畫質格式，如果選擇「最佳畫質」則返回 None
        """
        return self.result
