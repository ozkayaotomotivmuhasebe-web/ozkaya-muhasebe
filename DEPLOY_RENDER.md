# Render.com Deployment - ozkaya.onrender.com

## 🎨 Render ile Deployment (Ücretsiz)

### Adım 1: Hesap Oluştur
https://render.com/ → Sign up (GitHub ile)

### Adım 2: Proje Hazırlığı

#### requirements.txt güncellensin (hepsi bir arada)

### Adım 3: Deploy

1. **New Web Service** tıkla
2. **GitHub repo** bağla
3. Ayarlar:
   - **Name:** ozkaya
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt -r web_app/requirements_web.txt`
   - **Start Command:** `uvicorn web_app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan:** Free

4. **Create Web Service**

### Adım 4: Environment Variables
- `SECRET_KEY`: random-secret-key
- `DATABASE_URL`: (sqlite SQLite için gerek yok, PostgreSQL isterseniz ekleyin)

### Sonuç:
✅ `https://ozkaya.onrender.com`
✅ Otomatik HTTPS
✅ Sleep modu (15 dk aktivitesizlikten sonra uyur, ilk istek 30 sn sürer)
✅ Tamamen ücretsiz

---

## 💰 Maliyet
- **Free Plan:** Ücretsiz, sleep modu var
- **Paid Plan:** $7/ay, her zaman aktif

## ⚠️ Dikkat
- Free plan'da 15 dk aktivitesizlikten sonra uyur
- İlk istek 30 saniye sürebilir
- Ücretli planda bu sorun yok
