"""
使用 Nuitka 打包應用程式的腳本

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
    
    # 創建輸出目錄
    output_dir = os.path.join(current_dir, "output")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 檢查 ffmpeg.exe 是否存在
    ffmpeg_path = os.path.join(current_dir, "ffmpeg.exe")
    if not os.path.exists(ffmpeg_path):
        print("錯誤：找不到 ffmpeg.exe 檔案")
        return
    
    # 構建 Nuitka 命令
    main_py = os.path.join(current_dir, "main.py")
    icon_path = os.path.join(current_dir, "youtube.ico")
    
    cmd = [
        "python", "-m", "nuitka",
        "--standalone",
        "--mingw64",
        "--enable-plugin=pyside6",
        "--include-data-dir=ffmpeg.exe=.",
        f"--windows-icon-from-ico={icon_path}",
        "--output-dir=output",
        "--windows-disable-console",
        "--follow-imports",
        "--include-package=yt_dlp",
        "--include-package=core",
        "--include-package=ui",
        "--include-package=utils",
        "--show-progress",
        "--show-memory",
        "--assume-yes-for-downloads",
        main_py
    ]
    
    # 執行 Nuitka 命令
    print("正在執行 Nuitka 打包命令...")
    print(" ".join(cmd))
    
    try:
        subprocess.run(cmd, check=True)
        
        # 打包完成後，複製 ffmpeg.exe 到輸出目錄的 main.dist 目錄中
        dist_dir = os.path.join(output_dir, "main.dist")
        if os.path.exists(dist_dir):
            # 檢查 ffmpeg.exe 是否已經在輸出目錄中
            output_ffmpeg = os.path.join(dist_dir, "ffmpeg.exe")
            if not os.path.exists(output_ffmpeg):
                print(f"複製 ffmpeg.exe 到 {dist_dir}")
                shutil.copy2(ffmpeg_path, output_ffmpeg)
            
            print(f"打包完成！應用程式位於：{dist_dir}")
            print("你可以將整個 main.dist 目錄分發給使用者")
        else:
            print("警告：找不到輸出目錄 main.dist")
    
    except subprocess.CalledProcessError as e:
        print(f"打包失敗：{e}")
    except Exception as e:
        print(f"發生錯誤：{e}")

if __name__ == "__main__":
    main()
