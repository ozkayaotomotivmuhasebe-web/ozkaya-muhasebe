# Muhasebe Takip Sistemi - PowerShell Kurulum Scripti
# Kullanım: .\setup.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Muhasebe Takip Sistemi - PowerShell Kurulum" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# PowerShell yürütme ilkesi kontrol et
if ((Get-ExecutionPolicy) -eq "Restricted") {
    Write-Host "PowerShell yürütme ilkesi ayarlanıyor..." -ForegroundColor Yellow
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
}

# Python kontrol et
Write-Host "Python kontrol ediliyor..." -ForegroundColor Yellow
$pythonCheck = & python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ HATA: Python 3.x yüklü değil!" -ForegroundColor Red
    Write-Host "🔗 Lütfen https://www.python.org/ adresinden Python kurun" -ForegroundColor Yellow
    Write-Host "⚠️  Kurulum sırasında 'Add Python to PATH' seçeneğini işaretleyin" -ForegroundColor Yellow
    Read-Host "Devam etmek için Enter'e basın"
    exit 1
}

Write-Host "✓ Python bulundu: $pythonCheck" -ForegroundColor Green
Write-Host ""

# Bağımlılıkları kur
Write-Host "Bağımlılıklar yükleniyor..." -ForegroundColor Yellow
$requirements = Get-Content .\requirements.txt
foreach ($package in $requirements) {
    if ($package -and -not $package.StartsWith("#")) {
        Write-Host "  → $package" -ForegroundColor Gray
    }
}
Write-Host ""

pip install -r requirements.txt | Out-Null

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ HATA: Bağımlılıklar yüklenemedi!" -ForegroundColor Red
    Read-Host "Devam etmek için Enter'e basın"
    exit 1
}

Write-Host "✓ Bağımlılıklar başarıyla yüklendi" -ForegroundColor Green
Write-Host ""

# Örnek veri dosyaları oluştur
$sampleDataExists = Test-Path "sample_data"
if (-not $sampleDataExists) {
    Write-Host "Örnek Excel dosyaları oluşturuluyor..." -ForegroundColor Yellow
    python create_sample_data.py
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Green
Write-Host "✓ Kurulum başarıyla tamamlandı!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Uygulamayı başlat
Write-Host "Uygulamayı başlatmak için enter'e basın..." -ForegroundColor Cyan
Write-Host "çıkış yapmak için CTRL+C tuşlarına basın" -ForegroundColor Gray
Read-Host

Write-Host ""
Write-Host "Uygulamayı başlatıyor..." -ForegroundColor Yellow
python main.py
