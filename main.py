"""
影片下載器主程式入口點

啟動應用程式的主視窗
"""

import tkinter as tk
from ui.main_window import MainWindow

def main():
    """主程式入口點"""
    # 創建根視窗
    root = tk.Tk()
    
    # 設置主題 (如果支援)
    try:
        root.tk.call("source", "azure.tcl")
        root.tk.call("set_theme", "light")
    except:
        pass
    
    # 創建主視窗
    app = MainWindow(root)
    
    # 啟動主循環
    root.mainloop()

if __name__ == "__main__":
    main()
