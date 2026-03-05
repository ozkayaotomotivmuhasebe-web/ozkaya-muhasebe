from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, scoped_session, Session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
import config
from .models import Base

# Optimized engine - Connection pooling ve caching
engine = create_engine(
    config.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False,
    connect_args={
        'check_same_thread': False,
        'timeout': 30
    }
)

# SQLite optimizasyonları
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.execute("PRAGMA cache_size=10000")
    cursor.execute("PRAGMA temp_store=MEMORY")
    cursor.close()

# SessionLocal oluştur
SessionLocal = scoped_session(sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
))

def _run_migrations():
    """Eksik sütunları otomatik ekle"""
    with engine.connect() as conn:
        # credit_cards.parent_card_id
        try:
            conn.execute(text("SELECT parent_card_id FROM credit_cards LIMIT 1"))
        except Exception:
            try:
                conn.execute(text("ALTER TABLE credit_cards ADD COLUMN parent_card_id INTEGER REFERENCES credit_cards(id)"))
                conn.commit()
            except Exception:
                pass

        # transactions.due_date
        try:
            conn.execute(text("SELECT due_date FROM transactions LIMIT 1"))
        except Exception:
            try:
                conn.execute(text("ALTER TABLE transactions ADD COLUMN due_date DATE"))
                conn.commit()
            except Exception:
                pass

        # transactions.is_paid
        try:
            conn.execute(text("SELECT is_paid FROM transactions LIMIT 1"))
        except Exception:
            try:
                conn.execute(text("ALTER TABLE transactions ADD COLUMN is_paid BOOLEAN NOT NULL DEFAULT 0"))
                conn.commit()
            except Exception:
                pass

        # transactions.paid_date
        try:
            conn.execute(text("SELECT paid_date FROM transactions LIMIT 1"))
        except Exception:
            try:
                conn.execute(text("ALTER TABLE transactions ADD COLUMN paid_date DATE"))
                conn.commit()
            except Exception:
                pass

        # transactions.paid_amount
        try:
            conn.execute(text("SELECT paid_amount FROM transactions LIMIT 1"))
        except Exception:
            try:
                conn.execute(text("ALTER TABLE transactions ADD COLUMN paid_amount REAL NOT NULL DEFAULT 0.0"))
                conn.commit()
            except Exception:
                pass

def init_db():
    """Tüm tabloları oluştur"""
    Base.metadata.create_all(bind=engine)
    _run_migrations()

def get_db() -> Session:
    """Veritabanı session'ı al"""
    return SessionLocal()

@contextmanager
def session_scope():
    """Context manager ile session yönetimi"""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def close_db():
    """Veritabanı bağlantısını kapat"""
    SessionLocal.remove()
    engine.dispose()
