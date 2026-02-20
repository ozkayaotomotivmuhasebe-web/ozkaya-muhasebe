@echo off
echo ============================================
echo   GIT KURULUM KONTROLU
echo ============================================
echo.
echo Git yuklu degil!
echo.
echo COZUM 1: Git Kur (5 dakika)
echo.
echo 1. https://git-scm.com/download/win adresine git
echo 2. "Click here to download" tikla
echo 3. Kurulumdaki tum ayarlari varsayilan birak
echo 4. Kurulum bitince terminali yeniden baslat
echo 5. Bu dosyayi tekrar calistir: deploy_railway.bat
echo.
echo ============================================
echo.
echo COZUM 2: Railway CLI (Git olmadan)
echo.
echo 1. Node.js yuklu mu kontrol et: node --version
echo 2. Railway CLI kur: npm i -g @railway/cli
echo 3. Railway login: railway login
echo 4. Deploy: railway init && railway up
echo.
echo ============================================
echo.
echo COZUM 3: Manuel GitHub Upload (En basit)
echo.
echo 1. https://github.com/new adresine git
echo 2. Repository olustur: muhasebe-ozkaya
echo 3. "uploading an existing file" linkine tikla
echo 4. Proje klasorundeki TUM dosyalari surukle
echo 5. "Commit changes" tikla
echo 6. Railway'e git ve GitHub repo'yu sec
echo.
echo ============================================
pause

REM Tarayici ac
start https://git-scm.com/download/win
start https://github.com/new
