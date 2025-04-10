# 影片下載器打包腳本
Write-Host "開始打包影片下載器..." -ForegroundColor Green

# 創建輸出目錄
if (-not (Test-Path -Path "output")) {
    New-Item -Path "output" -ItemType Directory | Out-Null
}

# 檢查 ffmpeg.exe 是否存在
if (-not (Test-Path -Path "ffmpeg.exe")) {
    Write-Host "錯誤：找不到 ffmpeg.exe 檔案" -ForegroundColor Red
    exit 1
}

# 執行 Nuitka 打包命令
Write-Host "正在執行 Nuitka 打包命令..." -ForegroundColor Yellow

$nuitkaArgs = @(
    "-m", "nuitka",
    "--standalone",
    "--enable-plugin=pyside6",
    "--include-data-dir=.",
    "--windows-icon-from-ico=youtube.ico",
    "--output-dir=output",
    "--windows-disable-console",
    "--follow-imports",
    "--include-package=yt_dlp",
    "--include-package=core",
    "--include-package=ui",
    "--include-package=utils",
    "--assume-yes-for-downloads",
    "main.py"
)

# 執行 Nuitka 命令
& "python" $nuitkaArgs

# 檢查打包是否成功
if ($LASTEXITCODE -ne 0) {
    Write-Host "打包失敗！" -ForegroundColor Red
    exit 1
}

# 複製 ffmpeg.exe 到輸出目錄
Write-Host "複製 ffmpeg.exe 到輸出目錄..." -ForegroundColor Yellow
Copy-Item -Path "ffmpeg.exe" -Destination "output\main.dist\" -Force

Write-Host "打包完成！應用程式位於：output\main.dist" -ForegroundColor Green
Write-Host "你可以將整個 main.dist 目錄分發給使用者" -ForegroundColor Green
