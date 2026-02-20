#!/bin/bash
# Muhasebe Takip Sistemi - Linux/Mac Kurulum Scripti

echo "========================================"
echo "Muhasebe Takip Sistemi - Kurulum"
echo "========================================"
echo ""

# Python kontrol et
if ! command -v python3 &> /dev/null; then
    echo "❌ HATA: Python 3 yüklü değil!"
    echo "🔗 Ubuntu/Debian: sudo apt-get install python3 python3-pip"
    echo "🔗 macOS: brew install python3"
    exit 1
fi

echo "✓ Python bulundu: $(python3 --version)"
echo ""

# Sanal ortam oluştur (opsiyonel)
if [ ! -d "venv" ]; then
    echo "Sanal ortam oluşturuluyor..."
    python3 -m venv venv
    source venv/bin/activate
fi

# Bağımlılıkları kur
echo "Bağımlılıklar yükleniyor..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ HATA: Bağımlılıklar yüklenemedi!"
    exit 1
fi

echo ""
echo "✓ Kurulum başarıyla tamamlandı!"
echo ""

# Örnek veri oluştur
if [ ! -d "sample_data" ]; then
    echo "Örnek Excel dosyaları oluşturuluyor..."
    python3 create_sample_data.py
fi

echo ""
echo "Uygulamayı başlatıyor..."
python3 main.py
