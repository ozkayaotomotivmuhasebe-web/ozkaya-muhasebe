@echo off
echo ======================================
echo   Muhasebe Sistemi - Web Uygulamasi
echo ======================================
echo.

REM Web gereksinimleri yukle
echo Web uygulamasi gereksinimleri yukleniyor...
pip install -r web_app\requirements_web.txt

REM Uygulamayi baslat
echo.
echo Uygulama baslatiliyor...
echo URL: http://localhost:8000
echo Admin: admin / admin123
echo.

cd web_app
python main.py

pause
