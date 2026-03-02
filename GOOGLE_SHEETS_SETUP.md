# Google Sheets Entegrasyonu Rehberi

Bu rehber, Muhasebe Takip Sistemi ile Google Sheets arasında otomatik veri senkronizasyonu kurulumunu açıklar.

## 📋 İçindekiler
1. [Gereksinimler](#gereksinimler)
2. [Google Cloud Console Kurulumu](#google-cloud-console-kurulumu)
3. [Credentials Dosyası İndirme](#credentials-dosyası-i̇ndirme)
4. [Uygulama Ayarları](#uygulama-ayarları)
5. [Google Sheets Hazırlama](#google-sheets-hazırlama)
6. [Senkronizasyon Kullanımı](#senkronizasyon-kullanımı)
7. [Sorun Giderme](#sorun-giderme)

---

## ⚙️ Gereksinimler

- Google hesabı
- İnternet bağlantısı
- Google Sheets'te oluşturulmuş bir çalışma sayfası

---

## 🔧 Google Cloud Console Kurulumu

### Adım 1: Google Cloud Console'a Giriş
1. [Google Cloud Console](https://console.cloud.google.com/) adresine gidin
2. Google hesabınızla giriş yapın
3. Üst kısımdan "Yeni Proje Oluştur" seçeneğini tıklayın
4. Proje adı girin (örn: "Muhasebe-Sheets") ve "Oluştur" butonuna tıklayın

### Adım 2: Google Sheets API'yi Etkinleştir
1. Sol menüden **"API'ler ve Servisler"** > **"Kütüphane"** seçeneğine gidin
2. Arama çubuğuna **"Google Sheets API"** yazın
3. Google Sheets API'yi bulup tıklayın
4. **"Etkinleştir"** butonuna tıklayın

### Adım 3: OAuth Onay Ekranı Yapılandır
1. Sol menüden **"OAuth onay ekranı"** seçeneğine gidin
2. **"Harici"** (External) seçeneğini işaretleyin ve **"Oluştur"** butonuna tıklayın
3. Gerekli bilgileri girin:
   - **Uygulama adı**: Muhasebe Takip Sistemi
   - **Kullanıcı destek e-postası**: E-posta adresiniz
   - **Geliştirici iletişim bilgileri**: E-posta adresiniz
4. **"Kaydet ve Devam Et"** butonuna tıklayın
5. Kapsamlar (Scopes) ekranında hiçbir şey eklemeyin, **"Kaydet ve Devam Et"** butonuna tıklayın
6. Test kullanıcıları ekranında e-posta adresinizi ekleyin
7. **"Kaydet ve Devam Et"** butonuna tıklayın

---

## 📥 Credentials Dosyası İndirme

### Adım 1: OAuth 2.0 Client ID Oluştur
1. Sol menüden **"Kimlik Bilgileri"** (Credentials) seçeneğine gidin
2. Üstteki **"+ KİMLİK BİLGİLERİ OLUŞTUR"** butonuna tıklayın
3. **"OAuth client ID"** seçeneğini seçin
4. Uygulama türü olarak **"Masaüstü uygulaması"** (Desktop app) seçin
5. İsim girin (örn: "Muhasebe Desktop Client")
6. **"Oluştur"** butonuna tıklayın

### Adım 2: Credentials Dosyasını İndir
1. Oluşturulan client ID'nin yanındaki **"İNDİR"** (Download) ikonuna tıklayın
2. JSON dosyası indirilecek (örn: `client_secret_xxxxx.json`)
3. Bu dosyayı **`credentials.json`** olarak yeniden adlandırın

### Adım 3: Dosyayı Uygulamaya Ekle
1. İndirdiğiniz `credentials.json` dosyasını şu klasöre kopyalayın:
   ```
   [Uygulama Klasörü]/data/google_credentials/credentials.json
   ```
2. Eğer `google_credentials` klasörü yoksa oluşturun

---

## 🎨 Google Sheets Hazırlama

### Gerekli Sayfa Yapısı

#### 1. **Cariler** Sayfası (İsteğe Bağlı)
Cari hesapları içeren sayfa şu sütunlara sahip olmalı:

| Ad/Ünvan | Tür | Telefon | Adres | Vergi No/TC |
|----------|-----|---------|-------|-------------|
| ABC Ltd. | MÜŞTERİ | 0555... | İstanbul | 123... |
| XYZ A.Ş. | TEDARİKÇİ | 0532... | Ankara | 456... |

**Notlar:**
- İlk satır başlık satırıdır
- **Ad/Ünvan**: Zorunlu
- **Tür**: MÜŞTERİ veya TEDARİKÇİ (opsiyonel)
- Diğer sütunlar opsiyonel

#### 2. **İşlemler** Sayfası
İşlemleri içeren sayfa şu sütunlara sahip olmalı:

| Tarih | Tür | Tutar | Açıklama | Cari | Ödeme |
|-------|-----|-------|----------|------|-------|
| 01.01.2024 | GELİR | 5000 | Ürün satışı | ABC Ltd. | BANKA |
| 02.01.2024 | GİDER | 1200 | Ofis kirası | XYZ A.Ş. | NAKİT |

**Notlar:**
- İlk satır başlık satırıdır
- **Tarih**: dd.mm.yyyy formatında (örn: 24.02.2026)
- **Tür**: GELİR, GİDER, FATURA (opsiyonel)
- **Tutar**: Sayısal değer (virgül veya nokta kullanılabilir)
- **Açıklama**: İşlem açıklaması (opsiyonel)
- **Cari**: Cari hesap adı - Cariler sayfasındakiyle eşleşmeli (opsiyonel)
- **Ödeme**: NAKİT, BANKA, KART, CARİ (opsiyonel)

### Örnek Google Sheets Yapısı
```
📊 Muhasebe Verileri
├─ 📄 Cariler
│  └─ Cari hesap listesi
└─ 📄 İşlemler
   └─ Tüm mali işlemler
```

---

## 🔗 Uygulama Ayarları

### Adım 1: Ayarlar Sekmesine Git
1. Uygulamayı açın
2. **"⚙️ Ayarlar"** sekmesine gidin
3. **"📊 Google Sheets Senkronizasyonu"** bölümünü bulun

### Adım 2: Google Sheets URL'sini Girin
1. Google Sheets dosyanızı açın
2. Tarayıcıdaki URL'yi kopyalayın:
   ```
   https://docs.google.com/spreadsheets/d/1ABC...XYZ/edit#gid=0
   ```
3. Uygulamada **"Sheets URL"** alanına yapıştırın

### Adım 3: Sayfa İsimlerini Ayarlayın
1. **Cari Sayfası**: Google Sheets'teki cari listesi sayfa adını girin (varsayılan: "Cariler")
2. **İşlem Sayfası**: Google Sheets'teki işlemler sayfa adını girin (varsayılan: "İşlemler")

### Adım 4: Otomatik Senkronizasyon (İsteğe Bağlı)
- **"🔄 Otomatik Senkronizasyon"** kutusunu işaretleyin
- Uygulama her 10 dakikada bir otomatik olarak Google Sheets'ten veri çekecek

### Adım 5: Ayarları Kaydet
- **"💾 Google Sheets Ayarlarını Kaydet"** butonuna tıklayın

---

## 🚀 Senkronizasyon Kullanımı

### İlk Bağlantı
1. **"🔗 Bağlantıyı Test Et"** butonuna tıklayın
2. Tarayıcıda Google OAuth ekranı açılacak
3. Google hesabınızla giriş yapın
4. Uygulamaya Google Sheets erişim izni verin
5. **"İzin Ver"** butonuna tıklayın
6. Başarı mesajı görünecek

### Manuel Senkronizasyon
1. **"🔄 Şimdi Senkronize Et"** butonuna tıklayın
2. Senkronizasyon başlayacak (birkaç saniye sürebilir)
3. Başarı mesajında kaç cari ve işlem eklendiği gösterilecek
4. Dashboard otomatik olarak güncellenecek

### Otomatik Senkronizasyon
- Otomatik senkronizasyon etkinse, uygulama her 10 dakikada bir sessizce senkronize olacak
- Dashboard'da **"🔄 Google Sheets Senkronize"** butonu görünecek
- Bu butona tıklayarak manuel senkronizasyon da yapabilirsiniz

---

## 🔍 Nasıl Çalışır?

### Senkronizasyon Mantığı
1. **Cari Hesaplar**: 
   - Google Sheets'teki her cari kontrol edilir
   - Sistemde yoksa yeni cari oluşturulur
   - Varsa atlanır (güncelleme yapılmaz)

2. **İşlemler**:
   - Her işlem kontrol edilir (tarih + tutar + açıklama eşleşmesi)
   - Sistemde yoksa yeni işlem oluşturulur
   - Varsa atlanır (çift ekleme önlenir)

3. **Veri Güvenliği**:
   - Sadece **yeni** veriler eklenir
   - Mevcut veriler **silinmez** veya **değiştirilmez**
   - Google Sheets sadece **okunur** (yazma yapılmaz)

---

## ❗ Sorun Giderme

### "credentials.json dosyası bulunamadı" Hatası
**Çözüm:**
1. `credentials.json` dosyasını indirdiğinizden emin olun
2. Dosyayı şu konuma koyun:
   ```
   [Uygulama Klasörü]/data/google_credentials/credentials.json
   ```
3. Dosya adının tam olarak `credentials.json` olduğundan emin olun

### "Spreadsheet bulunamadı" Hatası
**Çözüm:**
1. Google Sheets URL'sini doğru kopyaladığınızdan emin olun
2. Google Sheets dosyasının paylaşım izinlerini kontrol edin
3. OAuth ile giriş yaptığınız Google hesabının sayfaya erişimi olmalı

### "Sayfa bulunamadı" Hatası
**Çözüm:**
1. Google Sheets'te sayfa isimlerini kontrol edin
2. Uygulama ayarlarında doğru sayfa isimlerini girdiğinizden emin olun
3. Sayfa isimlerinde büyük/küçük harf duyarlılığına dikkat edin

### "Tarih formatı tanınmıyor" Hatası
**Çözüm:**
1. Google Sheets'te tarih formatını `dd.mm.yyyy` olarak ayarlayın
2. Örnek: `24.02.2026`
3. Virgül yerine nokta kullanın

### OAuth Token Süresi Doldu
**Çözüm:**
1. `data/google_credentials/token.json` dosyasını silin
2. **"🔗 Bağlantıyı Test Et"** butonuna tekrar tıklayın
3. Yeniden giriş yapın

---

## 💡 İpuçları

1. **İlk Senkronizasyon**: 
   - Büyük veri setlerinde ilk senkronizasyon uzun sürebilir
   - Sabırla bekleyin, işlem tamamlanınca bildirim gelecek

2. **Veri Temizliği**:
   - Google Sheets'te boş satırları temizleyin
   - Tutarsız veri formatlarını düzeltin

3. **Yedekleme**:
   - Senkronizasyon öncesi veritabanı yedeği alın
   - Ayarlar > Veritabanı Yedekle

4. **Test Modu**:
   - İlk denemelerinizde az veriyle test edin
   - Başarılı olduktan sonra tüm veriyi senkronize edin

---

## 📞 Destek

Sorun yaşarsanız:
1. Uygulama loglarını kontrol edin
2. Hata mesajlarını kaydedin
3. Geliştirici ile iletişime geçin

**Not**: Google API kotaları nedeniyle çok sık senkronizasyon yapmaktan kaçının. Otomatik senkronizasyon 10 dakikada bir optimal bir seçenektir.

---

## ✅ Kurulum Kontrol Listesi

- [ ] Google Cloud Console'da proje oluşturuldu
- [ ] Google Sheets API etkinleştirildi
- [ ] OAuth onay ekranı yapılandırıldı
- [ ] OAuth Client ID oluşturuldu
- [ ] credentials.json dosyası indirildi
- [ ] credentials.json doğru konuma kopyalandı
- [ ] Google Sheets dosyası hazırlandı (Cariler ve İşlemler sayfaları)
- [ ] Uygulama ayarlarında URL girildi
- [ ] Sayfa isimleri doğru ayarlandı
- [ ] Bağlantı testi başarılı
- [ ] İlk senkronizasyon yapıldı
- [ ] Veriler doğru şekilde aktarıldı

---

**Başarılı entegrasyon dileriz! 🎉**
