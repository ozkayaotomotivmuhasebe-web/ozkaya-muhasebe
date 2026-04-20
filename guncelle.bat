@echo off
chcp 65001 >nul
title Muhasebe - Güncelleme

echo ================================================
echo   MUHASEBE TAKİP SİSTEMİ - GÜNCELLEME
echo ================================================
echo.
echo Yeni sürüm kontrol ediliyor...
echo.

REM GitHub API ile güncel sürümün download URL'sini al
for /f "delims=" %%U in ('powershell -NoProfile -Command "try { $r=(Invoke-WebRequest -Uri 'https://api.github.com/repos/ozkayaotomotivmuhasebe-web/ozkaya-muhasebe/releases/latest' -UseBasicParsing).Content | ConvertFrom-Json; ($r.assets | Where-Object { $_.name -eq 'Muhasebe.exe' }).browser_download_url } catch { '' }"') do set "EXE_URL=%%U"

if "%EXE_URL%"=="" (
    echo HATA: Guncel surum URL'si alinamadi. Internet baglantinizi kontrol edin.
    pause
    exit /b 1
)

echo Indiriliyor: %EXE_URL%
set "DEST=%TEMP%\Muhasebe_yeni.exe"

REM Mevcut EXE'nin konumunu bul
set "CURRENT_DIR=%~dp0"
set "TARGET=%CURRENT_DIR%Muhasebe.exe"

REM PowerShell ile indir
powershell -Command "& { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; $wc = New-Object System.Net.WebClient; Write-Host 'İndiriliyor...'; $wc.DownloadFile('%EXE_URL%', '%DEST%'); Write-Host 'İndirme tamamlandı.' }"

if not exist "%DEST%" (
    echo.
    echo HATA: Dosya indirilemedi! İnternet bağlantınızı kontrol edin.
    pause
    exit /b 1
)

REM Uygulama çalışıyorsa kapat
taskkill /f /im Muhasebe.exe >nul 2>&1
timeout /t 2 /nobreak >nul

REM Eski EXE'yi yenisiyle değiştir
echo Güncelleniyor...
move /y "%DEST%" "%TARGET%" >nul 2>&1

if not exist "%TARGET%" (
    REM Aynı klasörde değilse masaüstüne koy
    set "TARGET=%USERPROFILE%\Desktop\Muhasebe.exe"
    move /y "%DEST%" "%TARGET%" >nul 2>&1
)

echo.
echo ================================================
echo   Güncelleme tamamlandı!
echo ================================================
echo.
echo Uygulama başlatılıyor...
timeout /t 2 /nobreak >nul
start "" "%TARGET%"
exit
