# Muhasebe Takip Sistemi - Taşınabilir Kurulum Rehberi

## 📋 İçindekiler
1. [Gereksinimler](#gereksinimler)  
2. [Kurulum Adımları](#kurulum-adımları)
3. [İlk Başlatma](#ilk-başlatma)
4. [Örnek Veri Oluşturma](#örnek-veri-oluşturma)
5. [Başka Bilgisayara Taşıma](#başka-bilgisayara-taşıma)
6. [Sorun Giderme](#sorun-giderme)

---

## ⚙️ Gereksinimler

- **Windows 7 veya daha yeni** (Windows 10/11 önerilir)
- **Python 3.8 veya daha yeni**
- **1 GB boş disk alanı** (veritabanı için)
- **İnternet bağlantısı** (kurulum sırasında)

### Python Kurulumu

1. [python.org](https://www.python.org/downloads/) adresine gidin
2. **Python 3.11 LTS** sürümünü indirin
3. Kurulum sırasında **"Add Python to PATH"** seçeneğini işaretleyin ⚠️
4. Kurulumu tamamlayın

Python'un düzgün kurulduğunu kontrol etmek için:
```cmd
python --version
```

---

## 🚀 Kurulum Adımları

### Yöntem 1: Otomatik Kurulum (Önerilir)

1. Klasörü başka bilgisayara kopyalayın
2. **`setup.bat`** dosyasına çift tıklayın
3. Kurulum otomatik olarak yapılacak

### Yöntem 2: Manuel Kurulum

1. Komut istemini (cmd) açın
2. Proje klasörüne girin:
```cmd
cd C:\Users\[YourUsername]\Desktop\ÖZKAYA
```

3. Bağımlılıkları kurun:
```cmd
pip install -r requirements.txt
```

4. Uygulamayı başlatın:
```cmd
python main.py
```

---

## 🔑 İlk Başlatma

### Varsayılan Admin Hesabı
- **Kullanıcı adı:** `admin`
- **Şifre:** `admin123`

⚠️ **ÖNEMLİ:** İlk giriş sonrasında lütfen şifreyi değiştirin!

---

## 📊 Örnek Veri Oluşturma

### Örnek Excel Dosyaları Oluştur

Uygulamaya örnek veri aktarmak için:

1. Komut istemini açın veya PowerShell başlatın
2. Proje klasörüne girin
3. Şu komutu çalıştırın:
```cmd
python create_sample_data.py
```

4. `sample_data` klasöründe Excel dosyaları oluşturulacak:
   - `01_carileri_aktar.xlsx` - Müşteri/Tedarikçi
   - `02_banka_hesaplari_aktar.xlsx` - Banka Hesapları
   - `03_islemler_aktar.xlsx` - Finansal İşlemler
   - `04_faturalar_aktar.xlsx` - Faturalar
   - `05_kredi_kartlari_aktar.xlsx` - Kredi Kartları

### Excel Dosyalarını Uygulamaya Aktarma

1. Uygulamayı başlatın
2. Admin olarak giriş yapın
3. İlgili bölüme gidin (Cariler, Banka vb.)
4. "İçe Aktar" butonuna tıklayın
5. Excel dosyasını seçin
6. Verileri gözden geçirip onaylayın

---

## 💾 Başka Bilgisayara Taşıma

### Adım 1: Hazırlık
```
ÖZKAYA/
├── main.py
├── config.py
├── requirements.txt
├── setup.bat
├── create_sample_data.py
├── src/
├── data/             ← Veritabanı dosyaları
└── sample_data/      ← Excel dosyaları (opsiyonel)
```

### Adım 2: Dosyaları Kopyala

Tüm klasörü USB bellek veya bulut depolamasına kopyalayın:
- `ÖZKAYA` klasörünün tamamını kopyalayın
- `data` klasöründeki `muhasebe.db` dosyası veritabanını içerir
- `sample_data` klasörü opsiyonel (örnek veriler için)

### Adım 3: Hedef Bilgisayarda Kurulum

1. Klasörü yeni bilgisayara yapıştırın
2. `setup.bat` dosyasına çift tıklayın
3. Kurulum otomatik yapılacak

---

## 🔧 Yapılandırma

### config.py - Temel Ayarlar

Dosyayı bir metin editörü ile açıp düzenleyebilirsiniz:

```python
# Veritabanı konumu
DATABASE_URL = f"sqlite:///{DATABASE_DIR / 'muhasebe.db'}"

# Pencere boyutu
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900

# Oturum zaman aşımı (saniye)
SESSION_TIMEOUT = 1800  # 30 dakika
```

---

## ❓ Sorun Giderme

### Hata: "Python bulunamadı"

**Çözüm:**
1. Python yüklü olup olmadığını kontrol edin
2. Python kurulumu sırasında "Add Python to PATH" seçildi mi?
3. Bilgisayarı yeniden başlatın
4. İşletim sistemi PATH ayarlarını güncelleyin

### Hata: "PyQt5 yüklenemedi"

**Çözüm:**
```cmd
pip install --upgrade pip
pip install PyQt5==5.15.9
```

### Hata: "Veritabanı açılamıyor"

**Çözüm:**
1. `data` klasörünün var olup olmadığını kontrol edin
2. `data` klasörüne yazma izni olup olmadığını kontrol edin
3. İzin sorunları varsa:
   - `data` klasörüne sağ tıklayın
   - Özellikler → Güvenlik → İzinleri düzenleyin

### Hata: "Excel dosyası açılamıyor"

**Çözüm:**
- Excel dosyaları UTF-8 kodlanmış olmalıdır
- Dosya formatı `.xlsx` olmalıdır (`.xls` değil)
- Dosya başka bir programda açık değil mi kontrol edin

---

## 📱 Sık Sorulan Sorular

**S: Veritabanı yedeklemesi nasıl yapılır?**
- Cevap: `data/muhasebe.db` dosyasını kopyalayın. Bu tek bir dosya olarak yedeklenebilir.

**S: Başka bir bilgisayardan aynı veritabanını kullanabilir miyim?**
- Cevap: Evet. `data` klasörünü kopyalayın. SQLite tek bir dosya veritabanıdır.

**S: Veritabanı şifrele nasıl korunur?**
- Cevap: Şu anda SQLite basit bir veritabanı dosyasıdır. İleride şifreleme eklenebilir.

---

## 📞 Destek

Sorun yaşıyorsanız:
1. Bu rehberin "Sorun Giderme" bölümünü okuyun
2. Hata mesajını not alın
3. Gerekirse Python loglarını kontrol edin

---

**Son Güncelleme:** Şubat 2024  
**Versiyon:** 1.0.0
