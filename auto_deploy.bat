@echo off
setlocal enabledelayedexpansion

echo ============================================
echo   OTOMATIK RAILWAY DEPLOYMENT
echo ============================================
echo.

REM Git path tanimlari
set GIT="C:\Program Files\Git\cmd\git.exe"
set GH="C:\Program Files\GitHub CLI\gh.exe"

REM Klasore git
cd /d "%~dp0"

echo [1/8] Git config ayarlaniyor...
%GIT% config user.name "OZKAYA" 2>nul
%GIT% config user.email "kolayinsanlar@gmail.com" 2>nul

echo [2/8] Dosyalar Git'e ekleniyor...
%GIT% add .

echo [3/8] Commit yapiliyor...
%GIT% commit -m "Railway deployment - Muhasebe Sistemi" 2>nul

echo [4/8] GitHub CLI ile login...
%GH% auth login --web

echo [5/8] GitHub repository olusturuluyor...
%GH% repo create muhasebe-ozkaya --public --source=. --remote=origin --push

echo.
echo ============================================
echo   GITHUB'A PUSH TAMAMLANDI!
echo ============================================
echo.
echo Repository: https://github.com/kolayinsanlar/muhasebe-ozkaya
echo.
echo.
echo SIMDI RAILWAY'E GECIN:
echo.
echo 1. https://railway.app/dashboard
echo 2. New Project > Deploy from GitHub repo
echo 3. muhasebe-ozkaya repository'sini sec
echo 4. Deploy Now
echo.
echo Deploy bittikten sonra:
echo Settings > Networking > Generate Domain
echo Subdomain: ozkaya
echo.
pause

REM Railway dashboard'u ac
start https://railway.app/dashboard

echo.
echo Alternatif: Railway CLI ile deploy (network calisirsa)
echo railway up
echo.
pause
