import os
import sys
from pathlib import Path

# Proje kök dizini
if getattr(sys, "frozen", False):
	PROJECT_ROOT = Path(sys.executable).parent
else:
	PROJECT_ROOT = Path(__file__).parent
DATABASE_DIR = PROJECT_ROOT / "data"

# Veritabanı ayarları
DATABASE_URL = f"sqlite:///{DATABASE_DIR / 'muhasebe.db'}"

# Uygulama ayarları
APP_NAME = "Muhasebe Takip Sistemi"
APP_VERSION = "1.1.10"
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900

# Veritabanı arşivleme
DATABASE_DIR.mkdir(parents=True, exist_ok=True)

# Kullanıcı oturumu
SESSION_TIMEOUT = 1800  # 30 dakika

# ─── Otomatik Güncelleme ───────────────────────────────────────────────────────
# GitHub'da repo oluşturduktan sonra aşağıdaki URL'yi güncelleyin:
# https://raw.githubusercontent.com/GITHUB_KULLANICI/REPO_ADI/main/version.json
UPDATE_CHECK_URL = "https://raw.githubusercontent.com/ozkayaotomotivmuhasebe-web/ozkaya-muhasebe/main/version.json"
UPDATE_ENABLED   = True
