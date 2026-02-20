#!/bin/bash
echo "========================================"
echo "  PUBLIC URL - MUHASEBE SISTEMI"
echo "========================================"
echo ""

# Web uygulamasını arka planda başlat
echo "Web uygulaması başlatılıyor..."
cd "$(dirname "$0")"
python -m uvicorn web_app.main:app --host 0.0.0.0 --port 8000 &
WEB_PID=$!

echo "Web uygulaması başlatıldı (PID: $WEB_PID)"
sleep 3

# Ngrok kontrol
if command -v ngrok &> /dev/null; then
    echo ""
    echo "Ngrok ile tunnel oluşturuluyor..."
    ngrok http 8000
else
    # LocalTunnel alternatifi
    if command -v npx &> /dev/null; then
        echo ""
        echo "LocalTunnel ile tunnel oluşturuluyor..."
        echo "Subdomain girin (boş bırakabilirsiniz):"
        read -p "> " subdomain
        
        if [ -z "$subdomain" ]; then
            npx localtunnel --port 8000
        else
            npx localtunnel --port 8000 --subdomain "$subdomain"
        fi
    else
        echo ""
        echo "[HATA] Ngrok veya Node.js bulunamadı!"
        echo ""
        echo "Kurulum:"
        echo "- Ngrok: https://ngrok.com/download"
        echo "- Node.js: https://nodejs.org/"
        kill $WEB_PID
        exit 1
    fi
fi

# Temizlik
kill $WEB_PID 2>/dev/null
