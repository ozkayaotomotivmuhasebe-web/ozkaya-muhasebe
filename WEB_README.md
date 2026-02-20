# Muhasebe Sistemi - Web Versiyonu

## 🌐 Web Uygulaması Kurulumu

### Gereksinimler
- Python 3.8+
- FastAPI
- Uvicorn
- Mevcut veritabanı (SQLite)

### Kurulum Adımları

#### 1. Web Gereksinimlerini Yükleyin
```bash
pip install -r web_app/requirements_web.txt
```

#### 2. Uygulamayı Başlatın

**Windows için:**
```bash
start_web.bat
```

**Manuel başlatma:**
```bash
cd web_app
python main.py
```

Veya Uvicorn ile:
```bash
uvicorn web_app.main:app --reload --host 0.0.0.0 --port 8000
```

### 📱 Kullanım

1. Tarayıcınızda açın: `http://localhost:8000`
2. Giriş yapın:
   - **Kullanıcı Adı:** admin
   - **Şifre:** admin123

### 🔐 Özellikler

✅ **Kullanıcı Yönetimi**
- Admin paneli ile kullanıcı ekleme/düzenleme/silme
- Rol bazlı yetkilendirme (Admin / Kullanıcı)
- Sayfa bazlı yetki kontrolü

✅ **Yetki Sistemi**
Her kullanıcı için ayrı ayrı belirlenen yetkiler:
- 📊 Dashboard
- 📄 Faturalar
- 📋 Cari Hesaplar
- 🏦 Banka Hesapları
- 💳 Kredi Kartları
- 📊 Raporlar

✅ **Responsive Tasarım**
- Bootstrap 5 ile modern arayüz
- Mobil uyumlu
- Kolay kullanım

### 🏗️ Mimari

```
web_app/
├── main.py                 # FastAPI uygulaması
├── requirements_web.txt   # Web gereksinimleri
├── templates/             # HTML şablonları
│   ├── base.html         # Ana şablon
│   ├── login.html        # Giriş sayfası
│   ├── dashboard.html    # Kontrol paneli
│   ├── invoices.html     # Faturalar
│   ├── caris.html        # Cari hesaplar
│   ├── banks.html        # Banka hesapları
│   ├── reports.html      # Raporlar
│   ├── admin_users.html  # Kullanıcı yönetimi
│   └── error.html        # Hata sayfası
└── static/               # Statik dosyalar
    ├── css/
    └── js/
```

### 🔄 Desktop'tan Web'e Geçiş

**Avantajlar:**
- ✅ Mevcut servis katmanı aynen kullanılıyor
- ✅ SQLAlchemy veritabanı aynı
- ✅ İş mantığı değişmedi
- ✅ Her yerden erişim
- ✅ Çoklu kullanıcı desteği

**Yeni Özellikler:**
- 🌐 Web üzerinden erişim
- 📱 Mobil uyumlu
- 🔄 Otomatik API dokümantasyonu (http://localhost:8000/docs)
- ⚡ Daha hızlı performans

### 📊 API Endpoints

FastAPI otomatik dokümantasyon:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### 🚀 Production Deployment

#### Gunicorn ile (Linux):
```bash
pip install gunicorn
gunicorn web_app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

#### Docker ile:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt -r web_app/requirements_web.txt
CMD ["uvicorn", "web_app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Nginx Reverse Proxy (Önerilen):
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 🔒 Güvenlik

**Production için önemli:**
1. `SessionMiddleware` secret key'i değiştirin
2. HTTPS kullanın
3. Environment variables kullanın
4. CORS ayarlarını yapılandırın
5. Rate limiting ekleyin

### 💡 İleri Seviye Özellikler (Opsiyonel)

**REST API Eklemek için:**
```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/api/invoices")
async def get_invoices_api(user=Depends(require_auth)):
    return InvoiceService.get_user_invoices(user.id)
```

**WebSocket (Gerçek zamanlı bildirimler):**
```python
from fastapi import WebSocket

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    # Gerçek zamanlı bildirimler
```

### 📝 Notlar

- Mevcut desktop uygulaması çalışmaya devam edebilir
- Aynı veritabanını kullanırlar
- Web ve desktop paralel kullanılabilir

### 🆘 Sorun Giderme

**Port zaten kullanımda:**
```bash
uvicorn web_app.main:app --reload --port 8001
```

**Session hatası:**
- Browser cookie'leri temizleyin
- Secret key'i kontrol edin

**Import hatası:**
- Ana dizinde olduğunuzdan emin olun
- `sys.path` ayarlarını kontrol edin

### 📞 Destek

Sorularınız için: admin@ozkaya.com
