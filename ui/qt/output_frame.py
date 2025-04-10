"""
Qt 版本的輸出框架

顯示下載日誌和輸出資訊
"""

from PySide6.QtWidgets import (
    QPlainTextEdit, QPushButton, QLabel, QHBoxLayout, QVBoxLayout,
    QCheckBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QTextCursor, QTextCharFormat

from .base import BaseFrame
from .theme import ThemeManager

class OutputFrame(BaseFrame):
    """輸出框架，顯示下載日誌和輸出資訊"""
    
    # 自定義信號
    log_added = Signal(str)  # 日誌添加時發出
    
    # 日誌類型
    LOG_INFO = 0
    LOG_SUCCESS = 1
    LOG_WARNING = 2
    LOG_ERROR = 3
    
    def __init__(self, parent=None):
        """初始化輸出框架"""
        super().__init__(parent)
        
        # 自動滾動標誌
        self.auto_scroll = True
        
    def setup_ui(self):
        """設置 UI 元件"""
        # 標題區域
        title_layout = QHBoxLayout()
        self.main_layout.addLayout(title_layout)
        
        # 標題標籤
        self.title_label = self.create_heading("下載日誌")
        title_layout.addWidget(self.title_label)
        
        # 自動滾動選項
        self.auto_scroll_check = QCheckBox("自動滾動", self)
        self.auto_scroll_check.setChecked(True)
        self.auto_scroll_check.stateChanged.connect(self._on_auto_scroll_changed)
        title_layout.addWidget(self.auto_scroll_check)
        
        # 清除按鈕
        self.clear_button = QPushButton("清除日誌", self)
        self.clear_button.clicked.connect(self._on_clear_clicked)
        title_layout.addWidget(self.clear_button)
        
        # 輸出文本框
        self.output_text = QPlainTextEdit(self)
        self.output_text.setReadOnly(True)
        self.output_text.setMinimumHeight(150)
        self.output_text.setPlaceholderText("下載日誌將顯示在這裡...")
        
        # 設置文本框樣式
        self.output_text.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {ThemeManager.CARD_COLOR};
                border: 1px solid {ThemeManager.BORDER_COLOR};
                border-radius: {ThemeManager.BORDER_RADIUS}px;
                padding: {ThemeManager.PADDING_NORMAL}px;
                font-family: "Consolas", "Courier New", monospace;
                font-size: {ThemeManager.FONT_SIZE_NORMAL}pt;
            }}
        """)
        
        self.main_layout.addWidget(self.output_text)
    
    def add_log(self, message, log_type=LOG_INFO):
        """添加日誌"""
        if not message:
            return
        
        # 獲取文本顏色
        color = self._get_color_for_log_type(log_type)
        
        # 創建文本格式
        text_format = QTextCharFormat()
        text_format.setForeground(QColor(color))
        
        # 添加文本
        cursor = self.output_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        # 如果不是第一行，先添加換行
        if not self.output_text.toPlainText() == "":
            cursor.insertText("\n")
        
        # 設置文本格式
        cursor.setCharFormat(text_format)
        
        # 插入文本
        cursor.insertText(message)
        
        # 自動滾動
        if self.auto_scroll:
            self.output_text.setTextCursor(cursor)
            self.output_text.ensureCursorVisible()
        
        # 發出日誌添加信號
        self.log_added.emit(message)
    
    def add_info(self, message):
        """添加資訊日誌"""
        self.add_log(message, self.LOG_INFO)
    
    def add_success(self, message):
        """添加成功日誌"""
        self.add_log(message, self.LOG_SUCCESS)
    
    def add_warning(self, message):
        """添加警告日誌"""
        self.add_log(message, self.LOG_WARNING)
    
    def add_error(self, message):
        """添加錯誤日誌"""
        self.add_log(message, self.LOG_ERROR)
    
    def clear(self):
        """清除日誌"""
        self.output_text.clear()
    
    def get_text(self):
        """獲取日誌文本"""
        return self.output_text.toPlainText()
    
    def _on_auto_scroll_changed(self, state):
        """自動滾動選項變更時的處理"""
        self.auto_scroll = state == Qt.Checked
    
    def _on_clear_clicked(self):
        """清除按鈕點擊時的處理"""
        self.clear()
    
    def _get_color_for_log_type(self, log_type):
        """根據日誌類型獲取顏色"""
        if log_type == self.LOG_SUCCESS:
            return ThemeManager.SUCCESS_COLOR
        elif log_type == self.LOG_WARNING:
            return ThemeManager.WARNING_COLOR
        elif log_type == self.LOG_ERROR:
            return ThemeManager.ERROR_COLOR
        else:
            return ThemeManager.TEXT_PRIMARY
