"""
下載引擎抽象模組

提供下載引擎的抽象基類和工廠類，用於處理不同平台的影片下載
"""

from abc import ABC, abstractmethod
import os
from typing import List, Dict, Any, Optional, Tuple, Callable
import yt_dlp

from core.url_utils import detect_platform, clean_url, extract_video_id

class DownloadEngine(ABC):
    """下載引擎抽象基類"""
    
    def __init__(self):
        """初始化下載引擎"""
        self.platform = self.get_platform_name()
    
    @abstractmethod
    def get_platform_name(self) -> str:
        """獲取平台名稱"""
        pass
    
    @abstractmethod
    def get_available_formats(self, url: str) -> List[Dict[str, Any]]:
        """
        獲取影片可用的畫質選項
        
        Args:
            url: 影片 URL
            
        Returns:
            格式列表，每個格式包含 height, ext, quality, filesize 等資訊
        """
        pass
    
    @abstractmethod
    def download(self, url: str, output_path: str, format_choice: str, 
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
        pass
    
    def prepare_download_options(self, url: str, output_path: str, format_choice: str,
                                height: Optional[int] = None, progress_hook: Optional[Callable] = None) -> Dict[str, Any]:
        """
        準備下載選項
        
        Args:
            url: 影片 URL
            output_path: 輸出路徑
            format_choice: 格式選擇 ("1" 表示影片, "2" 表示音訊)
            height: 影片高度 (畫質)，如 720, 1080 等
            progress_hook: 進度回調函數
            
        Returns:
            下載選項字典
        """
        # 確保輸出目錄存在
        os.makedirs(output_path, exist_ok=True)
        
        # 基本下載選項
        ydl_opts = {
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'concurrent_fragment_downloads': 8,
            'retries': 10,
            'fragment_retries': 10,
            'http_chunk_size': 52428800,
            'buffersize': 1024*64,
            'socket_timeout': 60,
            'file_access_retries': 10,
            'extractor_retries': 5,
            'throttledratelimit': None,
            'ratelimit': None,
            'overwrites': True,
            'continuedl': True,
            'noprogress': False,
            'max_sleep_interval': 3,
            'sleep_interval': 0.5,
        }
        
        # 設置進度回調
        if progress_hook:
            ydl_opts['progress_hooks'] = [progress_hook]
        
        # 設置外部下載器
        ydl_opts.update({
            'external_downloader': 'aria2c',
            'external_downloader_args': [
                '--min-split-size=1M',
                '--max-connection-per-server=16',
                '--split=16',
                '--max-concurrent-downloads=16',
                '--max-tries=10',
                '--retry-wait=3',
                '--auto-file-renaming=false',
                '--allow-overwrite=true',
                '--continue=true',
                '--timeout=120',
                '--connect-timeout=120',
                '--stream-piece-selector=inorder'
            ]
        })
        
        return ydl_opts
    
    def extract_info(self, url: str) -> Dict[str, Any]:
        """
        提取影片資訊
        
        Args:
            url: 影片 URL
            
        Returns:
            影片資訊字典
        """
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            return ydl.extract_info(url, download=False)


class YouTubeDownloadEngine(DownloadEngine):
    """YouTube 下載引擎"""
    
    def get_platform_name(self) -> str:
        """獲取平台名稱"""
        return "youtube"
    
    def get_available_formats(self, url: str) -> List[Dict[str, Any]]:
        """獲取影片可用的畫質選項"""
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                formats = []
                seen_qualities = set()
                
                # 過濾並整理格式列表
                for f in info['formats']:
                    if 'height' in f and f['height'] is not None and f.get('vcodec') != 'none':
                        quality = f'{f["height"]}p'
                        if quality not in seen_qualities:
                            filesize = f.get('filesize', 0)
                            if filesize == 0:
                                filesize_str = "未知大小"
                            else:
                                filesize_str = f"{filesize / (1024 * 1024):.1f}MB"
                            
                            formats.append({
                                'height': f['height'],
                                'ext': f['ext'],
                                'quality': quality,
                                'filesize': filesize,
                                'filesize_str': filesize_str,
                                'vcodec': f.get('vcodec', 'unknown')
                            })
                            seen_qualities.add(quality)
                
                # 按畫質排序
                formats.sort(key=lambda x: x['height'], reverse=True)
                return formats
            except Exception as e:
                print(f"獲取影片格式失敗: {str(e)}")
                return []
    
    def download(self, url: str, output_path: str, format_choice: str, 
                height: Optional[int] = None, progress_hook: Optional[Callable] = None) -> bool:
        """下載 YouTube 影片"""
        try:
            # 準備基本下載選項
            ydl_opts = self.prepare_download_options(url, output_path, format_choice, height, progress_hook)
            
            # 根據格式選擇設置特定選項
            if format_choice == "2":  # MP3
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'format_sort': ['acodec:m4a', 'acodec:mp3', 'acodec'],
                    'prefer_ffmpeg': True,
                })
            else:  # MP4
                if height:
                    ydl_opts.update({
                        'format': f'bestvideo[height={height}]+bestaudio/best',
                        'merge_output_format': 'mp4',
                        'postprocessors': [{
                            'key': 'FFmpegVideoRemuxer',
                            'preferedformat': 'mp4',
                        }],
                        'postprocessor_args': [
                            '-c:v', 'copy',
                            '-c:a', 'aac',
                            '-strict', 'experimental'
                        ],
                    })
                else:
                    ydl_opts.update({
                        'format': 'bestvideo+bestaudio/best',
                        'merge_output_format': 'mp4',
                        'postprocessors': [{
                            'key': 'FFmpegVideoRemuxer',
                            'preferedformat': 'mp4',
                        }],
                        'postprocessor_args': [
                            '-c:v', 'copy',
                            '-c:a', 'aac',
                            '-strict', 'experimental'
                        ],
                    })
            
            # 執行下載
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            return True
        except Exception as e:
            print(f"下載 YouTube 影片失敗: {str(e)}")
            return False


class BilibiliDownloadEngine(DownloadEngine):
    """Bilibili 下載引擎"""
    
    def get_platform_name(self) -> str:
        """獲取平台名稱"""
        return "bilibili"
    
    def get_available_formats(self, url: str) -> List[Dict[str, Any]]:
        """獲取影片可用的畫質選項"""
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'http_headers': {  # Bilibili 需要特定的 headers
                'Referer': 'https://www.bilibili.com',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                formats = []
                seen_qualities = set()
                
                # 過濾並整理格式列表
                for f in info['formats']:
                    if 'height' in f and f['height'] is not None and f.get('vcodec') != 'none':
                        quality = f'{f["height"]}p'
                        if quality not in seen_qualities:
                            filesize = f.get('filesize', 0)
                            if filesize == 0:
                                filesize_str = "未知大小"
                            else:
                                filesize_str = f"{filesize / (1024 * 1024):.1f}MB"
                            
                            formats.append({
                                'height': f['height'],
                                'ext': f['ext'],
                                'quality': quality,
                                'filesize': filesize,
                                'filesize_str': filesize_str,
                                'vcodec': f.get('vcodec', 'unknown')
                            })
                            seen_qualities.add(quality)
                
                # 按畫質排序
                formats.sort(key=lambda x: x['height'], reverse=True)
                return formats
            except Exception as e:
                print(f"獲取 Bilibili 影片格式失敗: {str(e)}")
                return []
    
    def download(self, url: str, output_path: str, format_choice: str, 
                height: Optional[int] = None, progress_hook: Optional[Callable] = None) -> bool:
        """下載 Bilibili 影片"""
        try:
            # 準備基本下載選項
            ydl_opts = self.prepare_download_options(url, output_path, format_choice, height, progress_hook)
            
            # Bilibili 特定的下載選項
            ydl_opts.update({
                'http_headers': {  # Bilibili 需要特定的 headers
                    'Referer': 'https://www.bilibili.com',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
            })
            
            # 根據格式選擇設置特定選項
            if format_choice == "2":  # MP3
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'format_sort': ['acodec:m4a', 'acodec:mp3', 'acodec'],
                    'prefer_ffmpeg': True,
                })
            else:  # MP4
                if height:
                    ydl_opts.update({
                        'format': f'bestvideo[height={height}]+bestaudio/best',
                        'merge_output_format': 'mp4',
                        'postprocessors': [{
                            'key': 'FFmpegVideoRemuxer',
                            'preferedformat': 'mp4',
                        }],
                        'postprocessor_args': [
                            '-c:v', 'copy',
                            '-c:a', 'aac',
                            '-strict', 'experimental'
                        ],
                    })
                else:
                    ydl_opts.update({
                        'format': 'bestvideo+bestaudio/best',
                        'merge_output_format': 'mp4',
                        'postprocessors': [{
                            'key': 'FFmpegVideoRemuxer',
                            'preferedformat': 'mp4',
                        }],
                        'postprocessor_args': [
                            '-c:v', 'copy',
                            '-c:a', 'aac',
                            '-strict', 'experimental'
                        ],
                    })
            
            # 執行下載
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            return True
        except Exception as e:
            print(f"下載 Bilibili 影片失敗: {str(e)}")
            return False


class DownloadEngineFactory:
    """下載引擎工廠類"""
    
    @staticmethod
    def create_engine(url: str) -> DownloadEngine:
        """
        根據 URL 創建適合的下載引擎
        
        Args:
            url: 影片 URL
            
        Returns:
            下載引擎實例
        """
        # 清理 URL
        url = clean_url(url)
        
        # 檢測平台
        platform = detect_platform(url)
        
        # 根據平台選擇引擎
        if platform == "youtube":
            return YouTubeDownloadEngine()
        elif platform == "bilibili":
            return BilibiliDownloadEngine()
        else:
            # 默認使用 YouTube 引擎
            return YouTubeDownloadEngine()
