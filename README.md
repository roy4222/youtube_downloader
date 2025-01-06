# YouTube 影片下載工具

這是一個基於 Python 的 YouTube 影片下載工具，使用 yt-dlp 來下載 YouTube 影片。本工具提供圖形化使用者介面（GUI），支援多種下載格式和畫質選擇。

## 功能特點

- 圖形化使用者介面
- 支援下載不同畫質的影片
- 支援下載 MP4 視頻和 MP3 音頻
- 實時顯示下載進度和速度
- 支援多線程下載加速
- 支援斷點續傳
- 自動合併音視頻

## 系統需求

- Python 3.8 或更高版本
- aria2c（用於加速下載）
- FFmpeg（用於音視頻處理）

## 安裝步驟

1. 克隆倉庫：
```bash
git clone https://github.com/[your-username]/youtube-downloader.git
```

2. 安裝依賴：
```bash
pip install -r requirements.txt
```

3. 安裝 aria2c：
Windows:
```bash
winget install aria2
```
或使用 chocolatey：
```bash
choco install aria2
```

4. 安裝 FFmpeg：
Windows:
```bash
winget install ffmpeg
```
或使用 chocolatey：
```bash
choco install ffmpeg
```

## 使用方法

1. 運行程序：
```bash
python youtube_downloader.py
```

2. 在輸入框中貼上 YouTube 影片網址

3. 選擇下載位置

4. 選擇下載格式（MP4 或 MP3）

5. 點擊「開始下載」按鈕

## 特殊功能

- 多線程下載：使用 aria2c 實現多線程下載，提升下載速度
- 自動重試：網絡問題時自動重試
- 進度顯示：實時顯示下載進度、速度和預計剩餘時間
- 斷點續傳：支援斷點續傳功能

## 注意事項

- 請確保系統已安裝 FFmpeg
- 請確保系統已安裝 aria2c
- 下載速度可能受網絡條件影響
- 部分影片可能因版權限制無法下載

## 授權

MIT License
