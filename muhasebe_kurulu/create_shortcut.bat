@echo off
REM Muhasebe Masaüstü Kısayolu Oluşturma Scripti

echo Muhasebe Takip Sistemi masaüstü kısayolu oluşturuluyor...

setlocal enabledelayedexpansion

REM Mevcut dizin
set "CURRENT_DIR=%~dp0"
set "DESKTOP=%USERPROFILE%\Desktop"
set "EXE_PATH=%CURRENT_DIR%dist\Muhasebe.exe"

REM VBScript ile kısayol oluştur
(
    echo Set oWS = WScript.CreateObject("WScript.Shell"^)
    echo strDesktop = oWS.SpecialFolders("Desktop"^)
    echo strProgramFiles = oWS.SpecialFolders("Programs"^)
    echo.
    echo Set oLink = oWS.CreateShortcut(strDesktop ^& "\Muhasebe.lnk"^)
    echo oLink.TargetPath = "%EXE_PATH%"
    echo oLink.WorkingDirectory = "%CURRENT_DIR%"
    echo oLink.WindowStyle = 1
    echo oLink.Description = "Muhasebe Takip Sistemi"
    echo oLink.Save
    echo.
    echo MsgBox "Muhasebe masaüstü kısayolu oluşturuldu!", 0, "Başarılı"
) > create_shortcut.vbs

cscript create_shortcut.vbs

del create_shortcut.vbs

echo ✓ Kısayol oluşturuldu!
echo.
echo Masaüstünüzde "Muhasebe" simgesini göreceksiniz.
echo.
pause
