@echo off
echo ============================================
echo   RAILWAY DEPLOY - GIT OLMADAN
echo ============================================
echo.
echo Git olmadan deploy icin Railway CLI kullanin:
echo.

REM Node.js kontrol
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Node.js yuklu degil!
    echo Node.js indirin: https://nodejs.org/
    echo.
    start https://nodejs.org/
    pause
    exit /b 1
)

echo [OK] Node.js bulundu!
echo.

echo Railway CLI kuruluyor...
npm i -g @railway/cli

echo.
echo Railway'e login olun...
railway login

echo.
echo Proje baslatiliyor...
railway init

echo.
echo Deploy ediliyor...
railway up

echo.
echo ============================================
echo   DEPLOY TAMAMLANDI!
echo ============================================
echo.
echo Railway dashboard'a git:
echo https://railway.app/dashboard
echo.
echo Settings > Networking > Generate Domain
echo Subdomain: ozkaya
echo.
pause
