"""
Migrasyon: users tablosuna can_view_kira_takip sütunu ekle.
Çalıştırmak için: python migrate_add_kira_takip_permission.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.database.db import SessionLocal, engine
from sqlalchemy import text

def migrate():
    # Sütun zaten var mı kontrol et (ayrı bağlantı)
    col_exists = False
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT can_view_kira_takip FROM users LIMIT 1"))
            col_exists = True
    except Exception:
        col_exists = False

    if col_exists:
        print("✅ can_view_kira_takip sütunu zaten mevcut, migrasyon gerekmiyor.")
        return

    print("➕ can_view_kira_takip sütunu ekleniyor...")
    with engine.begin() as conn:
        conn.execute(text(
            "ALTER TABLE users ADD COLUMN can_view_kira_takip BOOLEAN NOT NULL DEFAULT 1"
        ))
    print("✅ Migrasyon tamamlandı: can_view_kira_takip sütunu eklendi (varsayılan: True)")

if __name__ == "__main__":
    migrate()
