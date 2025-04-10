"""
Qt 版本的格式選擇框架

處理下載格式的選擇
"""

from PySide6.QtWidgets import (
    QComboBox, QLabel, QHBoxLayout, QVBoxLayout, 
    QCheckBox
)
from PySide6.QtCore import Qt, Signal

from .base import BaseFrame
from .theme import ThemeManager

class FormatSelectionFrame(BaseFrame):
    """格式選擇框架，處理下載格式的選擇"""
    
    # 自定義信號
    format_changed = Signal(str)  # 格式變更時發出
    audio_only_changed = Signal(bool)  # 僅音訊選項變更時發出
    
    # 格式選項
    FORMAT_OPTIONS = [
        {"value": "best", "label": "最佳品質"},
        {"value": "1080p", "label": "1080p"},
        {"value": "720p", "label": "720p"},
        {"value": "480p", "label": "480p"},
        {"value": "360p", "label": "360p"},
        {"value": "240p", "label": "240p"},
        {"value": "bestaudio", "label": "最佳音訊"}
    ]
    
    def __init__(self, parent=None):
        """初始化格式選擇框架"""
        super().__init__(parent)
        
    def setup_ui(self):
        """設置 UI 元件"""
        # 標題
        self.title_label = self.create_heading("下載格式")
        self.main_layout.addWidget(self.title_label)
        
        # 格式選擇區域
        format_layout = QHBoxLayout()
        format_layout.setSpacing(ThemeManager.PADDING_NORMAL)
        self.main_layout.addLayout(format_layout)
        
        # 格式選擇下拉選單
        self.format_label = QLabel("選擇格式:", self)
        format_layout.addWidget(self.format_label)
        
        self.format_combo = QComboBox(self)
        self.format_combo.setMinimumHeight(36)
        
        # 添加格式選項
        for option in self.FORMAT_OPTIONS:
            self.format_combo.addItem(option["label"], option["value"])
        
        self.format_combo.currentIndexChanged.connect(self._on_format_changed)
        format_layout.addWidget(self.format_combo)
        
        # 僅下載音訊選項
        self.audio_only_check = QCheckBox("僅下載音訊", self)
        self.audio_only_check.stateChanged.connect(self._on_audio_only_changed)
        format_layout.addWidget(self.audio_only_check)
        
        # 提示文字
        self.hint_label = QLabel("選擇較低品質可加快下載速度", self)
        self.hint_label.setProperty("subheading", True)
        self.main_layout.addWidget(self.hint_label)
    
    def _on_format_changed(self, index):
        """格式變更時的處理"""
        format_value = self.format_combo.itemData(index)
        self.format_changed.emit(format_value)
        
        # 如果選擇了音訊格式，自動勾選僅音訊選項
        if format_value == "bestaudio":
            self.audio_only_check.setChecked(True)
    
    def _on_audio_only_changed(self, state):
        """僅音訊選項變更時的處理"""
        is_checked = state == Qt.Checked
        self.audio_only_changed.emit(is_checked)
        
        # 如果勾選了僅音訊，自動選擇最佳音訊格式
        if is_checked:
            for i in range(self.format_combo.count()):
                if self.format_combo.itemData(i) == "bestaudio":
                    self.format_combo.setCurrentIndex(i)
                    break
    
    def get_format(self):
        """獲取當前格式"""
        return self.format_combo.currentData()
    
    def set_format(self, format_value):
        """設置格式"""
        for i in range(self.format_combo.count()):
            if self.format_combo.itemData(i) == format_value:
                self.format_combo.setCurrentIndex(i)
                break
    
    def is_audio_only(self):
        """是否僅下載音訊"""
        return self.audio_only_check.isChecked()
    
    def set_audio_only(self, audio_only):
        """設置僅下載音訊選項"""
        self.audio_only_check.setChecked(audio_only)
