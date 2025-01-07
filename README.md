# YouTube 影片下載器

一個功能完整的 YouTube 影片下載工具，提供直觀的圖形介面，支援多種格式下載。

## 主要功能

### 下載功能
- 支援下載 YouTube 單一影片
- 支援下載 Bilibili 影片
- 可選擇影片品質（最高支援 4K，Bilibili 需要大會員權限）
- 支援純音樂下載（MP3 格式）
- 自動合併音訊和影片軌
- 支援斷點續傳
- 多線程下載加速

### 使用者介面
- 簡潔的圖形使用者介面
- 即時下載進度顯示
- 下載速度和剩餘時間顯示
- 可自訂下載目錄
- 支援檔案拖放功能
- 一鍵貼上 URL

### 其他功能
- 內建 ffmpeg，無需額外安裝
- 自動處理檔案名稱（移除非法字元）
- 顯示影片資訊（標題、時長、觀看次數等）
- 錯誤自動重試機制
- 支援代理伺服器設定

## 使用的函式庫

### 核心功能
- **yt-dlp**: 影片下載核心引擎，支援 YouTube 和 Bilibili
- **ffmpeg**: 影片處理和格式轉換
- **aria2c**: 多線程下載加速

### GUI 相關
- **tkinter**: 圖形介面框架
- **ttk**: 現代化 GUI 元件
- **PIL/Pillow**: 圖片處理（用於 GUI 圖示）

### 系統相關
- **os**: 檔案和路徑操作
- **sys**: 系統相關功能
- **pathlib**: 路徑處理
- **subprocess**: 外部程序執行
- **threading**: 多執行緒支援

## 使用方法

1. 下載最新的發行版本 `youtube_downloader.exe`
2. 執行程式（無需安裝，直接點擊執行）
3. 貼上 YouTube 或 Bilibili 影片網址（支援直接拖放）
4. 選擇下載格式：
   - 一般版（MP4 + 音頻）
   - 純音樂（MP3）
5. 選擇儲存位置
6. 點擊「開始下載」

## 開發環境需求

### 必要條件
- Python 3.11 或更高版本
- pip（Python 套件管理器）

### 相依套件
```
yt-dlp>=2023.12.30
tkinter
pillow
```
完整相依套件清單請見 `requirements.txt`

## 安裝開發環境

```bash
# 複製專案
git clone https://github.com/roy4222/youtube_downloader.git

# 進入專案目錄
cd youtube_downloader

# 安裝所需套件
pip install -r requirements.txt
```

## 打包執行檔

```bash
# 使用 PyInstaller 打包（包含 ffmpeg）
pyinstaller --onefile --noconsole --add-data "ffmpeg.exe;." youtube_downloader.py
```

## 常見問題

1. **下載速度慢？**
   - 檢查網路連線
   - 確認是否有使用代理伺服器
   - 可能是 YouTube 或 Bilibili 流量限制

2. **無法下載某些影片？**
   - 確認影片是否有地區限制
   - 檢查影片是否為會員專屬內容
   - 更新至最新版本

3. **下載失敗？**
   - 檢查網路連線
   - 確認磁碟空間是否足夠
   - 檢查是否有防火牆阻擋

## 貢獻指南

歡迎提交 Pull Request 或建立 Issue。

## 授權條款

MIT License

## 免責聲明

本工具僅供學習和個人使用。請遵守 YouTube 和 Bilibili 服務條款和著作權法。使用者須對下載內容負完全責任。
