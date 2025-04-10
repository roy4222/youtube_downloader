"""
UI 模組

提供影片下載器的使用者介面元件
"""

# 版本資訊
__version__ = "1.0.0"

# 導出主要類別，方便導入
from ui.main_window import MainWindow
from ui.url_frame import UrlInputFrame
from ui.path_frame import PathSelectionFrame
from ui.format_frame import FormatSelectionFrame
from ui.progress_frame import ProgressFrame
from ui.output_frame import OutputFrame
from ui.quality_dialog import QualityDialog
