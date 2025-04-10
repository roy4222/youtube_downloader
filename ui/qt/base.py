"""
Qt 版本的基礎 UI 元件

提供所有 UI 元件的基礎類別
"""

from PySide6.QtWidgets import QFrame, QDialog, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal

from .theme import ThemeManager

class BaseFrame(QFrame):
    """所有框架的基礎類別"""
    
    def __init__(self, parent=None):
        """初始化基礎框架"""
        super().__init__(parent)
        self.setObjectName(self.__class__.__name__)
        
        # 設置樣式
        self.setProperty("class", "card")
        self.setStyleSheet(f"""
            #{self.objectName()} {{
                {ThemeManager.get_card_style()}
            }}
        """)
        
        # 初始化佈局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(
            ThemeManager.PADDING_LARGE, 
            ThemeManager.PADDING_LARGE, 
            ThemeManager.PADDING_LARGE, 
            ThemeManager.PADDING_LARGE
        )
        self.main_layout.setSpacing(ThemeManager.PADDING_NORMAL)
        
        # 初始化 UI
        self.setup_ui()
        
    def setup_ui(self):
        """設置 UI 元件，子類別應重寫此方法"""
        pass
    
    def create_heading(self, text, parent=None):
        """創建標題標籤"""
        label = QLabel(text, parent or self)
        label.setProperty("heading", True)
        return label
    
    def create_subheading(self, text, parent=None):
        """創建副標題標籤"""
        label = QLabel(text, parent or self)
        label.setProperty("subheading", True)
        return label
    
    def create_horizontal_layout(self, spacing=None, margins=None, parent=None):
        """創建水平佈局"""
        layout = QHBoxLayout(parent)
        
        if spacing is not None:
            layout.setSpacing(spacing)
        else:
            layout.setSpacing(ThemeManager.PADDING_NORMAL)
            
        if margins is not None:
            layout.setContentsMargins(*margins)
        else:
            layout.setContentsMargins(0, 0, 0, 0)
            
        return layout
    
    def create_vertical_layout(self, spacing=None, margins=None, parent=None):
        """創建垂直佈局"""
        layout = QVBoxLayout(parent)
        
        if spacing is not None:
            layout.setSpacing(spacing)
        else:
            layout.setSpacing(ThemeManager.PADDING_NORMAL)
            
        if margins is not None:
            layout.setContentsMargins(*margins)
        else:
            layout.setContentsMargins(0, 0, 0, 0)
            
        return layout


class BaseDialog(QDialog):
    """所有對話框的基礎類別"""
    
    def __init__(self, parent=None, title="對話框", width=400, height=300):
        """初始化基礎對話框"""
        super().__init__(parent)
        self.setObjectName(self.__class__.__name__)
        
        # 設置視窗屬性
        self.setWindowTitle(title)
        self.setMinimumSize(width, height)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        
        # 設置樣式
        self.setStyleSheet(f"""
            #{self.objectName()} {{
                background-color: {ThemeManager.BACKGROUND_COLOR};
            }}
        """)
        
        # 初始化佈局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(
            ThemeManager.PADDING_LARGE, 
            ThemeManager.PADDING_LARGE, 
            ThemeManager.PADDING_LARGE, 
            ThemeManager.PADDING_LARGE
        )
        self.main_layout.setSpacing(ThemeManager.PADDING_NORMAL)
        
        # 初始化 UI
        self.setup_ui()
        
    def setup_ui(self):
        """設置 UI 元件，子類別應重寫此方法"""
        pass
    
    def create_heading(self, text, parent=None):
        """創建標題標籤"""
        label = QLabel(text, parent or self)
        label.setProperty("heading", True)
        return label
    
    def create_subheading(self, text, parent=None):
        """創建副標題標籤"""
        label = QLabel(text, parent or self)
        label.setProperty("subheading", True)
        return label
    
    def create_horizontal_layout(self, spacing=None, margins=None, parent=None):
        """創建水平佈局"""
        layout = QHBoxLayout(parent)
        
        if spacing is not None:
            layout.setSpacing(spacing)
        else:
            layout.setSpacing(ThemeManager.PADDING_NORMAL)
            
        if margins is not None:
            layout.setContentsMargins(*margins)
        else:
            layout.setContentsMargins(0, 0, 0, 0)
            
        return layout
    
    def create_vertical_layout(self, spacing=None, margins=None, parent=None):
        """創建垂直佈局"""
        layout = QVBoxLayout(parent)
        
        if spacing is not None:
            layout.setSpacing(spacing)
        else:
            layout.setSpacing(ThemeManager.PADDING_NORMAL)
            
        if margins is not None:
            layout.setContentsMargins(*margins)
        else:
            layout.setContentsMargins(0, 0, 0, 0)
            
        return layout
