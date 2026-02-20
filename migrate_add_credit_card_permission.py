"""
Migration: Kullanıcı tablosuna can_view_credit_cards kolonu ekler
"""
from src.database.db import SessionLocal, engine
from sqlalchemy import text

def migrate():
    """Migration'ı çalıştır"""
    session = SessionLocal()
    try:
        # Kolon var mı kontrol et
        result = session.execute(text("""
            SELECT COUNT(*) 
            FROM pragma_table_info('users') 
            WHERE name='can_view_credit_cards'
        """))
        
        exists = result.scalar() > 0
        
        if not exists:
            print("can_view_credit_cards kolonu ekleniyor...")
            session.execute(text("""
                ALTER TABLE users 
                ADD COLUMN can_view_credit_cards BOOLEAN DEFAULT 1
            """))
            session.commit()
            print("✓ can_view_credit_cards kolonu başarıyla eklendi!")
            print("✓ Tüm kullanıcılar için varsayılan olarak True olarak ayarlandı.")
        else:
            print("✓ can_view_credit_cards kolonu zaten mevcut.")
        
        return True
    except Exception as e:
        session.rollback()
        print(f"✗ Hata oluştu: {str(e)}")
        return False
    finally:
        session.close()

if __name__ == "__main__":
    print("=" * 60)
    print("Veritabanı Migration: Kredi Kartı İzni Ekleme")
    print("=" * 60)
    
    result = migrate()
    
    if result:
        print("\n" + "=" * 60)
        print("Migration başarıyla tamamlandı!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("Migration başarısız oldu!")
        print("=" * 60)
