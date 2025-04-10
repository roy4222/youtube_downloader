"""
Qt 版本的主題管理器

提供統一的顏色方案、字體設定和樣式表
"""

from PySide6.QtGui import QColor, QFont, QPalette
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

class ThemeManager:
    """Qt 主題管理器，提供統一的顏色方案和樣式設定"""
    
    # 主要顏色
    PRIMARY_COLOR = "#FF6B35"  # 橙色作為主要強調色
    SECONDARY_COLOR = "#3A86FF"  # 藍色作為次要強調色
    SUCCESS_COLOR = "#4CAF50"  # 綠色表示成功
    WARNING_COLOR = "#FFC107"  # 黃色表示警告
    ERROR_COLOR = "#F44336"  # 紅色表示錯誤
    
    # 背景顏色
    BACKGROUND_COLOR = "#F5F7FA"  # 淺灰色背景
    CARD_COLOR = "#FFFFFF"  # 白色卡片背景
    
    # 文字顏色
    TEXT_PRIMARY = "#333333"  # 主要文字顏色
    TEXT_SECONDARY = "#666666"  # 次要文字顏色
    TEXT_DISABLED = "#999999"  # 禁用文字顏色
    
    # 邊框和分隔線
    BORDER_COLOR = "#E0E0E0"
    
    # 字體設定
    FONT_FAMILY = "Segoe UI"  # 預設字體
    FONT_SIZE_SMALL = 9
    FONT_SIZE_NORMAL = 10
    FONT_SIZE_LARGE = 12
    FONT_SIZE_XLARGE = 14
    
    # 間距和圓角
    PADDING_SMALL = 4
    PADDING_NORMAL = 8
    PADDING_LARGE = 12
    BORDER_RADIUS = 8
    
    @classmethod
    def apply_theme(cls, app):
        """將主題應用到整個應用程式"""
        # 設置應用程式樣式表
        app.setStyleSheet(cls.get_stylesheet())
        
        # 設置調色板
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(cls.BACKGROUND_COLOR))
        palette.setColor(QPalette.WindowText, QColor(cls.TEXT_PRIMARY))
        palette.setColor(QPalette.Base, QColor(cls.CARD_COLOR))
        palette.setColor(QPalette.AlternateBase, QColor(cls.BACKGROUND_COLOR))
        palette.setColor(QPalette.Text, QColor(cls.TEXT_PRIMARY))
        palette.setColor(QPalette.Button, QColor(cls.CARD_COLOR))
        palette.setColor(QPalette.ButtonText, QColor(cls.TEXT_PRIMARY))
        palette.setColor(QPalette.Link, QColor(cls.SECONDARY_COLOR))
        palette.setColor(QPalette.Highlight, QColor(cls.PRIMARY_COLOR))
        palette.setColor(QPalette.HighlightedText, QColor("#FFFFFF"))
        
        app.setPalette(palette)
        
        # 設置預設字體
        font = QFont(cls.FONT_FAMILY, cls.FONT_SIZE_NORMAL)
        app.setFont(font)
    
    @classmethod
    def get_stylesheet(cls):
        """獲取全域樣式表"""
        return f"""
        /* 全域樣式 */
        QWidget {{
            font-family: "{cls.FONT_FAMILY}";
            color: {cls.TEXT_PRIMARY};
        }}
        
        /* 主視窗樣式 */
        QMainWindow {{
            background-color: {cls.BACKGROUND_COLOR};
        }}
        
        /* 框架樣式 */
        QFrame {{
            border-radius: {cls.BORDER_RADIUS}px;
        }}
        
        QFrame[frameShape="4"] {{  /* 用於分隔線 */
            background-color: {cls.BORDER_COLOR};
        }}
        
        /* 卡片樣式 */
        QFrame.card {{
            background-color: {cls.CARD_COLOR};
            border-radius: {cls.BORDER_RADIUS}px;
            border: 1px solid {cls.BORDER_COLOR};
        }}
        
        /* 標籤樣式 */
        QLabel {{
            color: {cls.TEXT_PRIMARY};
        }}
        
        QLabel[heading="true"] {{
            font-size: {cls.FONT_SIZE_LARGE}pt;
            font-weight: bold;
        }}
        
        QLabel[subheading="true"] {{
            font-size: {cls.FONT_SIZE_NORMAL}pt;
            color: {cls.TEXT_SECONDARY};
        }}
        
        /* 按鈕樣式 */
        QPushButton {{
            background-color: {cls.CARD_COLOR};
            border: 1px solid {cls.BORDER_COLOR};
            border-radius: {cls.BORDER_RADIUS}px;
            padding: {cls.PADDING_NORMAL}px {cls.PADDING_LARGE}px;
            color: {cls.TEXT_PRIMARY};
        }}
        
        QPushButton:hover {{
            background-color: #F0F0F0;
        }}
        
        QPushButton:pressed {{
            background-color: #E0E0E0;
        }}
        
        QPushButton:disabled {{
            color: {cls.TEXT_DISABLED};
            background-color: #F0F0F0;
        }}
        
        /* 主要按鈕樣式 */
        QPushButton[primary="true"] {{
            background-color: {cls.PRIMARY_COLOR};
            color: white;
            border: none;
        }}
        
        QPushButton[primary="true"]:hover {{
            background-color: #FF8255;
        }}
        
        QPushButton[primary="true"]:pressed {{
            background-color: #E55A25;
        }}
        
        QPushButton[primary="true"]:disabled {{
            background-color: #FFAB90;
            color: #FFFFFF;
        }}
        
        /* 次要按鈕樣式 */
        QPushButton[secondary="true"] {{
            background-color: {cls.SECONDARY_COLOR};
            color: white;
            border: none;
        }}
        
        QPushButton[secondary="true"]:hover {{
            background-color: #5A9FFF;
        }}
        
        QPushButton[secondary="true"]:pressed {{
            background-color: #2A76EF;
        }}
        
        /* 輸入框樣式 */
        QLineEdit, QTextEdit, QPlainTextEdit {{
            border: 1px solid {cls.BORDER_COLOR};
            border-radius: {cls.BORDER_RADIUS}px;
            padding: {cls.PADDING_NORMAL}px;
            background-color: {cls.CARD_COLOR};
            selection-background-color: {cls.PRIMARY_COLOR};
        }}
        
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border: 1px solid {cls.PRIMARY_COLOR};
        }}
        
        /* 下拉選單樣式 */
        QComboBox {{
            border: 1px solid {cls.BORDER_COLOR};
            border-radius: {cls.BORDER_RADIUS}px;
            padding: {cls.PADDING_NORMAL}px;
            background-color: {cls.CARD_COLOR};
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 20px;
        }}
        
        /* 進度條樣式 */
        QProgressBar {{
            border: 1px solid {cls.BORDER_COLOR};
            border-radius: {cls.BORDER_RADIUS}px;
            background-color: #F0F0F0;
            text-align: center;
        }}
        
        QProgressBar::chunk {{
            background-color: {cls.PRIMARY_COLOR};
            border-radius: {cls.BORDER_RADIUS}px;
        }}
        
        /* 滾動條樣式 */
        QScrollBar:vertical {{
            border: none;
            background-color: #F0F0F0;
            width: 10px;
            margin: 0px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: #CCCCCC;
            border-radius: 5px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: #AAAAAA;
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        
        QScrollBar:horizontal {{
            border: none;
            background-color: #F0F0F0;
            height: 10px;
            margin: 0px;
        }}
        
        QScrollBar::handle:horizontal {{
            background-color: #CCCCCC;
            border-radius: 5px;
            min-width: 20px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background-color: #AAAAAA;
        }}
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}
        
        /* 狀態標籤樣式 */
        QLabel[status="success"] {{
            color: {cls.SUCCESS_COLOR};
        }}
        
        QLabel[status="warning"] {{
            color: {cls.WARNING_COLOR};
        }}
        
        QLabel[status="error"] {{
            color: {cls.ERROR_COLOR};
        }}
        
        /* 對話框樣式 */
        QDialog {{
            background-color: {cls.BACKGROUND_COLOR};
        }}
        """
    
    @classmethod
    def get_card_style(cls):
        """獲取卡片樣式"""
        return f"""
        background-color: {cls.CARD_COLOR};
        border-radius: {cls.BORDER_RADIUS}px;
        border: 1px solid {cls.BORDER_COLOR};
        """
    
    @classmethod
    def get_primary_button_style(cls):
        """獲取主要按鈕樣式"""
        return f"""
        background-color: {cls.PRIMARY_COLOR};
        color: white;
        border: none;
        border-radius: {cls.BORDER_RADIUS}px;
        padding: {cls.PADDING_NORMAL}px {cls.PADDING_LARGE}px;
        """
    
    @classmethod
    def get_secondary_button_style(cls):
        """獲取次要按鈕樣式"""
        return f"""
        background-color: {cls.SECONDARY_COLOR};
        color: white;
        border: none;
        border-radius: {cls.BORDER_RADIUS}px;
        padding: {cls.PADDING_NORMAL}px {cls.PADDING_LARGE}px;
        """
