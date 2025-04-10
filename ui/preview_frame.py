"""
影片預覽框架元件

提供影片縮圖和標題預覽功能
"""

import os
import tempfile
import requests
import logging  # 添加日誌
from typing import Optional, Callable
from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QLabel,
    QSizePolicy,
    QWidget,
    QHBoxLayout,
)
from PySide6.QtCore import Qt, Signal, QSize, QUrl, QThread, QObject
from PySide6.QtGui import QPixmap, QImage, QFont, QFontMetrics

import re
import json
from urllib.parse import urlparse
import datetime  # 用於格式化日期
import locale    # 用於格式化數字

from ui.base import BaseFrame
from ui.theme import ThemeManager
from core.download_manager import get_video_info

# 設置日誌
logger = logging.getLogger(__name__)


class VideoInfoWorker(QObject):
    """影片資訊獲取工作線程"""
    
    finished = Signal(dict)
    error = Signal(str)
    
    def __init__(self, url: str):
        super().__init__()
        self.url = url
    
    def run(self):
        """執行影片資訊獲取"""
        try:
            info = get_video_info(self.url)
            self.finished.emit(info)
        except Exception as e:
            logger.error(f"獲取影片資訊時發生錯誤: {e}", exc_info=True)
            self.error.emit(str(e))


class VideoInfoThread(QThread):
    """影片資訊獲取線程"""
    
    def __init__(self, worker: VideoInfoWorker):
        super().__init__()
        self.worker = worker
        self.worker.moveToThread(self)
    
    def run(self):
        """執行線程"""
        self.worker.run()


class PreviewFrame(BaseFrame):
    """影片預覽框架元件"""
    
    # 自定義信號
    title_changed = Signal(str)  # 標題變更時發出
    
    # 縮圖比例常數
    ASPECT_RATIO = 16.0 / 9.0  # 使用浮點數確保精度
    
    def __init__(self, parent=None, **kwargs):
        self.video_info = None
        self.temp_thumbnail_path = None
        self.original_pixmap = None  # 保存原始縮圖
        super().__init__(parent, **kwargs)
    
    def setup_ui(self):
        """設置 UI"""
        # 調整邊距
        self.main_layout.setContentsMargins(0, 0, 0, 0) # 移除主佈局邊距
        self.main_layout.setSpacing(ThemeManager.PADDING_SMALL)
        
        # 標題標籤
        self.title_label = QLabel("尚未載入影片")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setWordWrap(True)
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(11) # 稍微增大標題字體
        self.title_label.setFont(title_font)
        self.title_label.setStyleSheet(f"color: {ThemeManager.TEXT_PRIMARY}; padding: {ThemeManager.PADDING_SMALL}px;") # 添加內邊距
        self.title_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        
        # 添加影片資訊標籤 (上傳日期、觀看次數、影片長度)
        self.info_container = QFrame(self)
        self.info_container.setObjectName("infoContainer")
        self.info_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        
        # 創建垂直佈局用於顯示影片資訊
        info_layout = QVBoxLayout(self.info_container)
        info_layout.setContentsMargins(ThemeManager.PADDING_SMALL, ThemeManager.PADDING_SMALL, 
                                      ThemeManager.PADDING_SMALL, ThemeManager.PADDING_SMALL)
        info_layout.setSpacing(5)  # 減小間距使垂直排列更緊湊
        
        # 創建各項資訊標籤
        self.upload_date_label = QLabel("上傳日期: --")
        self.view_count_label = QLabel("觀看次數: --")
        self.duration_label = QLabel("影片長度: --")
        
        # 設置字體和樣式
        info_font = QFont()
        info_font.setPointSize(9)
        info_style = f"color: {ThemeManager.TEXT_SECONDARY};"
        
        for label in [self.upload_date_label, self.view_count_label, self.duration_label]:
            label.setFont(info_font)
            label.setStyleSheet(info_style)
            label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # 左對齊
            info_layout.addWidget(label)
        
        # 縮圖容器 和 QLabel
        self.thumbnail_container = QFrame(self)
        self.thumbnail_container.setObjectName("thumbnailContainer")
        # 設定最小高度和策略，允許它垂直擴展
        self.thumbnail_container.setMinimumHeight(100)  # 增加最小高度從 150 到 250
        self.thumbnail_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # self.thumbnail_container.setStyleSheet("background-color: rgba(0, 255, 0, 50);") # Debug 背景色

        # 新增：為容器創建佈局以置中標籤
        container_layout = QHBoxLayout(self.thumbnail_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter) # 置中

        self.thumbnail_label = QLabel(self.thumbnail_container)
        self.thumbnail_label.setObjectName("thumbnailLabel")
        self.thumbnail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # 設定尺寸策略為 Fixed，因為我們會手動設定它的尺寸
        self.thumbnail_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        # self.thumbnail_label.setStyleSheet("background-color: rgba(255, 0, 0, 50);") # Debug 背景色

        # 將標籤添加到容器佈局中
        container_layout.addWidget(self.thumbnail_label)

        # 將標題、縮圖和影片資訊（順序調整）添加到主垂直佈局中
        self.main_layout.addWidget(self.title_label) 
        self.main_layout.addWidget(self.thumbnail_container)
        self.main_layout.addWidget(self.info_container)

    # --- 覆寫大小提示和高度計算 --- 
    def minimumSizeHint(self) -> QSize:
        # 提供一個合理的最小尺寸提示
        # 寬度基於父級或預設，高度基於 16:9
        base_width = super().minimumSizeHint().width()
        if base_width <= 0:
             base_width = 320 # 預設最小寬度
        return QSize(base_width, int(base_width / self.ASPECT_RATIO) + self.title_label.height()) 

    def sizeHint(self) -> QSize:
        # 提供建議尺寸
        width = super().sizeHint().width()
        if width <= 0:
            width = 480 # 預設建議寬度
        return QSize(width, int(width / self.ASPECT_RATIO) + self.title_label.height())

    # --- 影片資訊處理 --- 
    def load_video_info(self, url: str):
        """載入影片資訊"""
        if not url:
            self.clear_preview()
            return
        
        # 顯示加載中
        self.show_loading()
        
        # 創建工作線程
        worker = VideoInfoWorker(url)
        worker.finished.connect(self._on_video_info_received)
        worker.error.connect(self._on_video_info_error)
        
        # 啟動線程
        self.thread = VideoInfoThread(worker)
        self.thread.start()
    
    def _on_video_info_received(self, info: dict):
        """接收到影片資訊時的處理"""
        if not info:
            logger.warning("接收到空的影片資訊")
            self._on_video_info_error("無法獲取影片資訊")
            return
        
        # 記錄完整的 video_info 結構，幫助調試
        logger.debug(f"接收到影片資訊: {info.keys()}")
        
        # 保存影片資訊供日後使用
        self.video_info = info
        
        # 設置標題
        title = info.get('title', '未知標題')
        self.title_label.setText(title)
        self.title_changed.emit(title)
        
        # 更新影片詳細資訊
        self._update_video_details(info)
        
        # 獲取縮圖 URL
        thumbnail_url = self._get_best_thumbnail(info)
        
        if not thumbnail_url:
            logger.error("未找到合適的縮圖 URL")
            
            # 嘗試從 URL 直接獲取 bilibili 縮圖
            if 'webpage_url' in info and info['webpage_url']:
                url = info['webpage_url']
                if 'bilibili' in url:
                    logger.info("嘗試直接從 bilibili URL 獲取縮圖")
                    thumbnail_url = self._get_bilibili_thumbnail_from_url(url)
                    if thumbnail_url:
                        logger.info(f"成功從 bilibili URL 獲取縮圖: {thumbnail_url}")
            
            if not thumbnail_url:
                return
            
        logger.info(f"使用縮圖 URL: {thumbnail_url}")
        
        # 下載縮圖
        self._load_thumbnail(thumbnail_url)

    def _update_video_details(self, info: dict):
        """更新影片詳細資訊 (上傳日期、觀看次數、影片長度)"""
        try:
            # 格式化上傳日期
            upload_date = info.get('upload_date')
            if upload_date and len(upload_date) == 8:  # 通常為 YYYYMMDD 格式
                try:
                    # 轉換為日期物件
                    date_obj = datetime.datetime.strptime(upload_date, '%Y%m%d')
                    # 格式化為年月日
                    formatted_date = date_obj.strftime('%Y/%m/%d')
                    self.upload_date_label.setText(f"上傳日期: {formatted_date}")
                except ValueError:
                    self.upload_date_label.setText(f"上傳日期: {upload_date}")
            elif upload_date:
                self.upload_date_label.setText(f"上傳日期: {upload_date}")
            else:
                self.upload_date_label.setText("上傳日期: --")
                
            # 格式化觀看次數
            view_count = info.get('view_count')
            if view_count is not None:
                # 使用千分位分隔符格式化數字
                formatted_count = locale.format_string("%d", view_count, grouping=True)
                self.view_count_label.setText(f"觀看次數: {formatted_count}")
            else:
                self.view_count_label.setText("觀看次數: --")
                
            # 格式化影片長度
            duration = info.get('duration')
            if duration is not None:
                # 將秒數轉換為時分秒格式
                hours, remainder = divmod(int(duration), 3600)
                minutes, seconds = divmod(remainder, 60)
                
                if hours > 0:
                    formatted_duration = f"{hours}:{minutes:02d}:{seconds:02d}"
                else:
                    formatted_duration = f"{minutes}:{seconds:02d}"
                    
                self.duration_label.setText(f"影片長度: {formatted_duration}")
            else:
                self.duration_label.setText("影片長度: --")
                
        except Exception as e:
            logger.error(f"更新影片詳細資訊時發生錯誤: {e}", exc_info=True)
            self.upload_date_label.setText("上傳日期: --")
            self.view_count_label.setText("觀看次數: --")
            self.duration_label.setText("影片長度: --")

    def _on_video_info_error(self, error: str):
        """影片資訊載入錯誤"""
        self.clear_preview()
        self.title_label.setText(f"載入失敗: {error}")
        self.title_changed.emit(f"載入失敗: {error}")
    
    # --- 縮圖載入和顯示 --- 
    def _load_thumbnail(self, url: str):
        """下載並顯示縮圖"""
        logger.info(f"開始下載縮圖: {url}")
        try:
            # 使用 requests 下載縮圖
            response = requests.get(url)
            response.raise_for_status()  # 確保請求成功
            
            # 從響應內容創建 QImage
            image_data = response.content
            image = QImage()
            image.loadFromData(image_data)
            
            if image.isNull():
                logger.error(f"無法從 URL 加載圖片: {url}")
                self._clear_thumbnail()
                return
                
            logger.info(f"成功下載縮圖，尺寸: {image.width()}x{image.height()}")
            
            # 創建 QPixmap 並設置
            pixmap = QPixmap.fromImage(image)
            self.original_pixmap = pixmap
            
            # 縮放並顯示
            self._set_scaled_pixmap()
            
        except Exception as e:
            logger.error(f"下載或設置縮圖時出錯: {e}", exc_info=True)
            self._clear_thumbnail()

    def _clear_thumbnail(self):
        """清除縮圖"""
        self.thumbnail_label.clear()
        self.thumbnail_label.setText("無法載入縮圖")
        self.original_pixmap = None
        self._cleanup_temp_file()
        logger.debug("縮圖已清除")

    def _cleanup_temp_file(self):
        """清理舊的臨時縮圖文件"""
        if self.temp_thumbnail_path and os.path.exists(self.temp_thumbnail_path):
            try:
                os.unlink(self.temp_thumbnail_path)
                logger.debug(f"已刪除臨時縮圖文件: {self.temp_thumbnail_path}")
                self.temp_thumbnail_path = None
            except OSError as e:
                logger.warning(f"刪除臨時縮圖文件失敗: {e}")
                self.temp_thumbnail_path = None # 即使刪除失敗也重置路徑

    def show_loading(self):
        """顯示加載中狀態"""
        self.title_label.setText("載入中...")
        self.thumbnail_label.clear()
        self.thumbnail_label.setText("載入中...") # 在標籤上顯示文字
        self.original_pixmap = None
        self.title_changed.emit("載入中...")
        logger.debug("顯示載入中狀態")
    
    def clear_preview(self):
        """清除所有預覽信息"""
        self.video_info = None
        self.title_label.setText("尚未載入影片")
        self._clear_thumbnail()
        self.title_changed.emit("尚未載入影片")
        # 重設影片詳細資訊
        self.upload_date_label.setText("上傳日期: --")
        self.view_count_label.setText("觀看次數: --")
        self.duration_label.setText("影片長度: --")
        logger.debug("預覽已清除")

    # --- 事件處理 --- 
    def resizeEvent(self, event):
        """處理視窗或元件大小變化事件"""
        super().resizeEvent(event)
        logger.debug(f"resizeEvent 觸發，新尺寸: {event.size().width()}x{event.size().height()}")
        # 延遲一點調用縮放，確保佈局已經更新
        # QtCore.QTimer.singleShot(0, self._set_scaled_pixmap)
        # 或者直接調用，看看效果
        self._set_scaled_pixmap()

    def _set_scaled_pixmap(self):
        """根據 QLabel 的可用空間縮放並設置 QPixmap，保持 16:9 的寬高比。"""
        if self.original_pixmap is None:
            self.thumbnail_label.clear()
            logger.debug("_set_scaled_pixmap: 清除縮圖")
            return

        container_size = self.thumbnail_container.size()
        available_width = container_size.width()
        available_height = container_size.height()
        logger.debug(f"_set_scaled_pixmap: 容器尺寸 = {available_width}x{available_height}")

        if available_width <= 0 or available_height <= 0:
            logger.warning(f"_set_scaled_pixmap: 容器尺寸無效 ({available_width}x{available_height})，跳過縮放")
            # 即使尺寸無效，也嘗試設置原始圖片，或者一個預設/錯誤圖片
            # self.thumbnail_label.setPixmap(self.original_pixmap)
            return

        # 計算基於寬度的目標尺寸
        target_width_from_width = available_width
        target_height_from_width = int(target_width_from_width / self.ASPECT_RATIO)

        # 計算基於高度的目標尺寸
        target_height_from_height = available_height
        target_width_from_height = int(target_height_from_height * self.ASPECT_RATIO)

        # 決定最終目標尺寸
        if target_height_from_width <= available_height:
            # 使用基於寬度的尺寸 (寬度受限或剛好)
            target_width = target_width_from_width
            target_height = target_height_from_width
            logger.debug(f"縮放決策: 寬度限制. 目標尺寸: {target_width}x{target_height}")
        else:
            # 使用基於高度的尺寸 (高度受限)
            target_width = target_width_from_height
            target_height = target_height_from_height
            logger.debug(f"縮放決策: 高度限制. 目標尺寸: {target_width}x{target_height}")

        # 確保目標尺寸有效
        if target_width <= 0 or target_height <= 0:
            logger.warning(f"_set_scaled_pixmap: 計算出的目標尺寸無效 ({target_width}x{target_height})，跳過縮放")
            return

        logger.debug(f"_set_scaled_pixmap: 原始 pixmap 尺寸 = {self.original_pixmap.width()}x{self.original_pixmap.height()}")
        logger.debug(f"_set_scaled_pixmap: 最終目標縮放尺寸 = {target_width}x{target_height}")
        # 新增日誌: 比較原始尺寸和目標尺寸，判斷是放大還是縮小
        if self.original_pixmap.width() < target_width or self.original_pixmap.height() < target_height:
            logger.warning(f"需要放大縮圖！原始: {self.original_pixmap.width()}x{self.original_pixmap.height()}, 目標: {target_width}x{target_height}")
        else:
            logger.debug(f"需要縮小或維持縮圖。原始: {self.original_pixmap.width()}x{self.original_pixmap.height()}, 目標: {target_width}x{target_height}")

        try:
            # 縮放 pixmap 並保持寬高比，使用更平滑的轉換模式
            scaled_pixmap = self.original_pixmap.scaled(
                target_width,
                target_height,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation  # 使用平滑轉換
            )
            logger.debug(f"_set_scaled_pixmap: 縮放後 pixmap 尺寸 = {scaled_pixmap.width()}x{scaled_pixmap.height()}")

            # 確保縮放後的尺寸不超過容器，理論上不應發生，但作為安全檢查
            if scaled_pixmap.width() > available_width or scaled_pixmap.height() > available_height:
                logger.warning(f"縮放後的 pixmap ({scaled_pixmap.width()}x{scaled_pixmap.height()}) 超出容器 ({available_width}x{available_height})，重新裁剪")
                # 如果縮放結果超出，則以容器大小再次強制縮放（可能破壞比例，但不應發生）
                scaled_pixmap = scaled_pixmap.scaled(
                    available_width,
                    available_height,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )

            self.thumbnail_label.setPixmap(scaled_pixmap)
            # 確保 QLabel 尺寸與縮放後的 pixmap 同步，以便佈局正確置中
            self.thumbnail_label.setFixedSize(scaled_pixmap.size())
            logger.info(f"成功設置縮放後的縮圖，尺寸：{scaled_pixmap.width()}x{scaled_pixmap.height()}")

        except Exception as e:
            logger.error(f"縮放或設置 pixmap 時發生錯誤: {e}", exc_info=True)
            self.thumbnail_label.clear() # 出錯時清除

    def _get_bilibili_thumbnail_from_url(self, url):
        """從 bilibili URL 直接提取縮圖"""
        try:
            # 從 URL 中提取 BV 號或 AV 號
            logger.info(f"嘗試從 bilibili URL 提取縮圖: {url}")
            
            bv_match = re.search(r'BV\w+', url)
            av_match = re.search(r'av(\d+)', url)
            
            video_id = None
            if bv_match:
                video_id = bv_match.group(0)
                logger.info(f"從 URL 中提取到 BV 號: {video_id}")
            elif av_match:
                video_id = f"av{av_match.group(1)}"
                logger.info(f"從 URL 中提取到 AV 號: {video_id}")
            else:
                logger.warning(f"無法從 URL 中提取 bilibili 視頻 ID: {url}")
                return None
            
            # 構建 API URL
            api_url = f"https://api.bilibili.com/x/web-interface/view?bvid={video_id}" if video_id.startswith('BV') else f"https://api.bilibili.com/x/web-interface/view?aid={video_id[2:]}"
            logger.info(f"使用 bilibili API URL: {api_url}")
            
            # 請求 API
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Referer': 'https://www.bilibili.com'
            }
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()
            
            # 解析 JSON 響應
            data = response.json()
            if data['code'] == 0 and 'data' in data:
                pic_url = data['data'].get('pic')
                if pic_url:
                    logger.info(f"從 bilibili API 獲取到縮圖 URL: {pic_url}")
                    return pic_url
            
            logger.warning(f"bilibili API 響應中未找到縮圖: {data}")
            return None
            
        except Exception as e:
            logger.error(f"從 bilibili URL 提取縮圖時出錯: {e}", exc_info=True)
            return None

    def _get_best_thumbnail(self, info: dict) -> str | None:
        """從影片資訊中獲取最佳縮圖 URL"""
        # 檢查是否為 bilibili 視頻
        if 'webpage_url' in info and info['webpage_url'] and 'bilibili' in info['webpage_url']:
            logger.info("檢測到 bilibili 視頻，嘗試特殊處理")
            # 嘗試從 bilibili 特定字段獲取縮圖
            if 'thumbnail' in info and info['thumbnail']:
                logger.info(f"使用 bilibili 'thumbnail' 字段: {info['thumbnail']}")
                return info['thumbnail']
            
            # 嘗試直接從 URL 獲取縮圖
            bilibili_thumbnail = self._get_bilibili_thumbnail_from_url(info['webpage_url'])
            if bilibili_thumbnail:
                return bilibili_thumbnail
        
        # 檢查 info 中的縮圖信息
        thumbnails = info.get('thumbnails', [])
        
        # 詳細記錄縮圖信息
        logger.debug(f"原始縮圖信息: {thumbnails}")
        
        if not thumbnails or not isinstance(thumbnails, list):
            logger.warning(f"'thumbnails' 格式不正確: {thumbnails}")
            
            # 嘗試其他可能的縮圖字段
            logger.debug("嘗試查找其他可能的縮圖字段...")
            
            # 嘗試 thumbnail 字段
            if 'thumbnail' in info and info['thumbnail']:
                logger.info(f"使用 'thumbnail' 字段: {info['thumbnail']}")
                return info['thumbnail']
                
            # 嘗試 thumbnail_url 字段
            if 'thumbnail_url' in info and info['thumbnail_url']:
                logger.info(f"使用 'thumbnail_url' 字段: {info['thumbnail_url']}")
                return info['thumbnail_url']
            
            # 嘗試從 formats 中查找縮圖
            formats = info.get('formats', [])
            for fmt in formats:
                if isinstance(fmt, dict) and 'thumbnail' in fmt and fmt['thumbnail']:
                    logger.info(f"從 formats 中找到縮圖: {fmt['thumbnail']}")
                    return fmt['thumbnail']
            
            # 嘗試從 entries 中查找縮圖 (對於播放列表)
            entries = info.get('entries', [])
            if entries and isinstance(entries, list) and len(entries) > 0:
                entry = entries[0]
                if isinstance(entry, dict):
                    # 嘗試 entry 的 thumbnail
                    if 'thumbnail' in entry and entry['thumbnail']:
                        logger.info(f"從 entries[0] 中找到縮圖: {entry['thumbnail']}")
                        return entry['thumbnail']
                    
                    # 嘗試 entry 的 thumbnails
                    entry_thumbnails = entry.get('thumbnails', [])
                    if entry_thumbnails and isinstance(entry_thumbnails, list) and len(entry_thumbnails) > 0:
                        if isinstance(entry_thumbnails[0], dict) and 'url' in entry_thumbnails[0]:
                            logger.info(f"從 entries[0].thumbnails 中找到縮圖: {entry_thumbnails[0]['url']}")
                            return entry_thumbnails[0]['url']
            
            thumbnails = []

        valid_thumbnails = [
            t for t in thumbnails
            if t.get('url') and isinstance(t.get('width'), int) and isinstance(t.get('height'), int)
            # and 'webp' not in t.get('url', '').lower() # 暫時移除 webp 過濾，觀察是否有更高解析度的 webp
        ]

        if not valid_thumbnails:
            logger.warning("縮圖列表為空或無有效條目")
            return None

        # 按面積降序排序 (寬 * 高)
        valid_thumbnails.sort(key=lambda x: x['width'] * x['height'], reverse=True)

        best_thumbnail = valid_thumbnails[0]
        logger.info(f"選擇的最佳縮圖 URL: {best_thumbnail['url']} (原始尺寸: {best_thumbnail.get('width')}x{best_thumbnail.get('height')})")
        return best_thumbnail['url']
