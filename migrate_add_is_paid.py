"""
Migration: transactions tablosuna is_paid ve paid_date sütunları ekle
Çalıştırma: python migrate_add_is_paid.py
"""
import sqlite3
import os

# Veritabanı yolu
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "muhasebe.db")

def migrate():
    print(f"Veritabanı: {DB_PATH}")
    if not os.path.exists(DB_PATH):
        print("HATA: Veritabanı dosyası bulunamadı!")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Mevcut sütunları kontrol et
    cursor.execute("PRAGMA table_info(transactions)")
    columns = {row[1] for row in cursor.fetchall()}
    print(f"Mevcut sütunlar: {columns}")

    # is_paid sütunu ekle
    if "is_paid" not in columns:
        cursor.execute("ALTER TABLE transactions ADD COLUMN is_paid INTEGER NOT NULL DEFAULT 0")
        print("✅ is_paid sütunu eklendi.")
    else:
        print("ℹ️  is_paid sütunu zaten mevcut.")

    # paid_date sütunu ekle
    if "paid_date" not in columns:
        cursor.execute("ALTER TABLE transactions ADD COLUMN paid_date DATE")
        print("✅ paid_date sütunu eklendi.")
    else:
        print("ℹ️  paid_date sütunu zaten mevcut.")

    conn.commit()
    conn.close()
    print("\nMigration tamamlandı!")

if __name__ == "__main__":
    migrate()
