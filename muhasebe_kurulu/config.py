import os
from pathlib import Path

# Proje kök dizini
PROJECT_ROOT = Path(__file__).parent
DATABASE_DIR = PROJECT_ROOT / "data"

# Veritabanı ayarları
DATABASE_URL = f"sqlite:///{DATABASE_DIR / 'muhasebe.db'}"

# Uygulama ayarları
APP_NAME = "Muhasebe Takip Sistemi"
APP_VERSION = "1.0.0"
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900

# Veritabanı arşivleme
DATABASE_DIR.mkdir(exist_ok=True)

# Kullanıcı oturumu
SESSION_TIMEOUT = 1800  # 30 dakika
