# Railway.app Deployment - ozkaya.up.railway.app

## 🚂 Railway ile Deployment (5 Dakika)

### Adım 1: Railway Hesabı
1. https://railway.app/ → Sign up (GitHub ile)
2. Ücretsiz $5 credit alırsınız

### Adım 2: Proje Hazırlığı

#### a) Procfile oluştur:
```
web: uvicorn web_app.main:app --host 0.0.0.0 --port $PORT
```

#### b) runtime.txt oluştur:
```
python-3.11
```

#### c) requirements.txt'i güncelle:
(Mevcut + web requirements)

### Adım 3: Deploy

**Yöntem 1: GitHub'dan (Önerilen)**
```bash
# GitHub'a push
git init
git add .
git commit -m "Initial commit"
git remote add origin YOUR_GITHUB_REPO
git push -u origin main

# Railway'de:
# New Project → Deploy from GitHub → Repo seç
```

**Yöntem 2: Railway CLI**
```bash
# Railway CLI kur
npm i -g @railway/cli

# Login
railway login

# Deploy
railway init
railway up
```

### Adım 4: Custom Domain
- Railway Dashboard → Settings → Domains
- Generate Domain: `ozkaya.up.railway.app`
- Veya kendi domain'inizi bağlayın

### Sonuç:
✅ `https://ozkaya.up.railway.app`
✅ Otomatik HTTPS
✅ Her commit'te otomatik deploy
✅ Ücretsiz başlangıç ($5 credit)

---

## 💰 Maliyet
- İlk $5 ücretsiz
- Sonra ~$5/ay
- Sleep modu yok (her zaman aktif)
