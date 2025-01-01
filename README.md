# YouTube 影片下載工具

這是一個基於 Python 的 YouTube 影片下載工具，使用 yt-dlp 來下載 YouTube 影片。本工具提供簡單的命令行界面，支援多種畫質選擇。

## 功能特點

- 下載完整的 YouTube 影片
- 支援多種影片畫質選擇
- 即時顯示下載進度和速度
- 自動合併影片和音訊
- 智能檔案命名

## 系統需求

- Python 3.x
- yt-dlp
- ffmpeg（用於合併影片和音訊）

## 安裝方式

1. 複製此專案：
```bash
git clone [your-repository-url]
```

2. 安裝必要套件：
```bash
pip install -r requirements.txt
```

## 使用方法

執行 Python 腳本：

```bash
python youtube_downloader.py
```

程式會引導你：
1. 輸入 YouTube 影片網址
2. 選擇要下載的影片畫質
3. 等待下載完成

## 注意事項

- 預設將檔案儲存在 'downloads' 資料夾
- 下載過程中會顯示進度和下載速度
- 確保系統已安裝 ffmpeg

## 授權條款

本專案採用 MIT 授權條款。

## 參與貢獻

歡迎 fork 此專案並提交 pull requests 來改善功能。
