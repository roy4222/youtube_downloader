"""
Qt 版本的路徑選擇框架

處理下載位置的選擇
"""

from PySide6.QtWidgets import (
    QLineEdit, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, 
    QFileDialog
)
from PySide6.QtCore import Qt, Signal
import os

from .base import BaseFrame
from .theme import ThemeManager

class PathSelectionFrame(BaseFrame):
    """路徑選擇框架，處理下載位置的選擇"""
    
    # 自定義信號
    path_changed = Signal(str)  # 路徑變更時發出
    
    def __init__(self, parent=None, default_path=""):
        """初始化路徑選擇框架"""
        self.default_path = default_path or os.path.join(os.path.expanduser("~"), "Downloads")
        super().__init__(parent)
        
    def setup_ui(self):
        """設置 UI 元件"""
        # 標題
        self.title_label = self.create_heading("下載位置")
        self.main_layout.addWidget(self.title_label)
        
        # 路徑選擇區域
        path_layout = QHBoxLayout()
        path_layout.setSpacing(ThemeManager.PADDING_NORMAL)
        self.main_layout.addLayout(path_layout)
        
        # 路徑輸入框
        self.path_input = QLineEdit(self)
        self.path_input.setText(self.default_path)
        self.path_input.setMinimumHeight(36)
        self.path_input.textChanged.connect(self._on_path_changed)
        path_layout.addWidget(self.path_input)
        
        # 瀏覽按鈕
        self.browse_button = QPushButton("瀏覽...", self)
        self.browse_button.setMinimumHeight(36)
        self.browse_button.clicked.connect(self._on_browse_clicked)
        path_layout.addWidget(self.browse_button)
        
        # 提示文字
        self.hint_label = QLabel("選擇影片下載的儲存位置", self)
        self.hint_label.setProperty("subheading", True)
        self.main_layout.addWidget(self.hint_label)
    
    def _on_path_changed(self, path):
        """路徑變更時的處理"""
        self.path_changed.emit(path)
    
    def _on_browse_clicked(self):
        """瀏覽按鈕點擊時的處理"""
        current_path = self.path_input.text() or self.default_path
        
        # 確保路徑存在
        if not os.path.exists(current_path):
            current_path = self.default_path
        
        # 打開資料夾選擇對話框
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "選擇下載位置",
            current_path,
            QFileDialog.ShowDirsOnly
        )
        
        if folder_path:
            self.path_input.setText(folder_path)
    
    def get_path(self):
        """獲取當前路徑"""
        path = self.path_input.text().strip()
        
        # 確保路徑存在
        if not path or not os.path.exists(path):
            path = self.default_path
            self.path_input.setText(path)
            
            # 如果預設路徑不存在，則創建
            if not os.path.exists(path):
                try:
                    os.makedirs(path)
                except OSError:
                    # 如果無法創建，則使用當前目錄
                    path = os.getcwd()
                    self.path_input.setText(path)
        
        return path
    
    def set_path(self, path):
        """設置路徑"""
        if path and os.path.exists(path):
            self.path_input.setText(path)
        else:
            self.path_input.setText(self.default_path)
