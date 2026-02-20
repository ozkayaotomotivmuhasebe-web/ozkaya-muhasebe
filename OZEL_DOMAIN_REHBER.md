# 🌐 Özel Domain/Subdomain Seçenekleri

## "ozkaya" ile başlayan özel linkler:

| Platform | URL | Ücretsiz | Kurulum | Süre |
|----------|-----|----------|---------|------|
| **Railway** | `ozkaya.up.railway.app` | ✅ ($5 credit) | ⭐⭐⭐ | 5 dk |
| **Render** | `ozkaya.onrender.com` | ✅ | ⭐⭐⭐ | 5 dk |
| **Fly.io** | `ozkaya.fly.dev` | ✅ | ⭐⭐ | 10 dk |
| **Vercel** | `ozkaya.vercel.app` | ✅ | ⭐⭐⭐ | 5 dk |
| **Netlify** | `ozkaya.netlify.app` | ❌¹ | ⭐⭐ | - |
| **Heroku** | `ozkaya.herokuapp.com` | ❌² | ⭐⭐ | 10 dk |

¹ Sadece statik siteler için
² Artık ücretli ($5/ay)

---

## 🎯 TAVSİYEM: Railway.app

**Neden Railway?**
- ✅ En kolay deployment
- ✅ Custom subdomain: `ozkaya.up.railway.app`
- ✅ Her zaman aktif (sleep yok)
- ✅ Otomatik HTTPS
- ✅ GitHub ile otomatik deploy
- ✅ İlk $5 ücretsiz

**Hızlı Başlangıç:**
```bash
# 1. GitHub'a push et
git init
git add .
git commit -m "Deploy"
git push origin main

# 2. Railway'e git
https://railway.app/

# 3. New Project → Deploy from GitHub → Repo seç

# 4. Otomatik deploy!
```

**5 dakikada hazır!** 🚀

---

## 💡 Kendi Domain'im Var

Eğer `ozkaya.com` gibi bir domain'iniz varsa:

### Railway/Render/Fly.io'da:
```
Settings → Custom Domain → ozkaya.com ekle
DNS'e CNAME record ekle
```

### Domain almak için:
- Namecheap: ~$10/yıl
- Cloudflare: ~$10/yıl
- GoDaddy: ~$15/yıl

---

## 🚀 Hızlı Karşılaştırma

### Railway (ÖNERİLEN):
```bash
# Deploy dosyaları hazır (Procfile, runtime.txt)
# GitHub'a push et
# Railway'de import et
# ✅ ozkaya.up.railway.app
```

### Render:
```bash
# GitHub'a push et
# Render'da New Web Service
# Repository bağla
# ✅ ozkaya.onrender.com
```

### Fly.io:
```bash
fly launch
fly deploy
# ✅ ozkaya.fly.dev
```

---

## 📦 Hazırlık Dosyaları

Tüm deployment dosyaları hazır:
- ✅ `Procfile` - Railway/Render için
- ✅ `runtime.txt` - Python versiyonu
- ✅ `Dockerfile` - Fly.io/Railway için
- ✅ `DEPLOY_*.md` - Detaylı rehberler

---

## 💰 Maliyet Karşılaştırması

| Platform | Ücretsiz Plan | Ücretli Plan | Sleep | HTTPS |
|----------|---------------|--------------|-------|-------|
| Railway | $5 credit | $5/ay | ❌ | ✅ |
| Render | ✅ | $7/ay | ✅ (15dk) | ✅ |
| Fly.io | 3 app | ~$2/ay | ❌ | ✅ |
| Vercel | ✅ | $20/ay | ❌ | ✅ |

**Not:** "Sleep" = Aktivite yoksa uyur, ilk istek yavaş olur

---

## 🎯 Hangisini Seçmeliyim?

### Test/Demo için:
→ **Render** (Tamamen ücretsiz, sleep var)

### Ciddi kullanım için:
→ **Railway** (İlk $5 ücretsiz, sleep yok)

### Profesyonel için:
→ **Fly.io** (Global CDN, ölçeklenebilir)

### Budget yoksa:
→ **Render Free** ve 15 dakikada bir ping atın 😄

---

## 🚀 Hemen Başla

En hızlı seçenek için:

```bash
# 1. Railway.app'e git: https://railway.app/
# 2. GitHub ile giriş yap
# 3. New Project → Deploy from GitHub
# 4. Bu repo'yu seç
# 5. Otomatik deploy başlar!
# 6. Settings → Domains → Generate Domain
# 7. ✅ ozkaya.up.railway.app hazır!
```

**Toplam süre: 5 dakika** ⏱️

---

## 📞 Yardım

Hangisini seçeceğinize karar veremediyseniz:
- **En kolay:** Railway
- **En ucuz:** Render (free)
- **En profesyonel:** Fly.io

Ben Railway'i öneririm! 🚂
