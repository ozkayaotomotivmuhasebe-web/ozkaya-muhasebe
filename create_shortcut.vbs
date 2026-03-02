@echo off

echo Muhasebe masaüstü kısayolu oluşturuluyor...

setlocal enabledelayedexpansion

set "CURRENT_DIR=%~dp0"
set "DESKTOP=%USERPROFILE%\Desktop"
set "EXE_PATH=%CURRENT_DIR%dist\Muhasebe.exe"

if not exist "%EXE_PATH%" (
    echo ✓ Uygulamayı ayarlamak için setup.bat çalıştırın
    set "EXE_PATH=%CURRENT_DIR%setup.bat"
)

(
    echo Set oWS = WScript.CreateObject("WScript.Shell")
    echo strDesktop = oWS.SpecialFolders("Desktop")
    echo.
    echo Set oLink = oWS.CreateShortcut(strDesktop & "\Muhasebe.lnk")
    echo oLink.TargetPath = "%EXE_PATH%"
    echo oLink.WorkingDirectory = "%CURRENT_DIR%"
    echo oLink.IconLocation = "%EXE_PATH%"
    echo oLink.WindowStyle = 1
    echo oLink.Description = "Muhasebe Takip Sistemi"
    echo oLink.Save
    echo.
    echo MsgBox "Muhasebe masaüstü kısayolu oluşturuldu", 0, "Başarılı"
ECHO is off.
