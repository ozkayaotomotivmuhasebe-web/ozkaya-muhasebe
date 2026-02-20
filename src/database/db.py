from sqlalchemy import create_engine, event
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

def init_db():
    """Tüm tabloları oluştur"""
    Base.metadata.create_all(bind=engine)

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
