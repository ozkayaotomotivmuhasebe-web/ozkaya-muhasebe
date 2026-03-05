"""
transactions tablosuna due_date (vade tarihi) sütunu ekle.
Kesilen faturalarda otomatik 30 günlük vade takibi için kullanılır.
"""
import sqlite3
import os
from datetime import date, timedelta

db_path = "data/muhasebe.db"

if not os.path.exists(db_path):
    print(f"❌ Veritabanı bulunamadı: {db_path}")
    exit(1)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Sütunun var olup olmadığını kontrol et
    cursor.execute("PRAGMA table_info(transactions)")
    columns = [col[1] for col in cursor.fetchall()]

    if "due_date" in columns:
        print("✅ due_date sütunu zaten var")
    else:
        print("➕ due_date sütunu ekleniyor...")
        cursor.execute("ALTER TABLE transactions ADD COLUMN due_date DATE")
        conn.commit()
        print("✅ due_date sütunu eklendi")

        # Mevcut KESILEN_FATURA işlemlerine varsayılan 30 gün ekle
        print("📅 Mevcut kesilen faturalara 30 günlük vade atanıyor...")
        cursor.execute("""
            UPDATE transactions
            SET due_date = DATE(transaction_date, '+30 days')
            WHERE transaction_type = 'KESILEN_FATURA' AND due_date IS NULL
        """)
        conn.commit()
        updated = cursor.rowcount
        print(f"✅ {updated} kesilen faturaya vade tarihi atandı")

    # Kontrol
    cursor.execute("SELECT COUNT(*) FROM transactions WHERE transaction_type = 'KESILEN_FATURA'")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM transactions WHERE transaction_type = 'KESILEN_FATURA' AND due_date IS NOT NULL")
    with_due = cursor.fetchone()[0]
    print(f"📊 Kesilen fatura: {total} adet, vadeli: {with_due} adet")

    conn.close()
    print("✅ Migration tamamlandı!")

except Exception as e:
    print(f"❌ Hata: {str(e)}")
    import traceback
    traceback.print_exc()
    exit(1)
