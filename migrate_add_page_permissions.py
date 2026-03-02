"""
Migration: kullanici tablosuna yeni sayfa yetkileri kolonlarini ekler.
"""
from src.database.db import SessionLocal
from sqlalchemy import text

COLUMNS = [
    ("can_view_transactions", 0),
    ("can_view_cari_extract", 0),
    ("can_view_payroll", 1),
    ("can_view_employees", 1),
    ("can_view_bulk_payroll", 1),
    ("can_view_payroll_records", 1),
    ("can_view_settings", 1),
    ("can_view_admin_panel", 0),
]


def _column_exists(session, name):
    result = session.execute(text("""
        SELECT COUNT(*)
        FROM pragma_table_info('users')
        WHERE name = :name
    """), {"name": name})
    return result.scalar() > 0


def migrate():
    session = SessionLocal()
    try:
        for name, default in COLUMNS:
            if _column_exists(session, name):
                print(f"✓ {name} kolonu zaten mevcut.")
                continue

            print(f"{name} kolonu ekleniyor...")
            session.execute(text(f"""
                ALTER TABLE users
                ADD COLUMN {name} BOOLEAN DEFAULT {int(default)}
            """))
            session.commit()
            print(f"✓ {name} kolonu eklendi.")

        # Adminlere tum yeni yetkileri ac
        session.execute(text("""
            UPDATE users
            SET
                can_view_transactions = 1,
                can_view_cari_extract = 1,
                can_view_payroll = 1,
                can_view_employees = 1,
                can_view_bulk_payroll = 1,
                can_view_payroll_records = 1,
                can_view_settings = 1,
                can_view_admin_panel = 1
            WHERE role = 'admin'
        """))

        # Normal kullanicilar icin varsayilanlari tamamla
        session.execute(text("""
            UPDATE users
            SET
                can_view_transactions = COALESCE(can_view_transactions, 0),
                can_view_cari_extract = COALESCE(can_view_cari_extract, 0),
                can_view_payroll = COALESCE(can_view_payroll, 1),
                can_view_employees = COALESCE(can_view_employees, 1),
                can_view_bulk_payroll = COALESCE(can_view_bulk_payroll, 1),
                can_view_payroll_records = COALESCE(can_view_payroll_records, 1),
                can_view_settings = COALESCE(can_view_settings, 1),
                can_view_admin_panel = COALESCE(can_view_admin_panel, 0)
            WHERE role != 'admin'
        """))

        session.commit()
        return True
    except Exception as e:
        session.rollback()
        print(f"✗ Hata olustu: {str(e)}")
        return False
    finally:
        session.close()


if __name__ == "__main__":
    print("=" * 60)
    print("Veritabani Migration: Sayfa Yetkileri Ekleme")
    print("=" * 60)
    result = migrate()
    if result:
        print("\n" + "=" * 60)
        print("Migration basariyla tamamlandi!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("Migration basarisiz oldu!")
        print("=" * 60)
