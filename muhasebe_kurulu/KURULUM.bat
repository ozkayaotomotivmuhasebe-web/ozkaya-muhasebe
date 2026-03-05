@echo off
echo OZKAYA Muhasebe - Kurulum
echo.

set "APP=%~dp0"
set "EXE=%APP%Muhasebe.exe"

if not exist "%EXE%" (
    echo HATA: Muhasebe.exe bulunamadi!
    pause
    exit /b 1
)

if not exist "%APP%data" mkdir "%APP%data"
if not exist "%APP%data\google_credentials" mkdir "%APP%data\google_credentials"

echo Masaustu kisayolu olusturuluyor...
powershell -Command "$ws=New-Object -com WScript.Shell;$sc=$ws.CreateShortcut(\"$env:USERPROFILE\Desktop\OZKAYA Muhasebe.lnk\");$sc.TargetPath='%EXE%';$sc.WorkingDirectory='%APP%';$sc.IconLocation='%EXE%';$sc.Description='OZKAYA Muhasebe';$sc.Save()"

echo.
echo Kurulum tamamlandi!
echo Masaustundeki "OZKAYA Muhasebe" kisayoluna cift tiklayin.
echo.
echo Google Sheets icin: GOOGLE_SHEETS_KURULUM.txt dosyasini okuyun
echo.
set /p ST="Uygulamayi simdi baslat? (E/H): "
if /i "%ST%"=="E" start "" "%EXE%"
pause