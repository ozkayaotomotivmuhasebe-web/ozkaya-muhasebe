@echo off
chcp 65001 >nul
title Muhasebe - Güncelleme

echo ================================================
echo   MUHASEBE TAKİP SİSTEMİ - GÜNCELLEME
echo ================================================
echo.
echo Yeni sürüm indiriliyor, lütfen bekleyin...
echo.

set "EXE_URL=https://github.com/buraktekin060-glitch/ozkaya-muhasebe/releases/download/v1.0.3/Muhasebe.exe"
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
echo   Güncelleme tamamlandı!  Sürüm: v1.0.3
echo ================================================
echo.
echo Uygulama başlatılıyor...
timeout /t 2 /nobreak >nul
start "" "%TARGET%"
exit
