# 🌐 Public URL Hızlı Başlangıç

## En Hızlı Yöntem (3 Adım):

### 1️⃣ Ngrok ile (ÖNERİLEN)

```bash
# 1. Ngrok indir: https://ngrok.com/download
# 2. Token al ve kur:
ngrok config add-authtoken YOUR_TOKEN

# 3. Çalıştır:
setup_public_url.bat
```

**✅ Sonuç:** `https://abc123.ngrok-free.app` 

---

### 2️⃣ LocalTunnel ile (İNDİRME YOK)

Node.js varsa direkt:

```bash
start_public_quick.bat
```

**✅ Sonuç:** `https://muhasebe-ozkaya.loca.lt`

---

## 📦 Gereksinimler

| Yöntem | Gerekli | İndirme |
|--------|---------|---------|
| **Ngrok** | Ngrok.exe + Token | https://ngrok.com/download |
| **LocalTunnel** | Node.js | https://nodejs.org/ |

---

## 🎯 Hangi Dosyayı Çalıştırayım?

### Windows:
- **Ngrok:** `setup_public_url.bat`
- **LocalTunnel:** `start_public_quick.bat`
- **Normal (local):** `start_web.bat`

### Linux/Mac:
- **Ngrok/LocalTunnel:** `bash start_public.sh`

---

## 🔗 Link Aldıktan Sonra:

1. Linki kopyala: `https://abc123.ngrok-free.app`
2. Tarayıcıda aç
3. Giriş yap: `admin` / `admin123`
4. Linki paylaş! ✨

**Not:** Link herkese açık olur, dikkatli paylaşın!

---

## 🔒 Güvenlik İpuçları

- ⚠️ Demo/test için kullanın
- ⚠️ Hassas verileri paylaşmayın
- ⚠️ Kullanıcı şifrelerini değiştirin
- ⚠️ Production için VPS/Cloud kullanın

---

## 🆘 Sorun mu var?

1. **Port 8000 kullanımda:** Başka port deneyin (8001, 8080)
2. **Ngrok bağlanmıyor:** Token'i kontrol edin
3. **Session hatası:** Browser'ı değiştirin / Cookies temizleyin

Detaylı dokümantasyon: `PUBLIC_URL_GUIDE.md`
