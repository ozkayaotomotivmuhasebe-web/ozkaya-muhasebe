@echo off
chcp 65001 >nul 2>&1
title OZKAYA Muhasebe - Tasınabilir Paket Olusturucu

echo ================================================
echo  OZKAYA Muhasebe - Tasınabilir Paket Olusturucu
echo ================================================
echo.

set "SOURCE=%~dp0"
set "DEST=%USERPROFILE%\Desktop\OZKAYA_Muhasebe"

if exist "%DEST%" (
    echo Eski klasor temizleniyor...
    rmdir /s /q "%DEST%"
)
mkdir "%DEST%"
mkdir "%DEST%\data"
mkdir "%DEST%\data\google_credentials"

echo [1/6] EXE kopyalanıyor...
if not exist "%SOURCE%dist\Muhasebe.exe" (
    echo     HATA: dist\Muhasebe.exe bulunamadı. Once build_exe.bat calıstırın.
    pause
    exit /b 1
)
copy "%SOURCE%dist\Muhasebe.exe" "%DEST%\Muhasebe.exe" /y >nul
echo     OK: Muhasebe.exe

echo [2/6] Ikon ve gorseller kopyalanıyor...
if exist "%SOURCE%ICON.ico"        copy "%SOURCE%ICON.ico"       "%DEST%\" /y >nul
if exist "%SOURCE%yeni icon.ico"   copy "%SOURCE%yeni icon.ico"  "%DEST%\" /y >nul
if exist "%SOURCE%icon.png"        copy "%SOURCE%icon.png"       "%DEST%\" /y >nul
if exist "%SOURCE%logo.png"        copy "%SOURCE%logo.png"       "%DEST%\" /y >nul
echo     OK: Ikon dosyaları

echo [3/6] Veritabanı kopyalanıyor...
if exist "%SOURCE%data\muhasebe.db" (
    copy "%SOURCE%data\muhasebe.db" "%DEST%\data\muhasebe.db" /y >nul
    echo     OK: muhasebe.db verileri tasındı
) else (
    echo     UYARI: Veritaban bulunamadı uygulama ilk acılısta olusturacak
)

echo [4/6] Google Sheets kimlik bilgileri kopyalanıyor...
if exist "%SOURCE%data\google_credentials\credentials.json" (
    copy "%SOURCE%data\google_credentials\credentials.json" "%DEST%\data\google_credentials\credentials.json" /y >nul
    echo     OK: credentials.json kopyalandı
) else (
    echo     UYARI: credentials.json bulunamadı
    echo     Google Sheets ozelligi icin credentials.json gereklidir
)
if exist "%SOURCE%data\google_credentials\token.json" (
    copy "%SOURCE%data\google_credentials\token.json" "%DEST%\data\google_credentials\token.json" /y >nul
    echo     OK: token.json kopyalandı
)

echo [5/6] Kurulum dosyaları kopyalanıyor...
if exist "%SOURCE%KURULUM.bat"               copy "%SOURCE%KURULUM.bat"               "%DEST%\KURULUM.bat"               /y >nul
if exist "%SOURCE%GOOGLE_SHEETS_KURULUM.txt" copy "%SOURCE%GOOGLE_SHEETS_KURULUM.txt" "%DEST%\GOOGLE_SHEETS_KURULUM.txt" /y >nul
echo     OK: KURULUM.bat ve GOOGLE_SHEETS_KURULUM.txt

echo [6/6] Paket hazır.
echo.
echo ================================================
echo  PAKET HAZIR!
echo ================================================
echo.
echo  Konum: %DEST%
echo.
dir "%DEST%" /b
echo.
echo  Yeni bilgisayarda yapılacaklar:
echo   1. OZKAYA_Muhasebe klasorunu kopyalayın
echo   2. Icindeki KURULUM.bat calistırın
echo   3. Google Sheets icin GOOGLE_SHEETS_KURULUM.txt okuyun
echo.
pause
