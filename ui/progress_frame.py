"""
Qt 版本的進度框架

顯示下載進度和狀態
"""

from PySide6.QtWidgets import (
    QProgressBar, QLabel, QHBoxLayout, QVBoxLayout
)
from PySide6.QtCore import Qt, Signal, QTimer

from .base import BaseFrame
from .theme import ThemeManager

class ProgressFrame(BaseFrame):
    """進度框架，顯示下載進度和狀態"""
    
    # 自定義信號
    progress_updated = Signal(float)  # 進度更新時發出
    
    def __init__(self, parent=None):
        """初始化進度框架"""
        super().__init__(parent)
        
        # 下載狀態
        self.is_downloading = False
        
        # 進度更新計時器
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self._update_time_elapsed)
        
        # 開始時間
        self.start_time = 0
        self.time_elapsed = 0
        
    def setup_ui(self):
        """設置 UI 元件"""
        # 標題
        title_layout = QHBoxLayout()
        self.main_layout.addLayout(title_layout)
        
        # 標題標籤
        self.title_label = self.create_heading("下載進度")
        title_layout.addWidget(self.title_label)
        
        # 狀態標籤
        self.status_label = QLabel("準備就緒", self)
        self.status_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        title_layout.addWidget(self.status_label)
        
        # 進度條
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p%")
        self.progress_bar.setMinimumHeight(24)
        self.main_layout.addWidget(self.progress_bar)
        
        # 詳細資訊區域
        info_layout = QHBoxLayout()
        info_layout.setSpacing(ThemeManager.PADDING_LARGE)
        self.main_layout.addLayout(info_layout)
        
        # 檔案名稱標籤
        self.filename_label = QLabel("", self)
        self.filename_label.setProperty("subheading", True)
        info_layout.addWidget(self.filename_label)
        
        # 時間標籤
        self.time_label = QLabel("", self)
        self.time_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.time_label.setProperty("subheading", True)
        info_layout.addWidget(self.time_label)
        
        # 速度標籤
        self.speed_label = QLabel("", self)
        self.speed_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.speed_label.setProperty("subheading", True)
        info_layout.addWidget(self.speed_label)
    
    def set_progress(self, progress, filename="", speed=""):
        """設置進度"""
        # 更新進度條
        self.progress_bar.setValue(int(progress))
        
        # 更新檔案名稱
        if filename:
            self.filename_label.setText(filename)
        
        # 更新速度
        if speed:
            self.speed_label.setText(speed)
        
        # 發出進度更新信號
        self.progress_updated.emit(progress)
    
    def start_download(self, filename=""):
        """開始下載"""
        self.is_downloading = True
        self.status_label.setText("下載中...")
        self.status_label.setStyleSheet(f"color: {ThemeManager.SECONDARY_COLOR};")
        
        # 重置進度條
        self.progress_bar.setValue(0)
        
        # 設置檔案名稱
        if filename:
            self.filename_label.setText(filename)
        
        # 重置時間和速度
        self.start_time = 0
        self.time_elapsed = 0
        self.time_label.setText("00:00")
        self.speed_label.setText("")
        
        # 啟動計時器
        self.start_time = 0
        self.update_timer.start(1000)  # 每秒更新一次
    
    def finish_download(self, success=True):
        """完成下載"""
        self.is_downloading = False
        
        # 停止計時器
        self.update_timer.stop()
        
        if success:
            # 設置進度為 100%
            self.progress_bar.setValue(100)
            
            # 更新狀態
            self.status_label.setText("下載完成")
            self.status_label.setStyleSheet(f"color: {ThemeManager.SUCCESS_COLOR};")
        else:
            # 更新狀態
            self.status_label.setText("下載失敗")
            self.status_label.setStyleSheet(f"color: {ThemeManager.ERROR_COLOR};")
    
    def reset(self):
        """重置進度框架"""
        self.is_downloading = False
        
        # 停止計時器
        self.update_timer.stop()
        
        # 重置進度條
        self.progress_bar.setValue(0)
        
        # 重置標籤
        self.status_label.setText("準備就緒")
        self.status_label.setStyleSheet("")
        self.filename_label.setText("")
        self.time_label.setText("")
        self.speed_label.setText("")
    
    def _update_time_elapsed(self):
        """更新經過時間"""
        if not self.is_downloading:
            return
        
        self.time_elapsed += 1
        minutes = self.time_elapsed // 60
        seconds = self.time_elapsed % 60
        
        self.time_label.setText(f"{minutes:02d}:{seconds:02d}")
    
    def set_status(self, status, is_error=False):
        """設置狀態"""
        self.status_label.setText(status)
        
        if is_error:
            self.status_label.setStyleSheet(f"color: {ThemeManager.ERROR_COLOR};")
        else:
            self.status_label.setStyleSheet("")
