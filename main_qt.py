"""
影片下載器 Qt 版本主程式入口點

啟動 Qt 版本的應用程式主視窗
"""

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QCoreApplication, Qt

from ui.qt.main_window import MainWindow
from ui.qt.theme import ThemeManager

def main():
    """主程式入口點"""
    # 設置高 DPI 支援
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
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
