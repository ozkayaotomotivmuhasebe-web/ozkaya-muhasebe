@echo off
echo ========================================
echo   PUBLIC URL KURULUM - NGROK
echo ========================================
echo.

REM Ngrok yuklu mu kontrol et
where ngrok >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Ngrok yuklu degil!
    echo.
    echo Ngrok indirme adimlari:
    echo 1. https://ngrok.com/download adresine git
    echo 2. Windows icin indir
    echo 3. ZIP'i ac ve ngrok.exe dosyasini bu klasore kopyala
    echo 4. https://dashboard.ngrok.com/get-started/setup adresinden token al
    echo.
    pause
    exit /b 1
)

echo [OK] Ngrok bulundu!
echo.
echo Ngrok token'inizi girdiniz mi? (Y/N)
set /p token_ok="> "

if /i "%token_ok%"=="N" (
    echo.
    echo Token alma adimlari:
    echo 1. https://dashboard.ngrok.com/signup adresine kaydol (UCRETSIZ)
    echo 2. Dashboard'da authtoken'i kopyala
    echo 3. Komutu calistir: ngrok config add-authtoken YOUR_TOKEN
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   WEB UYGULAMASI BASLATILIYOR
echo ========================================
echo.

REM Yeni terminal penceresi ile web uygulamasini baslat
start "Muhasebe Web App" cmd /k "cd /d "%~dp0" && python -m uvicorn web_app.main:app --host 0.0.0.0 --port 8000"

echo Web uygulamasi baslatildi (Port 8000)...
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo   NGROK TUNNEL BASLATILIYOR
echo ========================================
echo.

REM Ngrok'u baslat
ngrok http 8000

pause
