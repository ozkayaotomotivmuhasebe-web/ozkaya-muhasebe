# 🚂 Railway Deployment Hızlı Başlangıç

## 📋 ÖN GEREKSİNİMLER

- ✅ Git yüklü
- ✅ GitHub hesabı
- ✅ Railway hesabı (GitHub ile giriş yapacağız)

---

## 🚀 ADIM 1: GitHub'a Push (2 dakika)

### Otomatik (Batch):
```bash
deploy_railway.bat
```

### Manuel:
```bash
# Git başlat
git init

# Dosyaları ekle
git add .

# Commit
git commit -m "Initial commit - Railway deployment"

# GitHub'da repository oluştur: https://github.com/new
# Sonra:
git remote add origin https://github.com/KULLANICI_ADINIZ/muhasebe-ozkaya.git
git branch -M main
git push -u origin main
```

---

## 🚂 ADIM 2: Railway'de Deploy (3 dakika)

### 1. Railway'e Git
https://railway.app/

### 2. GitHub ile Giriş Yap
"Login with GitHub" → İzin ver

### 3. Yeni Proje Oluştur
- **"New Project"** tıkla
- **"Deploy from GitHub repo"** seç
- Repository'nizi seçin: **muhasebe-ozkaya**
- **"Deploy Now"** tıkla

### 4. Otomatik Deployment Başlar
Railway otomatik olarak:
- ✅ `requirements.txt` tespit eder
- ✅ Python kurulumunu yapar
- ✅ Procfile'ı okur
- ✅ Uygulamayı başlatır

⏱️ **İlk deployment 2-3 dakika sürer**

---

## 🌐 ADIM 3: Domain Ayarla (30 saniye)

Deployment bittikten sonra:

1. **Settings** sekmesine git
2. **Networking** bölümünü bul
3. **Generate Domain** tıkla
4. **Custom subdomain** gir: `ozkaya`
5. **Save**

### ✨ Sonuç:
```
https://ozkaya.up.railway.app
```

---

## 🔧 ADIM 4: Environment Variables (Opsiyonel)

Daha güvenli için:

1. **Variables** sekmesine git
2. Ekle:
   ```
   SECRET_KEY = your-super-secret-key-123456
   DATABASE_URL = (SQLite için gerek yok)
   ```
3. **Deploy** tıkla (yeniden deploy eder)

---

## ✅ TAMAMLANDI!

Siteniz hazır: **https://ozkaya.up.railway.app**

### Giriş:
- **Kullanıcı:** admin
- **Şifre:** admin123

---

## 🔄 Sonraki Güncellemeler

Kod değişikliklerini otomatik deploy için:

```bash
git add .
git commit -m "Güncelleme mesajı"
git push
```

Railway **otomatik** olarak yeniden deploy eder! 🎉

---

## 📊 Railway Dashboard

https://railway.app/dashboard

Burada görebilirsiniz:
- 📈 Deployment logları
- 💰 Kullanım ($5 credit)
- 🔧 Settings
- 📊 Metrics

---

## 💰 Maliyet

- **İlk:** $5 ücretsiz credit
- **Sonra:** ~$5/ay (küçük projeler için)
- **Sleep modu:** YOK (her zaman aktif)

---

## 🆘 Sorun Giderme

### "Build failed" hatası:
- Deploy loglarını kontrol edin
- `requirements.txt` doğru mu?
- `Procfile` doğru mu?

### "Application failed to respond":
- Port `$PORT` kullanılıyor mu?
- Procfile'da `--port $PORT` var mı?

### Database hatası:
- SQLite lokal development için
- Production'da PostgreSQL önerilir (Railway ücretsiz verir)

---

## 🎯 PostgreSQL Eklemek İsterseniz (Önerilen)

1. Railway Dashboard → **Add Service** → **PostgreSQL**
2. Otomatik bağlanır
3. Environment variables'a `DATABASE_URL` eklenir
4. Code'unuzda:

```python
# config.py
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./muhasebe.db')

# SQLite yerine PostgreSQL kullan
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
```

5. requirements.txt'e ekle:
```
psycopg2-binary
```

---

## 📞 Yardım

Railway Discord: https://discord.gg/railway
Docs: https://docs.railway.app/

Başarılar! 🚀
