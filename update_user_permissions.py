"""
Mevcut kullanıcıların kredi kartı izinlerini ayarlama scripti
"""
from src.database.db import SessionLocal
from src.database.models import User

def update_existing_users():
    """Mevcut kullanıcıların kredi kartı izinlerini güncelle"""
    session = SessionLocal()
    try:
        users = session.query(User).all()
        
        print(f"\nToplam {len(users)} kullanıcı bulundu.\n")
        
        for user in users:
            # Admin ise tüm yetkileri ver
            if user.role == 'admin':
                user.can_view_credit_cards = True
                print(f"✓ {user.username} (Admin) - Kredi Kartı izni: Evet")
            else:
                # Normal kullanıcılara da varsayılan olarak ver
                if user.can_view_credit_cards is None:
                    user.can_view_credit_cards = True
                print(f"✓ {user.username} (Kullanıcı) - Kredi Kartı izni: {'Evet' if user.can_view_credit_cards else 'Hayır'}")
        
        session.commit()
        print("\n✓ Kullanıcı izinleri başarıyla güncellendi!")
        
        # Kullanıcıların son durumunu göster
        print("\n" + "="*80)
        print("KULLANICI YETKİ DURUMU")
        print("="*80)
        print(f"{'Kullanıcı':<15} {'Rol':<10} {'Dash':<6} {'Fatura':<8} {'Cari':<6} {'Banka':<7} {'Kredi':<7} {'Rapor':<7}")
        print("-"*80)
        
        for user in users:
            print(f"{user.username:<15} {user.role:<10} "
                  f"{'✓' if user.can_view_dashboard else '✗':<6} "
                  f"{'✓' if user.can_view_invoices else '✗':<8} "
                  f"{'✓' if user.can_view_caris else '✗':<6} "
                  f"{'✓' if user.can_view_banks else '✗':<7} "
                  f"{'✓' if user.can_view_credit_cards else '✗':<7} "
                  f"{'✓' if user.can_view_reports else '✗':<7}")
        
        print("="*80)
        
    except Exception as e:
        session.rollback()
        print(f"\n✗ Hata: {str(e)}")
    finally:
        session.close()

if __name__ == "__main__":
    print("="*80)
    print("KULLANICI İZİNLERİNİ GÜNCELLEME")
    print("="*80)
    update_existing_users()
