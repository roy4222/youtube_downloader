"""
影片下載器主程式入口點

啟動應用程式的主視窗
"""

import tkinter as tk
from ui.main_window import MainWindow
from ui.theme import ThemeManager

def main():
    """主程式入口點"""
    # 創建根視窗
    root = tk.Tk()
    root.title("影片下載器")
    
    # 設置應用程式圖示
    try:
        root.iconbitmap("youtube.ico")
    except:
        pass
    
    # 設置主題
    ThemeManager.setup_theme(root)
    
    # 設置視窗大小和位置
    window_width = 800
    window_height = 600
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    # 創建主視窗
    app = MainWindow(root)
    
    # 啟動主循環
    root.mainloop()

if __name__ == "__main__":
    main()
