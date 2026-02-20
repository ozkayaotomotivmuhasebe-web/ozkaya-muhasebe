@echo off
REM Muhasebe Takip Sistemi - Kurulum Betiği

echo ========================================
echo Muhasebe Takip Sistemi - Otomatik Kurulum
echo ========================================
echo.

REM Python'un yüklü olup olmadığını kontrol et
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo HATA: Python 3.x yüklü değil!
    echo Lütfen Python 3.x'i zamanında kurun.
    echo https://www.python.org/ adresinden indirebilirsiniz.
    pause
    exit /b 1
)

echo ✓ Python bulundu
echo.

echo Bağımlılıklar yükleniyor...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo HATA: Bağımlılıklar yüklenemedi!
    pause
    exit /b 1
)

echo.
echo ✓ Kurulum başarılı!
echo.
echo Uygulamayı başlatmak için: python main.py
echo.

REM Uygulamayı başlat
python main.py

pause
