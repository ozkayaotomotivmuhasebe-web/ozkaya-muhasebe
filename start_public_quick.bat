@echo off
echo ========================================
echo   HIZLI PUBLIC URL - LOCALTUNNEL
echo   (Ngrok alternatifi - daha hizli)
echo ========================================
echo.

REM Node.js yuklu mu kontrol et
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Node.js yuklu degil!
    echo.
    echo Node.js indirmek icin:
    echo https://nodejs.org/
    echo.
    echo Veya Ngrok kullanin: setup_public_url.bat
    pause
    exit /b 1
)

echo [OK] Node.js bulundu!
echo.

REM Web uygulamasini yeni pencerede baslat
echo Web uygulamasi baslatiliyor...
start "Muhasebe Web App" cmd /k "cd /d "%~dp0" && python -m uvicorn web_app.main:app --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo   PUBLIC URL OLUSTURULUYOR...
echo ========================================
echo.
echo Subdomain seciniz (bos birakabilirsiniz):
set /p subdomain="Subdomain (ornek: muhasebe-ozkaya): "

if "%subdomain%"=="" (
    echo.
    echo Random URL olusturuluyor...
    npx localtunnel --port 8000
) else (
    echo.
    echo https://%subdomain%.loca.lt adresinde aciliyor...
    npx localtunnel --port 8000 --subdomain %subdomain%
)

pause
