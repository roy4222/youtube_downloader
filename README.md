# YouTube 影片下載工具

這是一個基於 Python 的 YouTube 影片下載工具，使用 yt-dlp 來下載 YouTube 影片。本工具提供簡單的命令行界面，支援多種下載格式和畫質選擇。

## 功能特點

- 支援多種下載格式：
  - 一般版（MP4 + 音頻）
  - 純音樂（MP3）
- 支援多種影片畫質選擇（MP4版本）
- 即時顯示下載進度和速度
- 自動合併影片和音訊
- 智能檔案命名

## 系統需求

- Python 3.x
- yt-dlp
- ffmpeg（用於合併影片和音訊、轉換格式）

## 安裝方式

1. 複製此專案：
```bash
git clone [your-repository-url]
```

2. 安裝必要套件：
```bash
pip install -r requirements.txt
```

3. 確保已安裝 ffmpeg 並添加到系統環境變數中

## 使用方法

執行 Python 腳本：

```bash
python youtube_downloader.py
```

程式會引導你：
1. 輸入 YouTube 影片網址
2. 選擇下載格式（一般版/純音樂）
3. 選擇視頻畫質（如果選擇一般版）
4. 等待下載完成

## 注意事項

- 預設將檔案儲存在 'downloads' 資料夾
- 下載過程中會顯示進度和下載速度
- MP3 格式預設使用 192kbps 的音質
- 確保系統已安裝 ffmpeg

## 授權條款

本專案採用 MIT 授權條款。

## 參與貢獻

歡迎 fork 此專案並提交 pull requests 來改善功能。
