@echo off
echo ========================================
echo   LOCALTUNNEL - SIFRESIZ ERISIM
echo ========================================
echo.
echo NOT: LocalTunnel ilk erisimde IP dogrulamasi ister.
echo Bu normal bir guvenlik ozelligi.
echo.
echo Cozum: Tarayicida "Click to Continue" tiklayin
echo ve IP adresinizi onaylayin.
echo.
echo Alternatif: Ngrok kullanin (sifre sorunu yok)
echo.
pause

REM Web uygulamasini baslat
echo.
echo Web uygulamasi baslatiliyor...
start "Muhasebe Web" cmd /k "cd /d "%~dp0" && python -m uvicorn web_app.main:app --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak >nul

REM LocalTunnel'i subdomain ile baslat
echo.
echo LocalTunnel baslatiliyor...
echo URL: https://muhasebe-ozkaya.loca.lt
echo.
echo ONEMLI: Ilk erisimde IP dogrulamasi gerekir!
echo Terminal'de gosterilen instruksiyonlari takip edin.
echo.

npx localtunnel --port 8000 --subdomain muhasebe-ozkaya --print-requests

pause
