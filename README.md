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
