"""Migration: transactions tablosuna paid_amount sütunu ekle"""
import sqlite3, os

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "muhasebe.db")

def migrate():
    print(f"Veritabanı: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(transactions)")
    columns = {row[1] for row in cursor.fetchall()}
    if "paid_amount" not in columns:
        cursor.execute("ALTER TABLE transactions ADD COLUMN paid_amount REAL NOT NULL DEFAULT 0.0")
        print("✅ paid_amount sütunu eklendi.")
    else:
        print("ℹ️  paid_amount sütunu zaten mevcut.")
    conn.commit()
    conn.close()
    print("Migration tamamlandı!")

if __name__ == "__main__":
    migrate()
