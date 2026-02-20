@echo off
echo ============================================
echo   GITHUB MANUEL UPLOAD REHBERI
echo ============================================
echo.
echo Railway CLI timeout sorunu var.
echo En garantili yontem: GitHub uzerinden
echo.
echo ADIM 1: GitHub'da Repository Olustur
echo ----------------------------------------
echo 1. https://github.com/new acilacak
echo 2. Repository name: muhasebe-ozkaya
echo 3. Public sec
echo 4. "Create repository" tikla
echo.
echo ADIM 2: Dosyalari Yukle
echo ----------------------------------------
echo 5. "uploading an existing file" linkine tikla
echo 6. Su klasordeki TUM dosyalari surukle:
echo    %cd%
echo.
echo    Dahil edilecekler:
echo    - web_app klasoru
echo    - src klasoru
echo    - Procfile
echo    - requirements.txt
echo    - runtime.txt
echo    - config.py
echo    - main.py
echo    - Ve diger tum dosyalar
echo.
echo    HARİÇ tutulacaklar (suruklemEyin):
echo    - __pycache__
echo    - *.db
echo    - .git
echo.
echo 7. "Commit changes" tikla
echo.
echo ADIM 3: Railway'e Bagla
echo ----------------------------------------
echo 8. https://railway.app/dashboard acilacak
echo 9. "New Project" tikla
echo 10. "Deploy from GitHub repo" sec
echo 11. "muhasebe-ozkaya" repository'sini sec
echo 12. "Deploy Now" tikla
echo.
echo ADIM 4: Domain Ayarla (Deploy bitince)
echo ----------------------------------------
echo 13. Settings sekme > Networking
echo 14. "Generate Domain" tikla
echo 15. Custom subdomain: ozkaya
echo 16. Save
echo.
echo SONUC: https://ozkaya.up.railway.app
echo.
echo ============================================
pause

REM Tarayici ac
start https://github.com/new
timeout /t 2 >nul
start https://railway.app/dashboard
