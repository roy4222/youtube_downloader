import yt_dlp
import os
from pathlib import Path
import sys
import math
import subprocess
import glob
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from threading import Thread
import datetime

# 設定 ffmpeg 路徑
def get_ffmpeg_path():
    if getattr(sys, 'frozen', False):
        # 如果是打包後的執行檔
        base_path = sys._MEIPASS
    else:
        # 如果是直接執行 Python 腳本
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    ffmpeg_path = os.path.join(base_path, 'ffmpeg.exe')
    return ffmpeg_path

# 設定 ffmpeg 路徑
os.environ["PATH"] = os.path.dirname(get_ffmpeg_path()) + os.pathsep + os.environ["PATH"]

def format_time(seconds):
    """將秒數轉換為時分秒格式"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"

def my_hook(d):
    """下載進度回調函數"""
    if d['status'] == 'downloading':
        try:
            # 計算下載進度
            if 'total_bytes' in d:
                total = d['total_bytes']
                downloaded = d['downloaded_bytes']
                percentage = (downloaded / total) * 100
                speed = d.get('speed', 0)
                
                # 更新GUI進度條（如果在GUI模式下）
                if hasattr(sys.stdout, 'gui_instance'):
                    gui = sys.stdout.gui_instance
                    gui.update_progress(percentage, speed)
                else:
                    if speed:
                        speed_mb = speed / 1024 / 1024  # 轉換為 MB/s
                        print(f"\r下載進度: {percentage:.1f}% (速度: {speed_mb:.1f} MB/s)", end='', file=sys.stderr)
                    else:
                        print(f"\r下載進度: {percentage:.1f}%", end='', file=sys.stderr)
                        
            elif 'total_bytes_estimate' in d:
                total = d['total_bytes_estimate']
                downloaded = d['downloaded_bytes']
                percentage = (downloaded / total) * 100
                speed = d.get('speed', 0)
                
                # 更新GUI進度條（如果在GUI模式下）
                if hasattr(sys.stdout, 'gui_instance'):
                    gui = sys.stdout.gui_instance
                    gui.update_progress(percentage, speed)
                else:
                    print(f"\r下載進度: {percentage:.1f}% (預估)", end='', file=sys.stderr)
        except Exception as e:
            print(f"\r下載中... (錯誤: {str(e)})", end='', file=sys.stderr)
    elif d['status'] == 'finished':
        if hasattr(sys.stdout, 'gui_instance'):
            gui = sys.stdout.gui_instance
            gui.update_status("下載完成，正在處理...")
        else:
            print("\n下載完成，正在處理...", file=sys.stderr)

def get_available_formats(url):
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

def sanitize_filename(filename):
    """清理檔案名稱，移除或替換不安全的字元"""
    # 替換不安全的字元
    unsafe_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in unsafe_chars:
        filename = filename.replace(char, '_')
    return filename

def merge_video_audio(video_file, audio_file, output_file):
    """合併視頻和音頻文件"""
    try:
        print("\n開始合併文件...")
        # 檢查文件是否存在
        if not os.path.exists(video_file):
            print(f"錯誤：視頻文件不存在: {video_file}")
            return False
        if not os.path.exists(audio_file):
            print(f"錯誤：音頻文件不存在: {audio_file}")
            return False
            
        # 首先獲取視頻時長
        duration = get_video_duration(video_file)
        
        # 使用不同的FFmpeg參數
        print("正在執行FFmpeg合併...")
        process = subprocess.Popen([
            'ffmpeg',
            '-hide_banner',
            '-i', video_file,
            '-i', audio_file,
            '-map', '0:v:0',
            '-map', '1:a:0',
            '-c:v', 'copy',
            '-c:a', 'copy',
            '-movflags', '+faststart',
            '-progress', 'pipe:1',
            '-y',
            output_file
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        
        # 設置超時時間（10分鐘）
        try:
            print("合併進度：")
            current_time = 0
            
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    if 'out_time_ms=' in output:
                        try:
                            time_ms = int(output.split('=')[1])
                            current_time = time_ms / 1000000  # 轉換為秒
                            if duration:
                                progress = min(100, (current_time / duration) * 100)
                                bar_length = 50
                                filled_length = int(bar_length * progress / 100)
                                bar = '=' * filled_length + '-' * (bar_length - filled_length)
                                print(f'\r[{bar}] {progress:.1f}%', end='', flush=True)
                        except:
                            pass
            
            print()  # 換行
            process.stdout.close()
            return_code = process.wait(timeout=600)
            
            # 檢查輸出文件是否成功創建
            if return_code == 0 and os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                print(f"\n成功合併為: {output_file}")
                try:
                    # 檢查合併後的視頻信息
                    if check_video_info(output_file):
                        # 只有在成功檢查視頻信息後才刪除原始文件
                        os.remove(video_file)
                        os.remove(audio_file)
                        print("已刪除原始分離文件")
                except Exception as e:
                    print(f"刪除原始文件時出錯: {str(e)}")
                return True
            else:
                print(f"\n合併失敗：輸出文件未創建或為空")
                stderr = process.stderr.read()
                if stderr:
                    print(f"FFmpeg錯誤輸出: {stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            process.kill()
            print("\nFFmpeg 合併超時，請檢查文件大小或系統資源")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"\nFFmpeg 合併失敗: {e.stderr if hasattr(e, 'stderr') else str(e)}")
        return False
    except Exception as e:
        print(f"\n合併過程出錯: {str(e)}")
        return False

def get_video_duration(video_file):
    """獲取視頻時長（秒）"""
    try:
        process = subprocess.run([
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            video_file
        ], capture_output=True, text=True)
        
        if process.returncode == 0:
            return float(process.stdout.strip())
    except:
        pass
    return None

def find_downloaded_files(output_path, base_filename):
    """找出下載的視頻和音頻文件"""
    video_file = None
    audio_file = None
    
    # 列出所有可能的文件
    files = list(Path(output_path).glob(f'{base_filename}.f*.*'))
    
    # 視頻格式ID列表
    video_format_ids = {137, 248, 299, 303, 271, 313, 616}  # 1080p和更高
    # 音頻格式ID列表
    audio_format_ids = {140, 251, 250, 249}
    
    for file in files:
        file_str = str(file)
        # 檢查文件是否為視頻或音頻
        if '.f' in file_str:  # 確認是格式化的文件名
            format_id = file_str.split('.f')[-1].split('.')[0]  # 提取格式ID
            try:
                format_id = int(format_id)
                if format_id in video_format_ids:
                    video_file = file_str
                elif format_id in audio_format_ids:
                    audio_file = file_str
                # 如果都不匹配，根據格式ID的大小來判斷
                elif not video_file and format_id > 300:
                    video_file = file_str
                elif not audio_file and format_id <= 300:
                    audio_file = file_str
            except ValueError:
                continue
    
    print(f"找到的視頻文件: {video_file}")
    print(f"找到的音頻文件: {audio_file}")
    
    return video_file, audio_file

def download_video(url, output_path=None, quality=None):
    """下載YouTube視頻或音頻"""
    if output_path is None:
        output_path = str(Path.home() / "Downloads")
    
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'progress_hooks': [my_hook],
        'ffmpeg_location': get_ffmpeg_path(),
        'verbose': True,
        'ignoreerrors': True,
        'no_warnings': False,
        'socket_timeout': 30,  # 設置socket超時
        'retries': 10,        # 重試次數
        'fragment_retries': 10,  # 分段下載重試次數
        'file_access_retries': 10,  # 檔案訪問重試次數
        'extractor_retries': 10,    # 提取器重試次數
        'external_downloader': 'aria2c',  # 使用aria2c作為外部下載器
        'external_downloader_args': [  # aria2c的參數設置
            '--min-split-size=1M',     # 最小分割大小
            '--max-connection-per-server=16',  # 每個伺服器最大連接數
            '--split=16',              # 同時下載的分段數
            '--max-tries=10',          # 重試次數
            '--retry-wait=3',          # 重試等待時間
            '--connect-timeout=10',    # 連接超時
            '--timeout=10',            # 超時設置
            '--auto-file-renaming=true',  # 自動重命名
            '--allow-overwrite=true',     # 允許覆寫
            '--continue=true',            # 支援斷點續傳
        ],
    }
    
    if quality:
        ydl_opts['format'] = f'bestvideo[height<={quality}]+bestaudio/best[height<={quality}]'
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                # 先獲取影片信息
                info = ydl.extract_info(url, download=False)
                if info.get('duration', 0) > 7200:  # 如果影片超過2小時
                    print("注意：這是較長的影片，下載可能需要較長時間，請耐心等待...", file=sys.stderr)
                
                # 開始下載
                ydl.download([url])
                return True, None
            except Exception as e:
                error_msg = f"下載過程中發生錯誤: {str(e)}"
                print(error_msg, file=sys.stderr)
                return False, error_msg
    except Exception as e:
        error_msg = f"初始化下載器時發生錯誤: {str(e)}"
        print(error_msg, file=sys.stderr)
        return False, error_msg

def check_video_info(video_file):
    """檢查視頻文件的信息"""
    try:
        print(f"\n正在檢查視頻文件: {os.path.basename(video_file)}")
        # 使用絕對路徑
        video_file = os.path.abspath(video_file)
        
        process = subprocess.run([
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height,r_frame_rate,codec_name',
            '-of', 'json',
            video_file
        ], capture_output=True, text=True, shell=True)
        
        if process.returncode == 0:
            import json
            info = json.loads(process.stdout)
            if 'streams' in info and info['streams']:
                stream = info['streams'][0]
                width = stream.get('width', '未知')
                height = stream.get('height', '未知')
                codec = stream.get('codec_name', '未知')
                fps = stream.get('r_frame_rate', '').split('/')
                if len(fps) == 2:
                    try:
                        fps = round(float(fps[0]) / float(fps[1]), 2)
                    except:
                        fps = '未知'
                else:
                    fps = '未知'
                
                print(f"\n視頻信息:")
                print(f"分辨率: {width}x{height}")
                print(f"編碼格式: {codec}")
                print(f"幀率: {fps} FPS")
                
                # 計算文件大小
                size_bytes = os.path.getsize(video_file)
                size_mb = size_bytes / (1024 * 1024)
                print(f"文件大小: {size_mb:.2f} MB")
                
                return True
        
        print("無法獲取視頻信息")
        if process.stderr:
            print(f"錯誤信息: {process.stderr}")
        return False
        
    except Exception as e:
        print(f"檢查視頻文件時出錯: {str(e)}")
        return False

class YouTubeDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube 影片下載器")
        
        # 主框架
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # URL輸入框架
        url_frame = ttk.LabelFrame(self.main_frame, text="影片網址", padding="5")
        url_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(url_frame, textvariable=self.url_var, width=70)
        self.url_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        ttk.Button(url_frame, text="貼上", command=self.paste_url).grid(row=0, column=1, padx=5)
        
        # 下載位置框架
        path_frame = ttk.LabelFrame(self.main_frame, text="下載位置", padding="5")
        path_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        self.output_path_var = tk.StringVar(value=str(Path.home() / "Downloads"))
        self.output_path_entry = ttk.Entry(path_frame, textvariable=self.output_path_var, width=60)
        self.output_path_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        ttk.Button(path_frame, text="瀏覽", command=self.browse_output_path).grid(row=0, column=1, padx=5)
        
        # 格式選擇框架
        format_frame = ttk.LabelFrame(self.main_frame, text="下載格式", padding="5")
        format_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        self.format_var = tk.StringVar(value="1")
        ttk.Radiobutton(format_frame, text="一般版 (MP4 + 音頻)", variable=self.format_var, value="1").grid(row=0, column=0, padx=20)
        ttk.Radiobutton(format_frame, text="純音樂 (MP3)", variable=self.format_var, value="2").grid(row=0, column=1, padx=20)
        
        # 進度框架
        self.progress_frame = ttk.LabelFrame(self.main_frame, text="下載進度", padding="5")
        self.progress_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # 進度條
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.progress_frame, 
                                          variable=self.progress_var,
                                          mode='determinate',
                                          length=400)  # 加長進度條
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # 進度標籤
        self.progress_label = ttk.Label(self.progress_frame, text="準備下載...")
        self.progress_label.grid(row=1, column=0, sticky=(tk.W), padx=5, pady=2)
        
        # 速度標籤
        self.speed_label = ttk.Label(self.progress_frame, text="")
        self.speed_label.grid(row=2, column=0, sticky=(tk.W), padx=5, pady=2)
        
        # 輸出文本框
        self.output_text = tk.Text(self.main_frame, height=10, width=80, wrap=tk.WORD)
        self.output_text.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # 添加滾動條
        scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.output_text.yview)
        scrollbar.grid(row=4, column=3, sticky=(tk.N, tk.S))
        self.output_text.configure(yscrollcommand=scrollbar.set)
        
        # 下載按鈕
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=10)
        
        self.download_button = ttk.Button(button_frame, text="開始下載", command=self.start_download)
        self.download_button.grid(row=0, column=0, padx=5)
        
        self.complete_button = ttk.Button(button_frame, text="完成", command=self.close_window)
        self.complete_button.grid(row=0, column=1, padx=5)
        
        # 配置grid權重
        self.main_frame.columnconfigure(1, weight=1)
        self.progress_frame.columnconfigure(0, weight=1)
        
        # 重定向標準輸出到GUI
        sys.stdout = self
        sys.stderr = self
        
        # 設置GUI實例到stdout
        sys.stdout.gui_instance = self
        sys.stderr.gui_instance = self
    
    def write(self, text):
        """重定向輸出到GUI"""
        try:
            # 處理aria2c的進度
            if "[#" in text and "CN:" in text and "DL:" in text:
                import re
                progress_match = re.search(r'\((\d+)%\)', text)
                speed_match = re.search(r'DL:(\d+\.?\d*)(\w+)', text)
                
                if progress_match:
                    percentage = float(progress_match.group(1))
                    self.progress_var.set(percentage)
                    self.progress_label.config(text=f"下載進度: {percentage:.1f}%")
                
                if speed_match:
                    speed_val = float(speed_match.group(1))
                    speed_unit = speed_match.group(2)
                    if speed_unit == 'GiB':
                        speed_mb = speed_val * 1024
                    elif speed_unit == 'MiB':
                        speed_mb = speed_val
                    elif speed_unit == 'KiB':
                        speed_mb = speed_val / 1024
                    else:
                        speed_mb = speed_val / (1024 * 1024)
                    
                    self.speed_label.config(text=f"下載速度: {speed_mb:.1f} MB/s")
            
            # 處理yt-dlp的進度
            elif "[download]" in text and "%" in text:
                try:
                    # 解析進度信息
                    parts = text.split()
                    for part in parts:
                        if "%" in part:
                            percentage = float(part.replace("%", ""))
                            self.progress_var.set(percentage)
                            self.progress_label.config(text=f"下載進度: {percentage:.1f}%")
                        elif "at" in parts and parts.index(part) == parts.index("at") + 1:
                            speed = part
                            if speed.endswith("/s"):
                                speed_val = float(speed[:-3])
                                if speed.endswith("KiB/s"):
                                    speed_mb = speed_val / 1024
                                elif speed.endswith("MiB/s"):
                                    speed_mb = speed_val
                                elif speed.endswith("GiB/s"):
                                    speed_mb = speed_val * 1024
                                else:
                                    speed_mb = speed_val / (1024 * 1024)
                                self.speed_label.config(text=f"下載速度: {speed_mb:.1f} MB/s")
                except Exception as e:
                    print(f"Progress parsing error: {str(e)}")
            
            # 更新界面
            self.root.update()
            
            # 將文本添加到輸出框
            self.output_text.insert(tk.END, text)
            self.output_text.see(tk.END)
            self.output_text.update()
            
        except Exception as e:
            print(f"Write error: {str(e)}")
            self.output_text.insert(tk.END, text)
            self.output_text.see(tk.END)
            self.output_text.update()
    
    def flush(self):
        pass
        
    def paste_url(self):
        try:
            url = self.root.clipboard_get()
            if "youtube.com" in url or "youtu.be" in url:
                self.url_var.set(url)
        except:
            pass
            
    def browse_output_path(self):
        directory = filedialog.askdirectory(initialdir=self.output_path_var.get())
        if directory:
            self.output_path_var.set(directory)
    
    def clear_output(self):
        self.output_text.delete(1.0, tk.END)
    
    def start_download(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("錯誤", "請輸入YouTube URL")
            return
        
        output_path = self.output_path_var.get()
        if not output_path:
            messagebox.showerror("錯誤", "請選擇下載位置")
            return
        
        self.clear_output()
        self.download_button.state(['disabled'])
        Thread(target=self.download_thread, args=(url, output_path)).start()
    
    def download_thread(self, url, output_path):
        try:
            os.makedirs(output_path, exist_ok=True)
            
            # 獲取視頻信息
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                
            video_title = info.get('title', 'video')
            filename = os.path.join(output_path, f"{video_title}.{'mp3' if self.format_var.get() == '2' else 'mp4'}")
            
            if os.path.exists(filename):
                if not messagebox.askyesno("文件已存在", 
                    f"文件 '{os.path.basename(filename)}' 已存在。\n是否要重新下載？"):
                    self.write("\n已取消下載：文件已存在\n")
                    self.reset_ui()
                    return
            
            # 顯示視頻信息
            self.write(f"\n====== 視頻信息 ======\n")
            self.write(f"標題: {info.get('title', 'Unknown')}\n")
            self.write(f"時長: {format_time(info.get('duration', 0))}\n")
            self.write(f"觀看次數: {info.get('view_count', 0):,}\n")
            self.write("==================\n\n")
            
            format_choice = self.format_var.get()
            if format_choice == "1":  # MP4
                formats = get_available_formats(url)
                if formats:
                    self.show_quality_options(url, formats, output_path)
                else:
                    self.download_with_format(url, output_path, format_choice)
            else:  # MP3
                self.download_with_format(url, output_path, format_choice)
                
        except Exception as e:
            error_msg = str(e)
            if "HTTP Error 429" in str(e):
                error_msg = "YouTube 暫時限制了下載請求，請稍後再試"
            elif "This video is not available" in str(e):
                error_msg = "此影片可能有版權限制或地區限制"
            self.write(f"\n下載失敗: {error_msg}\n")
            messagebox.showerror("錯誤", error_msg)
        finally:
            self.reset_ui()
    
    def reset_ui(self):
        """重置UI狀態"""
        self.download_button.state(['!disabled'])  # 啟用下載按鈕
        self.url_var.set("")  # 清空URL
        self.progress_var.set(0)  # 重置進度條
        self.progress_label.config(text="準備下載...")  # 重置進度標籤
        self.speed_label.config(text="")  # 清空速度標籤
    
    def update_progress(self, percentage, speed=0):
        """更新下載進度和速度"""
        self.progress_var.set(percentage)
        speed_text = f"下載速度: {speed/1024/1024:.1f} MB/s" if speed > 0 else ""
        self.progress_label.config(text=f"下載進度: {percentage:.1f}%")
        self.speed_label.config(text=speed_text)
        self.root.update()
    
    def update_status(self, status):
        """更新狀態文本"""
        self.progress_label.config(text=status)
        self.root.update()
    
    def show_quality_options(self, url, formats, output_path):
        def on_quality_select():
            quality_window.destroy()  # Close the window first
            choice = quality_var.get()
            if choice and choice.isdigit() and 1 <= int(choice) <= len(formats):
                selected_format = formats[int(choice)-1]
                self.download_with_quality(url, output_path, selected_format['height'])
            else:
                self.download_with_quality(url, output_path, None)
        
        quality_window = tk.Toplevel(self.root)
        quality_window.title("選擇畫質")
        
        # 主框架
        main_frame = ttk.Frame(quality_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 標題標籤
        ttk.Label(main_frame, text="可用的畫質選項：", font=('', 10, 'bold')).pack(pady=(0,10))
        
        # 選項框架
        options_frame = ttk.Frame(main_frame)
        options_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        quality_var = tk.StringVar(value="0")
        
        # 添加最佳畫質選項
        ttk.Radiobutton(options_frame, 
                       text="最佳畫質 (自動選擇)", 
                       variable=quality_var, 
                       value="0").pack(anchor=tk.W, pady=2)
        
        # 添加分隔線
        ttk.Separator(options_frame, orient='horizontal').pack(fill='x', pady=5)
        
        # 添加其他畫質選項
        for i, fmt in enumerate(formats, 1):
            ttk.Radiobutton(options_frame, 
                          text=f"{fmt['quality']} ({fmt['ext']}) - {fmt['filesize_str']}", 
                          variable=quality_var, 
                          value=str(i)).pack(anchor=tk.W, pady=2)
        
        # 按鈕框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(10,0))
        
        # 確定按鈕
        confirm_button = ttk.Button(button_frame, 
                                  text="確定", 
                                  command=on_quality_select)
        confirm_button.pack(side=tk.RIGHT, padx=5)
        
        # 取消按鈕
        cancel_button = ttk.Button(button_frame, 
                                 text="取消", 
                                 command=quality_window.destroy)
        cancel_button.pack(side=tk.RIGHT, padx=5)
        
        # 設置默認焦點到確定按鈕
        confirm_button.focus_set()
        
        # 綁定回車鍵到確定按鈕
        quality_window.bind('<Return>', lambda e: confirm_button.invoke())
        
        # 綁定Esc鍵到取消按鈕
        quality_window.bind('<Escape>', lambda e: cancel_button.invoke())
        
        # 調整窗口大小以適應內容
        quality_window.update_idletasks()
        window_width = quality_window.winfo_reqwidth() + 20
        window_height = quality_window.winfo_reqheight() + 20
        quality_window.geometry(f"{window_width}x{window_height}")
        
        # 設置為模態窗口
        quality_window.transient(self.root)
        quality_window.grab_set()
        
        # 等待窗口關閉
        quality_window.wait_window()
        
    def download_with_quality(self, url, output_path, height):
        ydl_opts = {
            'format': f'bestvideo[height<={height}]+bestaudio/best[height<={height}]' if height else 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegVideoRemuxer',
                'preferedformat': 'mp4',
            }],
            'postprocessor_args': [
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-strict', 'experimental'
            ],
            # 優化選項
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
            'progress_hooks': [my_hook],
            'external_downloader': 'aria2c',
            'external_downloader_args': [
                '--min-split-size=1M',
                '--max-connection-per-server=16',
                '--split=16',
                '--max-concurrent-downloads=8',
                '--min-tls-version=TLSv1.2',
                '--optimize-concurrent-downloads=true',
                '--file-allocation=none',
                '--async-dns=true',
                '--disable-ipv6=true',
                '--summary-interval=1',  # 更頻繁地更新進度
                '--console-log-level=notice'  # 確保輸出進度信息
            ]
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.write("\n下載完成！\n")
        except Exception as e:
            raise e
    
    def download_with_format(self, url, output_path, format_choice):
        if format_choice == "2":  # MP3
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'format_sort': ['acodec:m4a', 'acodec:mp3', 'acodec'],
                'prefer_ffmpeg': True,
                # 優化選項
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
                'progress_hooks': [my_hook],
                'external_downloader': 'aria2c',
                'external_downloader_args': [
                    '--min-split-size=1M',
                    '--max-connection-per-server=16',
                    '--split=16',
                    '--max-concurrent-downloads=8',
                    '--min-tls-version=TLSv1.2',
                    '--optimize-concurrent-downloads=true',
                    '--file-allocation=none',
                    '--async-dns=true',
                    '--disable-ipv6=true'
                ]
            }
        else:  # MP4
            ydl_opts = {
                'format': 'bestvideo+bestaudio/best',
                'merge_output_format': 'mp4',
                'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegVideoRemuxer',
                    'preferedformat': 'mp4',
                }],
                # FFmpeg設置
                'postprocessor_args': [
                    '-c:v', 'copy',
                    '-c:a', 'aac',
                    '-strict', 'experimental'
                ],
                # 優化選項
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
                'progress_hooks': [my_hook],
                'external_downloader': 'aria2c',
                'external_downloader_args': [
                    '--min-split-size=1M',
                    '--max-connection-per-server=16',
                    '--split=16',
                    '--max-concurrent-downloads=8',
                    '--min-tls-version=TLSv1.2',
                    '--optimize-concurrent-downloads=true',
                    '--file-allocation=none',
                    '--async-dns=true',
                    '--disable-ipv6=true'
                ]
            }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.write("\n下載完成！\n")
        except Exception as e:
            raise e

    def close_window(self):
        """關閉視窗"""
        self.root.destroy()

def format_bytes(size):
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(size) < 1024.0:
            return f"{size:3.1f}{unit}B"
        size /= 1024.0
    return f"{size:.1f}YB"

def main():
    root = tk.Tk()
    app = YouTubeDownloaderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()