# UI 模組說明文件

本文件說明 UI 模組中各個檔案的功能和用途。UI 模組負責影片下載器的使用者介面元件，採用模組化設計，每個元件專注於單一職責。

## 檔案結構

```
ui/
├── __init__.py         # 模組初始化檔案
├── base.py             # 基礎 UI 元件類別
├── format_frame.py     # 下載格式選擇框架
├── main_window.py      # 主應用程式視窗
├── output_frame.py     # 輸出文本框架
├── path_frame.py       # 下載位置選擇框架
├── progress_frame.py   # 下載進度顯示框架
├── quality_dialog.py   # 畫質選擇對話框
├── url_frame.py        # URL 輸入框架
└── README.md           # 本說明文件
```

## 檔案說明

### __init__.py

模組初始化檔案，提供版本資訊並導出主要類別，方便導入。

```python
from ui.main_window import MainWindow
from ui.url_frame import UrlInputFrame
# 其他導入...
```

### base.py

提供基礎 UI 元件類別，包括 `BaseFrame` 和 `BaseDialog`，為其他 UI 元件提供共用功能和一致的介面。

- `BaseFrame`: UI 框架元件的基礎類別
- `BaseDialog`: 對話框的基礎類別

### main_window.py

主應用程式視窗，整合所有 UI 元件，提供完整的下載功能。

- `MainWindow`: 主視窗類別，管理所有 UI 元件和下載邏輯

### url_frame.py

URL 輸入框架，提供 URL 輸入和處理功能。

- `UrlInputFrame`: URL 輸入框架類別，繼承自 `ttk.LabelFrame`
- 功能：URL 輸入、貼上、清除、驗證

### path_frame.py

下載位置選擇框架，提供下載位置選擇和管理功能。

- `PathSelectionFrame`: 下載位置選擇框架類別，繼承自 `ttk.LabelFrame`
- 功能：路徑輸入、瀏覽選擇、路徑驗證

### format_frame.py

下載格式選擇框架，提供下載格式選擇功能。

- `FormatSelectionFrame`: 下載格式選擇框架類別，繼承自 `ttk.LabelFrame`
- 功能：選擇 MP4 或 MP3 格式

### progress_frame.py

下載進度顯示框架，提供下載進度顯示和管理功能。

- `ProgressFrame`: 下載進度顯示框架類別，繼承自 `ttk.LabelFrame`
- 功能：進度條顯示、下載速度顯示、狀態更新

### output_frame.py

輸出文本框架，提供下載日誌顯示功能。

- `OutputFrame`: 輸出文本框架類別，繼承自 `ttk.Frame`
- 功能：日誌顯示、進度解析、標準輸出重定向

### quality_dialog.py

畫質選擇對話框，提供影片畫質選擇功能。

- `QualityDialog`: 畫質選擇對話框類別，繼承自 `BaseDialog`
- 功能：顯示可用畫質選項、選擇特定畫質

## 設計原則

1. **單一職責原則**: 每個元件只負責一個功能，減少耦合
2. **開放封閉原則**: 元件設計為可擴展但不需修改現有代碼
3. **依賴反轉原則**: 通過回調函數和事件處理實現元件之間的通信
4. **介面分離原則**: 每個元件提供明確的公共介面

## 使用方式

主程式入口點 `main.py` 會創建主視窗並啟動應用程式：

```python
from ui.main_window import MainWindow

def main():
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()
```

## 擴展方式

要添加新的 UI 元件，可以：

1. 創建新的元件類別，繼承自適當的基礎類別
2. 實現必要的方法，如 `create_widgets`
3. 在 `MainWindow` 中整合新元件

例如，添加一個新的設定面板：

```python
class SettingsPanel(ttk.LabelFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, text="設定", padding="5", **kwargs)
        self.create_widgets()
        
    def create_widgets(self):
        # 實現設定面板的 UI 元件
        pass
```
