@echo off
REM Muhasebe Takip Sistemi - Yeni Logo ile EXE Oluşturma

echo ========================================
echo ÖZKAYA Logo ile EXE Oluşturma
echo ========================================
echo.

REM Venv Python'ı kullan (PyQt5 dahil)
set "VENV_PYTHON=C:\Users\aryam\AppData\Local\Programs\Python\Python311\python.exe"
if not exist "%VENV_PYTHON%" (
    set "VENV_PYTHON=.venv\Scripts\python.exe"
)
if not exist "%VENV_PYTHON%" set "VENV_PYTHON=python"

REM Logo ve ikon her build'de güncellensin
echo ✓ Logo ve ikon güncelleniyor...
%VENV_PYTHON% create_logo.py
set "ICON_FILE=ICON.ico"
if exist "yeni icon.ico" set "ICON_FILE=yeni icon.ico"
if not exist "%ICON_FILE%" (
    echo ❌ HATA: ICON.ico oluşturulamadı!
    pause
    exit /b 1
)

echo.
echo Eski build dosyaları temizleniyor...
if exist build rmdir /s /q build >nul 2>&1
if exist dist rmdir /s /q dist >nul 2>&1

echo.
echo ✓ Logo ile yeni EXE oluşturuluyor...
echo   (Bu biraz zaman alabilir...)
echo.

REM Python DLL'lerini bul (VC++ Runtime dahil etmek için)
set "PYTHON_DIR="
for /f "tokens=*" %%i in ('%VENV_PYTHON% -c "import sys, os; print(os.path.dirname(sys.executable))"') do set "PYTHON_DIR=%%i"
echo Python dizini: %PYTHON_DIR%

REM VC++ Runtime DLL'leri - python311.dll'nin bağımlılıkları (tekrar ekleme yok)
set "VCRT_ARGS="

REM VCRUNTIME140.dll - Python dir tercihli, yoksa System32
if exist "%PYTHON_DIR%\VCRUNTIME140.dll" (
    set "VCRT_ARGS=%VCRT_ARGS% --add-binary "%PYTHON_DIR%\VCRUNTIME140.dll;.""
) else if exist "C:\Windows\System32\VCRUNTIME140.dll" (
    set "VCRT_ARGS=%VCRT_ARGS% --add-binary "C:\Windows\System32\VCRUNTIME140.dll;.""
)

REM VCRUNTIME140_1.dll
if exist "%PYTHON_DIR%\VCRUNTIME140_1.dll" (
    set "VCRT_ARGS=%VCRT_ARGS% --add-binary "%PYTHON_DIR%\VCRUNTIME140_1.dll;.""
) else if exist "C:\Windows\System32\VCRUNTIME140_1.dll" (
    set "VCRT_ARGS=%VCRT_ARGS% --add-binary "C:\Windows\System32\VCRUNTIME140_1.dll;.""
)

REM MSVCP140.dll
if exist "%PYTHON_DIR%\MSVCP140.dll" (
    set "VCRT_ARGS=%VCRT_ARGS% --add-binary "%PYTHON_DIR%\MSVCP140.dll;.""
) else if exist "C:\Windows\System32\MSVCP140.dll" (
    set "VCRT_ARGS=%VCRT_ARGS% --add-binary "C:\Windows\System32\MSVCP140.dll;.""
)

REM python311.dll'yi de açıkça ekle
if exist "%PYTHON_DIR%\python311.dll" (
    set "VCRT_ARGS=%VCRT_ARGS% --add-binary "%PYTHON_DIR%\python311.dll;.""
)

echo VCRT_ARGS: %VCRT_ARGS%

%VENV_PYTHON% -m PyInstaller --clean --noconfirm --onefile --windowed --name "Muhasebe" --icon="%ICON_FILE%" --add-data "%ICON_FILE%;." --add-data "ICON.ico;." --add-data "logo.png;." --add-data "icon.png;." --hidden-import=PyQt5 %VCRT_ARGS% main.py

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

REM Dist klasörüne güncel icon kopyala
if exist ICON.ico (
    copy ICON.ico dist\ /y >nul
)
if exist "yeni icon.ico" (
    copy "yeni icon.ico" dist\ /y >nul
)
if exist icon.png (
    copy icon.png dist\ /y >nul
)
if exist logo.png (
    copy logo.png dist\ /y >nul
)

REM Mevcut paket güncelle
if exist muhasebe_kurulu (
    if not exist muhasebe_kurulu\dist mkdir muhasebe_kurulu\dist
    copy dist\Muhasebe.exe muhasebe_kurulu\dist\ /y >nul
    copy dist\Muhasebe.exe muhasebe_kurulu\Muhasebe.exe /y >nul
    if exist ICON.ico copy ICON.ico muhasebe_kurulu\ /y >nul
    if exist ICON.ico copy ICON.ico muhasebe_kurulu\dist\ /y >nul
    if exist "yeni icon.ico" copy "yeni icon.ico" muhasebe_kurulu\ /y >nul
    if exist "yeni icon.ico" copy "yeni icon.ico" muhasebe_kurulu\dist\ /y >nul
    if exist icon.png copy icon.png muhasebe_kurulu\ /y >nul
    if exist icon.png copy icon.png muhasebe_kurulu\dist\ /y >nul
    if exist logo.png copy logo.png muhasebe_kurulu\ /y >nul
    if exist logo.png copy logo.png muhasebe_kurulu\dist\ /y >nul
    copy main.py muhasebe_kurulu\ /y >nul
    copy config.py muhasebe_kurulu\ /y >nul
    copy version.json muhasebe_kurulu\ /y >nul
    copy guncelle.bat muhasebe_kurulu\ /y >nul
    if exist KURULUM.bat copy KURULUM.bat muhasebe_kurulu\ /y >nul
    if exist GOOGLE_SHEETS_KURULUM.txt copy GOOGLE_SHEETS_KURULUM.txt muhasebe_kurulu\ /y >nul
    if exist "yeni icon.ico" copy "yeni icon.ico" muhasebe_kurulu\ /y >nul
    copy requirements.txt muhasebe_kurulu\ /y >nul
    robocopy src muhasebe_kurulu\src /MIR /XD __pycache__ /NFL /NDL /NJH /NJS >nul
    echo ✓ muhasebe_kurulu klasoru exe-src-ayarlar ile guncellendi
)

echo.
echo ✓ Build tamamlandı, tekrar derleme atlandı.

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
