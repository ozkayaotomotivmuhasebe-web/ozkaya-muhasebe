@echo off
REM Muhasebe Takip Sistemi - Taşınabilir Kurulum Paketi Oluşturma

echo ========================================
echo Muhasebe Takip Sistemi - Kurulum Paketi Oluşturma
echo ========================================
echo.

setlocal enabledelayedexpansion

REM Hedef klasör
set "OUTPUT_DIR=muhasebe_kurulu"

echo Kurulum dosyaları hazırlanıyor...
echo.

REM Dizin oluştur
if exist "%OUTPUT_DIR%" rmdir /s /q "%OUTPUT_DIR%"
mkdir "%OUTPUT_DIR%"

REM Gerekli dosyaları kopyala
echo ✓ Ana dosyalar kopyalanıyor...
copy main.py "%OUTPUT_DIR%" >nul
copy config.py "%OUTPUT_DIR%" >nul
copy version.json "%OUTPUT_DIR%" >nul
copy guncelle.bat "%OUTPUT_DIR%" >nul
if exist KURULUM.bat copy KURULUM.bat "%OUTPUT_DIR%" >nul
if exist GOOGLE_SHEETS_KURULUM.txt copy GOOGLE_SHEETS_KURULUM.txt "%OUTPUT_DIR%" >nul
if exist ICON.ico copy ICON.ico "%OUTPUT_DIR%" >nul
if exist "yeni icon.ico" copy "yeni icon.ico" "%OUTPUT_DIR%" >nul
if exist logo.png copy logo.png "%OUTPUT_DIR%" >nul
copy requirements.txt "%OUTPUT_DIR%" >nul
copy PORTABLE_SETUP.md "%OUTPUT_DIR%" >nul
copy README.md "%OUTPUT_DIR%" >nul

echo ✓ Kaynak kodlar kopyalanıyor...
xcopy src "%OUTPUT_DIR%\src" /s /i /q >nul

echo ✓ Örnek veriler kopyalanıyor...
if exist sample_data xcopy sample_data "%OUTPUT_DIR%\sample_data" /s /i /q >nul

echo ✓ Çalıştırılabilir dosya kopyalanıyor...
if exist dist\Muhasebe.exe (
    mkdir "%OUTPUT_DIR%\dist"
    copy dist\Muhasebe.exe "%OUTPUT_DIR%\dist" >nul
    copy dist\Muhasebe.exe "%OUTPUT_DIR%\Muhasebe.exe" >nul
)

if exist ICON.ico (
    copy ICON.ico "%OUTPUT_DIR%\dist" >nul
)

echo ✓ Kurulum scriptleri kopyalanıyor...
copy setup.bat "%OUTPUT_DIR%" >nul
copy setup.ps1 "%OUTPUT_DIR%" >nul
copy setup.sh "%OUTPUT_DIR%" >nul
copy create_shortcut.bat "%OUTPUT_DIR%" >nul

REM Masaüstü kısayolu oluşturma scripti
(
    echo @echo off
    echo.
    echo echo Muhasebe masaüstü kısayolu oluşturuluyor...
    echo.
    echo setlocal enabledelayedexpansion
    echo.
    echo set "CURRENT_DIR=%%~dp0"
    echo set "DESKTOP=%%USERPROFILE%%\Desktop"
    echo set "EXE_PATH=%%CURRENT_DIR%%dist\Muhasebe.exe"
    echo.
    echo if not exist "%%EXE_PATH%%" ^(
    echo     echo ✓ Uygulamayı ayarlamak için setup.bat çalıştırın
    echo     set "EXE_PATH=%%CURRENT_DIR%%setup.bat"
    echo ^)
    echo.
    echo (
    echo     echo Set oWS = WScript.CreateObject("WScript.Shell"^)
    echo     echo strDesktop = oWS.SpecialFolders("Desktop"^)
    echo     echo.
    echo     echo Set oLink = oWS.CreateShortcut(strDesktop ^& "\Muhasebe.lnk"^)
    echo     echo oLink.TargetPath = "%%EXE_PATH%%"
    echo     echo oLink.WorkingDirectory = "%%CURRENT_DIR%%"
    echo     echo oLink.IconLocation = "%%EXE_PATH%%"
    echo     echo oLink.WindowStyle = 1
    echo     echo oLink.Description = "Muhasebe Takip Sistemi"
    echo     echo oLink.Save
    echo     echo.
    echo     echo MsgBox "Muhasebe masaüstü kısayolu oluşturuldu!", 0, "Başarılı"
    echo ) > create_shortcut.vbs
    echo.
    echo cscript create_shortcut.vbs
    echo del create_shortcut.vbs
    echo.
    echo echo ✓ Kısayol oluşturuldu!
    echo pause
) > "%OUTPUT_DIR%\kurulum_sonrasi.bat"

echo.
echo ========================================
echo ✓ Kurulum Paketi Hazır!
echo ========================================
echo.
echo Oluşturulan klasör: %OUTPUT_DIR%
echo.
echo İçeriği:
echo  ✓ Muhasebe.exe (çalıştırılabilir dosya)
echo  ✓ src/ (kaynak kodlar)
echo  ✓ sample_data/ (örnek Excel dosyaları)
echo  ✓ setup.bat (Windows kurulum)
echo  ✓ PORTABLE_SETUP.md (rehber)
echo.
echo Başka bilgisayara taşımak için:
echo 1. %OUTPUT_DIR% klasörünü USB/Buluta kopyalayın
echo 2. Hedef bilgisayarda setup.bat çalıştırın
echo    veya doğrudan Muhasebe.exe'ye çift tıklayın
echo 3. Kısayol oluşturmak için kurulum_sonrasi.bat çalıştırın
echo.
pause
