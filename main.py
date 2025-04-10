"""
影片下載器主程式入口點

啟動應用程式的主視窗
"""

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QCoreApplication, Qt

from ui.main_window import MainWindow
from ui.theme import ThemeManager

def main():
    """主程式入口點"""
    # 設置高 DPI 支援 (使用新的非棄用 API)
    # 在 Qt 6 中，高 DPI 縮放默認已啟用，不需要顯式設置
    # QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    # QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # 創建應用程式
    app = QApplication(sys.argv)
    app.setApplicationName("影片下載器")
    
    # 設置應用程式圖示
    icon_path = os.path.join(os.path.dirname(__file__), "youtube.ico")
    if os.path.exists(icon_path):
        from PySide6.QtGui import QIcon
        app.setWindowIcon(QIcon(icon_path))
    
    # 應用主題
    ThemeManager.apply_theme(app)
    
    # 創建並顯示主視窗
    window = MainWindow()
    window.show()
    
    # 執行應用程式
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
