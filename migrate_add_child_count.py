"""
Mevcut employees tablosuna child_count sütunu ekle
"""
import sqlite3
import os

db_path = "data/muhasebe.db"

if not os.path.exists(db_path):
    print(f"❌ Veritabanı bulunamadı: {db_path}")
    exit(1)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Sütunun var olup olmadığını kontrol et
    cursor.execute("PRAGMA table_info(employees)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if "child_count" in columns:
        print("✅ child_count sütunu zaten var")
    else:
        print("➕ child_count sütunu ekleniyor...")
        cursor.execute("ALTER TABLE employees ADD COLUMN child_count INTEGER DEFAULT 0")
        conn.commit()
        print("✅ child_count sütunu eklendi")
    
    # Kontrol et
    cursor.execute("SELECT COUNT(*) FROM employees")
    count = cursor.fetchone()[0]
    print(f"📊 Toplam {count} çalışan var")
    
    conn.close()
    print("✅ Migration tamamlandı!")
    
except Exception as e:
    print(f"❌ Hata: {str(e)}")
    exit(1)
