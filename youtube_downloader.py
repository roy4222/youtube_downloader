import yt_dlp
import os
from pathlib import Path
import sys
import math

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
                if 'height' in f and f['height'] is not None:
                    quality = f'{f["height"]}p'
                    if quality not in seen_qualities and f.get('vcodec') != 'none':
                        formats.append({
                            'format_id': f['format_id'],
                            'ext': f['ext'],
                            'quality': quality,
                            'filesize': f.get('filesize', 0),
                            'vcodec': f.get('vcodec', 'unknown')
                        })
                        seen_qualities.add(quality)
            
            # 按畫質排序
            formats.sort(key=lambda x: int(x['quality'][:-1]), reverse=True)
            return formats
        except Exception as e:
            print(f"獲取影片格式失敗: {str(e)}")
            return []

def download_video_segment(url, start_time, duration, output_path, part_num, total_parts, format_id=None):
    """下載影片的指定片段"""
    output_template = str(output_path / f'%(title)s_part{part_num}.%(ext)s')
    
    ydl_opts = {
        'format': format_id if format_id else 'best[ext=mp4]/best',  # 使用指定的格式ID或最佳品質
        'outtmpl': output_template,
        'quiet': False,
        'no_warnings': True,
        'ignoreerrors': True,
        'merge_output_format': 'mp4',
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
        'fragment_retries': 10,
        'retries': 10,
        'external_downloader_args': {
            'ffmpeg_i': ['-ss', str(start_time), '-t', str(duration), '-c:v', 'copy', '-c:a', 'copy']
        },
        'progress_hooks': [my_hook],
        'http_chunk_size': 10485760,  # 10MB per chunk
        'socket_timeout': 30,
        'extractor_retries': 5,
        'hls_prefer_native': False,
        'hls_prefer_ffmpeg': True,
        'prefer_ffmpeg': True,
        'postprocessor_args': {
            'ffmpeg': ['-c:v', 'copy', '-c:a', 'copy']
        }
    }

    try:
        print(f"\n開始下載第 {part_num} 段...")
        print(f"時間區間: {format_time(start_time)} - {format_time(start_time + duration)}")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            error_code = ydl.download([url])
            if error_code == 0:
                print(f"\n第 {part_num} 段下載完成")
                return True
            else:
                print(f"\n下載失敗，錯誤碼: {error_code}")
                return False
                
    except Exception as e:
        print(f"\n片段 {part_num}/{total_parts} 下載失敗: {str(e)}")
        if "This video is only available for registered users" in str(e):
            print("這是一個需要登入的影片，請確保你已登入並有權限觀看")
        return False

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
            format_id = None
        else:
            print("\n可用的畫質選項：")
            for i, fmt in enumerate(formats, 1):
                size_mb = fmt['filesize'] / (1024 * 1024) if fmt['filesize'] > 0 else 0
                print(f"{i}. {fmt['quality']} ({fmt['ext']}) - {size_mb:.1f}MB")
            
            while True:
                try:
                    choice = input("\n請選擇畫質 (輸入數字，直接按Enter使用最佳畫質): ").strip()
                    if not choice:  # 使用預設最佳畫質
                        format_id = None
                        break
                    choice = int(choice)
                    if 1 <= choice <= len(formats):
                        format_id = formats[choice-1]['format_id']
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
            return download_video_segment(url, 0, total_duration, output_path, 1, 1, format_id)

        # 計算需要分成幾段
        num_segments = math.ceil(total_duration / segment_duration)
        print(f"\n影片將被分成 {num_segments} 段下載")

        # 開始分段下載
        successful_parts = []
        for i in range(num_segments):
            start_time = i * segment_duration
            duration = min(segment_duration, total_duration - start_time)
            
            print(f"\n正在處理第 {i+1}/{num_segments} 段")
            
            if download_video_segment(url, start_time, duration, output_path, i+1, num_segments, format_id):
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
