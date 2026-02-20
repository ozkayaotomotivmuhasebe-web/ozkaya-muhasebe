@echo off
REM Muhasebe Takip Sistemi - Yeni Logo ile EXE Oluşturma

echo ========================================
echo ÖZKAYA Logo ile EXE Oluşturma
echo ========================================
echo.

REM Logo kontrol et
if not exist ICON.ico (
    echo ✓ Logo oluşturuluyor...
    python create_logo.py
    if not exist ICON.ico (
        echo ❌ HATA: Logo oluşturulamadı!
        pause
        exit /b 1
    )
)

echo.
echo Eski build dosyaları temizleniyor...
if exist build rmdir /s /q build >nul 2>&1
if exist dist rmdir /s /q dist >nul 2>&1

echo.
echo ✓ Logo ile yeni EXE oluşturuluyor...
echo   (Bu biraz zaman alabilir...)
echo.

pyinstaller --onefile --windowed --name "Muhasebe" --icon=ICON.ico main.py

if not exist dist\Muhasebe.exe (
    echo ❌ HATA: EXE oluşturulamadı!
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✓ Yeni EXE başarıyla oluşturuldu!
echo ========================================
echo.
echo Konum: dist\Muhasebe.exe
echo Logo: ICON.ico
echo.
echo Şimdi kurulum paketini güncelleyelim...
echo.

REM Mevcut paket güncelle
if exist muhasebe_kurulu\dist\Muhasebe.exe (
    copy dist\Muhasebe.exe muhasebe_kurulu\dist\ /y >nul
    echo ✓ muhasebe_kurulu klasörü güncellendi
)

echo.
echo Hazır! Masaüstü kısayolunu silip yeniden oluşturalım...
echo.

REM Masaüstü kısayolu
setlocal enabledelayedexpansion
set "DESKTOP=%USERPROFILE%\Desktop"
del "%DESKTOP%\Muhasebe.lnk" >nul 2>&1

set "CURRENT_DIR=%~dp0"
set "EXE_PATH=%CURRENT_DIR%dist\Muhasebe.exe"

(
    echo Set oWS = WScript.CreateObject("WScript.Shell"^)
    echo strDesktop = oWS.SpecialFolders("Desktop"^)
    echo.
    echo Set oLink = oWS.CreateShortcut(strDesktop ^& "\Muhasebe.lnk"^)
    echo oLink.TargetPath = "%EXE_PATH%"
    echo oLink.WorkingDirectory = "%CURRENT_DIR%"
    echo oLink.IconLocation = "%EXE_PATH%"
    echo oLink.WindowStyle = 1
    echo oLink.Description = "ÖZKAYA Muhasebe Takip Sistemi"
    echo oLink.Save
) > create_shortcut_temp.vbs

cscript create_shortcut_temp.vbs >nul 2>&1
del create_shortcut_temp.vbs

echo ✓ Masaüstü kısayolu güncellendi
echo.
echo ========================================
echo ✓ TÜM İŞLEMLER TAMAMLANDI!
echo ========================================
echo.
echo Masaüstünüzde ÖZKAYA logosu simgesini göreceksiniz
echo Şimdi main.py çalıştırarak test edebilirsiniz
echo.

pause
