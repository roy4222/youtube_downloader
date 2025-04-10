"""
UI 主題管理模組

提供應用程式的主題設定和樣式管理
"""

import tkinter as tk
from tkinter import ttk
import os
import platform

class ThemeManager:
    """主題管理器，提供應用程式的主題設定和樣式管理"""
    
    # 預設顏色方案
    COLORS = {
        'primary': '#3498db',      # 主要顏色 (藍色)
        'secondary': '#2ecc71',    # 次要顏色 (綠色)
        'accent': '#e74c3c',       # 強調顏色 (紅色)
        'background': '#f5f5f5',   # 背景顏色 (淺灰)
        'text': '#333333',         # 文字顏色 (深灰)
        'light_text': '#7f8c8d',   # 淺色文字 (中灰)
        'border': '#bdc3c7',       # 邊框顏色 (灰色)
        'hover': '#2980b9',        # 懸停顏色 (深藍)
        'success': '#27ae60',      # 成功顏色 (綠色)
        'warning': '#f39c12',      # 警告顏色 (橙色)
        'error': '#c0392b',        # 錯誤顏色 (深紅)
        'disabled': '#95a5a6'      # 禁用顏色 (灰色)
    }
    
    # 字體設定
    FONTS = {
        'default': ('Microsoft JhengHei UI', 10),  # 預設字體
        'title': ('Microsoft JhengHei UI', 12, 'bold'),  # 標題字體
        'header': ('Microsoft JhengHei UI', 11, 'bold'),  # 標頭字體
        'small': ('Microsoft JhengHei UI', 9),  # 小型字體
        'monospace': ('Consolas', 9)  # 等寬字體 (用於輸出)
    }
    
    # 間距設定
    PADDING = {
        'small': 5,    # 小間距
        'medium': 10,  # 中間距
        'large': 15    # 大間距
    }
    
    # 圓角設定
    CORNER_RADIUS = 4
    
    @classmethod
    def setup_theme(cls, root):
        """設置應用程式主題"""
        cls._setup_system_theme(root)
        cls._create_custom_styles()
    
    @classmethod
    def _setup_system_theme(cls, root):
        """設置系統主題 (如果可用)"""
        try:
            # 嘗試使用 sv_ttk (Sun Valley 主題)
            import sv_ttk
            sv_ttk.set_theme("light")
            return
        except ImportError:
            pass
        
        # 如果沒有 sv_ttk，使用內建主題
        style = ttk.Style(root)
        
        # 在 Windows 上使用 'vista' 主題
        if platform.system() == 'Windows':
            style.theme_use('vista')
        # 在 macOS 上使用 'aqua' 主題
        elif platform.system() == 'Darwin':
            style.theme_use('aqua')
        # 在 Linux 上使用 'clam' 主題
        else:
            style.theme_use('clam')
    
    @classmethod
    def _create_custom_styles(cls):
        """創建自定義樣式"""
        style = ttk.Style()
        
        # 設置 LabelFrame 樣式
        style.configure(
            'TLabelframe', 
            background=cls.COLORS['background'],
            borderwidth=1,
            relief='solid'
        )
        style.configure(
            'TLabelframe.Label', 
            font=cls.FONTS['header'],
            foreground=cls.COLORS['primary'],
            background=cls.COLORS['background']
        )
        
        # 設置 Frame 樣式
        style.configure(
            'TFrame', 
            background=cls.COLORS['background']
        )
        
        # 設置 Label 樣式
        style.configure(
            'TLabel', 
            font=cls.FONTS['default'],
            background=cls.COLORS['background'],
            foreground=cls.COLORS['text']
        )
        style.configure(
            'Title.TLabel', 
            font=cls.FONTS['title'],
            foreground=cls.COLORS['primary']
        )
        style.configure(
            'Subtitle.TLabel', 
            font=cls.FONTS['header'],
            foreground=cls.COLORS['secondary']
        )
        
        # 設置 Button 樣式
        style.configure(
            'TButton', 
            font=cls.FONTS['default'],
            padding=(cls.PADDING['medium'], cls.PADDING['small'])
        )
        style.configure(
            'Primary.TButton',
            background=cls.COLORS['primary'],
            foreground='white'
        )
        style.map(
            'Primary.TButton',
            background=[('active', cls.COLORS['hover']), ('disabled', cls.COLORS['disabled'])]
        )
        
        # 設置 Entry 樣式
        style.configure(
            'TEntry', 
            font=cls.FONTS['default'],
            padding=(cls.PADDING['small'], cls.PADDING['small']),
            fieldbackground='white'
        )
        
        # 設置 Combobox 樣式
        style.configure(
            'TCombobox', 
            font=cls.FONTS['default'],
            padding=(cls.PADDING['small'], cls.PADDING['small'])
        )
        
        # 設置 Progressbar 樣式
        style.configure(
            'TProgressbar', 
            background=cls.COLORS['secondary'],
            troughcolor=cls.COLORS['background'],
            borderwidth=0
        )
        
        # 設置 Checkbutton 樣式
        style.configure(
            'TCheckbutton', 
            font=cls.FONTS['default'],
            background=cls.COLORS['background']
        )
        
        # 設置 Radiobutton 樣式
        style.configure(
            'TRadiobutton', 
            font=cls.FONTS['default'],
            background=cls.COLORS['background']
        )

    @classmethod
    def get_button_style(cls, button_type='default'):
        """獲取按鈕樣式"""
        if button_type == 'primary':
            return 'Primary.TButton'
        return 'TButton'
    
    @classmethod
    def get_label_style(cls, label_type='default'):
        """獲取標籤樣式"""
        if label_type == 'title':
            return 'Title.TLabel'
        elif label_type == 'subtitle':
            return 'Subtitle.TLabel'
        return 'TLabel'
    
    @classmethod
    def apply_modern_widget_style(cls, widget):
        """應用現代風格到小部件"""
        if isinstance(widget, tk.Text):
            widget.configure(
                font=cls.FONTS['monospace'],
                background='white',
                foreground=cls.COLORS['text'],
                borderwidth=1,
                relief='solid',
                padx=cls.PADDING['small'],
                pady=cls.PADDING['small']
            )
            
            # 設置標籤顏色
            widget.tag_configure('info', foreground=cls.COLORS['primary'])
            widget.tag_configure('success', foreground=cls.COLORS['success'])
            widget.tag_configure('warning', foreground=cls.COLORS['warning'])
            widget.tag_configure('error', foreground=cls.COLORS['error'])
            widget.tag_configure('bold', font=('Consolas', 9, 'bold'))
            
        elif isinstance(widget, tk.Listbox):
            widget.configure(
                font=cls.FONTS['default'],
                background='white',
                foreground=cls.COLORS['text'],
                borderwidth=1,
                relief='solid',
                selectbackground=cls.COLORS['primary'],
                selectforeground='white'
            )
            
        elif isinstance(widget, tk.Canvas):
            widget.configure(
                background=cls.COLORS['background'],
                borderwidth=0,
                highlightthickness=0
            )
            
        # 可以根據需要添加更多小部件類型的樣式
