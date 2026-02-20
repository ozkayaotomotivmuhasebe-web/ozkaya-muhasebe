# Railway Deployment için önemli notlar

## Veritabanı Notu

Railway deployment'ta **SQLite** kullanıyorsunuz. Bu development için uygundur ancak production için bazı sınırlamaları vardır:

### ⚠️ SQLite Sınırlamaları (Railway'de):
- Her deploy'da sıfırlanır (ephemeral filesystem)
- Çoklu instance'da sorun olabilir
- Yedekleme zor

### ✅ Önerilen: PostgreSQL

Railway ücretsiz PostgreSQL verir:

1. Railway Dashboard → **New** → **Database** → **Add PostgreSQL**
2. Otomatik bağlanır (`DATABASE_URL` env variable)
3. Kalıcı storage
4. Backup otomatik

### 🔄 PostgreSQL'e Geçmek İçin:

**1. requirements.txt'e ekle:**
```txt
psycopg2-binary==2.9.9
```

**2. config.py'yi güncelle:**
```python
import os

# Railway'de DATABASE_URL varsa kullan, yoksa SQLite
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./muhasebe.db')

# Postgres URL'i düzelt (Railway postgres:// kullanır, SQLAlchemy postgresql:// ister)
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
```

**3. src/database/db.py'yi güncelle:**
```python
from sqlalchemy import create_engine
import config

engine = create_engine(
    config.DATABASE_URL,
    connect_args={"check_same_thread": False} if config.DATABASE_URL.startswith('sqlite') else {}
)
```

### 📝 Şimdilik SQLite İle Devam

İlk deployment için SQLite yeterli. Sonra PostgreSQL'e geçebilirsiniz.

**Not:** Her deploy'da veritabanı sıfırlanır, admin/admin123 ile yeniden giriş yapın.
