@echo off
echo ============================================
echo   RAILWAY DEPLOYMENT - ADIM ADIM
echo ============================================
echo.

REM Git yuklu mu kontrol et
where git >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Git yuklu degil!
    echo Git indirin: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo [1/6] Git repository baslatiliyor...
git init
echo.

echo [2/6] .gitignore kontrol ediliyor...
if not exist .gitignore (
    echo .gitignore olusturuluyor...
    echo __pycache__/ > .gitignore
    echo *.pyc >> .gitignore
    echo .env >> .gitignore
    echo *.db >> .gitignore
)
echo.

echo [3/6] Dosyalar ekleniyor...
git add .
echo.

echo [4/6] Commit yapiliyor...
git commit -m "Initial commit - Railway deployment"
echo.

echo ============================================
echo   GITHUB REPOSITORY OLUSTURMA
echo ============================================
echo.
echo Simdi GitHub'da repository olusturmaniz gerekiyor:
echo.
echo 1. https://github.com/new adresine git
echo 2. Repository name: muhasebe-ozkaya (veya istediginiz isim)
echo 3. Private veya Public sec
echo 4. Create repository tikla
echo.
echo GitHub repository URL'ini girin (ornek: https://github.com/kullanici/muhasebe-ozkaya.git):
set /p repo_url="> "

if "%repo_url%"=="" (
    echo [!] URL girilmedi!
    pause
    exit /b 1
)

echo.
echo [5/6] Remote repository ekleniyor...
git remote add origin %repo_url%
echo.

echo [6/6] GitHub'a push yapiliyor...
git branch -M main
git push -u origin main

echo.
echo ============================================
echo   GITHUB PUSH TAMAMLANDI!
echo ============================================
echo.
echo SIMDI RAILWAY'E GECIN:
echo.
echo 1. https://railway.app/ adresine git
echo 2. GitHub ile giris yap
echo 3. "New Project" tikla
echo 4. "Deploy from GitHub repo" sec
echo 5. Repository'nizi sec: muhasebe-ozkaya
echo 6. "Deploy Now" tikla
echo.
echo Otomatik deploy baslar!
echo.
echo Deployment bittikten sonra:
echo - Settings ^> Networking ^> Generate Domain
echo - ozkaya (veya istediginiz isim) yazip Save
echo - ozkaya.up.railway.app HAZIR!
echo.
pause
