import yt_dlp
import os
from pathlib import Path
import sys
import math
import subprocess
import glob
import time

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
                if speed:
                    speed_mb = speed / 1024 / 1024  # 轉換為 MB/s
                    print(f"\r下載進度: {percentage:.1f}% (速度: {speed_mb:.1f} MB/s)", end='', file=sys.stderr)
                else:
                    print(f"\r下載進度: {percentage:.1f}%", end='', file=sys.stderr)
            elif 'total_bytes_estimate' in d:
                total = d['total_bytes_estimate']
                downloaded = d['downloaded_bytes']
                percentage = (downloaded / total) * 100
                print(f"\r下載進度: {percentage:.1f}% (預估)", end='', file=sys.stderr)
        except Exception:
            print(f"\r下載中...", end='', file=sys.stderr)
    elif d['status'] == 'finished':
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

def download_video(url, output_path=None):
    """下載YouTube視頻或音頻"""
    if output_path is None:
        output_path = os.path.join(os.getcwd(), 'downloads')
    
    # 確保輸出目錄存在
    os.makedirs(output_path, exist_ok=True)
    
    try:
        # 獲取視頻信息
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            
        print("\n請選擇下載格式：")
        print("1. 一般版 (MP4 + 音頻)")
        print("2. 純音樂 (MP3)")
        
        while True:
            format_choice = input("\n請選擇格式 (1-2): ").strip()
            if format_choice in ['1', '2']:
                break
            print("請輸入有效的選項 (1-2)")
        
        # 基本下載選項
        ydl_opts = {
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'progress_hooks': [my_hook],
            'quiet': False,
            'no_warnings': True
        }
        
        if format_choice == '2':  # 純音樂 MP3
            print("\n正在下載 MP3 音頻...")
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })
            
            print(f"\n影片標題: {info.get('title', 'Unknown')}")
            print(f"總時長: {format_time(info.get('duration', 0))}")
            print(f"觀看次數: {info.get('view_count', 0)}\n")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                
        else:  # 一般版 MP4
            formats = get_available_formats(url)
            print("\n可用的畫質選項：")
            for i, fmt in enumerate(formats, 1):
                print(f"{i}. {fmt['quality']} ({fmt['ext']}) - {fmt['filesize_str']}")
            
            choice = input("\n請選擇畫質 (輸入數字，直接按Enter使用最佳畫質): ").strip()
            
            if choice and choice.isdigit() and 1 <= int(choice) <= len(formats):
                selected_format = formats[int(choice)-1]
                height = selected_format["height"]
            else:
                height = None
            
            # 更新下載選項，確保音頻也被下載
            ydl_opts.update({
                'format': f'bestvideo[height={height}]+bestaudio/best' if height else 'bestvideo+bestaudio/best',
                'merge_output_format': 'mp4',
                'postprocessors': [{
                    'key': 'FFmpegVideoRemuxer',
                    'preferedformat': 'mp4',
                }],
                # 添加 FFmpeg 參數以確保音頻被正確合併
                'postprocessor_args': [
                    '-c:v', 'copy',
                    '-c:a', 'aac',
                    '-strict', 'experimental'
                ]
            })
            
            print(f"\n影片標題: {info.get('title', 'Unknown')}")
            print(f"總時長: {format_time(info.get('duration', 0))}")
            print(f"觀看次數: {info.get('view_count', 0)}\n")
            
            print("開始下載視頻...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        
        print("\n下載完成！")
        return True
        
    except Exception as e:
        print(f"\n下載過程中出現錯誤: {str(e)}")
        if "HTTP Error 429" in str(e):
            print("YouTube 暫時限制了下載請求，請稍後再試")
        elif "This video is not available" in str(e):
            print("此影片可能有版權限制或地區限制")
        return False

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

def main():
    print("YouTube 影片下載器")
    print("-" * 50 + "\n")
    
    while True:
        url = input("請輸入 YouTube 影片網址 (輸入 'q' 退出): ").strip()
        if url.lower() == 'q':
            break
            
        if not url:
            print("請輸入有效的網址！")
            continue
            
        print("\n正在獲取影片資訊和可用畫質...\n")
        download_video(url)
        
        print("\n" + "-" * 50)

if __name__ == "__main__":
    main()
