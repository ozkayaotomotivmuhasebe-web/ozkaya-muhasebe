# 📊 Muhasebe Takip Sistemi

Kapsamlı, hızlı ve kullanıcı dostu masaüstü muhasebe yönetim uygulaması.

## 🎯 Özellikler

### ✅ Temel Modüller
- **👤 Kullanıcı Yönetimi**
  - Kayıt ve giriş sistemi
  - Şifre yönetimi
  - Profil bilgileri

- **📄 Fatura Takibi**
  - Gelen/Giden faturalar
  - Fatura durum takibi (DRAFT, SENT, PAID, CANCELLED)
  - Vergi hesaplamaları
  - Kalemlere ayrırılı faturalar

- **📋 Cari Hesap Yönetimi**
  - Müşteri/Tedarikçi yönetimi
  - Bakiye takibi
  - İletişim bilgileri kaydı

- **🏦 Banka Hesapları**
  - Çoklu banka hesabı desteği
  - Bakiye takibi
  - İşlem geçmişi
  - Gelir/Gider analizi

- **📊 Dashboard**
  - Özet istatistikler
  - Son işlemler
  - Hızlı erişim

## 🚀 Kurulum & Çalıştırma

### 1. Gereksinimler
- Python 3.8+
- pip (Python paket yöneticisi)

### 2. Adım Adım Kurulum

```bash
# 1. Projeyi klonla (varsa)
cd ÖZKAYA

# 2. Sanal ortam oluştur (opsiyonel ama önerilen)
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Gerekli paketleri yükle
pip install -r requirements.txt

# 4. Veritabanını hazırla (ilk çalıştırmada otomatik)
python main.py

# 5. Yeni hesap oluştur veya test hesabıyla giriş yap
```

## 📁 Proje Yapısı

```
ÖZKAYA/
├── main.py                 # Ana giriş noktası
├── config.py              # Konfigürasyon ayarları
├── requirements.txt       # Paket bağımlılıkları
└── src/
    ├── database/
    │   ├── db.py         # Veritabanı bağlantısı & session yönetimi
    │   ├── models.py     # SQLAlchemy ORM modelleri
    │   └── __init__.py
    ├── services/
    │   ├── auth_service.py       # Kimlik doğrulama
    │   ├── invoice_service.py    # Fatura yönetimi
    │   ├── cari_service.py       # Cari hesap yönetimi
    │   ├── bank_service.py       # Banka işlemleri
    │   └── __init__.py
    ├── ui/
    │   ├── main_window.py        # Ana pencere
    │   ├── dialogs/
    │   │   ├── login_dialog.py       # Giriş ekranı
    │   │   └── register_dialog.py    # Kayıt ekranı
    │   ├── widgets/
    │   │   └── dashboard_widgets.py
    │   └── __init__.py
    ├── utils/
    │   ├── constants.py   # Sabitler
    │   ├── helpers.py     # Yardımcı fonksiyonlar
    │   └── __init__.py
    └── __init__.py
└── data/
    └── muhasebe.db       # SQLite veritabanı (otomatik oluşur)
```

## 🎮 Kullanım

### İlk Başlangıç

1. **Yeni Hesap Oluştur**
   - "Yeni Kayıt" butonuna tıkla
   - Ad, email, kullanıcı adı ve şifreyi gir
   - "Kayıt Ol" butonuna tıkla

2. **Giriş Yap**
   - Kullanıcı adı ve şifreyi gir
   - "Giriş Yap" butonuna tıkla

3. **Ana Dashboard**
   - Toplam faturalar, ödenen ve beklemede olanları gör
   - Son işlemleri takip et

### Fatura Oluşturma

1. "📄 Faturalar" sekmesine git
2. "➕ Yeni Fatura" butonuna tıkla
3. İşletme ve fatura bilgilerini gir
4. Fatura kalemlerini ekle
5. Kaydet

### Cari Yönetimi

1. "📋 Cari Hesaplar" sekmesine git
2. "➕ Yeni Cari" butonuna tıkla
3. Müşteri/Tedarikçi bilgilerini gir
4. Kaydet ve takip et

## 🔧 Teknik Detaylar

### Teknoloji Stack
- **GUI**: PyQt5 (Modern, responsive interface)
- **Database**: SQLite (Dosya tabanlı, kolay distribution)
- **ORM**: SQLAlchemy 2.0 (Tip güvenli, performanslı)
- **Security**: werkzeug (Şifre hashing)

### Veritabanı Optimizasyonları
- **Connection Pooling**: Bağlantı havuzu
- **WAL Mode**: SQLite Write-Ahead Logging
- **Query Caching**: Session-level caching
- **Index Management**: Otomatik indexing

### Performans Özellikleri
- Lazy loading prevention
- Scope-based session management
- Indexed queries
- Batch operations

## 📊 Veri Modeli

### Users (Kullanıcılar)
- id, username, email, password_hash
- full_name, is_active
- created_at, last_login

### Invoices (Faturalar)
- invoice_number, invoice_date, due_date
- amount, tax_rate, tax_amount, total_amount
- status (DRAFT, SENT, PARTIALLY_PAID, PAID, CANCELLED)
- Relation: User, Cari, BankAccount

### Caris (Cari Hesaplar)
- name, cari_type (CUSTOMER, SUPPLIER, OTHER)
- tax_number, email, phone, address, city
- balance (otomatik hesaplanan)

### BankAccounts (Banka Hesapları)
- bank_name, account_number, iban
- balance, currency
- is_active

### BankTransactions (Banka İşlemleri)
- transaction_date, amount
- transaction_type (INCOME, EXPENSE)
- category, description, reference

## 🛡️ Güvenlik

- Tüm şifreler pbkdf2:sha256 ile hash'lenmiş
- Session-based kullanıcı yönetimi
- SQL injection koruması (SQLAlchemy ORM)
- Veritabanı transaction yönetimi

## 📝 Notlar

- Tüm finansal işlemler desimal hassasiyettle yapılır
- Tarih/saat bilgileri UTC formatında saklanır
- Gelecekte multi-user desteği planlı

## 🤝 Katkı

Sorunlar ve öneriler için lütfen bir issue açınız.

## 📄 Lisans

Bu proje açık kaynaklı ve akademik amaçlar için kullanılabilir.

---

**Sürüm**: 1.0.0  
**Son Güncelleme**: 2026-02-17#### 🏦 **Banka Hesap Yönetimi**
- Depoyu birden fazla banka hesabı ekle
- Hesap bakiyesi takibi
- Para birimi desteği (TRY, USD, EUR, GBP)

#### 📄 **Fatura Yönetimi**
- Gelen ve giden fatura oluştur
- Vergi hesaplaması
- Ödeme takibi
- Durum kontrolü (Taslak, Gönderilen, Ödemesi Yapılmış, vb.)

#### 📋 **Cari Hesaplar**
- Müşteri/Tedarikçi kayıtları
- Vergi numarası desteği
- Bakiye takiği
- İrtibat bilgileri

#### 📊 **Raporlar**
- Gelir/Gider özetleri
- Dönemsel raporlar
- PDF dışa aktarma
- İstatistiksel analizler

#### 👤 **Kullanıcı Sistemi**
- Kşifreli giriş
- Kişisel profil ayarları
- Şifre değiştirme

## 📁 Proje Yapısı

```
ÖZKAYA/
├── main.py                 # Uygulamanın giriş noktası
├── config.py               # Yapılandırma ayarları
├── requirements.txt        # Gerekli paketler
│
├── src/
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py       # SQLAlchemy ORM modelleri
│   │   └── db.py           # Veritabanı bağlantısı
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py      # Kullanıcı yönetimi
│   │   ├── invoice_service.py   # Fatura yönetimi
│   │   ├── bank_service.py      # Banka yönetimi
│   │   └── cari_service.py      # Cari yönetimi
│   │
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── main_window.py        # Ana pencere
│   │   ├── dialogs/
│   │   │   ├── __init__.py
│   │   │   └── login_dialog.py   # Giriş ve kayıt pencereleri
│   │   └── widgets/
│   │       ├── __init__.py
│   │       └── dashboard_widgets.py  # Dashboard widget'ları
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── constants.py  # Sabitler
│   │   └── helpers.py    # Yardımcı fonksiyonlar
│   └── __init__.py
│
└── data/
    └── muhasebe.db       # SQLite veritabanı dosyası
```

## 🚀 Teknolojiler

- **GUI**: PyQt5
- **Veritabanı**: SQLite + SQLAlchemy ORM
- **Raporlama**: Pandas, Matplotlib, ReportLab
- **Şifreleme**: Werkzeug

## 📝 Lisans

Bu proje açık kaynak olarak dağıtılmaktadır.

## 💡 Gelecek Özellikler

- [ ] PDF Fatura oluşturma
- [ ] Excel raporlama
- [ ] Hızlı Muhasebe Sistemi (QR) entegrasyonu
- [ ] Çok dilde dil desteği
- [ ] Tema seçenekleri
- [ ] Veri yedeği
- [ ] İstatistiksel tahminler

## 🔧 Sorun Giderme

### "Module not found" hatası
```bash
pip install -r requirements.txt
```

### Veritabanı hatası
Veritabanı dosyası otomatik oluşturulur. `data/muhasebe.db` dosyasını silip tekrar çalıştırmayı deneyin.

### Giriş problemi
Yeni hesap oluştur seçeneğini kullanarak kayıt olun.

## 📧 İletişim

Sorularınız için: özkaya@email.com
