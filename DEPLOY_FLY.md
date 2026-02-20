# Fly.io Deployment - ozkaya.fly.dev

## 🚁 Fly.io ile Deployment

### Adım 1: Fly CLI Kur
```bash
# Windows (PowerShell):
iwr https://fly.io/install.ps1 -useb | iex

# Veya Scoop:
scoop install flyctl
```

### Adım 2: Login
```bash
fly auth signup
# veya
fly auth login
```

### Adım 3: Dockerfile Oluştur

Fly.io için Dockerfile gerekli (otomatik oluşturabilir).

### Adım 4: Deploy
```bash
# Proje klasöründe
fly launch

# İsimler:
# App name: ozkaya
# Region: Frankfurt (Europe)
# Database: Hayır (SQLite kullanıyoruz)

# Deploy
fly deploy
```

### Sonuç:
✅ `https://ozkaya.fly.dev`
✅ Otomatik HTTPS
✅ Global CDN
✅ Her zaman aktif

---

## 💰 Maliyet
- İlk 3 app ücretsiz
- Sonra kullanım bazlı (genelde $0-5/ay)

## 🎯 Custom Domain
```bash
fly certs add ozkaya.com
```
