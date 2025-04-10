"""
Qt 版本的主視窗

整合所有 UI 元件，提供完整的應用程式界面
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QMessageBox, QSplitter, QFrame
)
from PySide6.QtCore import Qt, Signal, Slot, QSize
from PySide6.QtGui import QIcon, QPixmap, QFontMetrics

import os
import sys
import threading

from .theme import ThemeManager
from .url_frame import UrlInputFrame
from .path_frame import PathSelectionFrame
from .format_frame import FormatSelectionFrame
from .progress_frame import ProgressFrame
from .output_frame import OutputFrame
from .quality_dialog import QualityDialog
from .preview_frame import PreviewFrame

from core.download_manager import DownloadManager

class MainWindow(QMainWindow):
    """主視窗，整合所有 UI 元件"""
    
    # 自定義信號
    download_started = Signal()  # 下載開始時發出
    download_finished = Signal(bool)  # 下載完成時發出 (success)
    download_progress = Signal(float, str, str)  # 下載進度更新時發出 (progress, filename, speed)
    log_message = Signal(str, int)  # 日誌消息時發出 (message, log_type)
    
    def __init__(self):
        """初始化主視窗"""
        super().__init__()
        
        # 設置視窗屬性
        self.setWindowTitle("影片下載器")
        self.setMinimumSize(1000, 750)  # 增加最小視窗大小
        
        # 設置視窗圖示
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "youtube.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # 下載管理器
        self.download_manager = DownloadManager()
        
        # 下載線程
        self.download_thread = None
        
        # 正在下載標誌
        self.is_downloading = False
        
        # 設置中央部件
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # 主佈局
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(25, 25, 25, 25)  # 增加邊距
        self.main_layout.setSpacing(20)  # 增加間距
        
        # 初始化 UI
        self.setup_ui()
        
        # 連接信號
        self.connect_signals()
    
    def setup_ui(self):
        """設置 UI 元件"""
        # 頂部區域 - URL 輸入
        self.url_frame = UrlInputFrame(self)
        self.main_layout.addWidget(self.url_frame)
        
        # 中間區域 - 設定和下載
        middle_layout = QHBoxLayout()
        middle_layout.setSpacing(25)  # 增加間距
        self.main_layout.addLayout(middle_layout)
        
        # 左側 - 設定區域
        settings_layout = QVBoxLayout()
        settings_layout.setSpacing(20)  # 增加間距
        middle_layout.addLayout(settings_layout, 1)
        
        # 路徑選擇框架
        self.path_frame = PathSelectionFrame(self)
        settings_layout.addWidget(self.path_frame)
        
        # 格式選擇框架
        self.format_frame = FormatSelectionFrame(self)
        settings_layout.addWidget(self.format_frame)
        
        # 右側 - 預覽和下載
        right_layout = QVBoxLayout()
        right_layout.setSpacing(20)  # 增加間距
        middle_layout.addLayout(right_layout, 2)  # 增加右側區域的比例
        
        # 影片預覽區域
        self.preview_frame = PreviewFrame(self)
        right_layout.addWidget(self.preview_frame, stretch=3)
        
        # 下載按鈕區域
        button_layout = QHBoxLayout()  # 使用水平佈局
        button_layout.setSpacing(15)
        right_layout.addLayout(button_layout)
        
        # 添加彈性空間，使按鈕居中
        button_layout.addStretch(1)
        
        # 下載按鈕
        self.download_button = QPushButton("下載影片", self)
        self.download_button.setProperty("primary", True)
        self.download_button.setMinimumHeight(50)  # 增加按鈕高度
        self.download_button.setMinimumWidth(200)  # 設置按鈕寬度
        self.download_button.setIconSize(QSize(24, 24))  # 增加圖示大小
        button_layout.addWidget(self.download_button)
        
        # 添加彈性空間，使按鈕居中
        button_layout.addStretch(1)
        
        # 下載提示
        download_hint = QLabel("點擊按鈕開始下載，或按 Enter 鍵", self)
        download_hint.setProperty("subheading", True)
        download_hint.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(download_hint)
        
        # 進度框架
        self.progress_frame = ProgressFrame(self)
        right_layout.addWidget(self.progress_frame)
        
        # 底部區域 - 輸出日誌
        self.output_frame = OutputFrame(self)
        self.main_layout.addWidget(self.output_frame, stretch=0)
    
    def connect_signals(self):
        """連接信號"""
        # 下載按鈕點擊
        self.download_button.clicked.connect(self.start_download)
        
        # URL 變更時載入影片預覽
        self.url_frame.url_changed.connect(self.load_video_preview)
        
        # 預覽框架標題變更時調整視窗大小
        self.preview_frame.title_changed.connect(self.adjust_window_for_title)
        
        # 下載信號
        self.download_started.connect(self.on_download_started)
        self.download_finished.connect(self.on_download_finished)
        self.download_progress.connect(self.on_download_progress)
        self.log_message.connect(self.on_log_message)
    
    def load_video_preview(self, url: str):
        """載入影片預覽"""
        if url:
            self.preview_frame.load_video_info(url)
        else:
            self.preview_frame.clear_preview()
    
    def adjust_window_for_title(self, title: str):
        """根據標題長度調整視窗大小"""
        if not title or title == "載入中..." or title == "尚未載入影片":
            return
            
        # 計算標題的理想寬度
        font_metrics = QFontMetrics(self.preview_frame.title_label.font())
        title_width = font_metrics.horizontalAdvance(title)
        
        # 獲取當前視窗大小
        current_width = self.width()
        current_height = self.height()
        
        # 計算所需的最小寬度
        min_width = 1000  # 基本寬度
        
        # 如果標題很長，增加視窗寬度
        if title_width > 500:  # 增加閾值
            # 計算需要的額外寬度，但限制最大增加量
            extra_width = min(title_width - 500, 400)  # 增加最大寬度
            new_width = min_width + extra_width
            
            # 如果新寬度大於當前寬度，調整視窗大小
            if new_width > current_width:
                self.resize(new_width, current_height)
    
    def keyPressEvent(self, event):
        """按鍵事件處理"""
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            if not self.is_downloading and self.download_button.isEnabled():
                self.start_download()
        elif event.key() == Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)
    
    def start_download(self):
        """開始下載"""
        if self.is_downloading:
            return
        
        url = self.url_frame.get_url()
        if not url:
            QMessageBox.warning(self, "錯誤", "請輸入影片網址")
            return
        
        download_path = self.path_frame.get_path()
        if not download_path:
            QMessageBox.warning(self, "錯誤", "請選擇下載位置")
            return
        
        download_format = self.format_frame.get_format()
        audio_only = self.format_frame.is_audio_only()
        
        self.url_frame.add_to_history(url)
        
        self.is_downloading = True
        
        self.download_started.emit()
        
        self.download_thread = threading.Thread(
            target=self._download_thread,
            args=(url, download_path, download_format, audio_only)
        )
        self.download_thread.daemon = True
        self.download_thread.start()
    
    def _download_thread(self, url, download_path, download_format, audio_only):
        """下載線程"""
        try:
            self.log_message.emit(f"開始下載: {url}", OutputFrame.LOG_INFO)
            self.log_message.emit(f"下載位置: {download_path}", OutputFrame.LOG_INFO)
            self.log_message.emit(f"下載格式: {download_format}", OutputFrame.LOG_INFO)
            
            def progress_callback(progress, filename, speed):
                self.download_progress.emit(progress, filename, speed)
            
            def log_callback(message, log_type=OutputFrame.LOG_INFO):
                self.log_message.emit(message, log_type)
            
            result = self.download_manager.download(
                url, 
                download_path, 
                download_format, 
                audio_only=audio_only,
                progress_callback=progress_callback,
                log_callback=log_callback
            )
            
            self.download_finished.emit(result)
            
        except Exception as e:
            self.log_message.emit(f"下載錯誤: {str(e)}", OutputFrame.LOG_ERROR)
            
            self.download_finished.emit(False)
    
    @Slot()
    def on_download_started(self):
        """下載開始時的處理"""
        self.download_button.setEnabled(False)
        self.download_button.setText("下載中...")
        
        self.progress_frame.start_download()
        
        self.output_frame.add_info("下載已開始...")
    
    @Slot(bool)
    def on_download_finished(self, success):
        """下載完成時的處理"""
        self.is_downloading = False
        
        self.download_button.setEnabled(True)
        self.download_button.setText("下載影片")
        
        self.progress_frame.finish_download(success)
        
        if success:
            self.output_frame.add_success("下載完成！")
        else:
            self.output_frame.add_error("下載失敗！")
    
    @Slot(float, str, str)
    def on_download_progress(self, progress, filename, speed):
        """下載進度更新時的處理"""
        self.progress_frame.set_progress(progress, filename, speed)
    
    @Slot(str, int)
    def on_log_message(self, message, log_type):
        """日誌消息時的處理"""
        self.output_frame.add_log(message, log_type)
    
    def show_quality_dialog(self, formats):
        """顯示畫質選擇對話框"""
        return QualityDialog.show_dialog(self, "選擇畫質", formats)
    
    def closeEvent(self, event):
        """關閉視窗事件處理"""
        if self.is_downloading:
            reply = QMessageBox.question(
                self,
                "確認退出",
                "正在下載中，確定要退出嗎？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                event.ignore()
                return
        
        event.accept()
