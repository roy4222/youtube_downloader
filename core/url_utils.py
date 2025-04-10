"""
URL 處理工具模組

負責處理和清理不同平台的影片 URL，支援多種格式和平台
"""

import re
from typing import Optional, List, Dict, Tuple

class UrlProcessor:
    """URL 處理器類別，負責處理和清理不同平台的影片 URL"""
    
    # 支援的平台
    PLATFORM_YOUTUBE = "youtube"
    PLATFORM_BILIBILI = "bilibili"
    PLATFORM_UNKNOWN = "unknown"
    
    # URL 模式
    _URL_PATTERNS = {
        PLATFORM_YOUTUBE: [
            # 標準 YouTube URL
            r'(https?://(?:www\.)?youtube\.com/watch\?v=[\w\-]+[^\s]*)',
            # YouTube 短網址
            r'(https?://(?:www\.)?youtu\.be/[\w\-]+[^\s]*)'
        ],
        PLATFORM_BILIBILI: [
            # 標準 Bilibili URL (BV 格式)
            r'(https?://(?:www\.)?bilibili\.com/video/(?:BV[\w]+)/?[^\s\?"]*)',
            # 標準 Bilibili URL (av 格式)
            r'(https?://(?:www\.)?bilibili\.com/video/(?:av\d+)/?[^\s\?"]*)',
            # Bilibili 短網址
            r'(https?://b23\.tv/[\w]+/?[^\s\?"]*)'
        ]
    }
    
    @classmethod
    def clean_url(cls, url: str) -> str:
        """
        清理並提取有效的影片 URL
        
        Args:
            url: 原始 URL 字串，可能包含額外文字或參數
            
        Returns:
            清理後的 URL
        """
        if not url:
            return url
            
        # 檢查並清理各平台 URL
        platform = cls.detect_platform(url)
        
        if platform == cls.PLATFORM_UNKNOWN:
            return url
            
        patterns = cls._URL_PATTERNS.get(platform, [])
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                clean_url = match.group(1)
                
                # 處理 YouTube 的特殊情況，保留 v= 參數
                if platform == cls.PLATFORM_YOUTUBE and "youtube.com" in clean_url:
                    # 保留 v 參數但移除其他參數
                    video_id_match = re.search(r'v=([\w\-]+)', clean_url)
                    if video_id_match:
                        video_id = video_id_match.group(1)
                        return f"https://www.youtube.com/watch?v={video_id}"
                
                # 移除 Bilibili URL 中的多餘參數
                if platform == cls.PLATFORM_BILIBILI and '?' in clean_url:
                    clean_url = clean_url.split('?')[0]
                
                return clean_url
        
        return url
    
    @classmethod
    def detect_platform(cls, url: str) -> str:
        """
        檢測 URL 所屬的平台
        
        Args:
            url: 原始 URL 字串
            
        Returns:
            平台識別字串，如 "youtube", "bilibili" 或 "unknown"
        """
        if not url:
            return cls.PLATFORM_UNKNOWN
            
        if "youtube.com" in url or "youtu.be" in url:
            return cls.PLATFORM_YOUTUBE
            
        if "bilibili.com" in url or "b23.tv" in url:
            return cls.PLATFORM_BILIBILI
            
        return cls.PLATFORM_UNKNOWN
    
    @classmethod
    def validate_url(cls, url: str) -> bool:
        """
        驗證 URL 是否為有效的影片 URL
        
        Args:
            url: 要驗證的 URL
            
        Returns:
            布林值，表示 URL 是否有效
        """
        if not url:
            return False
            
        platform = cls.detect_platform(url)
        if platform == cls.PLATFORM_UNKNOWN:
            return False
            
        # 嘗試清理 URL，如果清理後與原 URL 不同，表示找到了有效的 URL 模式
        cleaned_url = cls.clean_url(url)
        return cleaned_url != url or any(
            re.search(pattern, url) for pattern in cls._URL_PATTERNS.get(platform, [])
        )
    
    @classmethod
    def extract_video_id(cls, url: str) -> Optional[str]:
        """
        從 URL 中提取影片 ID
        
        Args:
            url: 影片 URL
            
        Returns:
            影片 ID 或 None (如果無法提取)
        """
        if not url:
            return None
            
        platform = cls.detect_platform(url)
        
        if platform == cls.PLATFORM_YOUTUBE:
            # 提取 YouTube 影片 ID
            if "youtube.com" in url:
                match = re.search(r'v=([\w\-]+)', url)
                if match:
                    return match.group(1)
            elif "youtu.be" in url:
                match = re.search(r'youtu\.be/([\w\-]+)', url)
                if match:
                    return match.group(1)
                    
        elif platform == cls.PLATFORM_BILIBILI:
            # 提取 Bilibili 影片 ID
            if "bilibili.com" in url:
                # BV 格式
                bv_match = re.search(r'video/(BV[\w]+)', url)
                if bv_match:
                    return bv_match.group(1)
                    
                # av 格式
                av_match = re.search(r'video/av(\d+)', url)
                if av_match:
                    return f"av{av_match.group(1)}"
            
            # 短網址需要額外處理，這裡暫不實現
                    
        return None

# 為了向後兼容，提供模組級別的函數
def clean_url(url: str) -> str:
    """
    清理並提取有效的影片 URL (向後兼容函數)
    
    Args:
        url: 原始 URL 字串，可能包含額外文字或參數
        
    Returns:
        清理後的 URL
    """
    return UrlProcessor.clean_url(url)

def detect_platform(url: str) -> str:
    """
    檢測 URL 所屬的平台 (向後兼容函數)
    
    Args:
        url: 原始 URL 字串
        
    Returns:
        平台識別字串，如 "youtube", "bilibili" 或 "unknown"
    """
    return UrlProcessor.detect_platform(url)

def validate_url(url: str) -> bool:
    """
    驗證 URL 是否為有效的影片 URL (向後兼容函數)
    
    Args:
        url: 要驗證的 URL
        
    Returns:
        布林值，表示 URL 是否有效
    """
    return UrlProcessor.validate_url(url)

def extract_video_id(url: str) -> Optional[str]:
    """
    從 URL 中提取影片 ID (向後兼容函數)
    
    Args:
        url: 影片 URL
        
    Returns:
        影片 ID 或 None (如果無法提取)
    """
    return UrlProcessor.extract_video_id(url)
