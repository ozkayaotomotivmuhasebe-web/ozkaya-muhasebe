from pathlib import Path
import sys
from PyQt5.QtGui import QIcon


def _base_path() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parents[2]


def get_app_icon_path() -> Path | None:
    base = _base_path()
    for candidate in ["yeni icon.ico", "icon.png", "ICON.ico", "logo.png"]:
        path = base / candidate
        if path.exists():
            return path
    return None


def get_app_icon() -> QIcon:
    icon_path = get_app_icon_path()
    if icon_path:
        return QIcon(str(icon_path))
    return QIcon()
