"""
主應用程式視窗

整合所有 UI 元件，提供完整的下載功能
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from threading import Thread
from typing import Optional, Dict, Any, List

from ui.url_frame import UrlInputFrame
from ui.path_frame import PathSelectionFrame
from ui.format_frame import FormatSelectionFrame
from ui.progress_frame import ProgressFrame
from ui.output_frame import OutputFrame
from ui.quality_dialog import QualityDialog

from core.url_utils import clean_url, detect_platform, validate_url
from core.download_manager import get_available_formats, download_video, get_video_info, get_platform


class MainWindow:
    """主應用程式視窗類別"""
    
    def __init__(self, root):
        """
        初始化主應用程式視窗
        
        Args:
            root: Tkinter 根視窗
        """
        self.root = root
        self.root.title("影片下載器")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        
        # 設置圖標 (如果有)
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
        
        # 創建主框架
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 創建 UI 元件
        self._create_widgets()
        
        # 綁定事件
        self._bind_events()
        
        # 重定向標準輸出到 GUI
        sys.stdout = self.output_frame
        sys.stderr = self.output_frame
    
    def _create_widgets(self):
        """創建 UI 元件"""
        # URL 輸入框架
        self.url_frame = UrlInputFrame(self.main_frame)
        self.url_frame.pack(fill=tk.X, pady=5)
        
        # 下載位置選擇框架
        self.path_frame = PathSelectionFrame(self.main_frame)
        self.path_frame.pack(fill=tk.X, pady=5)
        
        # 格式選擇框架
        self.format_frame = FormatSelectionFrame(self.main_frame)
        self.format_frame.pack(fill=tk.X, pady=5)
        
        # 進度顯示框架
        self.progress_frame = ProgressFrame(self.main_frame)
        self.progress_frame.pack(fill=tk.X, pady=5)
        
        # 輸出文本框架
        self.output_frame = OutputFrame(
            self.main_frame, 
            progress_callback=self.progress_frame.update_progress
        )
        self.output_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 按鈕框架
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(fill=tk.X, pady=5)
        
        # 下載按鈕
        self.download_button = ttk.Button(
            self.button_frame, 
            text="開始下載", 
            command=self.start_download
        )
        self.download_button.pack(side=tk.LEFT, padx=5)
        
        # 退出按鈕
        self.exit_button = ttk.Button(
            self.button_frame, 
            text="退出", 
            command=self.close_window
        )
        self.exit_button.pack(side=tk.RIGHT, padx=5)
    
    def _bind_events(self):
        """綁定事件"""
        # 關閉視窗時的處理
        self.root.protocol("WM_DELETE_WINDOW", self.close_window)
        
        # 按鍵綁定
        self.root.bind("<Escape>", lambda e: self.close_window())
        self.root.bind("<Control-q>", lambda e: self.close_window())
        self.root.bind("<Control-d>", lambda e: self.download_button.invoke())
    
    def start_download(self):
        """開始下載"""
        # 獲取 URL
        url = self.url_frame.get_url()
        if not url:
            messagebox.showerror("錯誤", "請輸入 YouTube 或 Bilibili URL")
            return
        
        # 獲取下載位置
        output_path = self.path_frame.get_path()
        if not output_path:
            messagebox.showerror("錯誤", "請選擇下載位置")
            return
        
        # 清除輸出
        self.output_frame.clear()
        
        # 禁用下載按鈕
        self.download_button.state(['disabled'])
        
        # 啟動下載線程
        Thread(target=self.download_thread, args=(url, output_path)).start()
    
    def download_thread(self, url, output_path):
        """
        在後台執行下載任務
        
        Args:
            url: 影片 URL
            output_path: 輸出路徑
        """
        try:
            self.progress_frame.update_status("正在獲取影片資訊...")
            
            # 使用 URL 處理模組清理 URL
            original_url = url
            url = clean_url(url)
            
            if url != original_url:
                print(f"已清理 URL: {url}")
                
            # 檢測平台
            platform = get_platform(url)
            if platform != "unknown":
                print(f"檢測到平台: {platform.capitalize()}")
            
            # 確保輸出目錄存在
            os.makedirs(output_path, exist_ok=True)
            
            # 獲取視頻信息
            try:
                # 使用下載管理器獲取影片資訊
                info = get_video_info(url)
                    
                video_title = info.get('title', 'video')
                format_choice = self.format_frame.get_format()
                filename = os.path.join(output_path, f"{video_title}.{'mp3' if format_choice == '2' else 'mp4'}")
                
                # 檢查文件是否已存在
                if os.path.exists(filename):
                    if not messagebox.askyesno("文件已存在", 
                        f"文件 '{os.path.basename(filename)}' 已存在。\n是否要重新下載？"):
                        print("\n已取消下載：文件已存在")
                        self.reset_ui()
                        return
                
                # 顯示視頻信息
                print(f"\n====== 視頻信息 ======")
                print(f"標題: {info.get('title', 'Unknown')}")
                print(f"時長: {format_time(info.get('duration', 0))}")
                print(f"觀看次數: {info.get('view_count', 0):,}")
                
                # 顯示平台特定資訊
                if platform == "youtube":
                    print(f"頻道: {info.get('channel', 'Unknown')}")
                    print(f"上傳日期: {info.get('upload_date', 'Unknown')}")
                elif platform == "bilibili":
                    print(f"UP主: {info.get('uploader', 'Unknown')}")
                    
                print("==================\n")
                
                if format_choice == "1":  # MP4
                    # 使用下載管理器獲取可用格式
                    formats = get_available_formats(url)
                    if formats:
                        self.show_quality_options(url, formats, output_path)
                    else:
                        # 使用下載管理器下載影片
                        self.download_with_format(url, output_path, format_choice)
                else:  # MP3
                    # 使用下載管理器下載音訊
                    self.download_with_format(url, output_path, format_choice)
            
            except Exception as e:
                print(f"無法獲取影片資訊，嘗試直接下載: {str(e)}")
                # 如果無法獲取資訊，嘗試直接下載
                format_choice = self.format_frame.get_format()
                self.download_with_format(url, output_path, format_choice)
                
        except Exception as e:
            error_msg = str(e)
            if "HTTP Error 429" in str(e):
                error_msg = "YouTube 暫時限制了下載請求，請稍後再試"
            elif "This video is not available" in str(e):
                error_msg = "此影片可能有版權限制或地區限制"
            print(f"\n下載失敗: {error_msg}")
            messagebox.showerror("錯誤", error_msg)
        finally:
            self.reset_ui()
    
    def show_quality_options(self, url: str, formats: List[Dict[str, Any]], output_path: str):
        """
        顯示畫質選擇對話框
        
        Args:
            url: 影片 URL
            formats: 可用的畫質格式列表
            output_path: 輸出路徑
        """
        # 創建畫質選擇對話框
        dialog = QualityDialog(self.root, formats)
        
        # 等待用戶選擇
        selected_format = dialog.wait_for_result()
        
        # 處理選擇結果
        if selected_format:
            self.download_with_quality(url, output_path, selected_format['height'])
        else:
            self.download_with_quality(url, output_path, None)
    
    def download_with_quality(self, url: str, output_path: str, height: Optional[int]):
        """
        使用指定畫質下載影片
        
        Args:
            url: 影片 URL
            output_path: 輸出路徑
            height: 影片高度 (畫質)，如 720, 1080 等
        """
        try:
            print(f"\n開始下載影片，畫質: {height}p..." if height else "\n開始下載影片，最佳畫質...")
            
            # 使用下載管理器下載影片
            success = download_video(url, output_path, "1", height)
            
            if success:
                print("\n下載完成！")
            else:
                print("\n下載失敗，請檢查網路連線或嘗試其他畫質")
                
        except Exception as e:
            print(f"\n下載失敗: {str(e)}")
            raise e
    
    def download_with_format(self, url: str, output_path: str, format_choice: str):
        """
        使用指定格式下載影片或音訊
        
        Args:
            url: 影片 URL
            output_path: 輸出路徑
            format_choice: 格式選擇 ("1" 表示影片, "2" 表示音訊)
        """
        try:
            if format_choice == "2":  # MP3
                print("\n開始下載音訊 (MP3)...")
            else:  # MP4
                print("\n開始下載影片 (MP4)...")
            
            # 使用下載管理器下載
            success = download_video(url, output_path, format_choice, None)
            
            if success:
                print("\n下載完成！")
            else:
                print("\n下載失敗，請檢查網路連線或嘗試其他格式")
                
        except Exception as e:
            print(f"\n下載失敗: {str(e)}")
            raise e
    
    def reset_ui(self):
        """重置 UI 狀態"""
        self.download_button.state(['!disabled'])  # 啟用下載按鈕
        self.url_frame.set_url("")  # 清空 URL
        self.progress_frame.reset()  # 重置進度顯示
    
    def close_window(self):
        """關閉視窗"""
        if messagebox.askokcancel("確認退出", "確定要退出程式嗎？"):
            self.root.destroy()


def format_time(seconds):
    """
    將秒數轉換為時分秒格式
    
    Args:
        seconds: 秒數
        
    Returns:
        格式化的時間字符串
    """
    if not seconds:
        return "未知時長"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    
    if hours > 0:
        return f"{int(hours)}:{int(minutes):02d}:{int(seconds):02d}"
    else:
        return f"{int(minutes):02d}:{int(seconds):02d}"
