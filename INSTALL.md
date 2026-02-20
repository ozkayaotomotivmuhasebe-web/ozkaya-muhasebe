# Kurulum ve Test Rehberi

## 🚀 Hızlı Başlangıç

### 1. Adım: Paketleri Yükle
```powershell
cd C:\Users\MONSTER\Desktop\ÖZKAYA
pip install -r requirements.txt
```

### 2. Adım: Uygulamayı Çalıştır
```powershell
python main.py
```

### 3. Adım: Test Et
1. "Yeni Kayıt" tuşuna tıkla
2. Test hesabı bilgilerini gir:
   - Ad: Test Kullanıcı
   - Email: test@example.com
   - Username: testuser
   - Şifre: Test123
3. Kayıt ol ve giriş yap

## 📊 Uygulamanın Özellikleri

### Dashboard (📊)
- Toplam fatura istatistikleri
- Ödenen/Beklemede durumları
- Son fatura listesi

### Faturalar (📄)
- Yeni fatura oluşturma
- Fatura listesi görüntüleme
- Fatura durumunu güncelleme

### Cari Hesaplar (📋)
- Müşteri/Tedarikçi yönetimi
- Bakiye takibi
- İletişim bilgileri

### Banka Hesapları (🏦)
- Çoklu hesap desteği
- Bakiye görüntüleme
- İşlem geçmişi

### Ayarlar (⚙️)
- Profil bilgilerini görüntüleme
- Şifre değiştirme
- Çıkış

## 💡 Temel Fonksiyonaliteler

✅ Kullanıcı registrasyonu ve authentication
✅ Veritabanı connection pooling
✅ Modern PyQt5 UI
✅ SQLAlchemy ORM
✅ Optimize edilmiş SQL sorguları
✅ Transaction yönetimi
✅ Hızlı performans

## 🐛 Sorun Giderme

### "Package not found" Hatası
```powershell
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Veritabanı Hatası
Veritabanı dosyası silinerek yeniden oluşturulabilir:
```powershell
del data/muhasebe.db  # Windows
rm data/muhasebe.db   # Linux/Mac
```

## 📈 İleri Özellikleri (Coming Soon)

- 📊 Raporlar ve grafikler
- 📤 PDF/Excel export
- 📧 Email gönderme
- 🔔 Bildirimler
- 📱 Mobil uyumluluğu
- ☁️ Cloud backup

## 🔗 İlgili Dosyalar

- `config.py` - Uygulama konfigürasyonu
- `requirements.txt` - Python bağımlılıkları
- `src/database/models.py` - Veri modelleri
- `src/services/*.py` - İş mantığı
- `src/ui/*.py` - Arayüz bileşenleri

---

**Hazırlandı**: 2026-02-17
**Python Sürümü**: 3.8+
