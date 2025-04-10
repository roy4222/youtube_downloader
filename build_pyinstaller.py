"""
使用 PyInstaller 打包應用程式的腳本

此腳本會將應用程式打包成獨立的 .exe 檔案，包含所有必要的套件和 ffmpeg
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def main():
    """主函數"""
    print("開始打包應用程式...")
    
    # 獲取當前目錄
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 檢查 ffmpeg.exe 是否存在
    ffmpeg_path = os.path.join(current_dir, "ffmpeg.exe")
    if not os.path.exists(ffmpeg_path):
        print("錯誤：找不到 ffmpeg.exe 檔案")
        return
    
    # 構建 PyInstaller 命令
    main_py = os.path.join(current_dir, "main.py")
    icon_path = os.path.join(current_dir, "youtube.ico")
    
    # 執行 PyInstaller 命令
    print("正在執行 PyInstaller 打包命令...")
    
    cmd = [
        "pyinstaller",
        "--name=影片下載器",
        "--windowed",
        "--icon=" + icon_path,
        "--add-data=" + ffmpeg_path + ";.",
        "--add-data=" + icon_path + ";.",
        "--hidden-import=yt_dlp",
        "--hidden-import=core",
        "--hidden-import=ui",
        "--hidden-import=utils",
        "--hidden-import=PySide6.QtCore",
        "--hidden-import=PySide6.QtGui",
        "--hidden-import=PySide6.QtWidgets",
        main_py
    ]
    
    try:
        subprocess.run(cmd, check=True)
        
        # 打包完成後，檢查輸出目錄
        dist_dir = os.path.join(current_dir, "dist", "影片下載器")
        if os.path.exists(dist_dir):
            # 檢查 ffmpeg.exe 是否已經在輸出目錄中
            output_ffmpeg = os.path.join(dist_dir, "ffmpeg.exe")
            if not os.path.exists(output_ffmpeg):
                print(f"複製 ffmpeg.exe 到 {dist_dir}")
                shutil.copy2(ffmpeg_path, output_ffmpeg)
            
            print(f"打包完成！應用程式位於：{dist_dir}")
            print("你可以將整個 '影片下載器' 目錄分發給使用者")
        else:
            print(f"警告：找不到輸出目錄 {dist_dir}")
    
    except subprocess.CalledProcessError as e:
        print(f"打包失敗：{e}")
    except Exception as e:
        print(f"發生錯誤：{e}")

if __name__ == "__main__":
    main()
