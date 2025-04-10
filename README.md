# 影片下載器 - YouTube & Bilibili

一個模組化、功能強大的影片下載工具，支援 YouTube 和 Bilibili 影片下載，包括高畫質視頻、音訊下載和批量處理。

## 功能特點

- 支援 YouTube 和 Bilibili 影片下載
- 支援多種視頻格式和畫質選項下載
- 支援純音訊格式 (MP3) 下載
- 多任務並行下載管理
- 提供簡單易用的圖形界面
- 支援批量下載功能
- 自動檢測並安裝相關依賴

## 安裝方法

### 使用 pip 安裝

```bash
pip install youtube_downloader
```

### 從源碼安裝

```bash
git clone https://github.com/yourusername/youtube_downloader.git
cd youtube_downloader
pip install -e .
```

## 依賴項

本工具依賴以下外部程式：

- **yt-dlp**: 核心下載功能 (自動安裝)
- **FFmpeg**: 視頻處理與格式轉換 (需手動安裝)
- **aria2c**: 加速下載 (可選)

可通過以下命令檢查依賴：

```bash
ytdl --check
```

## 程式架構與組件化

本專案採用模組化設計，目前已完成以下組件化工作：

### 現有架構

```
youtube_downloader/
├── core/                     # 核心功能模組
│   ├── __init__.py           # 模組初始化檔案
│   ├── url_utils.py          # URL 處理工具
│   ├── download_engine.py    # 下載引擎抽象類
│   └── download_manager.py   # 下載管理器
├── ui/                       # 使用者介面模組
│   ├── __init__.py           # 模組初始化檔案
│   ├── base.py               # 基礎 UI 元件類別
│   ├── main_window.py        # 主視窗
│   ├── url_frame.py          # URL 輸入框架
│   ├── path_frame.py         # 下載位置選擇框架
│   ├── format_frame.py       # 下載格式選擇框架
│   ├── progress_frame.py     # 下載進度顯示框架
│   ├── output_frame.py       # 輸出文本框架
│   ├── quality_dialog.py     # 畫質選擇對話框
│   └── README.md             # UI 模組說明文件
├── utils/                    # 工具函數模組
│   └── __init__.py           # 模組初始化檔案
├── main.py                   # 程式入口
├── youtube_downloader.py     # 主程式（舊版）
├── requirements.txt          # 依賴項
└── README.md                 # 說明文件
```

### 已完成的組件化工作

1. **URL 處理模組**
   - 實現了 `UrlProcessor` 類別，提供完整的 URL 處理功能
   - 支援多種 URL 格式和平台 (YouTube, Bilibili)
   - 提供了 URL 清理、平台檢測、URL 驗證和影片 ID 提取功能

2. **下載引擎抽象化**
   - 建立了抽象下載引擎基類 `DownloadEngine`
   - 實現了平台特定下載器 `YouTubeDownloadEngine` 和 `BilibiliDownloadEngine`
   - 創建了下載引擎工廠類 `DownloadEngineFactory`，自動選擇適合的下載器
   - 實現了下載管理器 `DownloadManager`，提供統一的下載介面

3. **UI 元件分離**
   - 將大型 GUI 類拆分為多個專注的元件
   - 實現了基礎 UI 元件類別 `BaseFrame` 和 `BaseDialog`
   - 創建了專注的 UI 元件：URL 輸入、下載位置選擇、格式選擇、進度顯示等
   - 整合所有元件到主視窗 `MainWindow`

### 待完成的組件化工作

4. **設定管理模組**
   - 保存/載入使用者偏好設定
   - 記住上次的下載位置和格式選擇

5. **多語言支援**
   - 提取文字字串到語言檔案
   - 實現多語言切換功能

6. **下載任務管理**
   - 支援多任務並行下載
   - 實現暫停、繼續、取消等操作

## 使用方法

### 命令行使用

```bash
# 下載 YouTube 視頻
ytdl https://www.youtube.com/watch?v=xxxxxxxxxxx

# 下載 Bilibili 視頻
ytdl https://www.bilibili.com/video/BVxxxxxxxxxx

# 指定輸出目錄
ytdl https://www.youtube.com/watch?v=xxxxxxxxxxx -o /path/to/downloads

# 下載純音訊 (MP3)
ytdl https://www.youtube.com/watch?v=xxxxxxxxxxx -f audio

# 指定視頻畫質 (例如 720p)
ytdl https://www.youtube.com/watch?v=xxxxxxxxxxx -q 720

# 批量下載（從文件讀取URL）
ytdl --batch urls.txt

# 啟動圖形界面
ytdl --gui
```

### 作為Python模組使用

```python
from youtube_downloader.downloader import simple_download

# 下載 YouTube 視頻
success, file_path, error = simple_download(
    url="https://www.youtube.com/watch?v=xxxxxxxxxxx",
    output_path="./downloads",
    format_choice="video",
    height=720  # 可選: 指定畫質
)

# 下載 Bilibili 視頻
success, file_path, error = simple_download(
    url="https://www.bilibili.com/video/BVxxxxxxxxxx",
    output_path="./downloads",
    format_choice="video",
    height=720  # 可選: 指定畫質
)

if success:
    print(f"下載成功: {file_path}")
else:
    print(f"下載失敗: {error}")
```

## 進階使用

### 下載管理器

使用下載管理器進行並行下載和任務管理：

```python
from youtube_downloader.downloader import DownloadManager

# 創建下載管理器（最多同時下載2個視頻）
manager = DownloadManager(max_concurrent=2)

# 添加下載任務
task_id = manager.add_task(
    url="https://www.youtube.com/watch?v=xxxxxxxxxxx",
    output_path="./downloads",
    format_choice="video"
)

# 啟動下載
manager.start()

# 獲取任務信息
task_info = manager.get_task(task_id)
print(f"下載進度: {task_info['progress']}%")

# 停止下載管理器
manager.stop()
```

## 常見問題

### 下載速度慢？

- 檢查網路連線
- 確認是否已安裝 aria2c（可提升下載速度）
- YouTube 或 Bilibili 有時會限制下載速度

### 無法下載某些影片？

- 確認影片是否有地區限制
- 檢查影片是否為會員專屬內容
- 更新 yt-dlp 至最新版本
- Bilibili 影片可能需要登入才能下載

### 下載失敗？

- 檢查網路連線
- 確認磁碟空間是否足夠
- 檢查錯誤訊息，尋找具體原因

## 貢獻指南

歡迎提交 Pull Request 或建立 Issue。

## 授權條款

MIT License
