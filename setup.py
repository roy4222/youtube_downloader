import sys
from cx_Freeze import setup, Executable

# 依賴包
build_exe_options = {
    "packages": ["os", "tkinter", "yt_dlp"],
    "excludes": [],
    "include_files": [
        ("ffmpeg.exe", "ffmpeg.exe"),
    ],
}

# 基本信息
setup(
    name="YouTube下載器",
    version="1.0",
    description="YouTube影片下載工具",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "youtube_downloader.py",
            base="Win32GUI",
            target_name="YouTube下載器.exe",
        )
    ],
)
