@echo off
echo 開始打包影片下載器...

REM 設置環境變數
set PYTHONIOENCODING=utf-8
set PYTHONLEGACYWINDOWSSTDIO=1

REM 創建輸出目錄
if not exist output mkdir output

REM 檢查 ffmpeg.exe 是否存在
if not exist ffmpeg.exe (
    echo 錯誤：找不到 ffmpeg.exe 檔案
    exit /b 1
)

REM 執行 Nuitka 打包命令
echo 正在執行 Nuitka 打包命令...

python -m nuitka ^
    --standalone ^
    --enable-plugin=pyside6 ^
    --include-data-dir=. ^
    --windows-icon-from-ico=youtube.ico ^
    --output-dir=output ^
    --windows-disable-console ^
    --follow-imports ^
    --include-package=yt_dlp ^
    --include-package=core ^
    --include-package=ui ^
    --include-package=utils ^
    --assume-yes-for-downloads ^
    main.py

REM 檢查打包是否成功
if %ERRORLEVEL% neq 0 (
    echo 打包失敗！
    exit /b 1
)

REM 複製 ffmpeg.exe 到輸出目錄
echo 複製 ffmpeg.exe 到輸出目錄...
copy ffmpeg.exe output\main.dist\

echo 打包完成！應用程式位於：output\main.dist
echo 你可以將整個 main.dist 目錄分發給使用者
