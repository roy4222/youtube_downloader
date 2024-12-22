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
            '-c:a', 'aac',
            '-b:a', '192k',
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

def download_video_segment(url, start_time, duration, output_path, part_num, total_parts, format_choice=None):
    """下載影片的指定片段"""
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # 先獲取影片資訊以得到標題
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                title = sanitize_filename(info['title'])
                base_filename = f"{title}_part{part_num}"
            
            output_template = str(output_path / f'{base_filename}.%(ext)s')
            
            ydl_opts = {
                'format': f'bestvideo[height<={format_choice["height"]}]+bestaudio/best[height<={format_choice["height"]}]' if format_choice else 'bv*+ba/b',
                'outtmpl': output_template,
                'quiet': False,
                'no_warnings': True,
                'ignoreerrors': True,
                'merge_output_format': 'mp4',
                'fragment_retries': 10,
                'retries': 10,
                'progress_hooks': [my_hook],
                'http_chunk_size': 10485760,
                'socket_timeout': 30,
                'extractor_retries': 5,
                'prefer_ffmpeg': True,
                'ffmpeg_location': 'ffmpeg',
                'overwrites': True,
                'nopart': True,
                'no_resume': True
            }

            print(f"\n開始下載第 {part_num} 段... (嘗試 {retry_count + 1}/{max_retries})")
            print(f"時間區間: {format_time(start_time)} - {format_time(start_time + duration)}")
            
            # 在下載前清理可能存在的部分下載文件
            cleanup_partial_downloads(output_path, base_filename)
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                error_code = ydl.download([url])
                
                if error_code == 0:
                    # 在下載完成後檢查文件
                    video_file, audio_file = find_downloaded_files(output_path, base_filename)
                    
                    if video_file and audio_file:
                        print("\n找到分離的視頻和音頻文件，開始合併...")
                        output_file = str(Path(output_path) / f'{base_filename}_完整.mp4')
                        return merge_video_audio(video_file, audio_file, output_file)
                    else:
                        print(f"\n未找到需要合併的文件，請檢查下載的文件是否完整")
                        retry_count += 1
                        continue
                else:
                    print(f"\n下載失敗，錯誤碼: {error_code}")
                    retry_count += 1
                    continue
                    
        except Exception as e:
            print(f"\n片段 {part_num}/{total_parts} 下載失敗: {str(e)}")
            if "This video is only available for registered users" in str(e):
                print("這是一個需要登入的影片，請確保你已登入並有權限觀看")
                return False
            retry_count += 1
            if retry_count < max_retries:
                print(f"等待 5 秒後重試...")
                time.sleep(5)
            continue
            
    print(f"\n在 {max_retries} 次嘗試後仍然失敗")
    return False

def cleanup_partial_downloads(output_path, base_filename):
    """清理可能存在的部分下載文件"""
    try:
        pattern = f"{base_filename}.*"
        for file in Path(output_path).glob(pattern):
            try:
                os.remove(file)
                print(f"已刪除部分下載文件: {file}")
            except Exception as e:
                print(f"刪除文件時出錯: {str(e)}")
    except Exception as e:
        print(f"清理文件時出錯: {str(e)}")

def download_video(url, output_path=None, segment_duration=1800):
    try:
        # 如果沒有指定輸出路徑，則使用當前目錄下的 downloads 資料夾
        if output_path is None:
            output_path = Path.cwd() / 'downloads'
            output_path.mkdir(exist_ok=True)

        # 獲取可用的畫質選項
        print("正在獲取影片資訊和可用畫質...")
        formats = get_available_formats(url)
        if not formats:
            print("無法獲取影片格式，將使用預設最佳畫質")
            format_choice = None
        else:
            print("\n可用的畫質選項：")
            for i, fmt in enumerate(formats, 1):
                print(f"{i}. {fmt['quality']} ({fmt['ext']}) - {fmt['filesize_str']}")
            
            while True:
                try:
                    choice = input("\n請選擇畫質 (輸入數字，直接按Enter使用最佳畫質): ").strip()
                    if not choice:  # 使用預設最佳畫質
                        format_choice = formats[0] if formats else None
                        break
                    choice = int(choice)
                    if 1 <= choice <= len(formats):
                        format_choice = formats[choice-1]
                        break
                    else:
                        print("無效的選擇，請重試")
                except ValueError:
                    print("請輸入有效的數字")
        
        # 獲取影片資訊
        with yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info['title']
            total_duration = info.get('duration', 0)
        
        print(f"\n影片標題: {title}")
        print(f"總時長: {format_time(total_duration)}")
        if 'view_count' in info:
            print(f"觀看次數: {info['view_count']}")

        # 如果影片時長小於分段時長，直接下載完整影片
        if total_duration <= segment_duration:
            print("\n影片時長較短，將直接下載完整影片")
            return download_video_segment(url, 0, total_duration, output_path, 1, 1, format_choice)

        # 計算需要分成幾段
        num_segments = math.ceil(total_duration / segment_duration)
        print(f"\n影片將被分成 {num_segments} 段下載")

        # 開始分段下載
        successful_parts = []
        for i in range(num_segments):
            start_time = i * segment_duration
            duration = min(segment_duration, total_duration - start_time)
            
            print(f"\n正在處理第 {i+1}/{num_segments} 段")
            
            if download_video_segment(url, start_time, duration, output_path, i+1, num_segments, format_choice):
                successful_parts.append(i+1)
            else:
                print(f"第 {i+1} 段下載失敗")

        # 顯示下載結果
        if successful_parts:
            print(f"\n成功下載了 {len(successful_parts)}/{num_segments} 段")
            print(f"檔案保存在: {output_path}")
            if len(successful_parts) < num_segments:
                print("有些片段下載失敗，你可以稍後重試下載這些片段")
                print("失敗的片段:", [i+1 for i in range(num_segments) if i+1 not in successful_parts])
        else:
            print("\n所有片段都下載失敗")

    except Exception as e:
        print(f"\n下載過程中發生錯誤: {str(e)}")
        print("請確認影片是否可以正常播放，或者稍後再試")

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
    print("YouTube 影片下載器 (分段下載版)")
    print("-" * 50)
    
    while True:
        url = input("\n請輸入 YouTube 影片網址 (輸入 'q' 退出): ")
        if url.lower() == 'q':
            break
        
        # 詢問分段時長
        while True:
            try:
                minutes = input("請輸入每段影片的時長(分鐘，預設30分鐘): ").strip()
                if not minutes:
                    segment_duration = 1800  
                    break
                minutes = int(minutes)
                if minutes > 0:
                    segment_duration = minutes * 60
                    break
                else:
                    print("請輸入大於0的數字")
            except ValueError:
                print("請輸入有效的數字")
            
        # 開始下載
        download_video(url, segment_duration=segment_duration)
        
        print("\n" + "-" * 50)

if __name__ == "__main__":
    main()
