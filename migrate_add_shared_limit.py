"""
Migrasyon: credit_cards tablosuna parent_card_id sütunu ekleme
Ortak limit özelliği için - iki kart aynı limiti paylaşabilir.
"""
import sqlite3
import os
import sys
from pathlib import Path

# Proje kökünü sys.path'e ekle
sys.path.insert(0, str(Path(__file__).parent))

import config

def migrate():
    db_path = str(config.DATABASE_DIR / 'muhasebe.db')
    
    if not os.path.exists(db_path):
        print(f"Veritabanı bulunamadı: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Mevcut sütunları kontrol et
        cursor.execute("PRAGMA table_info(credit_cards)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'parent_card_id' not in columns:
            print("parent_card_id sütunu ekleniyor...")
            cursor.execute("""
                ALTER TABLE credit_cards 
                ADD COLUMN parent_card_id INTEGER REFERENCES credit_cards(id)
            """)
            conn.commit()
            print("✅ parent_card_id sütunu başarıyla eklendi!")
        else:
            print("ℹ️ parent_card_id sütunu zaten mevcut, atlanıyor.")
        
        return True
    except Exception as e:
        conn.rollback()
        print(f"❌ Migrasyon hatası: {e}")
        return False
    finally:
        conn.close()

if __name__ == '__main__':
    print("Ortak limit migrasyonu başlatılıyor...")
    success = migrate()
    if success:
        print("Migrasyon tamamlandı.")
    else:
        print("Migrasyon başarısız!")
        sys.exit(1)
