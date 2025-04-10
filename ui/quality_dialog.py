"""
Qt 版本的畫質選擇對話框

提供影片畫質選擇功能
"""

from PySide6.QtWidgets import (
    QListWidget, QListWidgetItem, QPushButton, QLabel, 
    QHBoxLayout, QVBoxLayout, QDialog
)
from PySide6.QtCore import Qt, Signal

from .base import BaseDialog
from .theme import ThemeManager

class QualityDialog(BaseDialog):
    """畫質選擇對話框，提供影片畫質選擇功能"""
    
    # 自定義信號
    quality_selected = Signal(str, str)  # 畫質選擇時發出 (format_id, format_note)
    
    def __init__(self, parent=None, title="選擇畫質", formats=None):
        """初始化畫質選擇對話框"""
        self.formats = formats or []
        super().__init__(parent, title, 500, 400)
        
    def setup_ui(self):
        """設置 UI 元件"""
        # 標題
        self.title_label = self.create_heading("請選擇影片畫質")
        self.main_layout.addWidget(self.title_label)
        
        # 提示文字
        self.hint_label = QLabel("選擇較低畫質可加快下載速度", self)
        self.hint_label.setProperty("subheading", True)
        self.main_layout.addWidget(self.hint_label)
        
        # 畫質列表
        self.quality_list = QListWidget(self)
        self.quality_list.setAlternatingRowColors(True)
        self.quality_list.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.main_layout.addWidget(self.quality_list)
        
        # 填充畫質列表
        self._populate_quality_list()
        
        # 按鈕區域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(ThemeManager.PADDING_NORMAL)
        self.main_layout.addLayout(button_layout)
        
        # 取消按鈕
        self.cancel_button = QPushButton("取消", self)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        # 確定按鈕
        self.ok_button = QPushButton("確定", self)
        self.ok_button.setProperty("primary", True)
        self.ok_button.clicked.connect(self._on_ok_clicked)
        button_layout.addWidget(self.ok_button)
    
    def _populate_quality_list(self):
        """填充畫質列表"""
        self.quality_list.clear()
        
        if not self.formats:
            item = QListWidgetItem("無可用畫質")
            item.setData(Qt.UserRole, {"format_id": "best", "format_note": "最佳品質"})
            self.quality_list.addItem(item)
            return
        
        # 添加畫質選項
        for fmt in self.formats:
            format_id = fmt.get("format_id", "")
            format_note = fmt.get("format_note", "")
            resolution = fmt.get("resolution", "")
            fps = fmt.get("fps", "")
            ext = fmt.get("ext", "")
            
            # 創建顯示文本
            display_text = ""
            if format_note:
                display_text += f"{format_note} "
            if resolution:
                display_text += f"({resolution}) "
            if fps:
                display_text += f"{fps}fps "
            if ext:
                display_text += f"[{ext}]"
                
            if not display_text:
                display_text = f"格式 {format_id}"
            
            # 創建列表項
            item = QListWidgetItem(display_text.strip())
            item.setData(Qt.UserRole, fmt)
            self.quality_list.addItem(item)
        
        # 選擇第一項
        if self.quality_list.count() > 0:
            self.quality_list.setCurrentRow(0)
    
    def _on_ok_clicked(self):
        """確定按鈕點擊時的處理"""
        current_item = self.quality_list.currentItem()
        if current_item:
            fmt = current_item.data(Qt.UserRole)
            format_id = fmt.get("format_id", "best")
            format_note = fmt.get("format_note", "最佳品質")
            
            # 發出畫質選擇信號
            self.quality_selected.emit(format_id, format_note)
            
            # 關閉對話框
            self.accept()
    
    def _on_item_double_clicked(self, item):
        """項目雙擊時的處理"""
        fmt = item.data(Qt.UserRole)
        format_id = fmt.get("format_id", "best")
        format_note = fmt.get("format_note", "最佳品質")
        
        # 發出畫質選擇信號
        self.quality_selected.emit(format_id, format_note)
        
        # 關閉對話框
        self.accept()
    
    def set_formats(self, formats):
        """設置可用格式"""
        self.formats = formats or []
        self._populate_quality_list()
    
    @classmethod
    def show_dialog(cls, parent=None, title="選擇畫質", formats=None):
        """顯示對話框並返回選擇的畫質"""
        dialog = cls(parent, title, formats)
        result = dialog.exec()
        
        if result == QDialog.Accepted:
            current_item = dialog.quality_list.currentItem()
            if current_item:
                fmt = current_item.data(Qt.UserRole)
                return fmt.get("format_id", "best"), fmt.get("format_note", "最佳品質")
        
        return None, None
