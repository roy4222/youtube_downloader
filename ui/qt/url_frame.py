"""
Qt 版本的 URL 輸入框架

處理 URL 輸入和平台檢測
"""

from PySide6.QtWidgets import (
    QLineEdit, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, 
    QComboBox, QCompleter
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon

from .base import BaseFrame
from .theme import ThemeManager
from core.url_utils import UrlProcessor

class UrlInputFrame(BaseFrame):
    """URL 輸入框架，處理 URL 輸入和平台檢測"""
    
    # 自定義信號
    url_changed = Signal(str)  # URL 變更時發出
    platform_detected = Signal(str)  # 平台檢測時發出
    
    def __init__(self, parent=None):
        """初始化 URL 輸入框架"""
        # 歷史記錄 - 移到 super().__init__ 之前初始化
        self.history = []
        
        # URL 處理器
        self.url_processor = UrlProcessor()
        
        super().__init__(parent)
        
    def setup_ui(self):
        """設置 UI 元件"""
        # 標題
        title_layout = QHBoxLayout()
        self.main_layout.addLayout(title_layout)
        
        # 標題標籤
        self.title_label = self.create_heading("輸入影片網址")
        title_layout.addWidget(self.title_label)
        
        # 平台標籤
        self.platform_label = QLabel("", self)
        self.platform_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.platform_label.setStyleSheet(f"color: {ThemeManager.SECONDARY_COLOR}; font-weight: bold;")
        title_layout.addWidget(self.platform_label)
        
        # URL 輸入區域
        input_layout = QHBoxLayout()
        input_layout.setSpacing(ThemeManager.PADDING_NORMAL)
        self.main_layout.addLayout(input_layout)
        
        # URL 輸入框
        self.url_input = QLineEdit(self)
        self.url_input.setPlaceholderText("輸入 YouTube 或 Bilibili 影片網址...")
        self.url_input.setMinimumHeight(36)
        self.url_input.textChanged.connect(self._on_url_changed)
        
        # 設置自動完成
        self.completer = QCompleter(self.history, self)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.url_input.setCompleter(self.completer)
        
        input_layout.addWidget(self.url_input)
        
        # 清除按鈕
        self.clear_button = QPushButton("清除", self)
        self.clear_button.setMinimumHeight(36)
        self.clear_button.clicked.connect(self._on_clear_clicked)
        input_layout.addWidget(self.clear_button)
        
        # 提示文字
        self.hint_label = QLabel("支援 YouTube 和 Bilibili 影片網址", self)
        self.hint_label.setProperty("subheading", True)
        self.main_layout.addWidget(self.hint_label)
    
    def _on_url_changed(self, url):
        """URL 變更時的處理"""
        # 發出 URL 變更信號
        self.url_changed.emit(url)
        
        # 檢測平台
        if url:
            platform = self.url_processor.detect_platform(url)
            if platform:
                self.platform_label.setText(f"平台: {platform}")
                self.platform_detected.emit(platform)
            else:
                self.platform_label.setText("未知平台")
                self.platform_detected.emit("")
        else:
            self.platform_label.setText("")
            self.platform_detected.emit("")
    
    def _on_clear_clicked(self):
        """清除按鈕點擊時的處理"""
        self.url_input.clear()
        self.platform_label.setText("")
        self.platform_detected.emit("")
    
    def get_url(self):
        """獲取當前 URL"""
        return self.url_input.text().strip()
    
    def set_url(self, url):
        """設置 URL"""
        self.url_input.setText(url)
    
    def add_to_history(self, url):
        """添加 URL 到歷史記錄"""
        url = url.strip()
        if url and url not in self.history:
            self.history.append(url)
            self.completer.setModel(None)  # 清除舊模型
            self.completer = QCompleter(self.history, self)
            self.completer.setCaseSensitivity(Qt.CaseInsensitive)
            self.url_input.setCompleter(self.completer)
    
    def clear_history(self):
        """清除歷史記錄"""
        self.history.clear()
        self.completer.setModel(None)
        self.completer = QCompleter(self.history, self)
        self.url_input.setCompleter(self.completer)
