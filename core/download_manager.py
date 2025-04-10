"""
下載管理器模組

整合下載引擎並提供統一的下載介面
"""

import os
from typing import List, Dict, Any, Optional, Tuple, Callable, Union

from core.download_engine import DownloadEngineFactory
from core.url_utils import clean_url, detect_platform, validate_url

class DownloadManager:
    """下載管理器類別，負責整合下載引擎並提供統一的下載介面"""
    
    def __init__(self):
        """初始化下載管理器"""
        self.factory = DownloadEngineFactory()
    
    def get_available_formats(self, url: str) -> List[Dict[str, Any]]:
        """
        獲取影片可用的畫質選項
        
        Args:
            url: 影片 URL
            
        Returns:
            格式列表，每個格式包含 height, ext, quality, filesize 等資訊
        """
        # 清理 URL
        url = clean_url(url)
        
        # 創建適合的下載引擎
        engine = self.factory.create_engine(url)
        
        # 獲取可用格式
        return engine.get_available_formats(url)
    
    def download_video(self, url: str, output_path: str, format_choice: str, 
                      height: Optional[int] = None, progress_hook: Optional[Callable] = None) -> bool:
        """
        下載影片
        
        Args:
            url: 影片 URL
            output_path: 輸出路徑
            format_choice: 格式選擇 ("1" 表示影片, "2" 表示音訊)
            height: 影片高度 (畫質)，如 720, 1080 等
            progress_hook: 進度回調函數
            
        Returns:
            下載是否成功
        """
        # 清理 URL
        url = clean_url(url)
        
        # 確保輸出目錄存在
        os.makedirs(output_path, exist_ok=True)
        
        # 創建適合的下載引擎
        engine = self.factory.create_engine(url)
        
        # 執行下載
        return engine.download(url, output_path, format_choice, height, progress_hook)
    
    def download(self, url: str, output_path: str, format_str: str = "best", 
                audio_only: bool = False, 
                progress_callback: Optional[Callable] = None,
                log_callback: Optional[Callable] = None) -> bool:
        """
        下載影片 (適用於 Qt 界面)
        
        Args:
            url: 影片 URL
            output_path: 輸出路徑
            format_str: 格式字串，如 "best", "1080p", "720p" 等
            audio_only: 是否僅下載音訊
            progress_callback: 進度回調函數，接收 (progress, filename, speed) 參數
            log_callback: 日誌回調函數，接收 (message, log_type) 參數
            
        Returns:
            下載是否成功
        """
        # 清理 URL
        url = clean_url(url)
        
        # 確保輸出目錄存在
        os.makedirs(output_path, exist_ok=True)
        
        # 創建適合的下載引擎
        engine = self.factory.create_engine(url)
        
        # 設置進度回調
        def progress_hook(d):
            if progress_callback:
                progress = d.get('percentage', 0)
                filename = d.get('filename', '').split('/')[-1].split('\\')[-1]
                speed = d.get('speed', '')
                
                # 格式化速度
                if isinstance(speed, (int, float)) and speed > 0:
                    if speed < 1024:
                        speed_str = f"{speed:.1f} B/s"
                    elif speed < 1024 * 1024:
                        speed_str = f"{speed/1024:.1f} KB/s"
                    else:
                        speed_str = f"{speed/(1024*1024):.1f} MB/s"
                else:
                    speed_str = ""
                
                progress_callback(progress, filename, speed_str)
            
            # 記錄下載狀態
            if log_callback:
                status = d.get('status', '')
                
                if status == 'downloading':
                    downloaded = d.get('downloaded_bytes', 0)
                    total = d.get('total_bytes', 0) or d.get('total_bytes_estimate', 0)
                    
                    if total > 0:
                        percent = downloaded / total * 100
                        log_callback(f"下載中: {percent:.1f}% ({self._format_size(downloaded)}/{self._format_size(total)})", 0)
                
                elif status == 'finished':
                    log_callback(f"下載完成: {d.get('filename', '')}", 1)
                
                elif status == 'error':
                    log_callback(f"下載錯誤: {d.get('error', '')}", 3)
        
        # 設置格式
        format_choice = "1"  # 預設為影片
        height = None
        
        if audio_only or format_str == "bestaudio":
            format_choice = "2"  # 音訊
        elif format_str == "best":
            format_choice = "1"  # 最佳品質影片
        elif format_str in ["1080p", "720p", "480p", "360p", "240p"]:
            format_choice = "1"
            # 從格式字串中提取高度
            try:
                height = int(format_str.replace("p", ""))
            except ValueError:
                if log_callback:
                    log_callback(f"無效的格式: {format_str}，使用最佳品質", 2)
        
        # 記錄開始下載
        if log_callback:
            platform = detect_platform(url)
            log_callback(f"開始從 {platform} 下載影片: {url}", 0)
            log_callback(f"下載格式: {format_str}{' (僅音訊)' if audio_only else ''}", 0)
            log_callback(f"下載位置: {output_path}", 0)
        
        # 執行下載
        try:
            result = engine.download(url, output_path, format_choice, height, progress_hook)
            
            # 記錄下載結果
            if log_callback:
                if result:
                    log_callback("下載成功完成！", 1)
                else:
                    log_callback("下載失敗！", 3)
            
            return result
        except Exception as e:
            # 記錄錯誤
            if log_callback:
                log_callback(f"下載過程中發生錯誤: {str(e)}", 3)
            return False
    
    def _format_size(self, size_bytes):
        """格式化檔案大小"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes/1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes/(1024*1024):.1f} MB"
        else:
            return f"{size_bytes/(1024*1024*1024):.1f} GB"
    
    def get_video_info(self, url: str) -> Dict[str, Any]:
        """
        獲取影片資訊
        
        Args:
            url: 影片 URL
            
        Returns:
            影片資訊字典
        """
        # 清理 URL
        url = clean_url(url)
        
        # 創建適合的下載引擎
        engine = self.factory.create_engine(url)
        
        # 獲取影片資訊
        return engine.extract_info(url)
    
    def get_platform(self, url: str) -> str:
        """
        獲取影片平台
        
        Args:
            url: 影片 URL
            
        Returns:
            平台名稱
        """
        # 清理 URL
        url = clean_url(url)
        
        # 檢測平台
        return detect_platform(url)


# 為了方便使用，提供模組級別的函數
_manager = DownloadManager()

def get_available_formats(url: str) -> List[Dict[str, Any]]:
    """
    獲取影片可用的畫質選項 (模組級別函數)
    
    Args:
        url: 影片 URL
        
    Returns:
        格式列表，每個格式包含 height, ext, quality, filesize 等資訊
    """
    return _manager.get_available_formats(url)

def download_video(url: str, output_path: str, format_choice: str, 
                  height: Optional[int] = None, progress_hook: Optional[Callable] = None) -> bool:
    """
    下載影片 (模組級別函數)
    
    Args:
        url: 影片 URL
        output_path: 輸出路徑
        format_choice: 格式選擇 ("1" 表示影片, "2" 表示音訊)
        height: 影片高度 (畫質)，如 720, 1080 等
        progress_hook: 進度回調函數
        
    Returns:
        下載是否成功
    """
    return _manager.download_video(url, output_path, format_choice, height, progress_hook)

def download(url: str, output_path: str, format_str: str = "best", 
            audio_only: bool = False, 
            progress_callback: Optional[Callable] = None,
            log_callback: Optional[Callable] = None) -> bool:
    """
    下載影片 (適用於 Qt 界面) (模組級別函數)
    
    Args:
        url: 影片 URL
        output_path: 輸出路徑
        format_str: 格式字串，如 "best", "1080p", "720p" 等
        audio_only: 是否僅下載音訊
        progress_callback: 進度回調函數，接收 (progress, filename, speed) 參數
        log_callback: 日誌回調函數，接收 (message, log_type) 參數
        
    Returns:
        下載是否成功
    """
    return _manager.download(url, output_path, format_str, audio_only, progress_callback, log_callback)

def get_video_info(url: str) -> Dict[str, Any]:
    """
    獲取影片資訊 (模組級別函數)
    
    Args:
        url: 影片 URL
        
    Returns:
        影片資訊字典
    """
    return _manager.get_video_info(url)

def get_platform(url: str) -> str:
    """
    獲取影片平台 (模組級別函數)
    
    Args:
        url: 影片 URL
        
    Returns:
        平台名稱
    """
    return _manager.get_platform(url)
