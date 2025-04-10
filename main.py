"""
影片下載器主程式入口

啟動影片下載器應用程式，支援 YouTube 和 Bilibili 影片下載
"""

import tkinter as tk
import sys
import os

# 確保可以導入模組
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 導入主程式
from youtube_downloader import YouTubeDownloaderGUI

def main():
    """主程式入口"""
    root = tk.Tk()
    app = YouTubeDownloaderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
