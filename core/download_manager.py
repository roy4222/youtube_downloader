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
